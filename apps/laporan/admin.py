from django.contrib import admin

from .models import LaporanKehilangan


@admin.register(LaporanKehilangan)
class LaporanKehilanganAdmin(admin.ModelAdmin):
    list_display = ("nama_barang", "jenis", "pelapor", "tanggal_kehilangan", "status", "dibuat_pada")
    list_filter = ("status", "jenis", "tanggal_kehilangan")
    search_fields = ("nama_barang", "pelapor__nama", "pelapor__nim", "lokasi")
    readonly_fields = ("dibuat_pada",)
