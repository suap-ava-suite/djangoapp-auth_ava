from django.db import models
from django.utils.translation import gettext_lazy as _


class TipoUsuario(models.TextChoices):
    DOCENTE = "Servidor (Docente)", _("Servidor (Docente)")
    TECNICO = "Servidor (Técnico-Administrativo)", _("Servidor (Técnico-Administrativo)")
    PRESTADOR = "Prestador de Serviço", _("Prestador de Serviço")
    ALUNO = "Aluno", _("Aluno")
    DESCONHECIDO = "Desconhecido", _("Desconhecido")


class TipoVinculo(models.TextChoices):
    SERVIDOR = "servidor", _("Servidor")
    ALUNO = "aluno", _("Aluno")
    PRESTADOR_SERVICO = "prestador_servico", _("Prestador de Serviço")
    OUTRO = "outro", _("Outro")


class TipoEmail(models.TextChoices):
    PREFERENCIAL = "preferencial", _("Preferencial")
    PESSOAL = "pessoal", _("Pessoal / Secundário")
    CORPORATIVO = "corporativo", _("Corporativo / Institucional")
    GOOGLE_CLASSROOM = "google_classroom", _("Google Classroom")
    ACADEMICO = "academico", _("Acadêmico")
    ESCOLAR = "escolar", _("Escolar")
    OUTRO = "outro", _("Outro")
