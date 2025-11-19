# 🛡️ DEVS ECOSYSTEM: TOKO ONLINE AMAN DENGAN BLOCKCHAIN AUDIT

Halo! Ini adalah proyek **DevSecOps E-commerce** yang saya rancang sendiri untuk menerapkan *Secure by Design*—keamanan harus otomatis sejak awal *coding*.

## 1. 🖥️ ARCHITECTURE & PILIHAN TEKNOLOGI SAYA

| Komponen | Teknologi | Alasan Saya Memilih |
| :--- | :--- | :--- |
| **Backend** | Python Flask | Cepat, ringan, dan efektif untuk *prototyping* yang aman. |
| **Database** | SQLite + Flask-SQLAlchemy | Persistence untuk data Pengguna dan Produk. |
| **Data Integrity** | Python Custom Ledger | Saya membuat *class* Blockchain sendiri (SHA-256) untuk menjamin setiap transaksi **tidak bisa diubah**. |
| **Security Headers** | Flask-Talisman | Saya gunakan ini untuk implementasi *Content Security Policy* (CSP) dan mengamankan *browser user*. |

---

## 2. ⚙️ PIPELINE DEVOPS SAYA (CI/CD OTOMATIS)

Pipeline saya menggunakan **GitHub Actions** dan mengintegrasikan **Safety** (SCA), **Bandit** (SAST), dan **OWASP ZAP** (DAST) untuk pengujian keamanan otomatis pada setiap *push*.

---

## 3. 🔑 SOLUSI PROBLEM SOLVING KRITIS SAYA

Ini adalah *highlight* yang menunjukkan bahwa saya menguasai *debugging* tingkat lanjut dan membuat keputusan arsitektur yang aman:

1.  **Mengatasi Data Corruption Persisten (The Immutability Challenge):**
    * **Masalah:** Ledger merekam *object* Python yang rusak (`<built-in method items...>)` alih-alih *string* nama produk.
    * **Solusi Saya:** Saya fokus memperbaiki *write logic* dengan memastikan **string formatting yang tepat** (`", ".join(items_summary)`) dan saya buat prosedur *Database Reset* wajib pada *environment* pengembangan untuk menjamin integritas data di Block baru.

2.  **Penerapan Akses Kontrol (RBAC) & Seeding Aman:**
    * **Masalah:** Saya perlu membedakan hak akses Admin dan Buyer tanpa mengizinkan user biasa mendaftar sebagai Admin.
    * **Solusi Saya:** Saya mengimplementasikan **Role-Based Access Control (RBAC)** dan membuat fungsi **`seed_admin()`** yang otomatis menanam akun Admin (`admin`/`admin123`) dengan *hashed password* saat *startup*. Ini mencegah pendaftaran Admin publik.

3.  **Frontend Security Hardening (CSP Tuning):**
    * **Masalah:** Pengaturan *default* CSP memblokir *styling* dan *icon* dari CDN (Bootstrap/FontAwesome), membuat tampilan rusak.
    * **Solusi Saya:** Saya secara manual mengatur ulang CSP untuk mengizinkan **`'unsafe-inline'`** untuk `style-src` dan mengizinkan `https://cdnjs.cloudflare.com` untuk `font-src`, yang menjamin tampilan tetap cantik sambil mempertahankan kontrol atas sumber daya yang diizinkan.

4.  **Menyelesaikan Konflik Jaringan DAST:**
    * **Masalah:** OWASP ZAP gagal tersambung ke aplikasi Flask saya dengan error *Connection Refused* pada GitHub Actions.
    * **Solusi Saya:** Saya berhasil mendiagnosis ini sebagai **masalah konfigurasi Docker Networking**. Saya menyelesaikan kegagalan koneksi dengan memverifikasi konfigurasi **`--network=host`** dan menggunakan *target* eksplisit `127.0.0.1`.

5.  **Memperbaiki Jinja Template Crash (Menangani Data Historis Rusak):**
    * **Masalah:** Admin Dashboard *crash* dengan *fatal error* **`TypeError`** saat membaca data lama yang rusak dari Blockchain.
    * **Solusi Saya:** Saya mengimplementasikan **Jinja Conditional Filter** (`|string`) pada *template* untuk memaksa objek yang rusak dikonversi menjadi *string* terlebih dahulu, mencegah *crash* fatal, dan menunjukkan bahwa aplikasi saya mampu menangani *corrupted historical data* dengan elegan.

---

## 4. 🚀 PANDUAN COMMAND LINE LENGKAP (CHEAT SHEET)

### 4.1. ⚙️ Setup & Instalasi Lingkungan

| Command | Keterangan |
| :--- | :--- |
| `python -m venv .venv` | Membuat *Virtual Environment* baru. |
| `.venv\Scripts\activate` | **Mengaktifkan** lingkungan (`(.venv)` muncul di terminal). |
| `pip install -r requirements.txt` | Menginstal semua *dependencies* proyek. |

### 4.2. 🗑️ Database & Maintenance

| Command | Keterangan |
| :--- | :--- |
| `Ctrl + C` | Mematikan Server Flask yang sedang berjalan. |
| `Remove-Item ecommerce.db` | Menghapus database lama (Wajib sebelum *fresh start* atau *seeding*). |

### 4.3. 🌐 Menjalankan Aplikasi & Akses

| Command | Keterangan |
| :--- | :--- |
| `python app.py` | Menjalankan Server Flask di **Port 5002**. |
| `http://127.0.0.1:5002` | **Akses Toko Online.** |
| `http://127.0.0.1:5002/admin` | **Akses Dashboard Admin.** |

| Kredensial Admin | Username | Password |
| :--- | :--- | :--- |
| **Super Admin** | `admin` | `admin123` |

### 4.4. ✅ Finalisasi Git (Submission)

| Command | Keterangan |
| :--- | :--- |
| `git add .` | Menandai semua file yang diubah/baru untuk di-*commit*. |
| `git commit -m "Final project completion and documentation."` | Merekam perubahan ke riwayat Git lokal. |
| `git push` | Mengunggah *commit* terakhir ke GitHub (Bukti akhir tugas). |

---

🅼🅰🅺🅰🆂🅸🅷, 🅶🆁🅰🆉🅸🅴, 🅳🅰🅽🅺 🅹🅴, 🆃🅷🅰🅽🅺 🆈🅾🆄
