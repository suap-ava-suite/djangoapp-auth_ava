import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
class TestAuthAvaViews:
    def test_oauth_error_view(self):
        client = Client()
        response = client.get(reverse("auth_ava:oauth_error") + "?error=Teste%20Erro")
        assert response.status_code == 400
        assert "Teste Erro" in response.content.decode("utf-8")

    def test_not_authorized_view(self):
        client = Client()
        response = client.get(reverse("auth_ava:not_authorized"))
        assert response.status_code == 403
        assert "Autorização Negada" in response.content.decode("utf-8")

    def test_invalid_grant_view(self):
        client = Client()
        response = client.get(reverse("auth_ava:invalid_grant"))
        assert response.status_code == 400
        assert "Código de Autorização Expirado" in response.content.decode("utf-8")
