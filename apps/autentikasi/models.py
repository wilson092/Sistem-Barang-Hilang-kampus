from datetime import timedelta

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils import timezone

MAKS_GAGAL_LOGIN = 5   # NF-04
MENIT_KUNCI = 15       # NF-04


class PenggunaManager(UserManager):
    def _create_user(self, username, email, password, **extra_fields):
        # Model ini tidak punya field `email` (kontak dipakai sebagai gantinya),
        # jadi argumen email dari manager bawaan diabaikan.
        if not username:
            raise ValueError("Username wajib diisi.")
        user = self.model(username=self.model.normalize_username(username), **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        # Superuser dipakai pengembang untuk panel admin; perannya Security.
        extra_fields.setdefault("role", Pengguna.Peran.SECURITY)
        return super().create_superuser(username, email, password, **extra_fields)


class Pengguna(AbstractUser):
    """Entitas Pengguna (SRS 3.6): satu tabel untuk peran Mahasiswa dan Security."""

    class Peran(models.TextChoices):
        MAHASISWA = "mahasiswa", "Mahasiswa"
        SECURITY = "security", "Security"

    # Field bawaan yang tidak dipakai (SRS memakai `nama` dan `kontak`).
    first_name = None
    last_name = None
    email = None

    nama = models.CharField(max_length=100)
    nim = models.CharField(max_length=30, unique=True)
    kontak = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=20, choices=Peran.choices, default=Peran.MAHASISWA, db_index=True)
    gagal_login = models.PositiveSmallIntegerField(default=0)
    terkunci_sampai = models.DateTimeField(null=True, blank=True)

    EMAIL_FIELD = "kontak"
    REQUIRED_FIELDS = ["nama", "nim"]

    objects = PenggunaManager()

    class Meta:
        db_table = "pengguna"
        verbose_name = "pengguna"
        verbose_name_plural = "pengguna"

    def __str__(self):
        return f"{self.nama} ({self.username})"

    def get_full_name(self):
        return self.nama

    def get_short_name(self):
        return self.nama

    @property
    def is_mahasiswa(self):
        return self.role == self.Peran.MAHASISWA

    @property
    def is_security(self):
        return self.role == self.Peran.SECURITY

    # --- Kunci akun (NF-04) -------------------------------------------------
    @property
    def terkunci(self):
        return self.terkunci_sampai is not None and self.terkunci_sampai > timezone.now()

    def sisa_menit_kunci(self):
        if not self.terkunci:
            return 0
        detik = (self.terkunci_sampai - timezone.now()).total_seconds()
        return max(1, int(-(-detik // 60)))  # pembulatan ke atas

    def catat_gagal_login(self):
        self.gagal_login += 1
        if self.gagal_login >= MAKS_GAGAL_LOGIN:
            self.terkunci_sampai = timezone.now() + timedelta(minutes=MENIT_KUNCI)
            self.gagal_login = 0
        self.save(update_fields=["gagal_login", "terkunci_sampai"])

    def reset_gagal_login(self):
        if self.gagal_login or self.terkunci_sampai:
            self.gagal_login = 0
            self.terkunci_sampai = None
            self.save(update_fields=["gagal_login", "terkunci_sampai"])


class LogAktivitas(models.Model):
    """Log aktivitas penting (NF-07): pengguna, aksi, waktu. Simpan minimal 1 tahun."""

    pengguna = models.ForeignKey(
        Pengguna, null=True, blank=True, on_delete=models.SET_NULL, related_name="log_aktivitas"
    )
    username = models.CharField(max_length=150, blank=True)  # tetap tercatat meski pengguna tak dikenal
    aksi = models.CharField(max_length=50, db_index=True)
    keterangan = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    waktu = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "log_aktivitas"
        ordering = ["-waktu"]
        verbose_name = "log aktivitas"
        verbose_name_plural = "log aktivitas"

    def __str__(self):
        return f"{self.waktu:%Y-%m-%d %H:%M} {self.username} {self.aksi}"
