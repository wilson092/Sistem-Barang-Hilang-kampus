from .models import LogAktivitas


def catat(request, pengguna, aksi, keterangan="", username=""):
    """Catat log aktivitas (NF-07). Dipakai semua modul pada iterasi berikutnya."""
    ip = request.META.get("REMOTE_ADDR") if request is not None else None
    LogAktivitas.objects.create(
        pengguna=pengguna,
        username=(pengguna.username if pengguna else username),
        aksi=aksi,
        keterangan=keterangan[:255],
        ip_address=ip or None,
    )
