import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
BASE = Path(__file__).resolve().parents[1]
DB = BASE / "orange_learn.db"

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_PUBLISHABLE_KEY") or os.getenv("SUPABASE_KEY")
if not url or not key:
    raise SystemExit("Set SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY first.")

supabase = create_client(url, key)
con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row

MAPPING = {
    "materi": ["id", "judul", "kategori", "deskripsi", "isi", "tingkat", "urutan"],
    "widget": ["id", "nama", "kategori", "deskripsi", "fungsi", "input_data", "output_data", "tingkat", "contoh", "urutan"],
    "workflow": ["id", "nama", "kategori", "tujuan", "deskripsi", "tingkat", "urutan"],
}

for table, columns in MAPPING.items():
    rows = con.execute(f"SELECT {', '.join(columns)} FROM {table} ORDER BY id").fetchall()
    payload = [dict(row) for row in rows]
    if payload:
        supabase.table(table).upsert(payload, on_conflict="id").execute()
    print(f"{table}: {len(payload)} rows migrated")

con.close()
print("Migration completed.")
