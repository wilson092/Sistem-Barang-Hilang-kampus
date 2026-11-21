# Sistem Informasi Pengelolaan Barang Hilang dan Temuan

**Universitas Esa Unggul — Kelompok 6**

- Mata Kuliah: Pengembangan Perangkat Lunak

---

## 1. Ringkasan Proyek

Sistem Informasi Pengelolaan Barang Hilang dan Temuan merupakan aplikasi web responsif yang dikembangkan untuk menggantikan proses pencatatan manual menggunakan buku tulis dan grup WhatsApp Security di lingkungan kampus.

Sistem ini membantu mahasiswa dalam melaporkan kehilangan dan mengajukan klaim barang. Sementara itu, Security dapat mencatat barang temuan, melakukan pencarian dan pencocokan data, serta memverifikasi kepemilikan barang secara digital dengan riwayat aktivitas yang tercatat.

**Teknologi yang digunakan:**
- Backend: Django (Python)
- Database: SQLite (Tahap Pengembangan)

---

## 2. Status Pengembangan

Pengembangan sistem dilakukan secara inkremental dalam enam iterasi berdasarkan dokumen BRD, PRD, dan SRS.

### Iterasi 1: Fondasi dan Autentikasi (Selesai)

**Cakupan:** PB-01, PB-02, dan PB-03.

Fitur yang dikembangkan:
- Login menggunakan NIM atau username.
- Logout.
- Pembatasan akses berdasarkan peran (Mahasiswa dan Security).
- Fitur lupa kata sandi dengan simulasi melalui terminal.
- Penguncian akun selama 15 menit setelah lima kali gagal login.
- Pencatatan log aktivitas dasar.

**Pengujian:** 30 pengujian otomatis berhasil dijalankan menggunakan Django Test. Alur login juga telah diuji melalui browser.

### Iterasi 2: Modul Pelaporan Kehilangan (Mahasiswa)

**Cakupan:** FR-04 sampai FR-07.

Fitur yang dikembangkan:
- Formulir laporan kehilangan yang mencakup nama barang, jenis, deskripsi, lokasi, tanggal, ciri-ciri, dan foto opsional.
- Validasi kelengkapan data laporan.
- Dasbor mahasiswa untuk melihat daftar laporan pribadi beserta statusnya (Diajukan, Menunggu, Cocok, dan Selesai).
- Halaman Security untuk melihat seluruh laporan kehilangan yang masuk.

### Iterasi 3: Modul Pencatatan Barang Temuan (Security)

**Cakupan:** FR-08 sampai FR-10.

Fitur yang dikembangkan:
- Formulir pencatatan barang temuan yang mencakup data barang, identitas penemu, lokasi ditemukan, dan lokasi penyimpanan.
- Fitur pengubahan data dan pembaruan status barang temuan.
- Halaman daftar barang temuan yang dapat diakses mahasiswa dengan hanya menampilkan informasi non-sensitif.

### Iterasi 4: Modul Pencarian dan Pencocokan (Security)

**Cakupan:** FR-11 sampai FR-14.

Fitur yang dikembangkan:
- Pencarian barang temuan berdasarkan kata kunci, jenis, lokasi, atau tanggal.
- Antarmuka pencocokan laporan kehilangan dengan barang temuan secara manual oleh Security.
- Status laporan menjadi Menunggu apabila belum ditemukan kecocokan.
- Pencocokan ulang dapat dilakukan ketika terdapat barang temuan baru.
- Informasi kontak pemilik laporan ditampilkan kepada Security ketika ditemukan kecocokan.

### Iterasi 5: Modul Klaim dan Verifikasi (Mahasiswa dan Security)

**Cakupan:** FR-15 sampai FR-19.

Fitur yang dikembangkan:
- Pengajuan klaim oleh mahasiswa terhadap barang temuan yang cocok.
- Antarmuka verifikasi bukti kepemilikan oleh Security sesuai jenis barang.
- Pencatatan hasil verifikasi dengan status Sesuai atau Tidak Sesuai.
- Penolakan klaim disertai alasan.
- Kesempatan bagi mahasiswa untuk mengajukan klaim ulang.
- Pencatatan serah terima barang dan riwayat pengembalian.

### Iterasi 6: Penyempurnaan UI/UX, Log Aktivitas, dan UAT

**Cakupan:** NF-01 sampai NF-13 dan pengujian UAT (BO-05).

Fitur dan aktivitas yang dikembangkan:
- Implementasi landing page final menggunakan Swiss-Grid Layout.
- Penyempurnaan tampilan responsif untuk perangkat mobile (minimal 360px) dan desktop.
- Pengembangan modul log aktivitas untuk Security dan Admin.
- Perbaikan bug dan persiapan User Acceptance Test (UAT).

**Target UAT:** Minimal 90% peserta dapat menyelesaikan proses pembuatan laporan dalam waktu lima menit.

---

## 3. Cara Menjalankan Aplikasi

Panduan berikut digunakan untuk menjalankan aplikasi pada sistem operasi Windows.

### 3.1 Instalasi Python

Instalasi Python hanya perlu dilakukan satu kali.

