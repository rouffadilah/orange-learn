# Gemini V5 Setup

Tambahkan `GEMINI_API_KEY` sebagai Secret di Vercel untuk Production.

Default model:
- `gemini-3.5-flash-lite`
- fallback `gemini-3.6-flash,gemini-3.5-flash`

Pengaturan ini dipilih untuk menjaga respons interaktif tetap cepat. Jika salah satu model sedang padat (mis. 503), aplikasi berpindah model secara otomatis dan kemudian menggunakan knowledge base lokal bila semua model tidak tersedia.

Jangan simpan API key di GitHub.
