from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.autentikasi.models import Pengguna

from .models import LaporanKehilangan
from .forms import LaporanKehilanganForm


class PembuatanLaporanTest(TestCase):
    def setUp(self):
        self.mahasiswa = Pengguna.objects.create_user(
            username="mahasiswa-wizard",
            password="Password123",
            nama="Mahasiswa Wizard",
            nim="81234567",
            role=Pengguna.Peran.MAHASISWA,
        )
        self.client.force_login(self.mahasiswa)

    def test_post_form_biasa_tanpa_javascript_menyimpan_laporan(self):
        data = {
            "nama_barang": "Tumbler biru",
            "jenis": LaporanKehilangan.Jenis.ELEKTRONIK,
            "deskripsi": "Saya baru sadar tumbler tertinggal setelah kelas.",
            "lokasi": "Gedung A",
            "tanggal_kehilangan": timezone.localdate().isoformat(),
            "ciri_ciri": "Merek X. Warna biru. Ada stiker kecil.",
        }

        response = self.client.post(reverse("buat_laporan"), data)

        laporan = LaporanKehilangan.objects.get(pelapor=self.mahasiswa)
        self.assertRedirects(
            response,
            reverse("laporan_berhasil", kwargs={"pk": laporan.pk}),
            fetch_redirect_response=False,
        )
        self.assertEqual(laporan.nama_barang, data["nama_barang"])
        self.assertEqual(laporan.jenis, data["jenis"])
        self.assertEqual(laporan.deskripsi, data["deskripsi"])
        self.assertEqual(laporan.lokasi, data["lokasi"])
        self.assertEqual(laporan.ciri_ciri, data["ciri_ciri"])
        self.assertEqual(laporan.status, LaporanKehilangan.Status.DIAJUKAN)
        self.assertFalse(laporan.foto)

    def test_tanpa_javascript_semua_field_tetap_tampil_dan_wajib(self):
        response = self.client.get(reverse("buat_laporan"))

        self.assertContains(response, '<form class="workspace-panel report-form report-wizard"', html=False)
        for field in ("nama_barang", "jenis", "deskripsi", "lokasi", "tanggal_kehilangan", "ciri_ciri", "foto"):
            self.assertContains(response, f'name="{field}"', html=False)

    def test_laporan_tidak_lengkap_tidak_disimpan(self):
        response = self.client.post(reverse("buat_laporan"), {"nama_barang": "Tumbler biru"})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(LaporanKehilangan.objects.filter(pelapor=self.mahasiswa).exists())
        self.assertTrue({"jenis", "deskripsi", "lokasi", "tanggal_kehilangan", "ciri_ciri"}.issubset(response.context["form"].errors))

    def test_foto_tepat_5_mib_valid_dan_lebih_satu_byte_ditolak(self):
        data = {
            "nama_barang": "Tas kain",
            "jenis": LaporanKehilangan.Jenis.AKSESORIS,
            "deskripsi": "Tas tertinggal setelah kuliah.",
            "lokasi": "Gedung A",
            "tanggal_kehilangan": timezone.localdate().isoformat(),
            "ciri_ciri": "Warna krem dengan satu kantong depan.",
        }
        batas = 5 * 1024 * 1024
        isi_foto = b"\xff\xd8\xff" + b"x" * (batas - 3)

        foto_batas = SimpleUploadedFile("tas.jpg", isi_foto, content_type="image/jpeg")
        form_batas = LaporanKehilanganForm(data=data, files={"foto": foto_batas})
        self.assertTrue(form_batas.is_valid(), form_batas.errors)

        foto_lebih = SimpleUploadedFile("tas.jpg", isi_foto + b"x", content_type="image/jpeg")
        form_lebih = LaporanKehilanganForm(data=data, files={"foto": foto_lebih})
        self.assertFalse(form_lebih.is_valid())
        self.assertIn("maksimal 5 MB", str(form_lebih.errors["foto"]))
