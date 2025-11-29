from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import csv
import io
from datetime import datetime
import random  # <--- Tambahkan ini di baris paling atas

app = Flask(__name__)
app.secret_key = 'rahasia_donk'
DB_NAME = "keuangan.db"

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabel Users (Tambah kolom budget)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            budget REAL DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            jenis TEXT NOT NULL,
            kategori TEXT NOT NULL,
            nominal REAL NOT NULL,
            keterangan TEXT,
            tanggal TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes Auth ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password, budget) VALUES (?, ?, 0)", (username, hashed_pw))
            conn.commit()
            conn.close()
            flash('Registrasi berhasil!', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username sudah ada!', 'danger')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        user = cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        else:
            flash('Login gagal!', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- Routes Utama & Fitur Baru ---

@app.route('/')
@login_required
def index():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    user_id = session['user_id']

    # --- LOGIKA SAPAAN & QUOTES (BARU) ---
    jam = datetime.now().hour
    if 5 <= jam < 11:
        sapaan = "Selamat Pagi ☀️"
    elif 11 <= jam < 15:
        sapaan = "Selamat Siang 🌤️"
    elif 15 <= jam < 18:
        sapaan = "Selamat Sore 🌇"
    else:
        sapaan = "Selamat Malam 🌙"

    daftar_quotes = [
        "Hemat pangkal kaya.",
        "Jangan beli kopi mahal terus!",
        "Tabung dulu, jajan kemudian.",
        "Gunakan uangmu untuk pengalaman, bukan sekadar barang.",
        "Investasi terbaik adalah leher ke atas (ilmu).",
        "Ingat, gajian masih lama."
    ]
    quote_pilihan = random.choice(daftar_quotes)

    
    # Fitur Pencarian & Filter
    q = request.args.get('q', '')
    filter_bulan = request.args.get('filter', 'all') # 'all' atau 'this_month'

    query = "SELECT * FROM transaksi WHERE user_id = ?"
    params = [user_id]

    if q:
        query += " AND (keterangan LIKE ? OR kategori LIKE ?)"
        params.extend([f'%{q}%', f'%{q}%'])

    if filter_bulan == 'this_month':
        bulan_sekarang = datetime.now().strftime('%Y-%m')
        query += " AND strftime('%Y-%m', tanggal) = ?"
        params.append(bulan_sekarang)

    query += " ORDER BY id DESC"
    
    cursor.execute(query, params)
    transaksi = cursor.fetchall()

    # Hitung Total
    total_pemasukan = sum(t['nominal'] for t in transaksi if t['jenis'] == 'Pemasukan')
    total_pengeluaran = sum(t['nominal'] for t in transaksi if t['jenis'] == 'Pengeluaran')
    saldo = total_pemasukan - total_pengeluaran

    # Ambil Budget User
    user = cursor.execute("SELECT budget FROM users WHERE id = ?", (user_id,)).fetchone()
    budget = user['budget']

    conn.close()
    
    return render_template('index.html', 
                           transaksi=transaksi, 
                           pemasukan=total_pemasukan, 
                           pengeluaran=total_pengeluaran, 
                           saldo=saldo,
                           user_name=session['username'],
                           budget=budget,
                           q=q,
                           filter_bulan=filter_bulan,
                           sapaan=sapaan,
                           quote=quote_pilihan)

@app.route('/add', methods=['POST'])
@login_required
def add_transaction():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # LOGIKA BARU: Cek apakah user mengisi tanggal manual?
    tanggal_input = request.form['tanggal_custom']
    
    if tanggal_input:
        # Kalau user isi, pakai waktu pilihan user
        # Format input HTML biasanya 'YYYY-MM-DDTHH:MM' (ada huruf T di tengah)
        # Kita ganti T jadi spasi agar cocok sama database
        waktu_final = tanggal_input.replace('T', ' ')
    else:
        # Kalau kosong, pakai waktu sekarang (Auto)
        waktu_final = datetime.now()

    cursor.execute("""
        INSERT INTO transaksi (user_id, jenis, kategori, nominal, keterangan, tanggal) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        session['user_id'], 
        request.form['jenis'], 
        request.form['kategori'], 
        float(request.form['nominal'].replace('.', '')), 
        request.form['keterangan'],
        waktu_final # Pakai waktu hasil logika di atas
    ))
    
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
@login_required
def delete_transaction(id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transaksi WHERE id = ? AND user_id = ?", (id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# --- Fitur Edit ---
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == 'POST':
        cursor.execute("""
            UPDATE transaksi 
            SET jenis=?, kategori=?, nominal=?, keterangan=? 
            WHERE id=? AND user_id=?
        """, (request.form['jenis'], request.form['kategori'], float(request.form['nominal'].replace('.', '')), request.form['keterangan'], id, session['user_id']))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    # Ambil data lama
    transaksi = cursor.execute("SELECT * FROM transaksi WHERE id=? AND user_id=?", (id, session['user_id'])).fetchone()
    conn.close()
    return render_template('edit.html', t=transaksi)

# --- Fitur Update Budget ---
@app.route('/set_budget', methods=['POST'])
@login_required
def set_budget():
    budget_baru = float(request.form['budget'])
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET budget = ? WHERE id = ?", (budget_baru, session['user_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# --- Fitur Export CSV ---
@app.route('/export')
@login_required
def export_csv():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT tanggal, jenis, kategori, nominal, keterangan FROM transaksi WHERE user_id = ? ORDER BY id DESC", (session['user_id'],))
    data = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Tanggal', 'Jenis', 'Kategori', 'Nominal', 'Keterangan']) # Header
    writer.writerows(data)
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=laporan_keuangan.csv"}
    )

if __name__ == '__main__':
    # host='0.0.0.0' artinya bisa diakses dari perangkat lain
    app.run(host='0.0.0.0', port=5000, debug=True)