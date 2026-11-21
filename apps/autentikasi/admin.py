from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import LogAktivitas, Pengguna


@admin.register(Pengguna)
class PenggunaAdmin(UserAdmin):
    """Kelola akun mahasiswa hasil registrasi dan akun Security."""

    list_display = ("id", "username", "nim", "nama", "role", "kontak", "is_active", "date_joined", "terkunci_sampai")
    list_filter = ("role", "is_active")
    search_fields = ("username", "nim", "nama", "kontak")
    ordering = ("username",)
    actions = ["buka_kunci"]

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Data pengguna", {"fields": ("nama", "nim", "kontak", "role")}),
        ("Status", {"fields": ("is_active", "gagal_login", "terkunci_sampai")}),
        ("Akses panel admin", {"fields": ("is_staff", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "nama", "nim", "kontak", "role", "password1", "password2"),
        }),
    )

    @admin.action(description="Buka kunci akun terpilih")
    def buka_kunci(self, request, queryset):
        for pengguna in queryset:
            pengguna.reset_gagal_login()


@admin.register(LogAktivitas)
class LogAktivitasAdmin(admin.ModelAdmin):
    """Log hanya bisa dibaca: tidak boleh diubah atau dihapus (retensi minimal 1 tahun, NF-07)."""

    list_display = ("waktu", "username", "aksi", "keterangan", "ip_address")
    list_filter = ("aksi",)
    search_fields = ("username", "aksi", "keterangan")
    date_hierarchy = "waktu"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
