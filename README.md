# django-auth-ava

[![PyPI Version](https://img.shields.io/pypi/v/django-auth-ava)](https://pypi.org/project/django-auth-ava/)
[![Tests](https://github.com/suap-ava-suite/djangoapp-auth_ava/actions/workflows/test.yml/badge.svg)](https://github.com/suap-ava-suite/djangoapp-auth_ava/actions/workflows/test.yml)
[![Python Versions](https://img.shields.io/pypi/pyversions/django-auth-ava.svg)](https://pypi.org/project/django-auth-ava/)
[![Django Versions](https://img.shields.io/badge/django-5.2%20|%206.0-blue)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Coverage](https://codecov.io/gh/suap-ava-suite/djangoapp-auth_ava/branch/main/graph/badge.svg)](https://codecov.io/gh/suap-ava-suite/djangoapp-auth_ava)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

App Django com modelos concretos e normalizados para autenticação e sincronização de dados do **SUAP** (Sistema Unificado de Administração Pública) no ecossistema do **AVA** (Ambiente Virtual de Aprendizagem).

Construído sobre o [`django-suap-auth`](https://pypi.org/project/django-suap-auth/), este pacote unifica a estrutura de usuários, múltiplos e-mails, vínculos, histórico e inlines do Django Admin para reutilização em projetos como `painel_ava` e `integrador_ava`.

---

## Recursos

- **Modelo Concreto de Usuário**: `Usuario` estende `AbstractUser` com `django-simple-history` (`HistoricalRecords`), sem o overhead de performance do `SafeDeleteModel`.
- **Múltiplos E-mails Normalizados (1xN)**: Tabela `EmailUsuario` para suportar dinamicamente novos tipos de e-mails do SUAP (`preferencial`, `pessoal`, `corporativo`, `google_classroom`, `academico`, `escolar`, etc.).
- **Vínculos Normalizados (1xN)**: Tabela `VinculoUsuario` com detalhamento de campus, cargos, cursos e status ativo.
- **Tolerância a Falhas nas APIs do SUAP**: O `AvaUserInfoFetcher` realiza chamadas com resiliência:
  - `/api/rh/eu/` (**Obrigatório**)
  - `/api/rh/meus-vinculos/` (**Tolerante a falhas**)
  - `/api/rh/meus-dados/` (**Tolerante a falhas**)
  - `/api/ensino/meus-dados-aluno/` (**Tolerante a falhas**)
  - `/api/ensino/periodos/` (**Tolerante a falhas**)
- **Auditoria e Debug (1x1)**: Tabela `UsuarioAuditData` armazena o mapa bruto consolidado dos endpoints em `last_json`.
- **Registro de Falhas (1xN)**: Tabela `SincronizacaoErro` para diagnósticos sem interromper o login do usuário.
- **Django Admin Pronto**: Inlines estruturados para e-mails, vínculos, auditoria e erros com compatibilidade ao `admintheme-dsgovbr`.

---

## Instalação

```bash
uv add django-auth-ava
# ou com pip:
pip install django-auth-ava
```

---

## Início Rápido

### 1. `settings.py`

```python
INSTALLED_APPS = [
    # Django padrão...
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Dependências
    "simple_history",
    "django_suap_auth",
    # App AVA Auth
    "auth_ava",
]

AUTH_USER_MODEL = "auth_ava.Usuario"

AUTHENTICATION_BACKENDS = [
    "auth_ava.backends.AvaAuthBackend",
    "django.contrib.auth.backends.ModelBackend",
]

SUAP_AUTH = {
    "CLIENT_ID": "seu-client-id",
    "CLIENT_SECRET": "seu-client-secret",
    "REDIRECT_URI": "https://seuapp.ifrn.edu.br/auth/suap/callback/",
    "USER_INFO_FETCHERS": [
        "auth_ava.fetchers.AvaUserInfoFetcher",
    ],
}
```

### 2. `urls.py`

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/suap/", include("django_suap_auth.urls")),
    path("auth/ava/", include("auth_ava.urls")),
]
```

---

## Desenvolvimento, Testes e Git Hooks

### Instalação de dependências de desenvolvimento

```bash
pip install -e ".[dev]"
```

### Configuração do pre-commit

Para habilitar a verificação de linting no commit e os testes automatizados no push:

```bash
# Habilita os hooks de commit (ruff, formatação, trailing-whitespace, etc.)
pre-commit install

# Habilita o hook de push (pytest com cobertura)
pre-commit install --hook-type pre-push
```

### Execução manual dos testes e linters

```bash
# Executar todos os testes com relatório de cobertura
pytest --cov=auth_ava --cov-report=term-missing

# Linting e formatação com Ruff
ruff check .
ruff format .

# Executar pre-commit manualmente
pre-commit run --all-files --hook-stage pre-commit
pre-commit run --all-files --hook-stage pre-push
```

---

## Documentação

A documentação completa é gerada com Sphinx e o tema `django_docs_theme`:

```bash
# Gerar HTML da documentação
python -m sphinx -b html docs docs/_build/html
```

---

## Licença

MIT © 2026 Kelson da Costa Medeiros
