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

- `OPENAI_API_KEY` = API key OpenAI Anda
- `OPENAI_MODEL` = `gpt-5.6-luna` (atau model yang tersedia di akun Anda)
- `OPENAI_RESPONSES_URL` = `https://api.openai.com/v1/responses`
- `OPENAI_TIMEOUT_SECONDS` = `20`

Setelah menambahkan variable, lakukan redeploy agar AI Tutor berpindah dari `Local Knowledge Mode` ke `Expert AI`.

API key hanya digunakan di backend `app.py` dan tidak ditanam ke JavaScript browser.
