import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = "test-secret-key-auth-ava"

DEBUG = True

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "simple_history",
    "django_suap_auth",
    "auth_ava",
]

AUTH_USER_MODEL = "auth_ava.Usuario"

AUTHENTICATION_BACKENDS = [
    "auth_ava.backends.AvaAuthBackend",
    "django.contrib.auth.backends.ModelBackend",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]

ROOT_URLCONF = "tests.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

STATIC_URL = "/static/"

SUAP_BASE_URL = "https://suap.ifrn.edu.br"

SUAP_AUTH = {
    "CLIENT_ID": "test-client-id",
    "CLIENT_SECRET": "test-client-secret",
    "REDIRECT_URI": "http://localhost:8000/auth/suap/callback/",
    "USER_INFO_FETCHERS": ["auth_ava.fetchers.AvaUserInfoFetcher"],
}
