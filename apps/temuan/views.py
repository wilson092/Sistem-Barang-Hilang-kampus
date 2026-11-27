from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from apps.autentikasi.decorators import peran_wajib
from apps.autentikasi.models import Pengguna
from apps.autentikasi.services import catat

from .forms import BarangTemuanForm
from .models import BarangTemuan


@peran_wajib(Pengguna.Peran.SECURITY)
@require_http_methods(["GET", "POST"])
def catat_barang(request):
    form = BarangTemuanForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        barang = form.save(commit=False)
        barang.dicatat_oleh = request.user
        barang.save()
        catat(request, request.user, "barang_temuan_dicatat", barang.nama_barang)
        messages.success(request, f"Barang temuan {barang.nama_barang} berhasil dicatat.")
        return redirect("daftar_barang_security")
    return render(request, "temuan/form.html", {"form": form, "mode": "baru"})


@peran_wajib(Pengguna.Peran.SECURITY)
@require_http_methods(["GET", "POST"])
def ubah_barang(request, pk):
    barang = get_object_or_404(BarangTemuan, pk=pk)
    status_sebelum = barang.status
    form = BarangTemuanForm(request.POST or None, instance=barang)
    if request.method == "POST" and form.is_valid():
        barang = form.save()
        catat(request, request.user, "barang_temuan_diperbarui", barang.nama_barang)
        if barang.status != status_sebelum:
            catat(
                request,
                request.user,
                "status_barang_temuan_diperbarui",
                f"{barang.nama_barang}: {barang.get_status_display()}",
            )
        messages.success(request, f"Data {barang.nama_barang} berhasil diperbarui.")
        return redirect("daftar_barang_security")
    return render(request, "temuan/form.html", {"form": form, "mode": "ubah", "barang": barang})


@peran_wajib(Pengguna.Peran.SECURITY)
def daftar_security(request):
    barang = BarangTemuan.objects.select_related("dicatat_oleh").all()
    return render(request, "temuan/security.html", {"barang_list": barang})


@peran_wajib(Pengguna.Peran.MAHASISWA)
def daftar_mahasiswa(request):
    barang = BarangTemuan.objects.defer(
        "nama_penemu",
        "kontak_penemu",
        "lokasi_penyimpanan",
        "ciri_ciri",
        "dicatat_oleh",
    )
    return render(request, "temuan/mahasiswa.html", {"barang_list": barang})
