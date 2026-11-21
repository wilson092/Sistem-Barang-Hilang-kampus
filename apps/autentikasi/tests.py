"""
Kriteria penerimaan iterasi 1: FR-01, FR-02, FR-03, NF-01, NF-02, NF-04, NF-05, NF-06, NF-07.
Jalankan:  python manage.py test
"""
from datetime import timedelta
from io import StringIO
from unittest import mock

from django.contrib.auth.tokens import default_token_generator
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import LogAktivitas, Pengguna

KATA_SANDI = "Password123"


def buat_pengguna(username="mhs", role=Pengguna.Peran.MAHASISWA, **kw):
    nim = kw.pop("nim", f"9{Pengguna.objects.count():06d}")
    return Pengguna.objects.create_user(
        username=username, password=KATA_SANDI, nama=f"Nama {username}", nim=nim,
        role=role, kontak=f"{username}@example.test", **kw
    )


def waktu_maju(**kw):
    """Patch jam sistem ke masa depan untuk menguji kunci akun dan sesi."""
    return mock.patch("django.utils.timezone.now", return_value=timezone.now() + timedelta(**kw))


class LoginTest(TestCase):
    def kirim(self, nim, password):
        return self.client.post(reverse("login"), {"nim": nim, "password": password})

    def test_halaman_login_tampil(self):
        response = self.client.get(reverse("login"))
        self.assertContains(response, "Masuk")
        self.assertContains(response, "Lupa kata sandi?")
        self.assertContains(response, reverse("lupa_password"))

    def test_mahasiswa_masuk_ke_dasbor_mahasiswa(self):
        user = buat_pengguna("mhs")
        r = self.kirim(user.nim, KATA_SANDI)
        self.assertRedirects(r, reverse("dasbor"), fetch_redirect_response=False)
        r = self.client.get(reverse("dasbor"))
        self.assertRedirects(r, reverse("dasbor_mahasiswa"))

    def test_security_masuk_ke_dasbor_security(self):
        user = buat_pengguna("sec", Pengguna.Peran.SECURITY)
        self.kirim(user.nim, KATA_SANDI)
        r = self.client.get(reverse("dasbor"))
        self.assertRedirects(r, reverse("dasbor_security"))

    def test_login_salah_tidak_menyebut_bagian_yang_salah(self):
        user = buat_pengguna("mhs")
        salah_sandi = self.kirim(user.nim, "salah-sekali")
        salah_nim = self.kirim("123456789", KATA_SANDI)
        self.assertContains(salah_sandi, "NIM atau kata sandi salah.")
        self.assertContains(salah_nim, "NIM atau kata sandi salah.")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_kolom_wajib_diisi(self):
        r = self.kirim("", "")
        self.assertContains(r, "NIM wajib diisi.")

    def test_akun_nonaktif_ditolak(self):
        user = buat_pengguna("mhs", is_active=False)
        self.assertContains(self.kirim(user.nim, KATA_SANDI), "NIM atau kata sandi salah.")


class RegistrasiTest(TestCase):
    def test_registrasi_menyimpan_akun_dengan_hash_dan_masuk_ke_dasbor(self):
        response = self.client.post(reverse("registrasi"), {
            "username": "wilson-fabian",
            "nim": "2024080",
            "password1": "SandiAman#2026",
            "password2": "SandiAman#2026",
        })
        user = Pengguna.objects.get(nim="2024080")
        self.assertEqual(user.username, "wilson-fabian")
        self.assertNotEqual(user.password, "SandiAman#2026")
        self.assertRedirects(response, reverse("dasbor"), fetch_redirect_response=False)

    def test_nim_hanya_angka_dan_tidak_boleh_sama(self):
        buat_pengguna("sudah-ada", nim="2024080")
        response = self.client.post(reverse("registrasi"), {
            "username": "akun-baru",
            "nim": "2024080",
            "password1": "SandiAman#2026",
            "password2": "SandiAman#2026",
        })
        self.assertContains(response, "NIM sudah terdaftar.")

        response = self.client.post(reverse("registrasi"), {
            "username": "akun-baru",
            "nim": "nimabc",
            "password1": "SandiAman#2026",
            "password2": "SandiAman#2026",
        })
        self.assertContains(response, "NIM hanya boleh berisi angka.")


