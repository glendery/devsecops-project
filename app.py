# app.py
from flask import Flask, request
from flask_talisman import Talisman

app = Flask(__name__)
Talisman(app)  

# Halaman utama
@app.route('/')
def home():
    return "Selamat datang di Toko E-commerce Sederhana!"

# Halaman login (ini akan kita buat 'rentan' nanti)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # TODO: Proses login yang aman
        username = request.form['username']
        return f"Halo, {username}! (Login belum aman)"
    
    # Menampilkan form login
    return """
    <form method="post">
        Username: <input type="text" name="username"><br>
        Password: <input type="password" name="password"><br>
        <input type="submit" value="Login">
    </form>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  #nosec B104