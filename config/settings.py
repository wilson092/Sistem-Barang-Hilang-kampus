"""
Pengaturan proyek Sistem Informasi Pengelolaan Barang Hilang dan Temuan.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Keamanan dasar ---------------------------------------------------------
# GANTI SECRET_KEY dan set DEBUG=False saat deployment (lihat README).
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "dev-only-ganti-saat-deployment-8f3k2j5h1g9d7s6a4p0q",
)
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

# --- Aplikasi: satu app per modul (NF-13) -----------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Modul proyek
    "apps.autentikasi",
    "apps.laporan",
    "apps.temuan",
    "apps.pencocokan",
    "apps.klaim",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- Basis data: SQLite (relasional). Ganti ke MySQL/PostgreSQL saat deployment.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# --- Autentikasi ------------------------------------------------------------
AUTH_USER_MODEL = "autentikasi.Pengguna"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dasbor"
LOGOUT_REDIRECT_URL = "login"

# NF-01: kata sandi minimal 8 karakter; Django menyimpannya sebagai hash ber-salt (PBKDF2).
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# NF-05: sesi berakhir setelah 15 menit tidak aktif.
# SAVE_EVERY_REQUEST memperpanjang masa sesi pada setiap permintaan (idle timeout).
SESSION_COOKIE_AGE = 15 * 60
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# NF-06: tautan reset kata sandi berlaku 30 menit dan hanya sekali pakai
# (token Django batal otomatis begitu kata sandi berubah).
PASSWORD_RESET_TIMEOUT = 30 * 60

# Pengiriman tautan reset: pengiriman otomatis di luar cakupan (BRD 4.2) dan kanal kontak
# belum ditetapkan. Saat pengembangan, "email" dicetak di jendela terminal server.
# Ganti ke SMTP saat deployment.
EMAIL_BACKEND = os.environ.get("DJANGO_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
DEFAULT_FROM_EMAIL = "noreply@barang-hilang.local"

# --- Lokal ------------------------------------------------------------------
LANGUAGE_CODE = "id"
TIME_ZONE = "Asia/Jakarta"
USE_I18N = True
USE_TZ = True

# --- Berkas statis ----------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# NF-03: HTTPS. Aktifkan di deployment (di belakang server yang sudah ber-HTTPS):
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
