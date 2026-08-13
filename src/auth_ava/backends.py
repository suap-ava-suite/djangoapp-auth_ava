import logging
from typing import Any, Dict

from django.db import transaction
from django.utils import timezone
from django_suap_auth.backends import SuapAuthBackend

from .models import EmailUsuario, SincronizacaoErro, Usuario, UsuarioAuditData, VinculoUsuario
from .utils import extract_user_emails, parse_suap_date

logger = logging.getLogger(__name__)


class AvaAuthBackend(SuapAuthBackend):
    """Backend de autenticação do AVA integrado com SUAP OAuth2 e normalização de dados."""

    def authenticate(self, request, suap_user_info: Any = None, **kwargs):
        if suap_user_info is None or not isinstance(suap_user_info, dict):
            return None

        username = suap_user_info.get("identificacao") or suap_user_info.get("matricula")
        if not username:
            logger.warning("Falha na autenticação: campo 'identificacao' ou 'matricula' ausente no retorno do SUAP.")
            return None

        username = str(username).strip()

        with transaction.atomic():
            user, created = self._sync_usuario(username, suap_user_info)
            self._sync_audit_data(user, suap_user_info)
            self._sync_emails(user, suap_user_info)
            self._sync_vinculos(user, suap_user_info)
            self._sync_errors(user, suap_user_info)

        return user

    def _sync_usuario(self, username: str, user_info: Dict[str, Any]) -> tuple[Usuario, bool]:
        """Cria ou atualiza os dados cadastrais do modelo Usuario."""
        first_name = user_info.get("primeiro_nome")
        last_name = user_info.get("ultimo_nome")

        nome_registro = user_info.get("nome_registro") or user_info.get("nome")
        if not first_name and nome_registro:
            parts = nome_registro.strip().split(" ", 1)
            first_name = parts[0]
            if len(parts) > 1 and not last_name:
                last_name = parts[1]

        data_nascimento = parse_suap_date(user_info.get("data_de_nascimento") or user_info.get("data_nascimento"))

        email = user_info.get("email_preferencial") or user_info.get("email") or f"{username}@ifrn.edu.br"

        defaults = {
            "first_name": (first_name or "")[:150],
            "last_name": (last_name or "")[:150],
            "email": email,
            "nome_registro": user_info.get("nome_registro") or "",
            "nome_social": user_info.get("nome_social") or "",
            "nome_usual": user_info.get("nome_usual") or "",
            "nome": user_info.get("nome") or "",
            "tipo_usuario": user_info.get("tipo_usuario") or "Desconhecido",
            "foto": user_info.get("foto") or user_info.get("url_foto_150x200") or "",
            "cpf": user_info.get("cpf") or "",
            "rg": user_info.get("rg") or "",
            "passaporte": user_info.get("passaporte") or "",
            "data_nascimento": data_nascimento,
            "sexo": user_info.get("sexo") or "",
            "naturalidade": user_info.get("naturalidade") or "",
            "campus": user_info.get("campus") or "",
        }

        user = Usuario.objects.filter(username=username).first()
        created = False

        if user is None:
            created = True
            user = Usuario.objects.create(
                username=username,
                is_staff=False,
                is_superuser=False,
                is_active=True,
                first_login=timezone.now(),
                **defaults,
            )
        else:
            if user.first_login is None:
                user.first_login = timezone.now()
            for key, value in defaults.items():
                if value is not None:
                    setattr(user, key, value)
            user.save()

        return user, created

    def _sync_audit_data(self, user: Usuario, user_info: Dict[str, Any]) -> None:
        """Armazena o payload bruto dos endpoints consultados para auditoria e debug."""
        raw_responses = user_info.get("_raw_responses", {})
        if not raw_responses:
            # Fallback caso não venha pelo fetcher
            raw_responses = {"/api/rh/eu/": user_info}

        UsuarioAuditData.objects.update_or_create(
            usuario=user,
            defaults={"last_json": raw_responses},
        )

    def _sync_emails(self, user: Usuario, user_info: Dict[str, Any]) -> None:
        """Normaliza e sincroniza os múltiplos e-mails do usuário."""
        emails = extract_user_emails(user_info)
        for tipo, email_addr in emails:
            EmailUsuario.objects.get_or_create(
                usuario=user,
                tipo=tipo,
                email=email_addr,
            )

    def _sync_vinculos(self, user: Usuario, user_info: Dict[str, Any]) -> None:
        """Normaliza e sincroniza todos os vínculos encontrados nos retornos do SUAP."""
        raw_responses = user_info.get("_raw_responses", {})

        # 1. Processa lista de /api/rh/meus-vinculos/
        vinc_data = raw_responses.get("/api/rh/meus-vinculos/")
        if isinstance(vinc_data, dict) and "results" in vinc_data and isinstance(vinc_data["results"], list):
            for item in vinc_data["results"]:
                if not isinstance(item, dict):
                    continue
                suap_id = item.get("id")
                identificador = item.get("identificador")
                tipo = item.get("tipo")
                campus = item.get("campus")
                estrangeiro = bool(item.get("estrangeiro", False))
                detalhamento = item.get("detalhamento") or {}

                ativo = True
                cargo = ""
                categoria = ""
                curso = ""
                modalidade = ""
                nivel_ensino = ""
                situacao = ""

                if isinstance(detalhamento, dict):
                    ativo = bool(detalhamento.get("ativo", True))
                    cargo = detalhamento.get("cargo") or ""
                    categoria = detalhamento.get("categoria") or ""
                    curso = detalhamento.get("curso") or ""
                    modalidade = detalhamento.get("modalidade") or ""
                    nivel_ensino = detalhamento.get("nivel_ensino") or ""
                    situacao = detalhamento.get("situacao_diario") or detalhamento.get("situacao") or ""

                lookup = {"usuario": user}
                if suap_id:
                    lookup["suap_id"] = suap_id
                elif identificador:
                    lookup["identificador"] = identificador
                else:
                    continue

                defaults = {
                    "identificador": identificador or "",
                    "tipo": tipo or "",
                    "campus": campus or "",
                    "ativo": ativo,
                    "cargo": cargo,
                    "categoria": categoria,
                    "curso": curso,
                    "modalidade": modalidade,
                    "nivel_ensino": nivel_ensino,
                    "situacao": situacao,
                    "estrangeiro": estrangeiro,
                    "detalhamento": detalhamento,
                }
                VinculoUsuario.objects.update_or_create(**lookup, defaults=defaults)

        # 2. Processa vínculo de /api/rh/meus-dados/ caso não tenha vindo no anterior
        rh_data = raw_responses.get("/api/rh/meus-dados/")
        if isinstance(rh_data, dict) and isinstance(rh_data.get("vinculo"), dict):
            v = rh_data["vinculo"]
            suap_id = v.get("id")
            matricula = v.get("matricula")
            if suap_id or matricula:
                lookup = {"usuario": user}
                if suap_id:
                    lookup["suap_id"] = suap_id
                else:
                    lookup["identificador"] = matricula

                defaults = {
                    "identificador": matricula or "",
                    "tipo": "servidor",
                    "campus": v.get("campus") or "",
                    "ativo": bool(v.get("matricula_regular", True)),
                    "cargo": v.get("cargo") or "",
                    "categoria": v.get("categoria") or "",
                    "curso": v.get("curso") or "",
                    "situacao": v.get("situacao") or v.get("situacao_sistemica") or "",
                    "detalhamento": v,
                }
                VinculoUsuario.objects.update_or_create(**lookup, defaults=defaults)

    def _sync_errors(self, user: Usuario, user_info: Dict[str, Any]) -> None:
        """Registra falhas secundárias de comunicação para diagnóstico e auditoria."""
        errors = user_info.get("_errors", [])
        for err in errors:
            if isinstance(err, dict) and "endpoint" in err and "error" in err:
                SincronizacaoErro.objects.create(
                    usuario=user,
                    endpoint=err["endpoint"],
                    status_code=err.get("status_code"),
                    mensagem_erro=err["error"],
                )
