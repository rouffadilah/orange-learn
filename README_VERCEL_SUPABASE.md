# orange-learn — Vercel + Supabase

This version keeps the original Flask pages and tutor/workflow behavior, but replaces the SQLite database with Supabase PostgreSQL.

## What changed
- Removed the bundled Windows `venv/` from deployment.
- Moved `static/` assets to `public/` for Vercel.
- Replaced SQLite reads with the Supabase Python client.
- Added `/health` to check that Vercel can reach Supabase.
- Added `supabase_schema.sql` and `supabase_seed.sql` generated from the original SQLite database.

## Supabase setup
1. Create a Supabase project.
2. In SQL Editor, run `supabase_schema.sql`.
3. Run `supabase_seed.sql`.
4. From the Supabase project Connect/API area, copy the Project URL and Publishable Key.

## Local setup
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in the Supabase values, then:

```bash
python app.py
```

Check: `http://127.0.0.1:5000/health`

## Vercel setup
Push this folder to GitHub, import the repository into Vercel, and add these environment variables in the Vercel project:

- `SUPABASE_URL`
- `SUPABASE_PUBLISHABLE_KEY`

Vercel detects `app.py` as the Flask entrypoint. The `public/` directory is served as static assets.

## Important security note
This application currently needs only read access, so the Supabase Publishable Key is used with Row Level Security (RLS) policies that allow public reads on the three content tables. Do not put a Supabase secret/service key in browser-side code.

## Original database
The original SQLite database was used only to generate the migration SQL and is intentionally not included in this deploy-ready folder.

## Mengaktifkan orange-learn AI Expert

Tambahkan Environment Variables di project Vercel:

## Environment Variables

- `GEMINI_API_KEY` = API key Gemini dari Google AI Studio
- `GEMINI_MODEL` = `gemini-3.5-flash-lite`
- `GEMINI_FALLBACK_MODELSS` = `gemini-3.5-flash-lite`
- `GEMINI_THINKING_LEVEL` = `high`
- `GEMINI_MAX_OUTPUT_TOKENS` = `8192`
- `GEMINI_TEMPERATURE` = `0.2`
- `GEMINI_TIMEOUT_SECONDS` = `30`

API key hanya digunakan di backend `app.py` dan tidak ditanam ke JavaScript browser.

Gemini API menyediakan Free Tier dengan batas penggunaan tertentu. Model `gemini-3.5-flash-lite` tercantum memiliki Free Tier; batas dapat berubah dan tetap tunduk pada kuota akun. Untuk aplikasi dengan volume tinggi, cek pricing resmi Google AI for Developers.


## Gemini V5 performance

- Page load tidak lagi memanggil API Gemini untuk sekadar diagnosis.
- Chat memakai model cepat terlebih dahulu dan berpindah model segera saat 429/503/5xx.
- Timeout interaktif dipangkas agar pengguna tidak menunggu terlalu lama; Local AI menjadi fallback tanpa menampilkan pesan error teknis di chat.
