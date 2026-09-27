# Setup Google Gemini untuk orange-learn

1. Buat API key di Google AI Studio.
2. Di Vercel → Project `orange-learn` → Settings → Environment Variables, tambahkan secret:

   `GEMINI_API_KEY`

3. Set environment ke Production (dan Preview bila diperlukan).
4. Redeploy tanpa menggunakan Build Cache setelah variable dibuat/diubah.

Konfigurasi default aplikasi:
- `GEMINI_MODEL=gemini-3.5-flash-lite`
- `GEMINI_FALLBACK_MODELSS=gemini-3.5-flash-lite`
- `GEMINI_THINKING_LEVEL=high`
- `GEMINI_MAX_OUTPUT_TOKENS=2800`
- `GEMINI_TEMPERATURE=0.2`
- `GEMINI_TIMEOUT_SECONDS=7`

API key jangan ditaruh di frontend, GitHub, atau dikirim melalui chat.


## Gemini V5 performance

- Page load tidak lagi memanggil API Gemini untuk sekadar diagnosis.
- Chat memakai model cepat terlebih dahulu dan berpindah model segera saat 429/503/5xx.
- Timeout interaktif dipangkas agar pengguna tidak menunggu terlalu lama; Local AI menjadi fallback tanpa menampilkan pesan error teknis di chat.
