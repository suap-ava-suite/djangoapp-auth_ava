from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def oauth_error(request: HttpRequest) -> HttpResponse:
    """View padrão para renderização de erros genéricos de OAuth."""
    error = request.GET.get("error", "Erro não especificado.")
    return render(request, "auth_ava/oauth_error.html", {"error": error}, status=400)


def not_authorized(request: HttpRequest) -> HttpResponse:
    """View para autorização negada pelo usuário no SUAP."""
    return render(request, "auth_ava/not_authorized.html", status=403)


def invalid_grant(request: HttpRequest) -> HttpResponse:
    """View para código de autorização expirado/inválido."""
    return render(request, "auth_ava/oauth_error_invalid_grant.html", status=400)
