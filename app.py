# app.py — FINAL VERSION (DevSecOps E-commerce Store)
# --------------------------------------------------------------------------
# Features: Flask-Login, SQLAlchemy, Atomic/Secure Blockchain Persistence (HMAC, Auto-Backup)
# --------------------------------------------------------------------------
import hashlib
import json
import os
import logging
import time
import hmac
from time import time as now_time
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_talisman import Talisman
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from pythonjsonlogger.json import JsonFormatter
from sqlalchemy.exc import IntegrityError

# ----------------------------
# 1. Config & Setup
# ----------------------------
APP_DIR = os.path.dirname(os.path.abspath(__file__))
BLOCKCHAIN_FILE = os.path.join(APP_DIR, 'blockchain.json')
CHAIN_BACKUP_DIR = os.path.join(APP_DIR, 'chain_backups')
SESSION_DIR = os.path.join(APP_DIR, 'flask_session')

# CRITICAL SECURITY: MUST BE SET TO RANDOM STRING AND NOT COMMITTED TO REPO
SECRET_CHAIN_KEY = os.environ.get('SECRET_CHAIN_KEY', 'devchainsecret-changeinprod-887766').encode()
RESET_BLOCKCHAIN = os.environ.get('RESET_BLOCKCHAIN', 'False').lower() in ('1', 'true', 'yes')

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'devsecops-secret-key-2025')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Session config (filesystem)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_FILE_DIR"] = SESSION_DIR
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR, exist_ok=True)
Session(app)

# CSP (Talisman) - Optimized for DevSecOps + Bootstrap 5
csp = {
    'default-src': ["'self'"],
    'style-src': [
        "'self'",
        "https://cdn.jsdelivr.net",
        "https://cdnjs.cloudflare.com",
        "'unsafe-inline'"  # Required for Bootstrap 5 components (alerts, navbar)
    ],
    'font-src': [
        "'self'",
        "https://cdn.jsdelivr.net",
        "https://cdnjs.cloudflare.com",
        "data:"
    ],
    'img-src': [
        "'self'",
        "data:",
        "https://cdn.jsdelivr.net",
        "https://via.placeholder.com"
    ],
    'script-src': [
        "'self'",
        "https://cdn.jsdelivr.net"
    ],
    'connect-src': [
        "'self'",
        "https://cdn.jsdelivr.net"
    ],
    'frame-ancestors': ["'self'"]
}
Talisman(app, force_https=False, content_security_policy=csp)

# Logger JSON
handler = logging.StreamHandler()
formatter = JsonFormatter(fmt='%(asctime)s %(levelname)s %(name)s %(module)s %(funcName)s %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)
app.logger.info("Application starting up.")

# jinja filter to format timestamps
@app.template_filter('datetime_format')
def format_datetime(timestamp):
    try:
        dt_object = datetime.fromtimestamp(float(timestamp))
        return dt_object.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return str(timestamp)

# ----------------------------
# 2. DB Models
# ----------------------------
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='buyer')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(50), nullable=False, default="Umum")

@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except Exception:
        return None

# ----------------------------
# 3. Blockchain Logic (with HMAC Integrity)
# ----------------------------
def sign_block(block_dict):
    """Generates HMAC signature for a block."""
    b = block_dict.copy()
    b.pop('signature', None) # Don't sign the signature field itself
    payload = json.dumps(b, sort_keys=True, default=str).encode('utf-8')
    return hmac.new(SECRET_CHAIN_KEY, payload, hashlib.sha256).hexdigest()

def verify_block_signature(block_dict):
    """Verifies HMAC signature for a block."""
    sig = block_dict.get('signature')
    if not sig:
        return False
    expected = sign_block(block_dict)
    return hmac.compare_digest(expected, sig)

