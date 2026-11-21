from django import forms
from django.contrib.auth.password_validation import validate_password

from .models import Pengguna


class LoginForm(forms.Form):
    nim = forms.CharField(
        max_length=30,
        label="NIM",
        error_messages={"required": "NIM wajib diisi."},
        widget=forms.TextInput(attrs={"autocomplete": "username", "autofocus": True}),
    )
    password = forms.CharField(
        label="Kata sandi",
        error_messages={"required": "Kata sandi wajib diisi."},
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )


class LupaPasswordForm(forms.Form):
    nim = forms.CharField(
        max_length=30,
        label="NIM",
        error_messages={"required": "NIM wajib diisi."},
        widget=forms.TextInput(attrs={"autocomplete": "username", "autofocus": True}),
    )


class RegistrasiForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label="Username",
        error_messages={"required": "Username wajib diisi."},
        widget=forms.TextInput(attrs={"autocomplete": "username"}),
    )
    nim = forms.CharField(
        max_length=30,
        label="NIM",
        error_messages={"required": "NIM wajib diisi."},
        widget=forms.TextInput(attrs={"autocomplete": "username", "inputmode": "numeric"}),
    )
    password1 = forms.CharField(
        label="Kata sandi",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label="Ulangi kata sandi",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    def clean_username(self):
        username = Pengguna.normalize_username(self.cleaned_data["username"])
        if Pengguna.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Username sudah digunakan. Silakan pilih username lain.")
        return username

    def clean_nim(self):
        nim = self.cleaned_data["nim"].strip()
        if not nim.isdigit():
            raise forms.ValidationError("NIM hanya boleh berisi angka.")
        if Pengguna.objects.filter(nim=nim).exists():
            raise forms.ValidationError("NIM sudah terdaftar.")
        return nim

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Kata sandi tidak sama.")
        if password1 and not self.errors.get("password1"):
            calon_pengguna = Pengguna(
                username=cleaned_data.get("username", ""),
                nama=cleaned_data.get("username", ""),
            )
            try:
                validate_password(password1, calon_pengguna)
            except forms.ValidationError as error:
                self.add_error("password1", error)
        return cleaned_data

    def save(self):
        return Pengguna.objects.create_user(
            username=self.cleaned_data["username"],
            password=self.cleaned_data["password1"],
            nama=self.cleaned_data["username"],
            nim=self.cleaned_data["nim"],
            role=Pengguna.Peran.MAHASISWA,
        )
