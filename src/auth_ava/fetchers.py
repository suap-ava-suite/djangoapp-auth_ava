import logging
from typing import Any, Dict, List, Optional

from django_suap_auth.exceptions import SuapUserInfoError
from django_suap_auth.fetchers import BaseUserInfoFetcher

logger = logging.getLogger(__name__)

PRIMARY_ENDPOINT = "/api/rh/eu/"
DEFAULT_SECONDARY_ENDPOINTS = [
    "/api/rh/meus-vinculos/",
    "/api/rh/meus-dados/",
    "/api/ensino/meus-dados-aluno/",
    "/api/ensino/periodos/",
]


class AvaUserInfoFetcher(BaseUserInfoFetcher):
    """Fetcher do ecossistema AVA que consome os endpoints do SUAP com tolerância a falhas.

    - `/api/rh/eu/` é obrigatório (identificação primária e dados essenciais).
    - `/api/rh/meus-vinculos/`, `/api/rh/meus-dados/`, `/api/ensino/meus-dados-aluno/` e
      `/api/ensino/periodos/` são tolerantes a falhas: se falharem (ex: 403/404 para alunos
      tentando dados de RH ou servidores tentando dados de aluno), o erro é registrado no
      payload para auditoria sem interromper a autenticação do usuário.
    """

    def fetch(self, client, access_token: str, user_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if user_info is None:
            user_info = {}

        raw_responses: Dict[str, Any] = {}
        errors: List[Dict[str, Any]] = []

        # 1. Endpoint obrigatório: /api/rh/eu/
        try:
            eu_data = client.get_endpoint_data(access_token, PRIMARY_ENDPOINT)
            if isinstance(eu_data, dict):
                raw_responses[PRIMARY_ENDPOINT] = eu_data
                user_info.update(eu_data)
            else:
                raw_responses[PRIMARY_ENDPOINT] = {"data": eu_data}
        except Exception as exc:
            logger.error("Falha ao obter dados obrigatórios do SUAP em '%s': %s", PRIMARY_ENDPOINT, exc)
            if isinstance(exc, SuapUserInfoError):
                raise
            raise SuapUserInfoError(f"Falha no endpoint obrigatório '{PRIMARY_ENDPOINT}': {exc}") from exc

        # 2. Endpoints secundários tolerantes a falhas
        secondary_endpoints = self.suap_settings.get("ava_secondary_endpoints", DEFAULT_SECONDARY_ENDPOINTS)

        for endpoint in secondary_endpoints:
            try:
                data = client.get_endpoint_data(access_token, endpoint)
                raw_responses[endpoint] = data

                # Se o endpoint trouxer dados úteis diretamente, mescla campos que não conflitem
                if isinstance(data, dict):
                    # Se for meus-dados, preserva campos que não existiam
                    for k, v in data.items():
                        if k not in user_info and v not in (None, "", "-"):
                            user_info[k] = v

            except Exception as exc:
                status_code = getattr(getattr(exc, "response", None), "status_code", None)
                msg = str(exc)
                logger.info(
                    "Endpoint secundário '%s' retornou status %s / erro: %s",
                    endpoint,
                    status_code,
                    msg,
                )
                raw_responses[endpoint] = {"error": msg, "status_code": status_code}
                errors.append(
                    {
                        "endpoint": endpoint,
                        "status_code": status_code,
                        "error": msg,
                    }
                )

        user_info["_raw_responses"] = raw_responses
        user_info["_errors"] = errors

        return user_info
