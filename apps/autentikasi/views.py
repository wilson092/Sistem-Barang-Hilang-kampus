from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetConfirmView
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.decorators.http import require_POST

from apps.laporan.models import LaporanKehilangan
from apps.temuan.models import BarangTemuan

from .decorators import peran_wajib
from .forms import LoginForm, LupaPasswordForm, RegistrasiForm
from .models import MAKS_GAGAL_LOGIN, Pengguna
from .services import catat

PESAN_LOGIN_SALAH = "NIM atau kata sandi salah."


def landing(request):
    return render(request, "landing.html")


def login_view(request):
    """FR-01 / UC-01."""
    if request.user.is_authenticated:
        return redirect("dasbor")

    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        nim = form.cleaned_data["nim"]
        password = form.cleaned_data["password"]
        user = Pengguna.objects.filter(nim=nim).first()

        # NF-04: akun terkunci ditolak, termasuk bila kata sandinya benar.
        if user and user.terkunci:
            catat(request, user, "login_ditolak_terkunci")
            form.add_error(
                None,
                f"Akun terkunci karena terlalu banyak percobaan gagal. "
                f"Coba lagi dalam {user.sisa_menit_kunci()} menit.",
            )
        elif user is None or not user.is_active or not user.check_password(password):
            if user:
                user.catat_gagal_login()
                catat(request, user, "login_gagal")
                if user.terkunci:
                    catat(request, user, "akun_terkunci", f"Gagal login {MAKS_GAGAL_LOGIN} kali berturut-turut")
            else:
                catat(request, None, "login_gagal", "NIM tidak dikenal", username=nim)
            # Pesan sama untuk NIM salah maupun kata sandi salah (FR-01).
            form.add_error(None, PESAN_LOGIN_SALAH)
        else:
            user.reset_gagal_login()
            login(request, user)  # membuat ulang kunci sesi (anti session fixation)
            catat(request, user, "login")
            return redirect("dasbor")

    return render(request, "autentikasi/login.html", {"form": form})


def registrasi(request):
    """Buat akun Mahasiswa baru dan mulai sesi pengguna tersebut."""
    if request.user.is_authenticated:
        return redirect("dasbor")

    form = RegistrasiForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        catat(request, user, "registrasi")
        login(request, user)
        messages.success(
            request,
            f"Akun tersimpan di database. Username Anda: {user.username}. "
            "Kata sandi menggunakan sandi yang Anda daftarkan.",
        )
        return redirect("dasbor")
    return render(request, "autentikasi/registrasi.html", {"form": form})


@require_POST
def logout_view(request):
    """FR-02: logout mengakhiri sesi."""
    if request.user.is_authenticated:
        catat(request, request.user, "logout")
    logout(request)
    messages.success(request, "Anda telah keluar.")
    return redirect("login")


@login_required
def dasbor(request):
    """Arahkan pengguna ke dasbor sesuai perannya."""
    if request.user.is_security:
        return redirect("dasbor_security")
    return redirect("dasbor_mahasiswa")


@peran_wajib(Pengguna.Peran.MAHASISWA)
def dasbor_mahasiswa(request):
    laporan = LaporanKehilangan.objects.filter(pelapor=request.user)
    return render(request, "mahasiswa/dasbor.html", {"laporan": laporan})


@peran_wajib(Pengguna.Peran.SECURITY)
def dasbor_security(request):
    laporan = LaporanKehilangan.objects.select_related("pelapor").all()[:5]
    barang_temuan = BarangTemuan.objects.all()[:5]
    return render(request, "security/dasbor.html", {"laporan": laporan, "barang_temuan": barang_temuan})


def lupa_password(request):
    """NF-06: minta tautan reset kata sandi (berlaku 30 menit, sekali pakai)."""
    form = LupaPasswordForm(request.POST or None)
    tautan_dev = None

    if request.method == "POST" and form.is_valid():
        user = Pengguna.objects.filter(nim=form.cleaned_data["nim"], is_active=True).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            tautan = request.build_absolute_uri(
                reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})
            )
            # PENGEMBANGAN: email dicetak di terminal server (EMAIL_BACKEND=console).
            # Ganti ke SMTP/SMS ke `user.kontak` saat deployment.
            send_mail(
                "Reset kata sandi",
                f"Buka tautan berikut untuk membuat kata sandi baru (berlaku 30 menit, sekali pakai):\n{tautan}\n",
                settings.DEFAULT_FROM_EMAIL,
                [user.kontak] if user.kontak else [],
                fail_silently=True,
            )
            catat(request, user, "reset_password_diminta")
            if settings.DEBUG:
                tautan_dev = tautan

        # Respons sama baik akun ada maupun tidak, agar NIM tidak bisa ditebak.
        return render(
            request,
            "autentikasi/lupa_password.html",
            {"form": LupaPasswordForm(), "terkirim": True, "tautan_dev": tautan_dev},
        )

    return render(request, "autentikasi/lupa_password.html", {"form": form})


class ResetPasswordConfirmView(PasswordResetConfirmView):
    """Form kata sandi baru dari tautan reset. Membuka kunci akun setelah berhasil."""

    template_name = "autentikasi/reset_password.html"
    success_url = reverse_lazy("login")
    post_reset_login = False

    def form_valid(self, form):
        response = super().form_valid(form)
        self.user.reset_gagal_login()
        catat(self.request, self.user, "reset_password_berhasil")
        messages.success(self.request, "Kata sandi berhasil diubah. Silakan login.")
        return response
