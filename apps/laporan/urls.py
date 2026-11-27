from django.urls import path

from . import views

urlpatterns = [
    path("mahasiswa/laporan/buat/", views.buat_laporan, name="buat_laporan"),
    path("security/laporan/", views.daftar_security, name="daftar_laporan_security"),
    path("laporan/<int:pk>/foto/", views.lihat_foto, name="foto_laporan"),
]
