from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/suap/", include("django_suap_auth.urls")),
    path("auth/ava/", include("auth_ava.urls")),
]
