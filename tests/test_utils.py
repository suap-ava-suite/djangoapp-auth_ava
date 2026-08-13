import datetime

from auth_ava.choices import TipoEmail
from auth_ava.utils import extract_user_emails, parse_suap_date


def test_parse_suap_date():
    assert parse_suap_date("1990-05-15") == datetime.date(1990, 5, 15)
    assert parse_suap_date("15/05/1990") == datetime.date(1990, 5, 15)
    assert parse_suap_date("1990/05/15") == datetime.date(1990, 5, 15)
    assert parse_suap_date("") is None
    assert parse_suap_date("-") is None
    assert parse_suap_date(None) is None
    assert parse_suap_date("invalid-date") is None


def test_extract_user_emails():
    info = {
        "email_preferencial": "pref@ifrn.edu.br",
        "email": "corp@ifrn.edu.br",
        "email_secundario": "pessoal@gmail.com",
        "email_google_classroom": "classroom@escolar.ifrn.edu.br",
        "email_academico": "acad@academico.ifrn.edu.br",
        "email_escolar": "-",
        "_raw_responses": {
            "/api/ensino/meus-dados-aluno/": {
                "email_escolar": "aluno.escolar@escolar.ifrn.edu.br",
                "email_academico": "-",
            },
            "/api/ensino/periodos/": ["lista-nao-dict"],
        },
    }
    extracted = extract_user_emails(info)
    assert (TipoEmail.PREFERENCIAL, "pref@ifrn.edu.br") in extracted
    assert (TipoEmail.CORPORATIVO, "corp@ifrn.edu.br") in extracted
    assert (TipoEmail.PESSOAL, "pessoal@gmail.com") in extracted
    assert (TipoEmail.GOOGLE_CLASSROOM, "classroom@escolar.ifrn.edu.br") in extracted
    assert (TipoEmail.ACADEMICO, "acad@academico.ifrn.edu.br") in extracted
    assert (TipoEmail.ESCOLAR, "aluno.escolar@escolar.ifrn.edu.br") in extracted
    assert len(extracted) == 6

    # Testa deduplicação e case insensitive
    info2 = {
        "email_preferencial": "Same@ifrn.edu.br",
        "_raw_responses": {"/api/rh/eu/": {"email_preferencial": "same@ifrn.edu.br"}},
    }
    extracted2 = extract_user_emails(info2)
    assert len(extracted2) == 1
    assert extracted2[0] == (TipoEmail.PREFERENCIAL, "same@ifrn.edu.br")
