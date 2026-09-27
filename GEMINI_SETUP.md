# Setup Google Gemini untuk orange-learn

1. Buat API key di Google AI Studio.
2. Di Vercel → Project `orange-learn` → Settings → Environment Variables, tambahkan secret:

   `GEMINI_API_KEY`

3. Set environment ke Production (dan Preview bila diperlukan).
4. Redeploy tanpa menggunakan Build Cache setelah variable dibuat/diubah.

Konfigurasi default aplikasi:
- `GEMINI_MODEL=gemini-3.8-flash`
- `GEMINI_FALLBACK_MODEL=gemini-3.8-flash`
- `GEMINI_THINKING_LEVEL=high`
- `GEMINI_MAX_OUTPUT_TOKENS=8192`
- `GEMINI_RETRY_COUNT=2`
- `GEMINI_TIMEOUT_SECONDS=18`

API key jangan ditaruh di frontend, GitHub, atau dikirim melalui chat.
