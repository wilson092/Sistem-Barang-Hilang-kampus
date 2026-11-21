from django.urls import path

from . import views

urlpatterns = [
    path("", views.landing, name="beranda"),
    path("dasbor/", views.dasbor, name="dasbor"),
    path("login/", views.login_view, name="login"),
    path("registrasi/", views.registrasi, name="registrasi"),
    path("logout/", views.logout_view, name="logout"),
    path("mahasiswa/dasbor/", views.dasbor_mahasiswa, name="dasbor_mahasiswa"),
    path("security/dasbor/", views.dasbor_security, name="dasbor_security"),
    path("lupa-password/", views.lupa_password, name="lupa_password"),
    path(
        "reset-password/<uidb64>/<token>/",
        views.ResetPasswordConfirmView.as_view(),
        name="password_reset_confirm",
    ),
]
