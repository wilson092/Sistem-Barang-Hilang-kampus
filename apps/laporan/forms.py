from django import forms
from django.utils import timezone

from .models import LaporanKehilangan


class LaporanKehilanganForm(forms.ModelForm):
    class Meta:
        model = LaporanKehilangan
        fields = (
            "nama_barang",
            "jenis",
            "deskripsi",
            "lokasi",
            "tanggal_kehilangan",
            "ciri_ciri",
            "foto",
        )
        widgets = {
            "nama_barang": forms.TextInput(attrs={"placeholder": "Contoh: Tumbler hitam"}),
            "deskripsi": forms.Textarea(attrs={"rows": 3, "placeholder": "Ceritakan singkat kronologi kehilangan."}),
            "lokasi": forms.TextInput(attrs={"placeholder": "Contoh: Perpustakaan lantai 2"}),
            "tanggal_kehilangan": forms.DateInput(attrs={"type": "date"}),
            "ciri_ciri": forms.Textarea(attrs={"rows": 3, "placeholder": "Warna, merek, atau tanda khusus."}),
            "foto": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }

    def clean_tanggal_kehilangan(self):
        tanggal = self.cleaned_data["tanggal_kehilangan"]
        if tanggal > timezone.localdate():
            raise forms.ValidationError("Tanggal kehilangan tidak boleh di masa depan.")
        return tanggal

    def clean_foto(self):
        foto = self.cleaned_data.get("foto")
        if foto:
            if foto.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Ukuran foto maksimal 5 MB.")
            tipe = getattr(foto, "content_type", "")
            if tipe not in {"image/jpeg", "image/png", "image/webp"}:
                raise forms.ValidationError("Gunakan foto JPG, PNG, atau WebP.")
            header = foto.read(12)
            foto.seek(0)
            signature_valid = (
                (tipe == "image/jpeg" and header.startswith(b"\xff\xd8\xff"))
                or (tipe == "image/png" and header.startswith(b"\x89PNG\r\n\x1a\n"))
                or (tipe == "image/webp" and header.startswith(b"RIFF") and header[8:12] == b"WEBP")
            )
            if not signature_valid:
                raise forms.ValidationError("Isi berkas tidak dikenali sebagai foto JPG, PNG, atau WebP.")
        return foto
