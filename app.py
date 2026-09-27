from flask import Flask, render_template, request, jsonify
import json
import os
import re
import urllib.error
import urllib.request
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__, static_folder=None)


def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_PUBLISHABLE_KEY") or os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError(
            "Supabase belum dikonfigurasi. Set SUPABASE_URL dan "
            "SUPABASE_PUBLISHABLE_KEY di environment variables."
        )
    return create_client(url, key)


def load_json(filename: str) -> list[dict[str, Any]]:
    path = BASE_DIR / "data" / filename
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def load_orange_knowledge():
    return load_json("orange_knowledge.json")


def load_workflow_templates():
    return load_json("workflow_templates.json")


def tokenise(text: str) -> set[str]:
    return {
        token for token in re.findall(r"[a-zA-Z0-9&+.-]+", str(text).lower()) if len(token) > 2
    }


def detect_workflow_type(question):
    question = question.lower().strip()
    templates = load_workflow_templates()
    q_tokens = tokenise(question)
    best_template = None
    best_score = 0
    for template in templates:
        score = 0
        for keyword in template.get("keywords", []):
            keyword_l = keyword.lower()
            if keyword_l in question:
                score += max(2, len(keyword_l))
            score += len(q_tokens.intersection(tokenise(keyword)))
        if score > best_score:
            best_score = score
            best_template = template
    return best_template


def search_orange_knowledge(question, limit=5):
    knowledge = load_orange_knowledge()
    question_l = question.lower().strip()
    q_tokens = tokenise(question)
    ranked = []
    for item in knowledge:
        score = 0
        for keyword in item.get("keywords", []):
            keyword_l = keyword.lower()
            if keyword_l in question_l:
                score += max(3, len(keyword_l))
            score += 2 * len(q_tokens.intersection(tokenise(keyword)))
        score += len(q_tokens.intersection(tokenise(item.get("question", ""))))
        score += len(q_tokens.intersection(tokenise(item.get("answer", ""))))
        if score:
            ranked.append((score, item))
    ranked.sort(key=lambda pair: pair[0], reverse=True)
    results = [item for score, item in ranked[:limit]]
    return {
        "found": bool(results),
        "results": results,
        "score": ranked[0][0] if ranked else 0,
        "answer": results[0]["answer"] if results else (
            "Saya belum menemukan jawaban yang cukup spesifik di knowledge base. "
            "Saya tetap bisa membantu secara konseptual atau menyusun langkah workflow."
        ),
    }


EXPERT_SYSTEM_PROMPT = """
Anda adalah orange-learn AI, tutor ahli Orange Data Mining untuk pembelajaran tingkat sekolah menengah hingga perguruan tinggi awal.
Fokus utama: Orange Data Mining, widget, data preparation, exploratory data analysis, klasifikasi, regresi, clustering, evaluasi model, visualisasi, workflow, dan praktik machine learning.

Aturan jawaban:
1. Jawab dalam Bahasa Indonesia yang jelas, terstruktur, dan bertahap.
2. Jangan hanya memberi definisi. Jelaskan kapan dipakai, mengapa dipakai, input-output, dan langkah praktik di Orange.
3. Untuk pertanyaan workflow, berikan urutan widget menggunakan panah serta alasan tiap widget.
4. Untuk evaluasi model, jelaskan metrik yang relevan dan cara membaca hasilnya.
5. Untuk debugging workflow, identifikasi titik putus alur, tipe data, target/class, preprocessing, dan koneksi widget berdasarkan informasi pengguna.
6. Gunakan contoh dataset pendidikan bila cocok, tetapi jangan mengarang hasil eksperimen yang belum dijalankan.
7. Bedakan fakta dari asumsi. Bila informasi tidak tersedia di konteks, nyatakan keterbatasannya dan sarankan verifikasi di dokumentasi Orange.
8. Hindari jargon yang tidak dijelaskan. Gunakan heading singkat dan bullet secukupnya.
9. Bila pengguna terlihat pemula, mulai dari konsep dasar lalu naikkan ke level teknis.
10. Selalu akhiri dengan satu langkah berikutnya yang konkret.
""".strip()


def build_local_expert_answer(question: str, knowledge_result: dict, template: dict | None):
    parts = []
    if knowledge_result["found"]:
        parts.append(knowledge_result["answer"])
        if len(knowledge_result["results"]) > 1:
            related = ", ".join(item.get("question", "") for item in knowledge_result["results"][1:4])
            parts.append(f"\nTopik yang juga relevan: {related}.")
    else:
        parts.append(knowledge_result["answer"])

    if template:
        flow = " → ".join(template.get("widgets", []))
        parts.append(
            f"\n\n**Rancangan workflow:** {flow}\n"
            f"Jenis analisis: {template.get('name', '-')}. {template.get('description', '')}"
        )
    parts.append("\n**Langkah berikutnya:** jelaskan dataset yang Anda gunakan (nama kolom dan target/class) agar workflow dapat disesuaikan lebih presisi.")
    return "\n".join(parts)


