from django.core.management.base import BaseCommand

from apps.autentikasi.models import Pengguna

# Akun contoh untuk pengembangan dan pengujian. GANTI kata sandi sebelum UAT/deployment.
KATA_SANDI_CONTOH = "Password123"

AKUN = [
    ("security1", "Petugas Security 1", "9000001", Pengguna.Peran.SECURITY, "security1@example.test"),
    ("security2", "Petugas Security 2", "9000002", Pengguna.Peran.SECURITY, "security2@example.test"),
    ("mahasiswa1", "Mahasiswa Contoh 1", "8000001", Pengguna.Peran.MAHASISWA, "mahasiswa1@example.test"),
    ("mahasiswa2", "Mahasiswa Contoh 2", "8000002", Pengguna.Peran.MAHASISWA, "mahasiswa2@example.test"),
]


class Command(BaseCommand):
    help = "Membuat akun contoh Mahasiswa dan Security (aman dijalankan berulang)."

    def handle(self, *args, **options):
        for username, nama, nim, role, kontak in AKUN:
            pengguna, dibuat = Pengguna.objects.get_or_create(
                username=username, defaults={"nama": nama, "nim": nim, "role": role, "kontak": kontak}
            )
            if dibuat:
                pengguna.set_password(KATA_SANDI_CONTOH)
                pengguna.save()
            elif pengguna.nim == username:
                # Perbarui NIM sementara hasil migrasi akun contoh lama.
                pengguna.nim = nim
                pengguna.save(update_fields=["nim"])
            self.stdout.write(f"{'dibuat' if dibuat else 'sudah ada'}: {username} ({role})")
        self.stdout.write(self.style.SUCCESS(f"Selesai. Kata sandi akun baru: {KATA_SANDI_CONTOH}"))