class KunciAkunTest(TestCase):
    def setUp(self):
        self.user = buat_pengguna("mhs")

    def gagal(self, n):
        for _ in range(n):
            self.client.post(reverse("login"), {"nim": self.user.nim, "password": "salah"})

    def test_terkunci_setelah_lima_kali_gagal_lalu_terbuka_setelah_15_menit(self):
        self.gagal(5)
        self.user.refresh_from_db()
        self.assertTrue(self.user.terkunci)

        # Kata sandi benar pun ditolak saat terkunci.
        r = self.client.post(reverse("login"), {"nim": self.user.nim, "password": KATA_SANDI})
        self.assertContains(r, "terkunci")
        self.assertNotIn("_auth_user_id", self.client.session)

        with waktu_maju(minutes=16):
            r = self.client.post(reverse("login"), {"nim": self.user.nim, "password": KATA_SANDI})
            self.assertRedirects(r, reverse("dasbor"), fetch_redirect_response=False)

    def test_empat_kali_gagal_belum_terkunci(self):
        self.gagal(4)
        self.user.refresh_from_db()
        self.assertFalse(self.user.terkunci)

    def test_login_berhasil_mereset_hitungan_gagal(self):
        self.gagal(2)
        self.user.refresh_from_db()
        self.assertEqual(self.user.gagal_login, 2)
        self.client.post(reverse("login"), {"nim": self.user.nim, "password": KATA_SANDI})
        self.user.refresh_from_db()
        self.assertEqual(self.user.gagal_login, 0)


class LogoutDanSesiTest(TestCase):
    def test_logout_mengakhiri_sesi(self):
        user = buat_pengguna("mhs")
        self.client.force_login(user)
        r = self.client.post(reverse("logout"))
        self.assertRedirects(r, reverse("login"), fetch_redirect_response=False)
        self.assertRedirects(
            self.client.get(reverse("dasbor")),
            f"{reverse('login')}?next=%2Fdasbor%2F",
        )

    def test_logout_wajib_post(self):
        self.client.force_login(buat_pengguna("mhs"))
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)

    def test_sesi_berakhir_setelah_15_menit_tidak_aktif(self):
        self.client.force_login(buat_pengguna("mhs"))
        self.assertEqual(self.client.get(reverse("dasbor_mahasiswa")).status_code, 200)
        with waktu_maju(minutes=16):
            r = self.client.get(reverse("dasbor_mahasiswa"))
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse("login"), r["Location"])

    def test_sesi_diperpanjang_selama_aktif(self):
        self.client.force_login(buat_pengguna("mhs"))
        with waktu_maju(minutes=10):
            self.assertEqual(self.client.get(reverse("dasbor_mahasiswa")).status_code, 200)
        with waktu_maju(minutes=20):  # 10 menit sejak aktivitas terakhir di atas
            self.assertEqual(self.client.get(reverse("dasbor_mahasiswa")).status_code, 200)


class RbacTest(TestCase):
    def test_mahasiswa_membuka_halaman_security_ditolak(self):
        self.client.force_login(buat_pengguna("mhs"))
        self.assertEqual(self.client.get(reverse("dasbor_security")).status_code, 403)

    def test_security_membuka_halaman_mahasiswa_ditolak(self):
        self.client.force_login(buat_pengguna("sec", Pengguna.Peran.SECURITY))
        self.assertEqual(self.client.get(reverse("dasbor_mahasiswa")).status_code, 403)

    def test_tamu_diarahkan_ke_login(self):
        for nama in ("dasbor", "dasbor_mahasiswa", "dasbor_security"):
            r = self.client.get(reverse(nama))
            self.assertEqual(r.status_code, 302, nama)
            self.assertIn(reverse("login"), r["Location"], nama)

    def test_akses_ditolak_tercatat_di_log(self):
        self.client.force_login(buat_pengguna("mhs"))
        self.client.get(reverse("dasbor_security"))
        self.assertTrue(LogAktivitas.objects.filter(aksi="akses_ditolak", username="mhs").exists())

    def test_halaman_403_berbahasa_indonesia(self):
        self.client.force_login(buat_pengguna("mhs"))
        self.assertContains(self.client.get(reverse("dasbor_security")), "Akses ditolak", status_code=403)


class KataSandiTest(TestCase):
    def test_kata_sandi_disimpan_sebagai_hash(self):
        user = buat_pengguna("mhs")
        self.assertNotEqual(user.password, KATA_SANDI)
        self.assertNotIn(KATA_SANDI, user.password)
        self.assertTrue(user.check_password(KATA_SANDI))
        self.assertTrue(user.password.startswith(("pbkdf2_sha256$", "argon2", "bcrypt")))