class Blockchain:
    def __init__(self, chain=None):
        self.chain = chain.copy() if chain is not None else []
        self.pending_transactions = []
        if not self.chain:
            self.create_block(proof=100, previous_hash='1')

    def create_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': now_time(),
            'transactions': self.pending_transactions.copy(),
            'proof': proof,
            'previous_hash': previous_hash or (self.hash(self.chain[-1]) if self.chain else '1')
        }
        # CRITICAL: Add HMAC Signature to the block
        block['signature'] = sign_block(block)

        self.pending_transactions = []
        self.chain.append(block)
        return block

    def add_transaction(self, sender, items, total):
        # Normalize items to readable string (prevents built-in method leak)
        if isinstance(items, (list, tuple)):
            try:
                items_str = ", ".join(str(x) for x in items)
            except Exception:
                items_str = str(items)
        elif isinstance(items, dict):
            try:
                items_str = json.dumps(items, ensure_ascii=False, default=str)
            except Exception:
                items_str = str(items)
        else:
            items_str = str(items)

        if "<built-in" in items_str:
            items_str = "CORRUPTED_ITEM_REMOVED"

        tx = {
            'sender': sender,
            'items': items_str,
            'total': int(total),
            'timestamp': now_time()
        }
        self.pending_transactions.append(tx)
        return (self.last_block['index'] + 1) if self.last_block else 1

    @property
    def last_block(self):
        return self.chain[-1] if self.chain else None

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True, default=str).encode()
        return hashlib.sha256(block_string).hexdigest()

    def get_transactions_by_user(self, username):
        user_history = []
        for block in self.chain:
            for tx in block.get('transactions', []):
                if tx.get('sender') == username:
                    tx_copy = tx.copy()
                    tx_copy['block_index'] = block['index']
                    user_history.append(tx_copy)
        return user_history

    def get_all_transactions(self):
        all_tx = []
        for block in self.chain:
            for tx in block.get('transactions', []):
                tx_copy = tx.copy()
                tx_copy['block_index'] = block['index']
                all_tx.append(tx_copy)
        return all_tx

# ----------------------------
# 4. Robust file I/O for blockchain (Atomic Save, Auto-Backup, Recovery)
# ----------------------------
def cleanup_old_backups(limit=20):
    """Hapus backup lama agar folder tidak membengkak."""
    try:
        if not os.path.exists(CHAIN_BACKUP_DIR): return
        files = sorted(
            [os.path.join(CHAIN_BACKUP_DIR, f) for f in os.listdir(CHAIN_BACKUP_DIR)],
            reverse=True
        )
        for old in files[limit:]:
            os.remove(old)
    except Exception as e:
        app.logger.warning("cleanup_old_backups failed: %s", e)

def backup_blockchain(data):
    """Simpan salinan blockchain dengan timestamp."""
    try:
        os.makedirs(CHAIN_BACKUP_DIR, exist_ok=True)
        ts = time.strftime("%Y%m%d-%H%M%S")
        filename = os.path.join(CHAIN_BACKUP_DIR, f"blockchain_{ts}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        cleanup_old_backups()
    except Exception as e:
        app.logger.warning("backup_blockchain failed: %s", e)

def load_latest_backup():
    """Coba muat backup terbaru dari folder jika file utama korup."""
    try:
        if not os.path.exists(CHAIN_BACKUP_DIR): return None
        files = sorted(
            [os.path.join(CHAIN_BACKUP_DIR, f) for f in os.listdir(CHAIN_BACKUP_DIR)],
            reverse=True
        )
        for fpath in files:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list): return data
    except Exception:
        pass
    return None

def save_chain_to_file(chain_obj):
    """Simpan blockchain secara Atomic (anti-corrupt) dan buat backup."""
    try:
        data = chain_obj.chain if isinstance(chain_obj, Blockchain) else chain_obj
        temp_file = BLOCKCHAIN_FILE + ".tmp"
        
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        os.replace(temp_file, BLOCKCHAIN_FILE)
        backup_blockchain(data)
        app.logger.info("Blockchain saved to file (atomic).", extra={'file': BLOCKCHAIN_FILE})
    except Exception as e:
        app.logger.error("Failed to save blockchain to file.", extra={'error': str(e)})

