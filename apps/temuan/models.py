from django.conf import settings
from django.db import models


class BarangTemuan(models.Model):
    class Jenis(models.TextChoices):
        ELEKTRONIK = "elektronik", "Elektronik"
        DOKUMEN = "dokumen", "Dokumen / Identitas"
        AKSESORIS = "aksesoris", "Aksesori"
        PAKAIAN = "pakaian", "Pakaian"
        LAINNYA = "lainnya", "Lainnya"

    class Status(models.TextChoices):
        TERSIMPAN = "tersimpan", "Tersimpan"
        DIPROSES = "diproses", "Dalam proses"
        DISERAHKAN = "diserahkan", "Diserahkan"

    nama_barang = models.CharField("Nama barang", max_length=120)
    jenis = models.CharField("Jenis barang", max_length=20, choices=Jenis.choices)
    deskripsi = models.TextField("Deskripsi", max_length=1000)
    nama_penemu = models.CharField("Nama penemu", max_length=100)
    kontak_penemu = models.CharField("Kontak penemu", max_length=100, blank=True)
    lokasi_ditemukan = models.CharField("Lokasi ditemukan", max_length=180)
    tanggal_ditemukan = models.DateField("Tanggal ditemukan")
    lokasi_penyimpanan = models.CharField("Lokasi penyimpanan", max_length=180)
    ciri_ciri = models.TextField("Ciri-ciri barang", max_length=700, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TERSIMPAN,
        db_index=True,
    )
    dicatat_oleh = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="barang_temuan_dicatat",
    )
    dibuat_pada = models.DateTimeField(auto_now_add=True)
    diperbarui_pada = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "barang_temuan"
        ordering = ["-dibuat_pada"]
        verbose_name = "barang temuan"
        verbose_name_plural = "barang temuan"

    def __str__(self):
        return f"{self.nama_barang} — {self.get_jenis_display()}"