class ResetPasswordTest(TestCase):
    def setUp(self):
        self.user = buat_pengguna("mhs")

    def tautan(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        return reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})

    def reset(self, tautan, sandi):
        """Ikuti tautan (Django mengalihkan ke URL internal) lalu kirim kata sandi baru."""
        r = self.client.get(tautan, follow=True)
        url_form = r.redirect_chain[-1][0] if r.redirect_chain else tautan
        return r, self.client.post(url_form, {"new_password1": sandi, "new_password2": sandi})

    def test_permintaan_reset_mengirim_tautan_dan_tidak_membocorkan_akun(self):
        r_ada = self.client.post(reverse("lupa_password"), {"nim": self.user.nim})
        r_tidak = self.client.post(reverse("lupa_password"), {"nim": "123456789"})
        pesan = "Jika akun ditemukan"
        self.assertContains(r_ada, pesan)
        self.assertContains(r_tidak, pesan)
        self.assertContains(r_ada, "auth-body")

    def test_reset_berhasil_lalu_sandi_baru_berlaku(self):
        _, r = self.reset(self.tautan(), "PasswordBaru#2026")
        self.assertRedirects(r, reverse("login"), fetch_redirect_response=False)
        r = self.client.post(reverse("login"), {"nim": self.user.nim, "password": "PasswordBaru#2026"})
        self.assertRedirects(r, reverse("dasbor"), fetch_redirect_response=False)

    def test_tautan_hanya_sekali_pakai(self):
        tautan = self.tautan()
        self.reset(tautan, "PasswordBaru#2026")
        r = self.client.get(tautan, follow=True)
        self.assertContains(r, "Tautan reset tidak valid")

    def test_tautan_kedaluwarsa_setelah_30_menit(self):
        tautan = self.tautan()
        sekarang = default_token_generator._now()
        with mock.patch.object(type(default_token_generator), "_now", return_value=sekarang + timedelta(minutes=31)):
            r = self.client.get(tautan, follow=True)
        self.assertContains(r, "Tautan reset tidak valid")

    def test_tautan_berlaku_sebelum_30_menit(self):
        tautan = self.tautan()
        sekarang = default_token_generator._now()
        with mock.patch.object(type(default_token_generator), "_now", return_value=sekarang + timedelta(minutes=29)):
            r = self.client.get(tautan, follow=True)
        self.assertContains(r, "Buat kata sandi baru")
        self.assertContains(r, "auth-body")

    def test_kata_sandi_baru_minimal_8_karakter(self):
        _, r = self.reset(self.tautan(), "Ab1")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "minimal 8 karakter")

    def test_reset_membuka_kunci_akun(self):
        self.user.terkunci_sampai = timezone.now() + timedelta(minutes=15)
        self.user.save()
        self.reset(self.tautan(), "PasswordBaru#2026")
        self.user.refresh_from_db()
        self.assertFalse(self.user.terkunci)


class LogAktivitasTest(TestCase):
    def test_login_logout_dan_gagal_login_tercatat(self):
        user = buat_pengguna("mhs")
        self.client.post(reverse("login"), {"nim": user.nim, "password": "salah"})
        self.client.post(reverse("login"), {"nim": user.nim, "password": KATA_SANDI})
        self.client.post(reverse("logout"))
        aksi = set(LogAktivitas.objects.values_list("aksi", flat=True))
        self.assertTrue({"login_gagal", "login", "logout"} <= aksi)
        log = LogAktivitas.objects.get(aksi="login")
        self.assertEqual(log.pengguna, user)
        self.assertIsNotNone(log.waktu)

    def test_nim_tidak_dikenal_tercatat(self):
        self.client.post(reverse("login"), {"nim": "123456789", "password": "x"})
        self.assertTrue(LogAktivitas.objects.filter(aksi="login_gagal", username="123456789").exists())

    def test_akun_terkunci_tercatat(self):
        buat_pengguna("mhs")
        for _ in range(5):
            user = Pengguna.objects.get(username="mhs")
            self.client.post(reverse("login"), {"nim": user.nim, "password": "salah"})
        self.assertTrue(LogAktivitas.objects.filter(aksi="akun_terkunci").exists())


class SeederTest(TestCase):
    def test_seed_membuat_akun_dan_aman_dijalankan_ulang(self):
        out = StringIO()
        call_command("seed_pengguna", stdout=out)
        call_command("seed_pengguna", stdout=out)
        self.assertEqual(Pengguna.objects.count(), 4)
        self.assertEqual(Pengguna.objects.filter(role=Pengguna.Peran.SECURITY).count(), 2)
        self.assertTrue(Pengguna.objects.get(username="mahasiswa1").check_password("Password123"))
