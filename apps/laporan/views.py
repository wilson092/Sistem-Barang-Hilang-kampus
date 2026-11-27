from django.contrib import messages
from django.http import FileResponse, Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from apps.autentikasi.decorators import peran_wajib
from apps.autentikasi.models import Pengguna
from apps.autentikasi.services import catat

from .forms import LaporanKehilanganForm
from .models import LaporanKehilangan


@peran_wajib(Pengguna.Peran.MAHASISWA)
@require_http_methods(["GET", "POST"])
def buat_laporan(request):
    form = LaporanKehilanganForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        laporan = form.save(commit=False)
        laporan.pelapor = request.user
        laporan.save()
        catat(request, request.user, "laporan_kehilangan_dibuat", laporan.nama_barang)
        messages.success(request, "Laporan kehilangan berhasil diajukan.")
        return redirect("dasbor_mahasiswa")
    return render(request, "laporan/buat.html", {"form": form})


@peran_wajib(Pengguna.Peran.SECURITY)
def daftar_security(request):
    laporan = LaporanKehilangan.objects.select_related("pelapor").all()
    return render(request, "laporan/security.html", {"laporan": laporan})


@peran_wajib(Pengguna.Peran.MAHASISWA, Pengguna.Peran.SECURITY)
def lihat_foto(request, pk):
    laporan = LaporanKehilangan.objects.filter(pk=pk).select_related("pelapor").first()
    if laporan is None or not laporan.foto:
        raise Http404
    if request.user.is_mahasiswa and laporan.pelapor_id != request.user.pk:
        raise Http404
    return FileResponse(
        laporan.foto.open("rb"),
        as_attachment=True,
        filename=laporan.foto.name.rsplit("/", 1)[-1],
        content_type="application/octet-stream",
    )
