import pytest
from django.contrib.auth import authenticate

from auth_ava.choices import TipoEmail
from auth_ava.models import Usuario


@pytest.mark.django_db
class TestAvaAuthBackend:
    def test_authenticate_new_user(self):
        user_info = {
            "identificacao": "20241010",
            "nome_registro": "Aluno da Silva Sauro",
            "nome_usual": "Silva Sauro",
            "email_preferencial": "sauro@academico.ifrn.edu.br",
            "email_secundario": "sauro@gmail.com",
            "cpf": "111.222.333-44",
            "tipo_usuario": "Aluno",
            "campus": "CNAT",
            "_raw_responses": {
                "/api/rh/eu/": {
                    "identificacao": "20241010",
                    "nome_registro": "Aluno da Silva Sauro",
                    "nome_usual": "Silva Sauro",
                },
                "/api/rh/meus-vinculos/": {
                    "results": [
                        {
                            "id": 9991,
                            "identificador": "20241010",
                            "tipo": "aluno",
                            "campus": "CNAT",
                            "detalhamento": {
                                "curso": "TADS",
                                "ativo": True,
                                "modalidade": "Presencial",
                                "nivel_ensino": "Superior",
                            },
                        },
                        {
                            # Vínculo sem suap_id mas com identificador
                            "identificador": "20241010-B",
                            "tipo": "aluno",
                            "campus": "CNAT",
                            "detalhamento": None,
                        },
                        {
                            # Item inválido / sem identificador e sem id
                            "detalhamento": {},
                        },
                        "item-invalido-string",
                    ]
                },
            },
            "_errors": [
                {
                    "endpoint": "/api/rh/meus-dados/",
                    "status_code": 403,
                    "error": "Não permitido",
                }
            ],
        }

        user = authenticate(request=None, suap_user_info=user_info)

        assert user is not None
        assert isinstance(user, Usuario)
        assert user.username == "20241010"
        assert user.nome_usual == "Silva Sauro"
        assert user.cpf == "111.222.333-44"
        assert user.first_login is not None
        assert user.is_staff is False
        assert user.is_superuser is False

        # Verifica Auditoria
        assert hasattr(user, "audit_data")
        assert "/api/rh/eu/" in user.audit_data.last_json

        # Verifica Emails normalizados
        assert user.emails.count() == 2
        pref_email = user.emails.filter(tipo=TipoEmail.PREFERENCIAL).first()
        assert pref_email.email == "sauro@academico.ifrn.edu.br"

        # Verifica Vínculos normalizados
        assert user.vinculos.count() == 2
        vinc = user.vinculos.filter(suap_id=9991).first()
        assert vinc.curso == "TADS"
        assert vinc.ativo is True

        # Verifica Erros registrados
        assert user.erros_sincronizacao.count() == 1
        err = user.erros_sincronizacao.first()
        assert err.endpoint == "/api/rh/meus-dados/"
        assert err.status_code == 403

    def test_authenticate_existing_user_updates_data(self):
        user = Usuario.objects.create(
            username="servidor123",
            first_name="Antigo",
            nome_usual="Nome Antigo",
            email="antigo@ifrn.edu.br",
        )

        user_info = {
            "identificacao": "servidor123",
            "primeiro_nome": "Novo",
            "ultimo_nome": "Servidor",
            "nome_usual": "Nome Novo",
            "email_preferencial": "novo@ifrn.edu.br",
            "tipo_usuario": "Servidor (Docente)",
            "campus": "PAR",
            "_raw_responses": {
                "/api/rh/meus-dados/": {
                    "vinculo": {
                        "id": 555,
                        "matricula": "servidor123",
                        "campus": "PAR",
                        "cargo": "Professor EBTT",
                        "matricula_regular": True,
                    }
                }
            },
        }

        updated_user = authenticate(request=None, suap_user_info=user_info)
        assert updated_user.pk == user.pk
        assert updated_user.nome_usual == "Nome Novo"
        assert updated_user.tipo_usuario == "Servidor (Docente)"
        assert updated_user.campus == "PAR"

        # Verifica vínculo de servidor extraído de meus-dados
        assert updated_user.vinculos.count() == 1
        v = updated_user.vinculos.first()
        assert v.suap_id == 555
        assert v.cargo == "Professor EBTT"

    def test_authenticate_rh_data_sem_suap_id_mas_com_matricula(self):
        user_info = {
            "matricula": "servidor_no_id",
            "nome_registro": "Servidor Sem Id",
            "email": "servidor@ifrn.edu.br",
            "_raw_responses": {
                "/api/rh/meus-dados/": {
                    "vinculo": {
                        "matricula": "servidor_no_id",
                        "campus": "SGA",
                        "cargo": "Assistente em Administração",
                    }
                }
            },
        }

        user = authenticate(request=None, suap_user_info=user_info)
        assert user.username == "servidor_no_id"
        assert user.vinculos.count() == 1
        assert user.vinculos.first().identificador == "servidor_no_id"

    def test_authenticate_fallback_raw_responses(self):
        # Sem _raw_responses no payload
        user_info = {
            "identificacao": "fallback_user",
            "nome_registro": "Fallback User",
        }
        user = authenticate(request=None, suap_user_info=user_info)
        assert user.audit_data.last_json == {"/api/rh/eu/": user_info}

    def test_authenticate_invalid_payloads(self):
        assert authenticate(request=None, suap_user_info=None) is None
        assert authenticate(request=None, suap_user_info={}) is None
        assert authenticate(request=None, suap_user_info="string-invalid") is None
        assert authenticate(request=None, suap_user_info={"sem_identificacao": "123"}) is None