def _valid_openai_key(value: str | None) -> bool:
    if not value:
        return False
    value = value.strip()
    return value.startswith("sk-") and len(value) > 20


def call_openai_expert(question: str, history: list[dict], context_text: str) -> tuple[str | None, str | None]:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not _valid_openai_key(api_key):
        return None, "OPENAI_API_KEY belum valid atau belum dipasang."

    model = os.getenv("OPENAI_MODEL", "gpt-5.6-sol")
    endpoint = os.getenv("OPENAI_RESPONSES_URL", "https://api.openai.com/v1/responses")
    clean_history = []
    for item in history[-10:]:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = str(item.get("content", "")).strip()
        if role in {"user", "assistant"} and content:
            clean_history.append({"role": role, "content": content[:6000]})

    input_messages = [
        {"role": "developer", "content": EXPERT_SYSTEM_PROMPT},
        *clean_history,
        {
            "role": "user",
            "content": (
                "Gunakan konteks lokal berikut bila relevan. Jangan mengarang hasil eksperimen. "
                "Jika konteks tidak cukup, jelaskan asumsi yang diperlukan.\n\n"
                f"KONTEKS ORANGE-LEARN:\n{context_text[:18000]}\n\n"
                f"PERTANYAAN:\n{question}"
            ),
        },
    ]
    payload_obj = {
        "model": model,
        "input": input_messages,
        "max_output_tokens": int(os.getenv("OPENAI_MAX_OUTPUT_TOKENS", "2200")),
    }
    if os.getenv("OPENAI_WEB_SEARCH", "true").lower() == "true":
        payload_obj["tools"] = [{"type": "web_search"}]
    payload = json.dumps(payload_obj).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    try:
        timeout = max(8, int(os.getenv("OPENAI_TIMEOUT_SECONDS", "45")))
        attempts = max(1, int(os.getenv("OPENAI_RETRY_COUNT", "2")))
        last_error = "OpenAI request gagal."
        for attempt in range(attempts):
            try:
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    data = json.loads(response.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                try:
                    detail = json.loads(body).get("error", {}).get("message", body)
                except json.JSONDecodeError:
                    detail = body[:500]
                last_error = f"OpenAI HTTP {exc.code}: {detail}"
                if exc.code not in {408, 409, 429, 500, 502, 503, 504} or attempt == attempts - 1:
                    return None, last_error
                time.sleep(1.5 * (attempt + 1))
            except (urllib.error.URLError, TimeoutError) as exc:
                last_error = f"Koneksi OpenAI gagal: {exc}"
                if attempt == attempts - 1:
                    return None, last_error
                time.sleep(1.5 * (attempt + 1))
            except json.JSONDecodeError as exc:
                return None, f"Respons OpenAI tidak valid: {exc}"
        else:
            return None, last_error
    except Exception as exc:
        return None, f"Kesalahan AI: {exc}"

    if isinstance(data.get("output_text"), str) and data["output_text"].strip():
        return data["output_text"].strip()

    texts = []
    for item in data.get("output", []) or []:
        for content in item.get("content", []) or []:
            text_value = content.get("text")
            if isinstance(text_value, str) and text_value.strip():
                texts.append(text_value.strip())
    return "\n\n".join(texts).strip() or None, None


def fetch_rows(table: str, order_column: str = "urutan") -> list[dict[str, Any]]:
    response = (
        get_supabase()
        .table(table)
        .select("*")
        .order(order_column, desc=False)
        .execute()
    )
    return response.data or []


def find_row(table: str, row_id: int) -> dict[str, Any] | None:
    response = (
        get_supabase()
        .table(table)
        .select("*")
        .eq("id", row_id)
        .limit(1)
        .execute()
    )
    return response.data[0] if response.data else None


@app.route("/health")
def health():
    try:
        get_supabase().table("materi").select("id").limit(1).execute()
        return jsonify({"ok": True, "database": "supabase"})
    except Exception:
        return jsonify({"ok": False, "database": "supabase"}), 503


@app.route("/")
def home():
    jumlah_materi = len(get_supabase().table("materi").select("id").execute().data or [])
    widget_rows = get_supabase().table("widget").select("id").execute().data or []
    workflow_rows = get_supabase().table("workflow").select("id").execute().data or []
    return render_template(
        "index.html",
        jumlah_materi=jumlah_materi,
        jumlah_widget=len(widget_rows),
        jumlah_workflow=len(workflow_rows),
        jumlah_kuis=5,
        expert_ai=bool(os.getenv("OPENAI_API_KEY")),
    )


@app.route("/workflow/builder")
def workflow_builder():
    data = fetch_rows("widget")
    return render_template("workflow_builder.html", widget=data)


@app.route("/workflow")
def workflow():
    data = fetch_rows("workflow")
    return render_template("workflow.html", workflow=data)


@app.route("/widget")
def widget():
    search = request.args.get("search", "").strip().lower()
    kategori = request.args.get("kategori", "").strip()
    data = fetch_rows("widget")

    if search:
        data = [
            row
            for row in data
            if any(
                search in str(row.get(field) or "").lower()
                for field in ("nama", "kategori", "deskripsi", "fungsi")
            )
        ]

    if kategori:
        data = [row for row in data if row.get("kategori") == kategori]

    kategori_data = sorted({row.get("kategori") for row in fetch_rows("widget") if row.get("kategori")})

    return render_template(
        "widget.html",
        widget=data,
        kategori_data=[{"kategori": value} for value in kategori_data],
        search=request.args.get("search", "").strip(),
        kategori=kategori,
    )


@app.route("/widget/<int:id>")
def widget_detail(id):
    data = find_row("widget", id)
    if data is None:
        return "Widget tidak ditemukan", 404
    return render_template("widget_detail.html", widget=data)


@app.route("/materi")
def materi():
    search = request.args.get("search", "").strip()
    data = fetch_rows("materi")
    if search:
        needle = search.lower()
        data = [
            row
            for row in data
            if any(
                needle in str(row.get(field) or "").lower()
                for field in ("judul", "kategori", "deskripsi")
            )
        ]
    return render_template("materi.html", materi=data, search=search)


@app.route("/materi/<int:id>")
def materi_detail(id):
    data = find_row("materi", id)
    if data is None:
        return "Materi tidak ditemukan", 404
    return render_template("materi_detail.html", materi=data)


@app.route("/api/ai-status")
def ai_status():
    key = os.getenv("OPENAI_API_KEY", "")
    enabled = _valid_openai_key(key)
    return jsonify({
        "success": True,
        "expert_mode": enabled,
        "provider": "OpenAI Responses API" if enabled else "Local Knowledge Base",
        "model": os.getenv("OPENAI_MODEL", "gpt-5.6-sol") if enabled else "local-expert",
        "web_search": enabled and os.getenv("OPENAI_WEB_SEARCH", "true").lower() == "true",
        "knowledge_items": len(load_orange_knowledge()),
        "workflow_templates": len(load_workflow_templates()),
    })


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(silent=True) or {}
    question = str(data.get("message", "")).strip()
    history = data.get("history", [])
    if not isinstance(history, list):
        history = []
    if not question:
        return jsonify({"success": False, "answer": "Silakan tuliskan pertanyaan tentang Orange Data Mining."}), 400

    knowledge_result = search_orange_knowledge(question)
    template = detect_workflow_type(question)
    context_chunks = [
        f"Q: {item.get('question', '')}\nA: {item.get('answer', '')}"
        for item in knowledge_result["results"][:5]
    ]
    if template:
        context_chunks.append(
            f"Workflow template: {template.get('name')} | {template.get('description')} | "
            f"{' → '.join(template.get('widgets', []))}"
        )
    context_text = "\n\n".join(context_chunks) or "Tidak ada konteks lokal yang cocok."

    expert_answer, ai_error = call_openai_expert(question, history, context_text)
    if expert_answer:
        answer, mode = expert_answer, "expert"
    else:
        answer, mode = build_local_expert_answer(question, knowledge_result, template), "local"

    return jsonify({
        "success": True,
        "answer": answer,
        "found": knowledge_result["found"],
        "score": knowledge_result["score"],
        "mode": mode,
        "workflow": ({"name": template.get("name"), "widgets": template.get("widgets", [])} if template else None),
        "ai_error": ai_error if mode == "local" else None,
    })


@app.route("/latihan")
def latihan():
    return render_template("latihan.html")


@app.route("/kuis")
def kuis():
    return render_template("kuis.html")


@app.route("/ai-tutor")
def ai_tutor():
    return render_template("ai_tutor.html")


@app.route("/api/generate-workflow", methods=["POST"])
def generate_workflow():
    data = request.get_json(silent=True) or {}
    question = str(data.get("message", "")).strip()
    if not question:
        return jsonify({"success": False, "message": "Pertanyaan belum diisi."}), 400

    template = detect_workflow_type(question)
    if not template:
        return jsonify({
            "success": False,
            "message": (
                "Saya belum dapat menentukan jenis analisis. Coba jelaskan "
                "apakah Anda ingin melakukan klasifikasi, regresi, clustering, "
                "atau eksplorasi data."
            ),
        })

    return jsonify({
        "success": True,
        "type": template["id"],
        "name": template["name"],
        "description": template["description"],
        "widgets": template["widgets"],
    })


if __name__ == "__main__":
    app.run(debug=True)
