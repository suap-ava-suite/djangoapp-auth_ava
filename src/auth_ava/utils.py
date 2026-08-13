import datetime
import logging
from typing import Any, Dict, List, Optional, Tuple

from .choices import TipoEmail

logger = logging.getLogger(__name__)


def parse_suap_date(val: Optional[str]) -> Optional[datetime.date]:
    """Converte strings de data retornadas pelo SUAP para datetime.date."""
    if not val or not isinstance(val, str):
        return None
    val = val.strip()
    if not val or val == "-":
        return None

    formats = ["%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"]
    for fmt in formats:
        try:
            return datetime.datetime.strptime(val, fmt).date()
        except ValueError:
            continue
    return None


def extract_user_emails(user_info: Dict[str, Any]) -> List[Tuple[str, str]]:
    """Extrai pares (tipo, email) dos múltiplos campos retornados pelo SUAP.

    Garante unicidade e remove e-mails vazios ou marcados com hífen.
    """
    field_to_type = {
        "email_preferencial": TipoEmail.PREFERENCIAL,
        "email": TipoEmail.CORPORATIVO,
        "email_secundario": TipoEmail.PESSOAL,
        "email_google_classroom": TipoEmail.GOOGLE_CLASSROOM,
        "email_academico": TipoEmail.ACADEMICO,
        "email_escolar": TipoEmail.ESCOLAR,
    }

    seen = set()
    extracted: List[Tuple[str, str]] = []

    for field, tipo in field_to_type.items():
        raw_email = user_info.get(field)
        if raw_email and isinstance(raw_email, str):
            email = raw_email.strip().lower()
            if email and email != "-" and "@" in email:
                key = (tipo, email)
                if key not in seen:
                    seen.add(key)
                    extracted.append((tipo, email))

    # Também inspeciona dicionários aninhados se houver
    raw_responses = user_info.get("_raw_responses", {})
    if isinstance(raw_responses, dict):
        for endpoint, data in raw_responses.items():
            if isinstance(data, dict):
                for field, tipo in field_to_type.items():
                    raw_email = data.get(field)
                    if raw_email and isinstance(raw_email, str):
                        email = raw_email.strip().lower()
                        if email and email != "-" and "@" in email:
                            key = (tipo, email)
                            if key not in seen:
                                seen.add(key)
                                extracted.append((tipo, email))

    return extracted
