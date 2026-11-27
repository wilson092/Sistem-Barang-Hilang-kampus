from django.contrib import admin

from .models import BarangTemuan


@admin.register(BarangTemuan)
class BarangTemuanAdmin(admin.ModelAdmin):
    list_display = ("nama_barang", "jenis", "tanggal_ditemukan", "status", "lokasi_penyimpanan", "dicatat_oleh")
    list_filter = ("status", "jenis", "tanggal_ditemukan")
    search_fields = ("nama_barang", "nama_penemu", "lokasi_ditemukan", "lokasi_penyimpanan")
    readonly_fields = ("dibuat_pada", "diperbarui_pada")
