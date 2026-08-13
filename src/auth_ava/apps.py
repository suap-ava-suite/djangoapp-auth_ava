from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AuthAvaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "auth_ava"
    verbose_name = _("Autenticação AVA")