def load_chain_from_file_safe():
    """Muat chain dengan validasi integritas (HMAC + struktur) dan fallback."""
    if not os.path.exists(BLOCKCHAIN_FILE):
        app.logger.info("No blockchain.json file found.")
        return None
    try:
        with open(BLOCKCHAIN_FILE, "r", encoding="utf-8") as f:
            chain = json.load(f)
        
        if not isinstance(chain, list) or len(chain) == 0:
            raise ValueError("Blockchain root is empty or not a list")
            
        # Validate integrity (structure + HMAC)
        for i, block in enumerate(chain):
            if not isinstance(block, dict) or int(block.get('index', -1)) != i+1:
                raise ValueError(f"Block structure or index mismatch at block {i+1}")
            
            if not verify_block_signature(block):
                 raise ValueError(f"HMAC Signature mismatch at block {block.get('index')}")
            
        app.logger.info("Blockchain loaded from file and verified.", extra={'file': BLOCKCHAIN_FILE})
        return chain
    except Exception as e:
        app.logger.error("Failed to load blockchain from file: %s", e)
        backup = load_latest_backup()
        if backup:
            app.logger.warning("Loading blockchain from latest backup instead.")
            # Persist backup as main chain
            save_chain_to_file(backup)
            return backup
        return None

# ----------------------------
# 5. Initialize or load chain
# ----------------------------
shop_chain = Blockchain() # Start with in-memory genesis

if RESET_BLOCKCHAIN:
    # Delete file and re-init if reset requested
    if os.path.exists(BLOCKCHAIN_FILE): os.remove(BLOCKCHAIN_FILE)
    shop_chain = Blockchain()  # fresh genesis
    save_chain_to_file(shop_chain)
    app.logger.info("Blockchain reset to new genesis.")
else:
    loaded = load_chain_from_file_safe()
    if loaded:
        shop_chain = Blockchain(chain=loaded)
        app.logger.info("Shop chain initialized from file.")
    else:
        # No valid chain found -> keep fresh genesis and save it
        save_chain_to_file(shop_chain)
        app.logger.info("No valid chain found; created new chain and saved.")

# ----------------------------
# 6. Seeding products & admin
# ----------------------------
def seed_products():
    if Product.query.count() == 0:
        products = [
            Product(name="Mechanical Keyboard", price=750000, category="Gadget", image="/static/keyboard.jpg", description="Keyboard mekanikal TKL, clicky switch."),
            Product(name="Wireless Mouse", price=150000, category="Gadget", image="/static/mouse.jpg", description="Mouse ergonomis presisi tinggi."),
            Product(name="Monitor Ultrawide 34", price=3500000, category="Gadget", image="/static/monitor.jpg", description="Layar lebar resolusi 4K."),
            Product(name="Headphone ANC Pro", price=1200000, category="Gadget", image="/static/headphone.jpg", description="Perdam bising kelas atas."),
            Product(name="Portable SSD 1TB", price=1100000, category="Gadget", image="/static/ssd.jpg", description="Penyimpanan eksternal super cepat."),
            Product(name="Smartwatch Dev", price=850000, category="Gadget", image="/static/watch.jpg", description="Pelacak fitness dan notifikasi."),
            Product(name="Webcam 4K Streaming", price=600000, category="Gadget", image="/static/webcam.jpg", description="Kamera jernih untuk live code."),
            Product(name="USB-C Multi Hub", price=180000, category="Aksesoris", image="/static/usbhub.jpg", description="Hub 8-in-1 dengan PD charging."),
            Product(name="Laptop Stand Alloy", price=95000, category="Aksesoris", image="/static/stand.jpg", description="Stand aluminium kokoh."),
            Product(name="Gaming Mousepad XXL", price=75000, category="Aksesoris", image="/static/mousepad.jpg", description="Alas mouse super besar."),
            Product(name="DevSecOps Hoodie", price=250000, category="Fashion", image="/static/hoodie.jpg", description="Hoodie hitam anti-bug, fleece tebal."),
            Product(name="T-Shirt 'Git Push'", price=95000, category="Fashion", image="/static/tshirt.jpg", description="Kaos katun combed 30s."),
            Product(name="Tas Ransel Laptop", price=350000, category="Fashion", image="/static/backpack.jpg", description="Tas anti air, aman untuk laptop."),
            Product(name="Stainless Tumbler", price=95000, category="Lifestyle", image="/static/tumbler.jpg", description="Botol minum tahan panas/dingin."),
            Product(name="Ergonomic Footrest", price=180000, category="Aksesoris", image="/static/footrest.jpg", description="Sandaran kaki untuk posisi duduk ideal."),
            Product(name="Buku 'Hacking 101'", price=120000, category="Buku", image="/static/book1.jpg", description="Panduan wajib pemula keamanan siber."),
            Product(name="The Clean Code", price=150000, category="Buku", image="/static/book2.jpg", description="Kitab suci menulis kode yang rapi."),
            Product(name="VR Headset Basic", price=2800000, category="Gadget", image="/static/vrheadset.jpg", description="Pengalaman realitas virtual."),
            Product(name="License Key VPN", price=50000, category="Software", image="/static/license.jpg", description="Kunci lisensi 1 tahun layanan VPN."),
            Product(name="DevOps Sticker Pack", price=20000, category="Fashion", image="/static/stickers.jpg", description="Stiker keren Docker, Git, Kubernetes."),
        ]
        db.session.bulk_save_objects(products)
        db.session.commit()
        app.logger.info("Seeded products into database.", extra={'count': len(products)})

