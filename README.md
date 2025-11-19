# 🛡️ DEVS ECOSYSTEM: TOKO ONLINE AMAN DENGAN BLOCKCHAIN AUDIT

Halo! Selamat datang di repositori proyek **DevSecOps E-commerce** ini.

Proyek ini adalah **aplikasi *e-commerce* yang saya rancang sendiri** dan saya jadikan arena simulasi untuk menerapkan prinsip **DevSecOps (Shift-Left Security)**. Fokus saya adalah membuktikan bahwa aplikasi modern itu harus *Secure by Design*—keamanan harus otomatis sejak awal *coding*.

## 1. 🖥️ ARCHITECTURE & PILIHAN TEKNOLOGI SAYA

| Komponen | Teknologi | Alasan Saya Memilih |
| :--- | :--- | :--- |
| **Backend** | Python Flask | Cepat, ringan, dan efektif untuk membuat *routing* serta logika bisnis yang aman. |
| **Database** | SQLite + Flask-SQLAlchemy | Persistence untuk data Pengguna dan Produk. |
| **Data Integrity** | Python Custom Ledger | Saya membuat *class* Blockchain sendiri (SHA-256) untuk menjamin setiap transaksi **tidak bisa diubah**. |
| **Security Headers** | Flask-Talisman | Saya gunakan ini untuk implementasi *Content Security Policy* (CSP) dan mengamankan *browser user*. |

---

## 2. ⚙️ PIPELINE DEVOPS SAYA (CI/CD OTOMATIS)

Saya menggunakan **GitHub Actions** untuk membuat *pipeline* yang otomatis menguji keamanan kode saya setiap kali saya melakukan *push*.

| Tahap Pipeline | Alat | Apa yang Saya Uji? | Bukti Kerja Keras Saya |
| :--- | :--- | :--- | :--- |
| **1. Dependency Check** | **Safety** (SCA) | Menganalisis *library* untuk mengecek apakah ada **CVE (kerentanan) publik**. | Ini menjamin *software* saya bebas dari risiko **Supply Chain Attack**. |
| **2. SAST (Static Code)** | **Bandit** | Menganalisis kode sumber Python. Saya harus memperbaiki *warning* seperti penggunaan port tanpa *disclaimer* (e.g., `#nosec B104`). | Saya belajar cara memberi *disclaimer* yang benar pada kode yang aman. |
| **3. DAST (Runtime Scan)** | **OWASP ZAP** | Menyerang aplikasi saya saat berjalan. Mencari lubang keamanan web (misal: *misconfigured headers*). | Ini membuktikan aplikasi saya aman dalam kondisi nyata. |
| **4. Observability** | **JSON Logger** | Saya implementasikan *logging* terstruktur (JSON) untuk semua event penting. Ini penting untuk *auditing* dan *troubleshooting*. |

---

## 3. 🔑 SOLUSI PROBLEM SOLVING KRITIS SAYA

1.  **Mengatasi Data Corruption Persisten (The Immutability Challenge):** Saya fokus memperbaiki *write logic* dengan memastikan **string formatting yang tepat** (`", ".join(items_summary)`) dan melakukan prosedur *Database Reset* wajib pada *environment* pengembangan untuk menjamin integritas data di Block baru.
2.  **Menyelesaikan Konflik Jaringan DAST & CSP:** Saya berhasil mendiagnosis ini sebagai **masalah konfigurasi Docker Networking**. Saya menyelesaikan kegagalan koneksi dengan memaksakan konfigurasi **`--network=host`** dan menggunakan `127.0.0.1` sebagai target.
3.  **Memperbaiki Jinja Template Crash:** Saya mengimplementasikan **Jinja Conditional Filter** (`|string`) pada *template* untuk menanggulangi *TypeError* saat data lama yang rusak dibaca, mencegah *crash* fatal.

---

## 4. 🚀 PANDUAN COMMAND LINE LENGKAP (CHEAT SHEET)

Ini adalah semua perintah yang dibutuhkan untuk mengelola, menjalankan, dan menyelesaikan proyek ini.

### 4.1. ⚙️ Setup & Instalasi Lingkungan

| Command | Keterangan |
| :--- | :--- |
| `python -m venv .venv` | Membuat *Virtual Environment* baru. |
| `.venv\Scripts\activate` | **Mengaktifkan** lingkungan (`(.venv)` muncul di terminal). |
| `pip install -r requirements.txt` | Menginstal semua *dependencies* (Flask, SQLAlchemy, ZAP, Bandit, dll.). |

### 4.2. 🗑️ Database & Maintenance

| Command | Keterangan |
| :--- | :--- |
| `Ctrl + C` | Mematikan Server Flask yang sedang berjalan. |
| `Remove-Item ecommerce.db` | Menghapus database lama (Wajib sebelum *fresh start* atau *seeding*). |

### 4.3. 🌐 Menjalankan Aplikasi & Akses

| Command | Keterangan |
| :--- | :--- |
| `python app.py` | Menjalankan Server Flask di **Port 5002**. |
| `http://127.0.0.1:5002` | **Akses Utama:** URL Toko Online Anda. |
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

**Proyek ini membuktikan saya tidak hanya bisa *ngoding*, tapi juga *ngamanin*!**