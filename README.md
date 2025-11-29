# 💰 Dompet Keuangan (Simple Finance Tracker)

Aplikasi pencatat keuangan sederhana berbasis web yang didesain agar **menyenangkan** dan **mudah digunakan**. 
Dibuat dengan Python (Flask) dengan tampilan yang santai menggunakan font **Comic Sans** dan fitur keamanan privasi ala M-Banking.

## ✨ Fitur Unggulan

Aplikasi ini dilengkapi fitur-fitur yang memanjakan pengguna:

* **🔐 Login & Register:** Data tiap pengguna terpisah dan aman (Password di-hash).
* **👁️ Sensor Privasi (Privacy Mode):** Sembunyikan nominal saldo menjadi bintang (`*******`) dengan satu klik (seperti M-Banking), aman dibuka di tempat umum.
* **⚡ Input Cepat:** Tombol *shortcut* nominal (5rb, 10rb, 50rb) dan kategori (Makan, Bensin, Kuota) agar mencatat tidak ribet.
* **📅 Backdate Transaction:** Bisa catat transaksi tanggal kemarin jika lupa mencatat.
* **💸 Format Rupiah Otomatis:** Ketik angka `1000000`, otomatis muncul titik `1.000.000`.
* **📊 Dashboard Pintar:** Grafik visual (Chart.js), filter per bulan, dan target budget bulanan dengan indikator warna.
* **📂 Export Data:** Download laporan keuangan ke format CSV (Excel) kapan saja.
* **🎨 Tampilan Unik:** Menggunakan font *Comic Sans MS* dengan sapaan personal dan *Quotes* keuangan acak setiap kali login.

## 🛠️ Teknologi yang Digunakan

* **Backend:** Python (Flask)
* **Database:** SQLite (Built-in, otomatis dibuat, ringan)
* **Frontend:** HTML5, CSS3 (Bootstrap 5), JavaScript
* **Icons:** Bootstrap Icons
* **Grafik:** Chart.js

## 🚀 Cara Menjalankan di Komputer Kamu (Localhost)

Ingin mencoba aplikasi ini di komputermu? Ikuti langkah mudah ini:


Ketik perintah ini di terminal/CMD: 

  python app.py

Akses alamat berikut: http://127.0.0.1:5000