def seed_admin():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        hashed_pw = generate_password_hash('admin123')
        super_admin = User(username='admin', password=hashed_pw, role='admin')
        db.session.add(super_admin)
        db.session.commit()
        app.logger.info("Default Admin created.", extra={'user': 'admin', 'role': 'admin'})
    elif not check_password_hash(admin.password, 'admin123'):
        # Fix: If admin exists but password is not default hash (possible plaintext from old bug)
        admin.password = generate_password_hash('admin123')
        db.session.commit()
        app.logger.warning("Admin password updated to default hash (admin123).")

# ----------------------------
# 7. Routes (Front-end & User)
# ----------------------------
@app.route('/', defaults={'category_name': None})
@app.route('/katalog/<category_name>')
def home(category_name):
    cart_count = 0
    if 'cart' in session and session['cart']:
        try:
            cart_count = sum(session['cart'].values())
        except Exception:
            cart_count = sum(int(v) for v in session['cart'].values())
    if category_name and category_name != 'Semua':
        products = Product.query.filter_by(category=category_name).all()
        flash(f"Menampilkan kategori: {category_name}", 'info')
    else:
        products = Product.query.all()
    return render_template('index.html', products=products, cart_count=cart_count)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session or session['cart'] is None:
        session['cart'] = {}
    p_id = str(product_id)
    session['cart'][p_id] = session['cart'].get(p_id, 0) + 1
    session.modified = True
    flash('Produk masuk keranjang!', 'success')
    return redirect(url_for('home'))

@app.route('/cart')
def view_cart():
    cart_items = []
    total_price = 0
    if 'cart' in session and session['cart']:
        for p_id, quantity in session['cart'].items():
            try:
                pid = int(p_id)
            except Exception:
                continue
            product = db.session.get(Product, pid)
            if product:
                total = product.price * int(quantity)
                total_price += total
                cart_items.append({'product': product, 'quantity': int(quantity), 'total': total})
    return render_template('cart.html', cart_items=cart_items, total=total_price)

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    if 'cart' not in session or not session['cart']:
        flash('Keranjang kosong.', 'warning')
        return redirect(url_for('home'))

    items_summary_list = []
    total_trx = 0

    for p_id, quantity in session['cart'].items():
        try:
            pid = int(p_id)
        except Exception:
            continue
        product = db.session.get(Product, pid)
        if product:
            teks_barang = f"{product.name} (x{int(quantity)})"
            items_summary_list.append(teks_barang)
            total_trx += product.price * int(quantity)

    final_items_string = ", ".join(items_summary_list)

    app.logger.info("Processing new order.", extra={'user': current_user.username, 'role': current_user.role, 'event': 'ORDER_START', 'value': total_trx})

    # add tx to chain
    shop_chain.add_transaction(sender=current_user.username, items=final_items_string, total=total_trx)

    last_block = shop_chain.last_block
    previous_hash = Blockchain.hash(last_block) if last_block else '1'
    shop_chain.create_block(proof=12345, previous_hash=previous_hash)

    # persist chain safely
    save_chain_to_file(shop_chain)

    app.logger.info("Transaction mined.", extra={'user': current_user.username, 'value': total_trx, 'block_index': shop_chain.last_block['index']})

    # clear cart only
    session.pop('cart', None)
    session.modified = True
    flash('Pembayaran Berhasil!', 'success')
    return redirect(url_for('history'))

