# Gemini AI Fix V5

Perbaikan fokus pada kecepatan dan ketahanan saat provider Gemini mengembalikan 503.

- Model utama: `gemini-3.5-flash-lite` untuk interaksi cepat.
- Failover otomatis: `gemini-3.6-flash`, lalu `gemini-3.5-flash`.
- Timeout per percobaan dipangkas menjadi 5 detik.
- Tidak ada retry panjang; 429/503/5xx langsung berpindah model.
- Halaman AI Tutor tidak lagi melakukan panggilan Gemini diagnostik saat pertama dibuka.
- Pesan error teknis provider tidak ditampilkan kepada pengguna; aplikasi menggunakan Local Knowledge fallback.
- Endpoint chat selalu mengembalikan JSON.
