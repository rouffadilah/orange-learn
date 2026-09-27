# orange-learn
Deployment configuration updated.




## Fitur AI Tutor Expert

AI sekarang memakai Google Gemini API dengan konteks percakapan, knowledge base lokal, workflow detection, retry otomatis, dan reasoning bertingkat. Web search tidak diaktifkan pada mode ini agar tetap sesuai dengan jalur Free Tier.

AI Tutor memiliki dua mode:
- Expert Gemini AI, aktif saat `GEMINI_API_KEY` tersedia di environment server/Vercel. Model dapat diatur lewat `GEMINI_MODEL` (default `gemini-3.5-flash-lite`).
- Local Knowledge Mode sebagai fallback tanpa API.

Simpan API key hanya di environment variables server/Vercel, jangan di JavaScript browser.


## AI Tutor

AI Tutor menggunakan Google Gemini melalui `GEMINI_API_KEY`. Default model `gemini-3.5-flash-lite` dipilih untuk reasoning dan workflow yang kompleks. Bila API tidak tersedia, aplikasi otomatis menggunakan Local Knowledge Base.


## Gemini V5 performance

- Page load tidak lagi memanggil API Gemini untuk sekadar diagnosis.
- Chat memakai model cepat terlebih dahulu dan berpindah model segera saat 429/503/5xx.
- Timeout interaktif dipangkas agar pengguna tidak menunggu terlalu lama; Local AI menjadi fallback tanpa menampilkan pesan error teknis di chat.

## Panduan Fitur Visual
Orange Learn kini menyediakan halaman `/fitur` untuk menjelaskan widget dan fitur Orange Data Mining melalui ilustrasi orisinal yang mengikuti struktur canvas, widget, port input-output, dan channel.

## Workflow Builder visual + CSV

Workflow Builder sekarang menyediakan canvas visual bergaya node-and-port seperti workflow desktop: widget dapat ditambah, dipindahkan, dihubungkan, disimpan, dimuat, divalidasi, dan dijalankan. Widget File mendukung upload CSV langsung dari browser.

Fitur olah dataset yang tersedia pada builder:
- Import CSV dengan delimiter koma, titik koma, atau tab
- Preview Data Table
- Profil kolom, tipe data, missing value, min/avg/max
- Select Columns untuk memilih fitur dan target/class
- Data Sampler untuk membuat subset data
- Preprocess untuk menangani missing value
- Distribution/Histogram sederhana
- Scatter Plot dua variabel numerik
- Export kembali menjadi CSV setelah transformasi
- Dataset contoh `public/datasets/contoh_siswa.csv`
