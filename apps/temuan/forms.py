from django import forms
from django.utils import timezone

from .models import BarangTemuan


class BarangTemuanForm(forms.ModelForm):
    class Meta:
        model = BarangTemuan
        fields = (
            "nama_barang",
            "jenis",
            "deskripsi",
            "ciri_ciri",
            "nama_penemu",
            "kontak_penemu",
            "lokasi_ditemukan",
            "tanggal_ditemukan",
            "lokasi_penyimpanan",
            "status",
        )
        widgets = {
            "nama_barang": forms.TextInput(attrs={"placeholder": "Contoh: Payung lipat biru"}),
            "deskripsi": forms.Textarea(attrs={"rows": 3, "placeholder": "Deskripsi singkat barang yang ditemukan."}),
            "ciri_ciri": forms.Textarea(attrs={"rows": 2, "placeholder": "Tanda khusus untuk membantu pencocokan."}),
            "nama_penemu": forms.TextInput(attrs={"placeholder": "Nama orang yang menemukan barang"}),
            "kontak_penemu": forms.TextInput(attrs={"placeholder": "Nomor telepon atau kontak (opsional)"}),
            "lokasi_ditemukan": forms.TextInput(attrs={"placeholder": "Contoh: Kantin gedung C"}),
            "tanggal_ditemukan": forms.DateInput(attrs={"type": "date"}),
            "lokasi_penyimpanan": forms.TextInput(attrs={"placeholder": "Contoh: Pos Security Kampus"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].initial = self.instance.status or BarangTemuan.Status.TERSIMPAN

    def clean_tanggal_ditemukan(self):
        tanggal = self.cleaned_data["tanggal_ditemukan"]
        if tanggal > timezone.localdate():
            raise forms.ValidationError("Tanggal ditemukan tidak boleh di masa depan.")
        return tanggal
