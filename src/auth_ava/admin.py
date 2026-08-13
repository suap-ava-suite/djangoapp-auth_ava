from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import EmailUsuario, SincronizacaoErro, Usuario, UsuarioAuditData, VinculoUsuario


class EmailUsuarioInline(admin.TabularInline):
    model = EmailUsuario
    extra = 0
    fields = ["tipo", "email"]


class VinculoUsuarioInline(admin.StackedInline):
    model = VinculoUsuario
    extra = 0
    fields = [
        ("tipo", "identificador", "campus", "ativo"),
        ("cargo", "categoria", "curso"),
        ("modalidade", "nivel_ensino", "situacao", "estrangeiro"),
        "detalhamento",
    ]


class UsuarioAuditDataInline(admin.StackedInline):
    model = UsuarioAuditData
    extra = 0
    readonly_fields = ["atualizado_em", "last_json"]
    can_delete = False


class SincronizacaoErroInline(admin.TabularInline):
    model = SincronizacaoErro
    extra = 0
    readonly_fields = ["endpoint", "status_code", "mensagem_erro", "data_ocorrencia"]
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = [
        "username",
        "photo_thumb",
        "show_name",
        "email",
        "tipo_usuario",
        "campus",
        "is_active",
        "is_staff",
    ]
    list_filter = ["tipo_usuario", "campus", "is_active", "is_staff", "is_superuser"]
    search_fields = ["username", "nome_usual", "nome_registro", "nome_social", "email", "cpf"]
    ordering = ["username"]

    fieldsets = [
        (
            _("Identificação"),
            {
                "fields": [
                    "username",
                    "nome_usual",
                    "nome_registro",
                    "nome_social",
                    "nome",
                    "foto",
                ]
            },
        ),
        (
            _("Documentos e Dados Pessoais"),
            {
                "fields": [
                    ("cpf", "rg", "passaporte"),
                    ("data_nascimento", "sexo", "naturalidade"),
                ]
            },
        ),
        (
            _("Classificação Institucional"),
            {
                "fields": [
                    ("tipo_usuario", "campus"),
                ]
            },
        ),
        (
            _("Permissões"),
            {
                "fields": [
                    ("is_active", "is_staff", "is_superuser"),
                    "groups",
                    "user_permissions",
                ]
            },
        ),
        (
            _("Datas e Histórico"),
            {
                "fields": [
                    ("date_joined", "first_login", "last_login"),
                ]
            },
        ),
        (
            _("Preferências e Acessibilidade"),
            {
                "fields": ["settings"],
                "classes": ["collapse"],
            },
        ),
    ]

    readonly_fields = ["date_joined", "first_login", "last_login"]
    inlines = [
        EmailUsuarioInline,
        VinculoUsuarioInline,
        UsuarioAuditDataInline,
        SincronizacaoErroInline,
    ]

    @admin.display(description=_("Foto"))
    def photo_thumb(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius:50%; object-fit:cover;" />',
                obj.foto_url,
            )
        return "-"


@admin.register(EmailUsuario)
class EmailUsuarioAdmin(admin.ModelAdmin):
    list_display = ["usuario", "tipo", "email"]
    list_filter = ["tipo"]
    search_fields = ["usuario__username", "usuario__nome_usual", "email"]


@admin.register(VinculoUsuario)
class VinculoUsuarioAdmin(admin.ModelAdmin):
    list_display = ["usuario", "tipo", "identificador", "campus", "ativo", "cargo", "curso"]
    list_filter = ["tipo", "campus", "ativo"]
    search_fields = ["usuario__username", "identificador", "cargo", "curso"]


@admin.register(SincronizacaoErro)
class SincronizacaoErroAdmin(admin.ModelAdmin):
    list_display = ["usuario", "endpoint", "status_code", "data_ocorrencia"]
    list_filter = ["endpoint", "status_code", "data_ocorrencia"]
    search_fields = ["usuario__username", "endpoint", "mensagem_erro"]
    readonly_fields = ["usuario", "endpoint", "status_code", "mensagem_erro", "data_ocorrencia"]
