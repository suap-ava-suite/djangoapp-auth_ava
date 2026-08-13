from unittest.mock import MagicMock

import pytest
from django_suap_auth.exceptions import SuapUserInfoError

from auth_ava.fetchers import AvaUserInfoFetcher


class TestAvaUserInfoFetcher:
    def test_fetch_success_all_endpoints(self):
        client = MagicMock()

        def mock_get_endpoint_data(access_token, path):
            if path == "/api/rh/eu/":
                return {
                    "identificacao": "1234567",
                    "nome_registro": "Fulano da Silva",
                    "nome_usual": "Fulano",
                    "email_preferencial": "fulano@ifrn.edu.br",
                    "campus": "CNAT",
                }
            elif path == "/api/rh/meus-vinculos/":
                return {
                    "results": [
                        {
                            "id": 1,
                            "identificador": "1234567",
                            "tipo": "servidor",
                            "campus": "CNAT",
                            "detalhamento": {"cargo": "Professor", "ativo": True},
                        }
                    ]
                }
            elif path == "/api/rh/meus-dados/":
                return {
                    "cpf": "000.000.000-00",
                    "naturalidade": "Natal/RN",
                    "vinculo": {"matricula": "1234567", "campus": "CNAT"},
                }
            elif path == "/api/ensino/meus-dados-aluno/":
                return {"curso": "TADS", "ira": "90.0"}
            elif path == "/api/ensino/periodos/":
                return {"results": [{"id": 10, "semestre": "2024.1"}]}
            return {}

        client.get_endpoint_data.side_effect = mock_get_endpoint_data

        fetcher = AvaUserInfoFetcher()
        result = fetcher.fetch(client, "fake-token")

        assert result["identificacao"] == "1234567"
        assert result["nome_usual"] == "Fulano"
        assert result["cpf"] == "000.000.000-00"
        assert result["curso"] == "TADS"
        assert "_raw_responses" in result
        assert "/api/rh/eu/" in result["_raw_responses"]
        assert "/api/rh/meus-vinculos/" in result["_raw_responses"]
        assert len(result["_errors"]) == 0

    def test_fetch_primary_not_dict(self):
        client = MagicMock()
        client.get_endpoint_data.return_value = ["item1", "item2"]

        fetcher = AvaUserInfoFetcher()
        result = fetcher.fetch(client, "fake-token")
        assert result["_raw_responses"]["/api/rh/eu/"] == {"data": ["item1", "item2"]}

    def test_fetch_failure_primary_endpoint_raises_suap_error(self):
        client = MagicMock()
        client.get_endpoint_data.side_effect = SuapUserInfoError("SUAP Indisponível")

        fetcher = AvaUserInfoFetcher()
        with pytest.raises(SuapUserInfoError):
            fetcher.fetch(client, "fake-token")

    def test_fetch_failure_primary_endpoint_raises_generic_error(self):
        client = MagicMock()
        client.get_endpoint_data.side_effect = RuntimeError("Erro de conexão socket")

        fetcher = AvaUserInfoFetcher()
        with pytest.raises(SuapUserInfoError) as exc_info:
            fetcher.fetch(client, "fake-token")
        assert "Falha no endpoint obrigatório" in str(exc_info.value)

    def test_fetch_resilience_secondary_endpoints_fail(self):
        client = MagicMock()

        def mock_get_endpoint_data(access_token, path):
            if path == "/api/rh/eu/":
                return {
                    "identificacao": "aluno123",
                    "nome_registro": "Aluno Exemplo",
                    "email_preferencial": "aluno@ifrn.edu.br",
                    "campus": "CAL",
                }
            elif path == "/api/rh/meus-vinculos/":
                return {"results": []}
            elif path == "/api/rh/meus-dados/":
                raise SuapUserInfoError("403 Forbidden: Usuário não é servidor")
            elif path == "/api/ensino/meus-dados-aluno/":
                return {"curso": "Informática", "ingresso": "2024/1"}
            elif path == "/api/ensino/periodos/":
                raise Exception("500 Internal Error")
            return {}

        client.get_endpoint_data.side_effect = mock_get_endpoint_data

        fetcher = AvaUserInfoFetcher()
        result = fetcher.fetch(client, "fake-token")

        assert result["identificacao"] == "aluno123"
        assert result["curso"] == "Informática"
        assert len(result["_errors"]) == 2
        endpoints_with_errors = [e["endpoint"] for e in result["_errors"]]
        assert "/api/rh/meus-dados/" in endpoints_with_errors
        assert "/api/ensino/periodos/" in endpoints_with_errors