1. Unduh Python melalui [https://www.python.org/downloads/](https://www.python.org/downloads/).
2. Jalankan installer Python.
3. Centang opsi **Add python.exe to PATH**.
4. Pilih Install Now.
5. Tutup terminal atau VS Code, kemudian buka kembali.
6. Periksa instalasi Python menggunakan perintah:

```bat
python --version
```

Jika perintah tersebut tidak dikenali, gunakan:

```bat
py --version
```

### 3.2 Menjalankan Proyek Pertama Kali

Buka terminal pada direktori proyek yang berisi file `manage.py`, kemudian jalankan perintah berikut:

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_pengguna
python manage.py runserver
```

Setelah server berhasil dijalankan, buka aplikasi melalui browser:

[http://127.0.0.1:8000](http://127.0.0.1:8000)

Untuk menghentikan server, tekan `Ctrl + C` pada terminal.

### 3.3 Menjalankan Proyek Berikutnya

Jika konfigurasi awal sudah selesai, jalankan perintah berikut setiap kali ingin menjalankan aplikasi:

```bat
venv\Scripts\activate
python manage.py runserver
```

### 3.4 Catatan Pengembangan

- Jika perintah `venv\Scripts\activate` ditolak oleh PowerShell, gunakan Command Prompt (CMD) atau jalankan perintah berikut satu kali:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

- Jika perintah `python` tidak dikenali tetapi `py` dapat digunakan, ganti seluruh perintah `python` menjadi `py`.
- Aplikasi tidak memerlukan MySQL, Laragon, atau Composer.
- Database menggunakan SQLite dengan file `db.sqlite3` yang dibuat melalui proses migrasi.

---

## 4. Akun Pengujian

Akun berikut dapat digunakan untuk menguji fitur aplikasi.

| Username | NIM | Peran | Kata Sandi |
|---|---|---|---|
| mahasiswa1 | 8000001 | Mahasiswa | Password123 |
| mahasiswa2 | 8000002 | Mahasiswa | Password123 |
| security1 | 9000001 | Security | Password123 |
| security2 | 9000002 | Security | Password123 |

**Catatan:** Ganti kata sandi akun contoh sebelum pelaksanaan UAT.

### 4.1 Registrasi Mahasiswa

Mahasiswa dapat membuat akun melalui tautan **Daftar sekarang** pada halaman login. Akun yang dibuat melalui registrasi mandiri akan mendapatkan peran Mahasiswa secara otomatis.

### 4.2 Akun Security dan Admin

Akun Security dan Admin dibuat oleh administrator melalui panel admin atau menggunakan perintah:

```bat
python manage.py createsuperuser
```

Panel admin dapat diakses melalui:

[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

Panel tersebut digunakan untuk mengelola akun dan melihat log aktivitas.

### 4.3 Menjalankan Pengujian Otomatis

Untuk menjalankan seluruh pengujian otomatis Django, gunakan perintah:

```bat
python manage.py test
```

---

## 5. Pemetaan Kebutuhan (Traceability)

Tabel berikut menunjukkan hubungan antara kebutuhan BRD/SRS dengan implementasi pada kode program.

| Kebutuhan (BRD/SRS) | Implementasi |
|---|---|
| FR-01 sampai FR-03, NF-02 (Autentikasi dan RBAC) | `apps/autentikasi/views.py`, `decorators.py` |
| NF-01 (Minimal 8 karakter dan hash ber-salt) | `AUTH_PASSWORD_VALIDATORS` dan hash PBKDF2 Django |
| NF-03 (HTTPS) | `config/settings.py` (aktif saat `DJANGO_DEBUG=0`) |
| NF-04 (Penguncian 15 menit setelah 5 kali gagal login) | `Pengguna.catat_gagal_login()` |
| NF-05 (Sesi berakhir setelah 15 menit) | `SESSION_COOKIE_AGE`, `SESSION_SAVE_EVERY_REQUEST` |
| NF-06 (Reset kata sandi 30 menit) | `PASSWORD_RESET_TIMEOUT` dan token Django |
| NF-07 (Log aktivitas) | Model `LogAktivitas` dan fungsi `catat()` di `services.py` |
| NF-11 (Responsif minimal 360px) | `static/css/app.css` dan template Tailwind |
| FR-04 sampai FR-07 (Pelaporan Kehilangan) | `apps/laporan/` |
| FR-08 sampai FR-10 (Barang Temuan) | `apps/temuan/` |
| FR-11 sampai FR-14 (Pencarian dan Pencocokan) | `apps/pencocokan/` |
| FR-15 sampai FR-19 (Klaim dan Verifikasi) | `apps/klaim/` |

---

## 6. Catatan Pengembangan

### 6.1 Pencocokan Manual

Sesuai revisi BRD/SRS, proses pencocokan laporan kehilangan dengan barang temuan (FR-11 sampai FR-13) dilakukan secara manual oleh Security melalui antarmuka sistem. Sistem tidak menggunakan mekanisme pencocokan otomatis.

### 6.2 Perlindungan Data Sensitif

Bukti verifikasi yang bersifat sensitif, seperti password atau pola HP, tidak disimpan di database. Security hanya mencatat hasil verifikasi berupa status Sesuai atau Tidak Sesuai beserta catatan pendukung.

### 6.3 Reset Kata Sandi

Pengiriman email otomatis tidak termasuk dalam cakupan pengembangan. Pada tahap pengembangan, tautan reset kata sandi akan ditampilkan melalui terminal server.

### 6.4 Struktur Folder

Proyek menggunakan arsitektur modular Django. Setiap modul dikembangkan secara terpisah untuk mempermudah pengelolaan kode dan pemeliharaan sistem.

Modul yang digunakan meliputi:

- `apps/autentikasi/` — Pengelolaan autentikasi dan hak akses pengguna.
- `apps/laporan/` — Pengelolaan laporan kehilangan.
- `apps/temuan/` — Pengelolaan barang temuan.
- `apps/pencocokan/` — Pencarian dan pencocokan barang.
- `apps/klaim/` — Pengelolaan klaim dan verifikasi kepemilikan.

---

**Universitas Esa Unggul**  
**Kelompok 6 — Pengembangan Perangkat Lunak**