import hashlib
import json
import os
import logging
from time import time
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_talisman import Talisman
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from pythonjsonlogger import jsonlogger # IMPORT BARU UNTUK LOGGING JSON

app = Flask(__name__)
app.config['SECRET_KEY'] = 'devsecops-secret-key-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- KONFIGURASI JSON LOGGER (AUDIT LOG) ---
# Mengatur handler untuk mencatat log ke konsol
handler = logging.StreamHandler()
# Mengatur format log menjadi JSON
formatter = jsonlogger.JsonFormatter(
    fmt='%(asctime)s %(levelname)s %(name)s %(module)s %(funcName)s %(message)s'
)
handler.setFormatter(formatter)

# Konfigurasi logger aplikasi
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO) 
app.logger.info("Application starting up.") # Log saat aplikasi dimulai
# --- END KONFIGURASI JSON LOGGER ---

# CONFIG SESSION
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_FILE_DIR"] = "./flask_session"
Session(app)

# KEAMANAN: Content Security Policy
csp = {
    'default-src': ["'self'"],
    'style-src': ["'self'", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com", "'unsafe-inline'"],
    'font-src': ["'self'", "https://cdnjs.cloudflare.com"],
    # INI KUNCINYA: Mengizinkan sumber placeholder yang spesifik
    'img-src': ["'self'", "data:", "https://via.placeholder.com"], 
    'script-src': ["'self'", "https://cdn.jsdelivr.net"],
    'connect-src': ["'self'", "https://cdn.jsdelivr.net"] 
}
Talisman(app, force_https=False, content_security_policy=csp)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # type: ignore

# --- MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    # Role: 'admin' (Seller) atau 'buyer' (Customer)
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
    return User.query.get(int(user_id))

# --- BLOCKCHAIN ---
class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.create_block(previous_hash='1', proof=100)

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.pending_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.pending_transactions = []
        self.chain.append(block)
        return block

    def add_transaction(self, sender, items, total):
        self.pending_transactions.append({
            'sender': sender, 'items': items, 'total': total, 'timestamp': time()
        })
        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def get_transactions_by_user(self, username):
        user_history = []
        for block in self.chain:
            for tx in block['transactions']:
                if tx['sender'] == username:
                    tx['block_index'] = block['index']
                    user_history.append(tx)
        return user_history

    def get_all_transactions(self):
        all_tx = []
        for block in self.chain:
            for tx in block['transactions']:
                tx['block_index'] = block['index']
                all_tx.append(tx)
        return all_tx

shop_chain = Blockchain()

# --- SEEDING DATA ---
def seed_products():
    if Product.query.count() == 0:
        products = [
            # GADGET & AKSESORIS
            Product(name="Mechanical Keyboard", price=750000, category="Gadget", image="/static/keyboard.jpg", description="Keyboard mekanikal TKL, clicky switch."), # type: ignore
            Product(name="Wireless Mouse", price=150000, category="Gadget", image="/static/mouse.jpg", description="Mouse ergonomis presisi tinggi."), # type: ignore
            Product(name="Monitor Ultrawide 34", price=3500000, category="Gadget", image="/static/monitor.jpg", description="Layar lebar resolusi 4K."), # type: ignore
            Product(name="Headphone ANC Pro", price=1200000, category="Gadget", image="/static/headphone.jpg", description="Perdam bising kelas atas."), # type: ignore
            Product(name="Portable SSD 1TB", price=1100000, category="Gadget", image="/static/ssd.jpg", description="Penyimpanan eksternal super cepat."), # type: ignore
            Product(name="Smartwatch Dev", price=850000, category="Gadget", image="/static/watch.jpg", description="Pelacak fitness dan notifikasi."), # type: ignore
            Product(name="Webcam 4K Streaming", price=600000, category="Gadget", image="/static/webcam.jpg", description="Kamera jernih untuk live code."), # type: ignore
            Product(name="USB-C Multi Hub", price=180000, category="Aksesoris", image="/static/usbhub.jpg", description="Hub 8-in-1 dengan PD charging."), # type: ignore
            Product(name="Laptop Stand Alloy", price=95000, category="Aksesoris", image="/static/stand.jpg", description="Stand aluminium kokoh."), # type: ignore
            Product(name="Gaming Mousepad XXL", price=75000, category="Aksesoris", image="/static/mousepad.jpg", description="Alas mouse super besar."), # type: ignore
            
            # FASHION, LIFESTYLE & BUKU
            Product(name="DevSecOps Hoodie", price=250000, category="Fashion", image="/static/hoodie.jpg", description="Hoodie hitam anti-bug, fleece tebal."), # type: ignore
            Product(name="T-Shirt 'Git Push'", price=95000, category="Fashion", image="/static/tshirt.jpg", description="Kaos katun combed 30s."), # type: ignore
            Product(name="Tas Ransel Laptop", price=350000, category="Fashion", image="/static/backpack.jpg", description="Tas anti air, aman untuk laptop."), # type: ignore
            Product(name="Stainless Tumbler", price=95000, category="Lifestyle", image="/static/tumbler.jpg", description="Botol minum tahan panas/dingin."), # type: ignore
            Product(name="Ergonomic Footrest", price=180000, category="Aksesoris", image="/static/footrest.jpg", description="Sandaran kaki untuk posisi duduk ideal."), # type: ignore
            Product(name="Buku 'Hacking 101'", price=120000, category="Buku", image="/static/book1.jpg", description="Panduan wajib pemula keamanan siber."), # type: ignore
            Product(name="The Clean Code", price=150000, category="Buku", image="/static/book2.jpg", description="Kitab suci menulis kode yang rapi."), # type: ignore
            Product(name="VR Headset Basic", price=2800000, category="Gadget", image="/static/vrheadset.jpg", description="Pengalaman realitas virtual."), # type: ignore
            Product(name="License Key VPN", price=50000, category="Software", image="/static/license.jpg", description="Kunci lisensi 1 tahun layanan VPN."), # type: ignore
            Product(name="DevOps Sticker Pack", price=20000, category="Fashion", image="/static/stickers.jpg", description="Stiker keren Docker, Git, Kubernetes."), # type: ignore
        ]
        db.session.bulk_save_objects(products) # type: ignore
        db.session.commit()
        print("Database produk berhasil diupdate dengan 20 Item Lokal!")

# --- SEEDING ADMIN (Penjual Otomatis) ---
def seed_admin():
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        hashed_pw = generate_password_hash('admin123') 
        super_admin = User(username='admin', password=hashed_pw, role='admin') # type: ignore
        db.session.add(super_admin)
        db.session.commit()
        app.logger.info("Default Admin created.", extra={'user': 'admin', 'role': 'admin', 'event': 'USER_SEED'})
        print(">>> ADMIN READY: User='admin', Pass='admin123'")

# --- ROUTES ---
@app.route('/', defaults={'category_name': None})
@app.route('/katalog/<category_name>')
def home(category_name):
    cart_count = 0
    if 'cart' in session:
        cart_count = sum(session['cart'].values())
    
    # --- LOGIKA FILTER BARU ---
    if category_name and category_name != 'Semua':
        # Filter produk berdasarkan kategori yang dipilih
        products = Product.query.filter_by(category=category_name).all()
        flash(f"Menampilkan kategori: {category_name}", 'info')
    else:
        # Tampilkan semua produk jika tidak ada filter
        products = Product.query.all()
    # --- END LOGIKA FILTER BARU ---

    return render_template('index.html', products=products, cart_count=cart_count)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = {}
    p_id = str(product_id)
    if p_id in session['cart']:
        session['cart'][p_id] += 1
    else:
        session['cart'][p_id] = 1
    flash('Produk masuk keranjang!', 'success')
    return redirect(url_for('home'))

@app.route('/cart')
def view_cart():
    if 'cart' not in session or not session['cart']:
        return render_template('cart.html', cart_items=[], total=0)
    cart_items = []
    total_price = 0
    for p_id, quantity in session['cart'].items():
        product = Product.query.get(int(p_id))
        if product:
            total = product.price * quantity
            total_price += total
            cart_items.append({'product': product, 'quantity': quantity, 'total': total})
    return render_template('cart.html', cart_items=cart_items, total=total_price)

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    if 'cart' not in session or not session['cart']:
        return redirect(url_for('home'))
    
    items_summary_list = []
    total_trx = 0
    
    for p_id, quantity in session['cart'].items():
        product = Product.query.get(int(p_id))
        if product:
            teks_barang = f"{product.name} (x{quantity})"
            items_summary_list.append(teks_barang)
            total_trx += product.price * quantity
            
    final_items_string = ", ".join(items_summary_list)

    # LOG: Pesanan sedang diproses
    app.logger.info(
        "Processing new order.",
        extra={'user': current_user.username, 'role': current_user.role, 'event': 'ORDER_START', 'value': total_trx}
    )
    
    # Simpan Transaksi ke Blockchain (Block Pending)
    shop_chain.add_transaction(
        sender=current_user.username, 
        items=final_items_string, 
        total=total_trx
    )
    
    # Mining Block baru
    last_block = shop_chain.last_block
    previous_hash = shop_chain.hash(last_block)
    shop_chain.create_block(proof=12345, previous_hash=previous_hash)
    
    # LOG: Transaksi Berhasil
    app.logger.info(
        "Transaction successfully mined to blockchain.",
        extra={'user': current_user.username, 'role': current_user.role, 'event': 'ORDER_COMPLETE', 'value': total_trx, 'block_index': shop_chain.last_block['index']}
    )
    
    session['cart'] = {}
    flash('Pembayaran Berhasil!', 'success')
        
    return redirect(url_for('my_orders'))

@app.route('/my_orders')
@login_required
def my_orders():
    # Hanya bisa diakses oleh Buyer
    if current_user.role != 'buyer':
        flash('Akses Ditolak.', 'danger')
        return redirect(url_for('home'))
        
    history = shop_chain.get_transactions_by_user(current_user.username)
    return render_template('history.html', history=history)

@app.route('/admin')
@login_required
def admin_dashboard():
    # Hanya bisa diakses oleh Admin
    if current_user.role != 'admin':
        flash('Akses Ditolak! Anda bukan Admin.', 'danger')
        return redirect(url_for('home'))
    
    all_transactions = shop_chain.get_all_transactions()
    all_users = User.query.all()
    total_revenue = sum(tx['total'] for tx in all_transactions)
    
    return render_template('admin.html', transactions=all_transactions, users=all_users, revenue=total_revenue)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            # LOG SUKSES
            app.logger.info(
                "User logged in successfully.",
                extra={'user': username, 'role': user.role, 'event': 'AUTH_SUCCESS'}
            )
            
            # Redirect berdasarkan Role
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('home'))
                
        # LOG GAGAL
        app.logger.warning(
            "Failed login attempt.",
            extra={'user': username, 'event': 'AUTH_FAIL', 'reason': 'Invalid credentials'}
        )
        flash('Login gagal.', 'danger')
        
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # OTOMATIS JADI BUYER (Tidak ada pilihan role di form)
        role = 'buyer' 

        if User.query.filter_by(username=username).first():
            app.logger.warning(
                "Registration attempt failed.",
                extra={'user': username, 'event': 'REG_FAIL', 'reason': 'Username already exists'}
            )
            flash('Username sudah ada.', 'warning')
            return redirect(url_for('register'))
        
        new_user = User(username=username, password=generate_password_hash(password), role=role) # type: ignore
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        
        # LOG SUKSES
        app.logger.info(
            "New user registered.",
            extra={'user': username, 'role': role, 'event': 'REG_SUCCESS'}
        )
        
        flash('Pendaftaran berhasil, Selamat Berbelanja!', 'success')
        return redirect(url_for('home'))
        
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    app.logger.info(
        "User logged out.",
        extra={'user': current_user.username, 'role': current_user.role, 'event': 'AUTH_LOGOUT'}
    )
    logout_user()
    session.clear()
    return redirect(url_for('home'))

@app.route('/explorer')
def explorer():
    return render_template('explorer.html', chain=shop_chain.chain)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_products()
        seed_admin() # Otomatis membuat Super Admin
    app.run(host='0.0.0.0', port=5002) #nosec B104