from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .services import catat


def peran_wajib(*peran):
    """RBAC (FR-03, NF-02): hanya peran yang disebutkan yang boleh mengakses view.

    Contoh:  @peran_wajib(Pengguna.Peran.SECURITY)
    Tamu diarahkan ke login; peran yang salah mendapat 403.
    """

    def dekorator(view):
        @wraps(view)
        @login_required
        def dibungkus(request, *args, **kwargs):
            if request.user.role not in peran:
                catat(request, request.user, "akses_ditolak", request.path)
                raise PermissionDenied("Anda tidak memiliki akses ke halaman ini.")
            return view(request, *args, **kwargs)

        return dibungkus

    return dekorator
