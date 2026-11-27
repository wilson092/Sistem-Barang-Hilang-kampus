from django.urls import path

from . import views

urlpatterns = [
    path("mahasiswa/temuan/", views.daftar_mahasiswa, name="daftar_barang_mahasiswa"),
    path("security/temuan/", views.daftar_security, name="daftar_barang_security"),
    path("security/temuan/baru/", views.catat_barang, name="catat_barang"),
    path("security/temuan/<int:pk>/ubah/", views.ubah_barang, name="ubah_barang"),
]
