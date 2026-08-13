import pytest
from django.db import IntegrityError

from auth_ava.choices import TipoEmail, TipoUsuario, TipoVinculo
from auth_ava.models import EmailUsuario, SincronizacaoErro, Usuario, UsuarioAuditData, VinculoUsuario


@pytest.mark.django_db
class TestUsuarioModel:
    def test_create_usuario_basico(self):
        user = Usuario.objects.create(
            username="1234567",
            first_name="João",
            last_name="Silva",
            email="joao.silva@ifrn.edu.br",
            nome_usual="João Silva",
            tipo_usuario=TipoUsuario.TECNICO,
            campus="CNAT",
        )
        assert user.pk is not None
        assert str(user) == "João Silva [1234567]"
        assert user.show_name == "João Silva"
        assert user.campus_sigla == "CNAT"
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_show_name_fallbacks(self):
        user1 = Usuario.objects.create(username="u1", nome_social="Maria Social")
        assert user1.show_name == "Maria Social"

        user2 = Usuario.objects.create(username="u2", first_name="Carlos", last_name="Medeiros")
        assert user2.show_name == "Carlos Medeiros"

        user3 = Usuario.objects.create(username="u3")
        assert user3.show_name == "u3"

    def test_foto_url(self):
        user_sem_foto = Usuario.objects.create(username="u_nofoto")
        assert user_sem_foto.foto_url.endswith("img/user.png")

        user_rel = Usuario.objects.create(username="u_rel", foto="/media/fotos/123.jpg")
        assert user_rel.foto_url == "https://suap.ifrn.edu.br/media/fotos/123.jpg"

        user_abs = Usuario.objects.create(username="u_abs", foto="https://cdn.example.com/foto.png")
        assert user_abs.foto_url == "https://cdn.example.com/foto.png"

    def test_settings_properties(self):
        user_default = Usuario.objects.create(username="u_default", campus="")
        assert user_default.campus_sigla == ""
        assert user_default.theme_selected == "dsgovbr"
        assert user_default.dyslexia_friendly is False
        assert user_default.vlibras_active is True

        user_custom = Usuario.objects.create(
            username="u_custom",
            settings={
                "theme": {"selected": "ifrn25"},
                "accessibility": {"dyslexia_friendly": True, "vlibras_active": False},
            },
        )
        assert user_custom.theme_selected == "ifrn25"
        assert user_custom.dyslexia_friendly is True
        assert user_custom.vlibras_active is False

        # Settings não dict
        user_invalid_settings = Usuario.objects.create(username="u_inv", settings="invalid")
        assert user_invalid_settings.theme_selected == "dsgovbr"
        assert user_invalid_settings.dyslexia_friendly is False
        assert user_invalid_settings.vlibras_active is True

    def test_history_creation(self):
        user = Usuario.objects.create(username="u_history", first_name="Nome 1")
        assert user.history.count() == 1
        user.first_name = "Nome 2"
        user.save()
        assert user.history.count() == 2


@pytest.mark.django_db
class TestEmailUsuarioModel:
    def test_create_emails(self):
        user = Usuario.objects.create(username="u_email")
        e1 = EmailUsuario.objects.create(
            usuario=user,
            tipo=TipoEmail.PREFERENCIAL,
            email="pref@ifrn.edu.br",
        )
        e2 = EmailUsuario.objects.create(
            usuario=user,
            tipo=TipoEmail.PESSOAL,
            email="pessoal@gmail.com",
        )
        assert str(e1) == "pref@ifrn.edu.br (Preferencial)"
        assert e2.email == "pessoal@gmail.com"
        assert user.emails.count() == 2

    def test_unique_together_constraint(self):
        user = Usuario.objects.create(username="u_email_unique")
        EmailUsuario.objects.create(
            usuario=user,
            tipo=TipoEmail.CORPORATIVO,
            email="corp@ifrn.edu.br",
        )
        with pytest.raises(IntegrityError):
            EmailUsuario.objects.create(
                usuario=user,
                tipo=TipoEmail.CORPORATIVO,
                email="corp@ifrn.edu.br",
            )


@pytest.mark.django_db
class TestVinculoUsuarioModel:
    def test_create_vinculo(self):
        user = Usuario.objects.create(username="u_vinc")
        v = VinculoUsuario.objects.create(
            usuario=user,
            suap_id=159509,
            identificador="1234567",
            tipo=TipoVinculo.SERVIDOR,
            campus="CNAT",
            ativo=True,
            cargo="ANALISTA DE TI",
            categoria="Técnico Administrativo",
            detalhamento={"jornada": "40h"},
        )
        assert v.pk is not None
        assert str(v) == "Servidor - 1234567 (CNAT)"
        assert user.vinculos.count() == 1

        v2 = VinculoUsuario.objects.create(
            usuario=user,
            suap_id=999,
            identificador="",
            tipo=TipoVinculo.ALUNO,
            campus="",
        )
        assert str(v2) == "Aluno - 999 ()"


@pytest.mark.django_db
class TestUsuarioAuditDataModel:
    def test_create_audit_data(self):
        user = Usuario.objects.create(username="u_audit")
        payload = {"/api/rh/eu/": {"identificacao": "u_audit"}}
        audit = UsuarioAuditData.objects.create(usuario=user, last_json=payload)
        assert audit.last_json == payload
        assert "Auditoria de u_audit" in str(audit)


@pytest.mark.django_db
class TestSincronizacaoErroModel:
    def test_create_erro(self):
        user = Usuario.objects.create(username="u_erro")
        err = SincronizacaoErro.objects.create(
            usuario=user,
            endpoint="/api/ensino/meus-dados-aluno/",
            status_code=403,
            mensagem_erro="Acesso negado",
        )
        assert err.pk is not None
        assert "Erro em /api/ensino/meus-dados-aluno/ [403]" in str(err)
