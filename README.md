# orange-learn
Deployment configuration updated.




## Fitur AI Tutor Expert

AI sekarang memakai Google Gemini API dengan konteks percakapan, knowledge base lokal, workflow detection, retry otomatis, dan reasoning bertingkat. Web search tidak diaktifkan pada mode ini agar tetap sesuai dengan jalur Free Tier.

AI Tutor memiliki dua mode:
- Expert Gemini AI, aktif saat `GEMINI_API_KEY` tersedia di environment server/Vercel. Model dapat diatur lewat `GEMINI_MODEL` (default `gemini-3.7-flash`).
- Local Knowledge Mode sebagai fallback tanpa API.

Simpan API key hanya di environment variables server/Vercel, jangan di JavaScript browser.


## AI Tutor

AI Tutor menggunakan Google Gemini melalui `GEMINI_API_KEY`. Default model `gemini-3.7-flash` dipilih untuk reasoning dan workflow yang kompleks. Bila API tidak tersedia, aplikasi otomatis menggunakan Local Knowledge Base.