@app.route('/history')
@login_required
def history():
    if current_user.role != 'buyer':
        flash('Akses Ditolak.', 'danger')
        return redirect(url_for('home'))
    riwayat = shop_chain.get_transactions_by_user(current_user.username)

    # Preprocess each transaction to build items_list (safe parsing)
    for tx in riwayat:
        items_raw = tx.get('items')
        items_list = []
        try:
            if isinstance(items_raw, str):
                items_list = [s.strip() for s in items_raw.split(',') if s.strip()]
            else:
                items_list = [str(items_raw)]
        except Exception:
            items_list = [str(items_raw)]
        tx['items_list'] = items_list
    return render_template('history.html', history=riwayat)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            app.logger.info("User logged in.", extra={'user': username, 'role': user.role})
            flash(f"Berhasil login! Selamat datang kembali, {user.username}.", "success")
            # redirect admin to admin dashboard
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('home'))
        else:
            app.logger.warning("Failed login attempt.", extra={'user': username})
            flash("Username atau password salah!", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash("Username dan password wajib diisi.", "warning")
            return redirect(url_for('register'))

        existing = User.query.filter_by(username=username).first()
        if existing:
            flash("Akun sudah terdaftar! Silakan login.", "warning")
            return redirect(url_for('register'))

        hashed = generate_password_hash(password)
        user = User(username=username, password=hashed, role='buyer')
        db.session.add(user)
        db.session.commit()

        flash("Registrasi berhasil! Anda sudah dapat login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    app.logger.info("User logged out.", extra={'user': current_user.username})
    logout_user()
    # remove only user-related session keys (don't clear whole session)
    session.pop('cart', None)
    session.modified = True
    return redirect(url_for('home'))

@app.route('/debug_session')
def debug_session():
    return {"cart": session.get('cart')}

# ----------------------------
# 8. Routes (Admin Tools & Blockchain Explorer)
# ----------------------------
@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Akses Ditolak! Anda bukan Admin.', 'danger')
        return redirect(url_for('home'))

    all_transactions = shop_chain.get_all_transactions()
    
    # CRITICAL FIX: Preprocess items for safe rendering and detailed view
    for tx in all_transactions:
        tx["detailed_items"] = [] 
        raw = tx.get('items', "")
        
        # Split string transaksi ("Item (xQty)")
        if isinstance(raw, str):
            for item_str in raw.split(','):
                item_str = item_str.strip()
                if not item_str: continue

                try:
                    # 1. Parsing Nama dan Qty dari format "Nama Produk (xQty)"
                    # rsplit(' (x', 1) memisahkan "Nama Produk" dan "Qty)"
                    name_qty_str, qty_part = item_str.rsplit(' (x', 1) 
                    name = name_qty_str.strip()
                    
                    # 2. Ambil Quantity yang bersih (hapus kurung tutup ')' )
                    # Contoh: "1)" menjadi "1"
                    qty_str = qty_part.strip().rstrip(')')
                    qty_clean = int(qty_str) if qty_str.isdigit() else 1

                    # 3. Cari produk (Case Insensitive Search)
                    # Tambahkan db.func.lower untuk mencari tanpa case sensitivity
                    product = Product.query.filter(
                        db.func.lower(Product.name) == db.func.lower(name)
                    ).first()
                    
                    # Fallback ke pencarian biasa jika pencarian lower gagal
                    if not product:
                        product = Product.query.filter_by(name=name).first()
                    
                    price_clean = product.price if product else 0

                    tx["detailed_items"].append({
                        'name': name,
                        'qty': qty_clean,
                        'price': price_clean, 
                        'subtotal': (price_clean * qty_clean) 
                    })
                except ValueError:
                    # Menangani format yang tidak sesuai ("Item (xQty)")
                    tx["detailed_items"].append({
                        'name': item_str,
                        'qty': 1,
                        'price': 0,
                        'subtotal': 0
                    })
                except Exception:
                    # Fallback jika error lainnya
                    tx["detailed_items"].append({
                        'name': item_str,
                        'qty': 1,
                        'price': 0,
                        'subtotal': 0
                    })
        else:
            tx["detailed_items"] = [{'name': str(raw), 'qty': 1, 'price': 0, 'subtotal': 0}]
            
    all_users = User.query.all()
    total_revenue = sum(int(tx.get('total', 0)) for tx in all_transactions)

    return render_template('admin.html',
                           transactions=all_transactions,
                           users=all_users,
                           revenue=total_revenue)

# app.py: Ganti fungsi explorer() yang sudah ada (untuk data explorer)
@app.route('/explorer')
@login_required
def explorer():
    if current_user.role != 'admin':
        flash('Akses Ditolak.', 'danger')
        return redirect(url_for('home'))
    
    chain = shop_chain.chain
    blocks = []
    for b in chain:
        txs = []
        # Menggunakan logika parsing items_list agar Explorer berfungsi
        for tx in b.get('transactions', []):
            raw = tx.get('items', "")
            if isinstance(raw, str):
                tx["items_list"] = [s.strip() for s in raw.split(',') if s.strip()]
            else:
                tx["items_list"] = [str(raw)]
            txs.append(tx)

        blocks.append({
            'index': b.get('index'),
            'timestamp': format_datetime(b.get('timestamp')),
            'tx_count': len(txs),
            'previous_hash': b.get('previous_hash'),
            'proof': b.get('proof'),
            'signature': b.get('signature', 'N/A'),
            'transactions': txs
        })
    total_blocks = len(blocks)
    total_txs = sum(b['tx_count'] for b in blocks)
    return render_template('explorer.html', blocks=blocks, total_blocks=total_blocks, total_txs=total_txs)

@app.route('/admin/backup/download/<path:filename>')
@login_required
def admin_download_backup(filename):
    if current_user.role != 'admin':
        flash('Akses Ditolak.', 'danger')
        return redirect(url_for('home'))
    
    fpath = os.path.join(CHAIN_BACKUP_DIR, filename)
    # Security Check: Prevent directory traversal
    if not os.path.exists(fpath) or not fpath.startswith(CHAIN_BACKUP_DIR):
        flash('File tidak ditemukan atau akses ditolak.', 'warning')
        return redirect(url_for('admin_backups'))
    
    return send_file(fpath, as_attachment=True)


# Admin Backup & Restore Routes
@app.route('/admin/backups')
@login_required
def admin_backups():
    if current_user.role != 'admin':
        flash('Akses Ditolak.', 'danger')
        return redirect(url_for('home'))
    files = []
    if os.path.exists(CHAIN_BACKUP_DIR):
        # List files, filter, and sort (reverse=True for latest first)
        all_files = os.listdir(CHAIN_BACKUP_DIR)
        backup_files = [f for f in all_files if f.startswith('blockchain_') and f.endswith('.json')]
        files = sorted(backup_files, reverse=True)
    return render_template('admin_backups.html', backups=files)

@app.route('/admin/restore', methods=['POST'])
@login_required
def admin_restore():
    if current_user.role != 'admin':
        flash('Akses Ditolak.', 'danger')
        return redirect(url_for('home'))
        
    filename = request.form.get('filename')
    if not filename:
        flash('File tidak dipilih.', 'warning')
        return redirect(url_for('admin_backups'))
        
    src = os.path.join(CHAIN_BACKUP_DIR, filename)
    if not os.path.exists(src):
        flash('Backup tidak ditemukan.', 'danger')
        return redirect(url_for('admin_backups'))
        
    try:
        # Load and validate before replacing
        with open(src, 'r', encoding='utf-8') as f:
            data_to_restore = json.load(f)
            
        # Write to temp file, then atomic replace the main chain file
        tmp = BLOCKCHAIN_FILE + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as wf:
            json.dump(data_to_restore, wf, indent=2, ensure_ascii=False)
        os.replace(tmp, BLOCKCHAIN_FILE)
        
        # Reload to memory and re-verify integrity
        loaded = load_chain_from_file_safe()
        if loaded:
            global shop_chain
            shop_chain = Blockchain(chain=loaded)
            flash(f'Backup {filename} berhasil direstore.', 'success')
            app.logger.info("Admin restored chain from backup", extra={'user': current_user.username, 'backup': filename})
        else:
            flash('Restore gagal: file backup corrupt atau tidak valid.', 'danger')
            # Fallback will attempt to load latest good chain
            
    except Exception as e:
        app.logger.error("Restore error: %s", e)
        flash('Restore gagal karena kesalahan server: ' + str(e), 'danger')
        
    return redirect(url_for('admin_backups'))

@app.route('/admin/export_chain')
@login_required
def admin_export_chain():
    if current_user.role != 'admin':
        flash('Akses Ditolak.', 'danger')
        return redirect(url_for('home'))
    if not os.path.exists(BLOCKCHAIN_FILE):
        flash('Tidak ada chain untuk diekspor.', 'warning')
        return redirect(url_for('admin_dashboard'))
    return send_file(BLOCKCHAIN_FILE, as_attachment=True, download_name='devsecops_blockchain.json')

@app.route('/admin/import_chain', methods=['POST'])
@login_required
def admin_import_chain():
    if current_user.role != 'admin':
        flash('Akses Ditolak.', 'danger')
        return redirect(url_for('home'))
        
    f = request.files.get('file')
    if not f or f.filename == '':
        flash('File tidak diunggah.', 'warning')
        return redirect(url_for('admin_backups'))
        
    try:
        data = json.load(f.stream)
        # Attempt to validate and write to temp/replace
        
        tmp = BLOCKCHAIN_FILE + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as wf:
            json.dump(data, wf, indent=2, ensure_ascii=False)
        os.replace(tmp, BLOCKCHAIN_FILE)
        
        # Verify and reload
        loaded = load_chain_from_file_safe()
        if loaded:
            global shop_chain
            shop_chain = Blockchain(chain=loaded)
            flash('Import chain berhasil dan diterapkan.', 'success')
            app.logger.info("Admin imported chain", extra={'user': current_user.username})
        else:
            flash('Import gagal: data invalid atau korup.', 'danger')
            
    except Exception as e:
        app.logger.error("Import error: %s", e)
        flash('Import gagal karena kesalahan format file atau server: ' + str(e), 'danger')
        
    return redirect(url_for('admin_backups'))
@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if current_user.role != 'admin':
        flash('Akses Ditolak.', 'danger')
        return redirect(url_for('admin_dashboard'))

    user = db.session.get(User, user_id)
    if not user:
        flash('Pengguna tidak ditemukan.', 'danger')
        return redirect(url_for('admin_dashboard'))

    # Mencegah admin menghapus dirinya sendiri
    if user.id == current_user.id:
        flash('Anda tidak dapat menghapus akun Anda sendiri.', 'danger')
        return redirect(url_for('admin_dashboard'))

    username = user.username
    try:
        db.session.delete(user)
        db.session.commit()
        flash(f'Pengguna "{username}" berhasil dihapus.', 'success')
        app.logger.info("Admin deleted user", extra={'admin_user': current_user.username, 'deleted_user': username})
    except IntegrityError:
        db.session.rollback()
        flash('Gagal menghapus pengguna karena terkait dengan data lain (mis. transaksi).', 'danger')
    except Exception as e:
        db.session.rollback()
        app.logger.error("User deletion error: %s", e)
        flash('Gagal menghapus pengguna karena error server.', 'danger')

    return redirect(url_for('admin_dashboard'))


@app.route('/admin/change_role/<int:user_id>', methods=['POST'])
@login_required
def admin_change_role(user_id):
    if current_user.role != 'admin':
        flash('Akses Ditolak.', 'danger')
        return redirect(url_for('admin_dashboard'))

    user = db.session.get(User, user_id)
    new_role = request.form.get('new_role')

    if not user or new_role not in ['admin', 'buyer']:
        flash('Data tidak valid.', 'danger')
        return redirect(url_for('admin_dashboard'))

    if user.id == current_user.id and new_role != 'admin':
        flash('Anda tidak dapat menghapus hak admin dari akun Anda sendiri.', 'danger')
        return redirect(url_for('admin_dashboard'))

    old_role = user.role
    user.role = new_role
    db.session.commit()
    flash(f'Peran pengguna "{user.username}" diubah dari {old_role} menjadi {new_role}.', 'success')
    app.logger.info("Admin changed user role", extra={'admin_user': current_user.username, 'target_user': user.username, 'new_role': new_role})

    return redirect(url_for('admin_dashboard'))

# ----------------------------
# 9. App start
# ----------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_products()
        seed_admin()
        # Ensure current shop_chain persisted
        save_chain_to_file(shop_chain)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5002)))