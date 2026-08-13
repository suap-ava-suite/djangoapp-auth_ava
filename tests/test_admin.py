import pytest
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory

from auth_ava.admin import (
    EmailUsuarioAdmin,
    SincronizacaoErroAdmin,
    SincronizacaoErroInline,
    UsuarioAdmin,
    VinculoUsuarioAdmin,
)
from auth_ava.models import EmailUsuario, SincronizacaoErro, Usuario, VinculoUsuario


class DummySite(AdminSite):
    pass


@pytest.mark.django_db
class TestAdminConfig:
    def test_usuario_admin_photo_thumb(self):
        site = DummySite()
        admin = UsuarioAdmin(Usuario, site)

        user_with_foto = Usuario(username="u_foto", foto="https://suap.ifrn.edu.br/foto.png")
        html = admin.photo_thumb(user_with_foto)
        assert '<img src="https://suap.ifrn.edu.br/foto.png"' in html

        user_no_foto = Usuario(username="u_nofoto")
        assert admin.photo_thumb(user_no_foto) == "-"

    def test_sincronizacao_erro_inline_no_add_permission(self):
        site = DummySite()
        inline = SincronizacaoErroInline(Usuario, site)
        rf = RequestFactory()
        request = rf.get("/admin/")
        assert inline.has_add_permission(request) is False

    def test_model_admins_registered(self):
        site = DummySite()
        admin_user = UsuarioAdmin(Usuario, site)
        admin_email = EmailUsuarioAdmin(EmailUsuario, site)
        admin_vinc = VinculoUsuarioAdmin(VinculoUsuario, site)
        admin_err = SincronizacaoErroAdmin(SincronizacaoErro, site)

        assert admin_user is not None
        assert admin_email is not None
        assert admin_vinc is not None
        assert admin_err is not None
