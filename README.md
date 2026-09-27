# orange-learn
Deployment configuration updated.




## Fitur AI Tutor Expert

AI Tutor memiliki dua mode:
- Expert AI, aktif saat `OPENAI_API_KEY` tersedia di environment server/Vercel. Model dapat diatur lewat `OPENAI_MODEL` (default `gpt-5.6-luna`).
- Local Knowledge Mode sebagai fallback tanpa API.

Simpan API key hanya di environment variables server/Vercel, jangan di JavaScript browser.
