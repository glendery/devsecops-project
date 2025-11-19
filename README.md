# DevSecOps E-Commerce & Blockchain Ledger

![DevSecOps](https://img.shields.io/badge/DevSecOps-Enabled-green?style=for-the-badge&logo=github-actions)
![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python)
![Security](https://img.shields.io/badge/Security-OWASP%20ZAP%20%7C%20Bandit-red?style=for-the-badge)

Proyek ini adalah implementasi **Secure Software Development Life Cycle (SSDLC)** untuk aplikasi E-Commerce sederhana yang terintegrasi dengan teknologi **Blockchain** untuk transparansi transaksi.

Tujuan utama proyek ini bukan hanya membangun aplikasi, tetapi mendemonstrasikan penerapan pipeline **DevSecOps** yang otomatis, aman, dan patuh standar (Compliance).

## 🚀 Fitur Utama

### 🛒 Fitur Aplikasi
* **Manajemen Pengguna:** Registrasi & Login aman (Hashing SHA-256/PBKDF2).
* **E-Commerce:** Katalog produk, Keranjang Belanja, dan Checkout.
* **Blockchain Ledger:** Setiap transaksi pembelian dicatat dalam *immutable ledger* (buku besar yang tidak bisa diubah) menggunakan *Proof-of-Work* sederhana.
* **Blockchain Explorer:** Halaman khusus `/explorer` untuk memantau blok transaksi secara transparan.

### 🛡️ Fitur Keamanan (DevSecOps)
* **Content Security Policy (CSP):** Perlindungan terhadap XSS menggunakan `flask-talisman`.
* **Secure Headers:** Implementasi HSTS, X-Frame-Options, dan X-Content-Type-Options.
* **Input Validation:** Sanitasi input pada form Login/Register untuk mencegah SQL Injection.
* **Automated Pipeline:** Integrasi CI/CD penuh menggunakan GitHub Actions.

---

## 🛠️ Arsitektur & Tech Stack

* **Backend:** Python (Flask)
* **Database:** SQLite (dengan SQLAlchemy ORM)
* **Frontend:** HTML5, Bootstrap 5, FontAwesome
* **Security Tools:**
    * **SCA (Software Composition Analysis):** `safety` (Mengecek library rentan).
    * **SAST (Static Application Security Testing):** `bandit` (Menganalisis kode Python).
    * **DAST (Dynamic Application Security Testing):** `OWASP ZAP` (Menyerang aplikasi aktif untuk mencari celah runtime).

---

## ⚙️ Pipeline DevSecOps (CI/CD)

Proyek ini menggunakan **GitHub Actions** untuk mengotomatisasi pengujian keamanan pada setiap `push` atau `pull request`.

**Alur Pipeline (`.github/workflows/security_pipeline.yml`):**

1.  **Build & Install:** Menyiapkan lingkungan Python dan menginstall dependensi.
2.  **Dependency Scanning:** Memeriksa `requirements.txt` terhadap database kerentanan umum (CVE).
3.  **SAST (Static Analysis):** Menjalankan `bandit` untuk mencari pola kode tidak aman (misal: *hardcoded password*, *unsafe functions*).
4.  **Application Health Check:** Memastikan aplikasi berhasil berjalan (`curl localhost:5002`).
5.  **DAST (Dynamic Analysis):** Menjalankan **OWASP ZAP Baseline Scan** untuk memindai aplikasi yang sedang berjalan dari celah keamanan web (XSS, CSRF, Misconfiguration).

---

## 💻 Cara Menjalankan (Lokal)

Ikuti langkah ini untuk menjalankan aplikasi di komputer Anda:

1.  **Clone Repository**
    ```bash
    git clone [https://github.com/USERNAME_ANDA/devsecops-project.git](https://github.com/USERNAME_ANDA/devsecops-project.git)
    cd devsecops-project
    ```

2.  **Buat Virtual Environment**
    ```bash
    python -m venv venv
    venv\Scripts\activate  # (atau source venv/bin/activate di Mac/Linux)
    ```

3.  **Install Dependensi**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Jalankan Aplikasi**
    ```bash
    python app.py
    ```

5.  **Akses Aplikasi (Port 5002)**
    * **Toko Online:** Buka `http://127.0.0.1:5002` di browser.
    * **Blockchain Explorer:** Buka `http://127.0.0.1:5002/explorer`.

### 🔑 Akun Super Admin Default

Anda dapat menguji Dashboard Admin tanpa mendaftar (akun dibuat otomatis saat startup):
* **Username:** `admin`
* **Password:** `admin123`

---

## 🧪 Pengujian Blockchain

Untuk membuktikan integritas Blockchain, Anda dapat menjalankan unit test yang tersedia:

```bash
python test_blockchain.py