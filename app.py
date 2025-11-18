from flask import Flask, render_template, request
from flask_talisman import Talisman

app = Flask(__name__)

# Konfigurasi CSP untuk mengizinkan Bootstrap CDN & Gambar Unsplash
csp = {
    'default-src': ["'self'"],
    'style-src': ["'self'", "https://cdn.jsdelivr.net"],
    'img-src': ["'self'", "https://images.unsplash.com", "data:"],
    'script-src': ["'self'", "https://cdn.jsdelivr.net"]
}

# Terapkan Talisman dengan CSP yang sudah disesuaikan
Talisman(app, force_https=False, content_security_policy=csp)

@app.route('/')
def home():
    # Render file HTML yang ada di folder templates
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # TODO: Proses login yang aman
        username = request.form['username']
        return f"Halo, {username}! (Login belum aman)"
    
    return """
    <form method="post">
        Username: <input type="text" name="username"><br>
        Password: <input type="password" name="password"><br>
        <input type="submit" value="Login">
    </form>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) #nosec B104