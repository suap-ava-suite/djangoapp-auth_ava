from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from .choices import TipoEmail, TipoUsuario, TipoVinculo


class Usuario(AbstractUser):
    """Modelo de usuário customizado e enriquecido com dados do SUAP para o ecossistema AVA."""

    username = models.CharField(
        _("IFRN-id"),
        max_length=150,
        unique=True,
        validators=[AbstractUser.username_validator],
        error_messages={
            "unique": _("Um usuário com este IFRN-id já existe."),
        },
    )
    nome_registro = models.CharField(_("nome civil"), max_length=255, null=True, blank=True)
    nome_social = models.CharField(_("nome social"), max_length=255, null=True, blank=True)
    nome_usual = models.CharField(_("nome de apresentação"), max_length=255, null=True, blank=True)
    nome = models.CharField(_("nome no SUAP"), max_length=255, null=True, blank=True)
    tipo_usuario = models.CharField(
        _("tipo de usuário"),
        max_length=50,
        choices=TipoUsuario.choices,
        default=TipoUsuario.DESCONHECIDO,
        null=True,
        blank=True,
    )
    foto = models.CharField(_("URL da foto"), max_length=1024, null=True, blank=True)
    cpf = models.CharField(_("CPF"), max_length=14, null=True, blank=True)
    rg = models.CharField(_("RG"), max_length=50, null=True, blank=True)
    passaporte = models.CharField(_("passaporte"), max_length=50, null=True, blank=True)
    data_nascimento = models.DateField(_("data de nascimento"), null=True, blank=True)
    sexo = models.CharField(_("sexo"), max_length=10, null=True, blank=True)
    naturalidade = models.CharField(_("naturalidade"), max_length=255, null=True, blank=True)
    campus = models.CharField(_("campus"), max_length=50, null=True, blank=True)
    first_login = models.DateTimeField(_("primeiro login"), null=True, blank=True)
    settings = models.JSONField(_("configurações"), default=dict, blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("usuário")
        verbose_name_plural = _("usuários")

    def __str__(self):
        return f"{self.show_name} [{self.username}]"

    @property
    def show_name(self) -> str:
        """Nome preferencial de exibição do usuário."""
        if self.nome_usual:
            return self.nome_usual
        if self.nome_social:
            return self.nome_social
        full = self.get_full_name()
        if full:
            return full
        return self.username

    @property
    def foto_url(self) -> str:
        """Retorna a URL completa da foto do usuário ou fallback estático."""
        if not self.foto:
            static_url = getattr(settings, "STATIC_URL", "/static/")
            return f"{static_url}img/user.png"
        if self.foto.lower().startswith("http://") or self.foto.lower().startswith("https://"):
            return self.foto
        suap_base_url = getattr(settings, "SUAP_BASE_URL", "https://suap.ifrn.edu.br")
        return f"{suap_base_url}{self.foto}"

    @property
    def campus_sigla(self) -> str:
        """Retorna a sigla do campus do usuário."""
        return self.campus or ""

    @property
    def theme_selected(self) -> str:
        """Tema visual selecionado nas preferências do usuário."""
        if isinstance(self.settings, dict):
            return self.settings.get("theme", {}).get("selected", "dsgovbr")
        return "dsgovbr"

    @property
    def dyslexia_friendly(self) -> bool:
        """Preferencia de acessibilidade: fonte amigavel para dislexia."""
        if isinstance(self.settings, dict):
            return self.settings.get("accessibility", {}).get("dyslexia_friendly", False)
        return False

    @property
    def vlibras_active(self) -> bool:
        """Preferencia de acessibilidade: VLibras ativo."""
        if isinstance(self.settings, dict):
            return self.settings.get("accessibility", {}).get("vlibras_active", True)
        return True


class EmailUsuario(models.Model):
    """Armazenamento normalizado de múltiplos e-mails associados ao usuário."""

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="emails",
        verbose_name=_("usuário"),
    )
    tipo = models.CharField(
        _("tipo de e-mail"),
        max_length=50,
        choices=TipoEmail.choices,
        default=TipoEmail.PREFERENCIAL,
    )
    email = models.EmailField(_("endereço de e-mail"), max_length=254)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("e-mail do usuário")
        verbose_name_plural = _("e-mails do usuário")
        unique_together = ("usuario", "tipo", "email")

    def __str__(self):
        return f"{self.email} ({self.get_tipo_display()})"


class VinculoUsuario(models.Model):
    """Armazenamento normalizado de vínculos (servidor, discente, prestador) do usuário."""

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="vinculos",
        verbose_name=_("usuário"),
    )
    suap_id = models.BigIntegerField(_("ID no SUAP"), null=True, blank=True)
    identificador = models.CharField(_("identificador / matrícula"), max_length=255, null=True, blank=True)
    tipo = models.CharField(
        _("tipo de vínculo"),
        max_length=50,
        choices=TipoVinculo.choices,
        null=True,
        blank=True,
    )
    campus = models.CharField(_("campus"), max_length=50, null=True, blank=True)
    ativo = models.BooleanField(_("ativo"), default=True)
    cargo = models.CharField(_("cargo"), max_length=255, null=True, blank=True)
    categoria = models.CharField(_("categoria"), max_length=255, null=True, blank=True)
    curso = models.CharField(_("curso"), max_length=255, null=True, blank=True)
    modalidade = models.CharField(_("modalidade"), max_length=100, null=True, blank=True)
    nivel_ensino = models.CharField(_("nível de ensino"), max_length=100, null=True, blank=True)
    situacao = models.CharField(_("situação"), max_length=100, null=True, blank=True)
    estrangeiro = models.BooleanField(_("estrangeiro"), default=False)
    detalhamento = models.JSONField(_("detalhamento adicional"), default=dict, blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("vínculo")
        verbose_name_plural = _("vínculos")

    def __str__(self):
        desc = self.identificador or str(self.suap_id or "")
        return f"{self.get_tipo_display()} - {desc} ({self.campus or ''})"


class UsuarioAuditData(models.Model):
    """Armazenamento 1x1 dos retornos brutos JSON das APIs do SUAP para auditoria e debug."""

    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name="audit_data",
        primary_key=True,
        verbose_name=_("usuário"),
    )
    last_json = models.JSONField(_("último JSON consolidado"), default=dict, blank=True)
    atualizado_em = models.DateTimeField(_("atualizado em"), auto_now=True)

    class Meta:
        verbose_name = _("dados de auditoria")
        verbose_name_plural = _("dados de auditoria")

    def __str__(self):
        return f"Auditoria de {self.usuario.username} ({self.atualizado_em.strftime('%d/%m/%Y %H:%M')})"


class SincronizacaoErro(models.Model):
    """Registro de erros ocorridos durante a sincronização de endpoints secundários."""

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="erros_sincronizacao",
        verbose_name=_("usuário"),
    )
    endpoint = models.CharField(_("endpoint"), max_length=255)
    status_code = models.IntegerField(_("status HTTP"), null=True, blank=True)
    mensagem_erro = models.TextField(_("mensagem de erro"))
    data_ocorrencia = models.DateTimeField(_("data da ocorrência"), auto_now_add=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("erro de sincronização")
        verbose_name_plural = _("erros de sincronização")
        ordering = ["-data_ocorrencia"]

    def __str__(self):
        return f"Erro em {self.endpoint} [{self.status_code}]: {self.mensagem_erro[:50]}"
