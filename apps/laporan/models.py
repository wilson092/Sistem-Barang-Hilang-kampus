from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models


class LaporanKehilangan(models.Model):
    class Jenis(models.TextChoices):
        ELEKTRONIK = "elektronik", "Elektronik"
        DOKUMEN = "dokumen", "Dokumen / Identitas"
        AKSESORIS = "aksesoris", "Aksesori"
        PAKAIAN = "pakaian", "Pakaian"
        LAINNYA = "lainnya", "Lainnya"

    class Status(models.TextChoices):
        DIAJUKAN = "diajukan", "Diajukan"
        MENUNGGU = "menunggu", "Menunggu"
        COCOK = "cocok", "Cocok"
        SELESAI = "selesai", "Selesai"

    pelapor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="laporan_kehilangan",
    )
    nama_barang = models.CharField("Nama barang", max_length=120)
    jenis = models.CharField("Jenis barang", max_length=20, choices=Jenis.choices)
    deskripsi = models.TextField("Deskripsi", max_length=1000)
    lokasi = models.CharField("Lokasi kehilangan", max_length=180)
    tanggal_kehilangan = models.DateField("Tanggal kehilangan")
    ciri_ciri = models.TextField("Ciri-ciri barang", max_length=700)
    foto = models.FileField(
        "Foto (opsional)",
        upload_to="laporan/",
        blank=True,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])],
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DIAJUKAN,
        db_index=True,
    )
    dibuat_pada = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "laporan_kehilangan"
        ordering = ["-dibuat_pada"]
        verbose_name = "laporan kehilangan"
        verbose_name_plural = "laporan kehilangan"

    def __str__(self):
        return f"{self.nama_barang} — {self.pelapor.nama}"
