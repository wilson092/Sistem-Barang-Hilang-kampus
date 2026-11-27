"""
Rute per modul (NF-13). Iterasi berikutnya menambah satu baris include per modul:
laporan, temuan, pencocokan, klaim.
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.autentikasi.urls")),
    path("", include("apps.laporan.urls")),
    path("", include("apps.temuan.urls")),
]
