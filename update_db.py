import sqlite3

# Koneksi ke database yang sudah ada
conn = sqlite3.connect('keuangan.db')
cursor = conn.cursor()

try:
    # Perintah SQL untuk "Menyisipkan" kolom baru ke tabel yang sudah ada
    # Misal mau nambah kolom 'metode'
    cursor.execute("ALTER TABLE transaksi ADD COLUMN metode TEXT")
    print("Berhasil menambahkan kolom 'metode'!")
    
    # Kalau mau nambah kolom lain, copy paste baris execute di atas
    
except sqlite3.OperationalError:
    print("Kolom mungkin sudah ada, tidak perlu diupdate.")

conn.commit()
conn.close()