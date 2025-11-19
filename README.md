# 🛡️ DEVS ECOSYSTEM: SECURE E-COMMERCE WITH BLOCKCHAIN AUDIT LEDGER

## 1. 🌐 PROJECT OVERVIEW & ARCHITECTURE

Proyek ini adalah implementasi **Full-Stack E-commerce** yang berorientasi pada prinsip **DevSecOps (Shift-Left Security)**. Tujuan utamanya adalah membangun pipeline CI/CD otomatis yang mengintegrasikan pengujian keamanan sejak fase *commit*, dan menjamin integritas data transaksi menggunakan teknologi *immutable ledger* (Blockchain).

### A. Teknologi Inti (Tech Stack)
| Komponen | Teknologi | Tujuan |
| :--- | :--- | :--- |
| **Backend** | Python 3.11+, Flask | Routing, API, dan Logika Aplikasi. |
| **Database** | SQLite + Flask-SQLAlchemy | Persistence untuk data Pengguna dan Produk. |
| **Frontend** | HTML5, Jinja2, Bootstrap 5 | Tampilan responsif dan User Interface. |
| **Data Integrity** | Python Custom Class + SHA-256 | Implementasi *Proof-of-Work* sederhana untuk mencatat transaksi pembelian. |
| **Version Control** | Git/GitHub | Source code management dan pemicu CI/CD. |

### B. Model Data Kunci
Proyek ini menggunakan model `User` yang mendukung **Role-Based Access Control (RBAC)** dan model `Product` yang di-seed otomatis saat startup.

---

## 2. ⚙️ DEVS ECOSYSTEM PIPELINE (CI/CD)

Pipeline ini diimplementasikan menggunakan **GitHub Actions** dan dirancang untuk mengintegrasikan pengujian keamanan statis dan dinamis pada setiap *push* kode.

| Tahap Pipeline | Alat | Keterangan Teknis |
| :--- | :--- | :--- |
| **1. Dependency Check** | **Safety** (SCA) | Menganalisis `requirements.txt` terhadap database kerentanan CVE yang diketahui. |
| **2. SAST** | **Bandit** | Menganalisis kode sumber Python (`app.py`) untuk mencari pola *security anti-patterns* (misalnya: penggunaan `host='0.0.0.0'` tanpa *disclaimer*, *insecure hashing*, dll.). |
| **3. DAST (Runtime)** | **OWASP ZAP Baseline** | Menyerang aplikasi yang sedang berjalan di *host network* (Port 5002) untuk mencari celah *runtime* (misalnya, *misconfigured headers*). |
| **4. Observability** | **Python JSON Logger** | Menghasilkan log audit terstruktur (JSON) untuk semua peristiwa kritis (Login, Registrasi, Checkout) yang dapat dianalisis oleh sistem monitoring (ELK Stack/Splunk). |
| **Kebijakan Gagal** | Custom Logic | Pipeline diatur untuk **gagal** jika ditemukan kerentanan *Critical/High* (SAST/SCA), tetapi akan *pass* jika hanya ditemukan *Warnings* (setelah *Risk Acceptance*). |

---

## 3. 🛡️ IMPLEMENTASI KEAMANAN & FITUR KHUSUS

### A. Secure Logic & Access Control
* **Seeding Admin:** Akun **Super Admin** (`admin`/`admin123`) dibuat secara otomatis pada startup server untuk menjamin keberadaan pengguna tingkat tinggi tanpa perlu pendaftaran publik.
* **Role-Based Access:** Logika akses ke `/admin` dilindungi oleh dekorator `@login_required` dan pemeriksaan `current_user.role == 'admin'`, mencegah akses tidak sah.
* **Password Hashing:** Menggunakan fungsi `generate_password_hash` dari Werkzeug dengan algoritma modern (PBKDF2/Scrypt) untuk penyimpanan kredensial yang aman.

### B. Content Security Policy (CSP)
Aplikasi ini menggunakan **Flask-Talisman** untuk menerapkan *security headers*. Konfigurasi CSP telah di-tune secara manual untuk:
* Mengizinkan pemuatan file dari CDN (`cdn.jsdelivr.net`, `cdnjs.cloudflare.com`).
* Mengizinkan *inline styles* (`'unsafe-inline'`) untuk Bootstrap, tanpa membuka celah XSS yang luas.
* Mengizinkan gambar hanya dari sumber lokal (`'self'`) untuk demonstrasi (dikonfigurasi untuk menggunakan gambar *placeholder* lokal).

### C. Solusi Bug (Membuktikan Problem Solving)
Selama pengembangan, kami menemukan dan menyelesaikan dua bug persisten yang menunjukkan kerumitan *runtime* Python:
1.  **Bug Data Corrupted:** Mengatasi masalah di mana *transaction ledger* merekam objek Python yang rusak (`<built-in method items of dict object...>)` alih-alih *string* nama produk. Masalah ini diselesaikan dengan memastikan **string formatting yang tepat** (`", ".join(items_summary)`) dan mematikan server secara paksa.
2.  **Jinja TypeError:** Mengatasi *crash* pada Dashboard Admin yang disebabkan oleh **Jinja** yang mencoba menggunakan operator `in` pada objek yang rusak. Solusi melibatkan penambahan filter pengecekan `|string` pada template untuk mencegah `TypeError`.

---

## 4. 🚀 CARA MENJALANKAN & VERIFIKASI

### A. Akses Aplikasi (Port 5002)
* **Web Toko:** `http://127.0.0.1:5002`
* **Dashboard Admin:** `http://127.0.0.1:5002/admin`

### B. Kredensial Uji Coba
| Akun | Username | Password | Hak Akses |
| :--- | :--- | :--- | :--- |
| **Super Admin** | `admin` | `admin123` | Akses Dashboard Penuh, Semua Data Transaksi. |
| **Buyer (Contoh)** | (Daftar manual) | (Bebas) | Belanja, Riwayat Pesanan Saya. |

### C. Verifikasi Keamanan
Untuk menguji pipeline, lakukan perubahan kecil pada `app.py` dan lakukan `git commit` & `git push`. Pipeline GitHub Actions akan langsung berjalan untuk memverifikasi keamanan statis (Bandit/Safety) dan dinamis (ZAP).