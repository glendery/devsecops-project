# 🛡️ DEVS ECOSYSTEM: TOKO ONLINE AMAN DENGAN BLOCKCHAIN AUDIT

Halo! Selamat datang di repositori proyek **DevSecOps E-commerce** ini.

Proyek ini bukan cuma toko online biasa, tapi **simulasi ekosistem keamanan** lengkap. Saya tunjukkan bahwa aplikasi modern itu harus *Secure by Design*—keamanan harus otomatis sejak awal *coding*.

## 1. 🖥️ ARCHITECTURE & PILIHAN TEKNOLOGI SAYA

| Komponen | Teknologi | Alasan Saya Memilih |
| :--- | :--- | :--- |
| **Backend** | Python Flask | Cepat, ringan, dan efektif untuk membuat *routing* serta logika bisnis yang aman. |
| **Database** | SQLite + Flask-SQLAlchemy | Simpel untuk pengembangan (*persistence* data lokal). |
| **Data Integrity** | Python Custom Ledger | Saya membuat *class* Blockchain sendiri (SHA-256) untuk menjamin setiap transaksi **tidak bisa diubah**. |
| **Security Headers** | Flask-Talisman | Saya gunakan ini untuk implementasi *Content Security Policy* (CSP) dan mengamankan *browser user*. |

---

## 2. ⚙️ PIPELINE DEVOPS SAYA (CI/CD OTOMATIS)

Ini adalah jantung DevSecOps-nya! Saya menggunakan **GitHub Actions** untuk memastikan setiap kode yang saya *push* itu aman.

| Tahap Pipeline | Alat | Apa yang Saya Uji? | Bukti Kerja Keras Saya |
| :--- | :--- | :--- | :--- |
| **1. Dependency Check** | **Safety** (SCA) | Saya menganalisis *library* untuk mengecek apakah ada **CVE (kerentanan) publik**. | Ini menjamin *software* saya bebas dari risiko **Supply Chain Attack**. |
| **2. SAST (Static Code)** | **Bandit** | Saya menganalisis kode sumber Python. Saya harus memperbaiki *warning* seperti penggunaan port tanpa *disclaimer* (e.g., `#nosec B104`). | Saya belajar cara memberi *disclaimer* yang benar pada kode yang aman. |
| **3. DAST (Runtime Scan)** | **OWASP ZAP** | Saya menyerang aplikasi saya sendiri saat berjalan. Mencari lubang keamanan web (misal: *missing headers*, *misconfiguration*). | Ini membuktikan aplikasi saya aman dalam kondisi nyata. |
| **4. Observability** | **JSON Logger** | Saya implementasikan *logging* terstruktur (JSON) untuk semua event penting (Login, Checkout, Register). Ini penting untuk *auditing* dan *troubleshooting* di masa depan. |

---

## 3. 🔑 SOLUSI PROBLEM SOLVING SAYA

Ini adalah *highlight* yang menunjukkan saya menyelesaikan masalah teknis yang tidak trivial dan mengamankan aplikasi:

1.  **Bug Data Corrupted:** Saya mengatasi *bug* di mana *ledger* merekam objek Python yang rusak (`<built-in method items...>)` dan berhasil memperbaikinya dengan **string formatting yang tepat** (`", ".join(...)`).
2.  **Solusi Jinja TypeError:** Saya memperbaiki *crash* pada Dashboard Admin yang disebabkan oleh data lama dengan menambahkan filter **`|string`** pada Jinja untuk menanggulangi `TypeError` saat rendering.
3.  **Mengamankan Headers:** Saya *tune* sendiri konfigurasi **Flask-Talisman** untuk *Content Security Policy* (CSP) untuk mengizinkan gambar dan *styling* eksternal tanpa mengorbankan keamanan.

---

## 4. 🚀 CARA MENJALANKAN & KREDENSIAL

### A. Akses Aplikasi (Port 5002)

1.  Jalankan di terminal: `python app.py`
2.  **Toko Online:** Buka `http://127.0.0.1:5002`
3.  **Dashboard Admin:** Buka `http://127.0.0.1:5002/admin`

### B. Kredensial Uji Coba

| Akun | Username | Password |
| :--- | :--- | :--- |
| **Super Admin** | `admin` | `admin123` |
| **Pembeli** | (Daftar Lewat Web) | (Bebas) |

---

**Proyek ini membuktikan saya tidak hanya bisa *ngoding*, tapi juga *ngamanin*!**