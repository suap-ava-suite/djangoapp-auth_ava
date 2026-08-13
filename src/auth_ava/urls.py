from django.urls import path

from . import views

app_name = "auth_ava"

urlpatterns = [
    path("error/", views.oauth_error, name="oauth_error"),
    path("not-authorized/", views.not_authorized, name="not_authorized"),
    path("invalid-grant/", views.invalid_grant, name="invalid_grant"),
]
