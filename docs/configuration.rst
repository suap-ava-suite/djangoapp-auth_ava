Configuração
============

1. Configuração no ``settings.py``
----------------------------------

Adicione os apps necessários ao ``INSTALLED_APPS`` e defina o modelo de usuário:

.. code-block:: python

   INSTALLED_APPS = [
       # Django apps padrão...
       "django.contrib.admin",
       "django.contrib.auth",
       "django.contrib.contenttypes",
       "django.contrib.sessions",
       "django.contrib.messages",
       "django.contrib.staticfiles",

       # Terceiros
       "simple_history",
       "django_suap_auth",

       # AVA Auth
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

2. Configuração de URLs
-----------------------

No arquivo ``urls.py`` principal do seu projeto Django:

.. code-block:: python

   from django.contrib import admin
   from django.urls import path, include

   urlpatterns = [
       path("admin/", admin.site.urls),
       path("auth/suap/", include("django_suap_auth.urls")),
       path("auth/ava/", include("auth_ava.urls")),
   ]
