# orange-learn
Deployment configuration updated.




## Fitur AI Tutor Expert

AI sekarang memakai Responses API dengan konteks percakapan, knowledge base lokal, workflow detection, retry otomatis, dan opsi web search untuk memperkaya jawaban teknis yang membutuhkan dokumentasi terbaru.

AI Tutor memiliki dua mode:
- Expert AI, aktif saat `OPENAI_API_KEY` tersedia di environment server/Vercel. Model dapat diatur lewat `OPENAI_MODEL` (default `gpt-5.6-sol`).
- Local Knowledge Mode sebagai fallback tanpa API.

Simpan API key hanya di environment variables server/Vercel, jangan di JavaScript browser.
