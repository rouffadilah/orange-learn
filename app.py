from flask import Flask, render_template, request, jsonify, redirect, session
import json
import os
import re
import urllib.error
import urllib.request
import urllib.parse
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__, static_folder=None)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'orange-learn-local-dev-secret')


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


def load_orange_features():
    return load_json("orange_features.json")


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


EXPERT_SYSTEM_PROMPT = r"""
Anda adalah orange-learn AI, tutor ahli Orange Data Mining untuk pembelajaran tingkat sekolah menengah hingga perguruan tinggi awal.
Fokus utama: Orange Data Mining, widget, data preparation, exploratory data analysis, klasifikasi, regresi, clustering, evaluasi model, visualisasi, workflow, dan praktik machine learning.

Aturan jawaban:
1. Jawab dalam Bahasa Indonesia yang jelas, terstruktur, dan bertahap.
2. Fokus pada jawaban yang praktis: apa yang dilakukan, kapan dipakai, mengapa, input-output, dan langkah di Orange.
3. Untuk workflow, tulis urutan widget dengan panah Unicode sederhana seperti: File → Data Table → Test & Score.
4. Untuk evaluasi model, jelaskan metrik yang relevan dan cara membaca hasilnya.
5. Untuk debugging, cek data, target/class, tipe kolom, preprocessing, leakage, dan koneksi widget.
6. Jangan mengarang hasil eksperimen, angka akurasi, atau konfigurasi dataset yang belum diberikan.
7. Bedakan fakta dan asumsi. Bila informasi tidak tersedia, katakan apa yang masih perlu diverifikasi.
8. Gunakan Markdown yang bersih dan konsisten. Heading singkat, bullet secukupnya, dan paragraf pendek.
9. JANGAN gunakan LaTeX, MathJax, delimiters seperti $, $$, \(, \), atau perintah seperti \text{}, \rightarrow, \right. Gunakan teks biasa dan simbol Unicode.
10. JANGAN menulis garis pemisah '---', kode escape mentah, atau karakter format yang tidak perlu.
11. Hindari pembukaan yang bertele-tele. Mulai langsung dari jawaban inti.
12. Bila pengguna pemula, mulai dari konsep dasar lalu naikkan ke teknis.
13. Akhiri dengan satu langkah berikutnya yang konkret dan singkat.
""".strip()


def clean_ai_output(text: str) -> str:
    """Normalize common Markdown/LaTeX artifacts before sending text to the browser."""
    value = str(text or "").replace("\r\n", "\n").replace("\r", "\n")
    replacements = {
        "\\rightarrow": "→",
        "\\to": "→",
        "\\Rightarrow": "⇒",
        "\\leftarrow": "←",
        "\\leftrightarrow": "↔",
        "\\geq": "≥",
        "\\leq": "≤",
        "\\times": "×",
        "\\cdot": "·",
        "\\pm": "±",
        "\\text{": "",
        "\\mathrm{": "",
        "\\mathbf{": "",
    }
    for src, dst in replacements.items():
        value = value.replace(src, dst)
    # Remove common TeX wrappers/brackets.
    value = re.sub(r"\$\$(.*?)\$\$", r"\1", value, flags=re.S)
    value = re.sub(r"\$(.*?)\$", r"\1", value, flags=re.S)
    value = value.replace("\\(", "").replace("\\)", "")
    value = value.replace("\\[", "").replace("\\]", "")
    value = value.replace("\\right", "").replace("\\left", "")
    # Collapse noisy separators/escape-only lines.
    value = re.sub(r"^\s*---\s*$", "", value, flags=re.M)
    value = re.sub(r"^[ \t]*[0-9]+[.)][ \t]*$", "", value, flags=re.M)
    value = re.sub(r"\n{3,}", "\n\n", value)
    # Balance common braces left by \text{...} style output.
    value = value.replace("{", "").replace("}", "")
    return value.strip()


def clean_display_text(text: str) -> str:
    """Clean Markdown/LaTeX artifacts for browser-facing educational content."""
    value = str(text or "").replace("\r\n", "\n").replace("\r", "\n")
    # TeX-style arrows and relations.
    replacements = {
        r"\longrightarrow": "→", r"\rightarrow": "→", r"\to": "→",
        r"\Rightarrow": "⇒", r"\Longrightarrow": "⇒", r"\leftarrow": "←",
        r"\leftrightarrow": "↔", r"\geq": "≥", r"\leq": "≤",
        r"\times": "×", r"\cdot": "·", r"\pm": "±", r"\neq": "≠",
    }
    for src, dst in replacements.items():
        value = value.replace(src, dst)
    # Remove common wrappers repeatedly, including simple nested braces.
    for _ in range(4):
        value = re.sub(r"\\(?:text|mathrm|mathbf|operatorname|textrm|textit)\s*\{([^{}]*)\}", r"\1", value)
    value = re.sub(r"\$\$(.*?)\$\$", r"\1", value, flags=re.S)
    value = re.sub(r"\$(.*?)\$", r"\1", value, flags=re.S)
    value = re.sub(r"\\\((.*?)\\\)", r"\1", value, flags=re.S)
    value = re.sub(r"\\\[(.*?)\\\]", r"\1", value, flags=re.S)
    value = value.replace(r"\left", "").replace(r"\right", "")
    value = value.replace(r"\{", "{").replace(r"\}", "}")
    # Markdown headings -> plain headings; bullets -> readable bullets.
    cleaned_lines = []
    for raw in value.split("\n"):
        line = raw.strip()
        if not line:
            cleaned_lines.append("")
            continue
        if re.fullmatch(r"(?:---+|___+|===+)", line):
            continue
        if re.fullmatch(r"\*+", line):
            continue
        line = re.sub(r"^#{1,6}\s+", "", line)
        line = re.sub(r"^[*•]\s+", "• ", line)
        # Remove isolated ordered-list markers that were generated on their own line.
        if re.fullmatch(r"\d+[.)]", line):
            continue
        # Markdown link -> label.
        line = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", line)
        # Remove emphasis/code markers while retaining the actual text.
        line = line.replace("**", "").replace("__", "")
        line = re.sub(r"(^|\s)\*([^*]+)\*(?=\s|$)", r"\1\2", line)
        line = re.sub(r"`([^`]+)`", r"\1", line)
        line = re.sub(r"\\\\+", " ", line)
        line = re.sub(r"[ \t]{2,}", " ", line)
        line = line.replace("{", "").replace("}", "")
        cleaned_lines.append(line)
    value = "\n".join(cleaned_lines)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


@app.template_filter("clean")
def clean_template_text(value):
    return clean_display_text(value)


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


def _valid_gemini_key(value: str | None) -> bool:
    if not value:
        return False
    value = value.strip()
    return len(value) >= 20 and "YOUR_" not in value.upper()



GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
]


def google_oauth_config() -> dict[str, str | bool]:
    client_id = (os.getenv("GOOGLE_CLIENT_ID") or "").strip()
    client_secret = (os.getenv("GOOGLE_CLIENT_SECRET") or "").strip()
    redirect_uri = (os.getenv("GOOGLE_OAUTH_REDIRECT_URI") or "").strip()
    if not redirect_uri:
        redirect_uri = request.url_root.rstrip("/") + "/api/google/oauth/callback"
    ready = bool(client_id and client_secret and os.getenv("FLASK_SECRET_KEY"))
    return {
        "enabled": ready,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
    }


def google_http_json(url: str, *, method: str = "GET", payload: dict | None = None,
                     access_token: str | None = None, timeout: int = 12) -> dict:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def google_form_post(url: str, payload: dict, *, timeout: int = 12) -> dict:
    body = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def google_columns(n: int) -> str:
    out = ""
    while n:
        n, rem = divmod(n - 1, 26)
        out = chr(65 + rem) + out
    return out or "A"


def _gemini_contents(history: list[dict], question: str) -> list[dict]:
    """Convert the frontend chat history into Gemini generateContent turns."""
    contents = []
    last_user = ""
    for item in history[-10:]:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = str(item.get("content", "")).strip()
        if not content or role not in {"user", "assistant", "model"}:
            continue
        gemini_role = "model" if role in {"assistant", "model"} else "user"
        # The frontend can include the current user message in history. Avoid duplicating it.
        if gemini_role == "user" and content == question.strip():
            last_user = content
            continue
        contents.append({"role": gemini_role, "parts": [{"text": content[:8000]}]})

    # Always end with the actual current user question.
    contents.append({
        "role": "user",
        "parts": [{"text": question.strip()[:12000]}],
    })
    return contents


def call_gemini_expert(question: str, history: list[dict], context_text: str) -> tuple[str | None, str | None]:
    """Fast, resilient Gemini call with model failover and no long retry waits."""
    api_key = (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()
    if not _valid_gemini_key(api_key):
        return None, "GEMINI_API_KEY belum valid atau belum dipasang di Vercel."

    primary_model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()
    fallback_raw = os.getenv(
        "GEMINI_FALLBACK_MODELS",
        os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.7-flash,gemini-3.8-flash"),
    )
    fallback_models = [m.strip() for m in fallback_raw.split(",") if m.strip()]
    models_to_try = []
    for model in [primary_model, *fallback_models]:
        if model and model not in models_to_try:
            models_to_try.append(model)
        if len(models_to_try) >= 2:
            break

    # Keep interactive chat fast. The server falls back to Local AI rather than
    # holding the browser for a long sequence of retries.
    timeout = min(6, max(4, int(os.getenv("GEMINI_TIMEOUT_SECONDS", "5"))))
    max_output_tokens = min(2048, max(512, int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "1800"))))
    temperature = float(os.getenv("GEMINI_TEMPERATURE", "0.2"))
    temperature = min(1.0, max(0.0, temperature))

    system_instruction = (
        EXPERT_SYSTEM_PROMPT
        + "\n\nKonteks Orange Learn yang relevan:\n"
        + context_text[:12000]
        + "\n\nKamu adalah tutor ahli, bukan sekadar generator jawaban. "
          "Saat menganalisis workflow, jelaskan struktur data, tipe kolom, target/class, "
          "hubungan input-output widget, potensi data leakage, validasi, dan cara membaca hasil. "
          "Prioritaskan jawaban yang langsung bisa dipraktikkan di Orange Data Mining."
    )
    generation_config = {
        "maxOutputTokens": max_output_tokens,
        "temperature": temperature,
    }

    payload_obj = {
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        "contents": _gemini_contents(history, question),
        "generationConfig": generation_config,
    }

    def request_model(model: str):
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        payload = json.dumps(payload_obj).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=payload,
            headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    last_error = "Gemini sedang tidak tersedia."
    for index, model in enumerate(models_to_try):
        try:
            data = request_model(model)
            candidates = data.get("candidates") or []
            if not candidates:
                feedback = data.get("promptFeedback") or {}
                reason = feedback.get("blockReason") or "tidak ada kandidat respons"
                return None, f"Gemini tidak mengembalikan jawaban ({reason})."

            parts = ((candidates[0].get("content") or {}).get("parts") or [])
            texts = [
                str(part.get("text", "")).strip()
                for part in parts
                if str(part.get("text", "")).strip()
            ]
            answer = clean_ai_output("\n\n".join(texts))
            if not answer:
                finish_reason = candidates[0].get("finishReason", "UNKNOWN")
                return None, f"Gemini tidak menghasilkan teks ({finish_reason})."
            return answer, None
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(body)
                err = parsed.get("error", {}) if isinstance(parsed, dict) else {}
                detail = err.get("message", body)
            except json.JSONDecodeError:
                detail = body[:500]
            last_error = f"Gemini HTTP {exc.code}: {detail}"

            # 400/404 can be model/config specific: move immediately to another model.
            # 401/403/402 indicate configuration/account issues: don't waste latency retrying.
            # 429/5xx are transient: fail over immediately; avoid long browser waits.
            if exc.code in {400, 404, 408, 409, 429, 500, 502, 503, 504} and index + 1 < len(models_to_try):
                continue
            return None, last_error
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = f"Koneksi Gemini gagal: {exc}"
            if index + 1 < len(models_to_try):
                continue
            return None, last_error
        except json.JSONDecodeError as exc:
            return None, f"Respons Gemini tidak valid: {exc}"
        except Exception as exc:
            return None, f"Kesalahan Gemini: {exc}"

    return None, last_error

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
        expert_ai=_valid_gemini_key(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")),
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


@app.route("/fitur")
def fitur():
    search = request.args.get("search", "").strip()
    kategori = request.args.get("kategori", "").strip()
    data = load_orange_features()
    if search:
        needle = search.lower()
        data = [row for row in data if any(needle in str(row.get(field) or "").lower() for field in ("name", "category", "summary", "purpose"))]
    if kategori:
        data = [row for row in data if row.get("category") == kategori]
    categories = sorted({row.get("category") for row in load_orange_features() if row.get("category")})
    return render_template("fitur.html", features=data, categories=categories, search=search, kategori=kategori)


@app.route("/fitur/<slug>")
def fitur_detail(slug):
    feature = next((row for row in load_orange_features() if row.get("slug") == slug), None)
    if feature is None:
        return "Fitur tidak ditemukan", 404
    return render_template("fitur_detail.html", feature=feature)


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
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
    enabled = _valid_gemini_key(key)
    return jsonify({
        "success": True,
        "expert_mode": enabled,
        "provider": "Google Gemini API" if enabled else "Local Knowledge Base",
        "configured": enabled,
        "model": os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite") if enabled else "local-expert",
        "thinking_level": os.getenv("GEMINI_THINKING_LEVEL", "high") if enabled else None,
        "web_search": False,
        "knowledge_items": len(load_orange_knowledge()),
        "workflow_templates": len(load_workflow_templates()),
    })



@app.route("/api/google/config")
def google_config_route():
    cfg = google_oauth_config()
    return jsonify({"enabled": cfg["enabled"], "client_id": cfg["client_id"], "redirect_uri": cfg["redirect_uri"]})


@app.route("/api/google/oauth/start")
def google_oauth_start():
    cfg = google_oauth_config()
    if not cfg["enabled"]:
        return jsonify({"success": False, "message": "Integrasi Google belum dikonfigurasi di server."}), 503
    state = os.urandom(24).hex()
    session["google_oauth_state"] = state
    params = {
        "client_id": cfg["client_id"],
        "redirect_uri": cfg["redirect_uri"],
        "response_type": "code",
        "scope": " ".join(GOOGLE_SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    return redirect("https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params))


@app.route("/api/google/oauth/callback")
def google_oauth_callback():
    cfg = google_oauth_config()
    if not cfg["enabled"]:
        return "<h3>Integrasi Google belum dikonfigurasi.</h3>", 503
    state = request.args.get("state", "")
    expected = session.pop("google_oauth_state", "")
    if not state or state != expected:
        return "<h3>Autorisasi Google tidak valid. Silakan coba lagi.</h3>", 400
    code = request.args.get("code", "")
    if not code:
        return "<h3>Autorisasi Google dibatalkan atau gagal.</h3>", 400
    try:
        token = google_form_post("https://oauth2.googleapis.com/token", {
            "code": code,
            "client_id": cfg["client_id"],
            "client_secret": cfg["client_secret"],
            "redirect_uri": cfg["redirect_uri"],
            "grant_type": "authorization_code",
        })
        access_token = token.get("access_token")
        if not access_token:
            raise RuntimeError(token.get("error_description") or token.get("error") or "Token Google tidak tersedia")
        token_json = json.dumps(access_token)
        origin_json = json.dumps(request.url_root.rstrip("/"))
        return f"""<!doctype html><html><body><script>
const accessToken = {token_json};
const targetOrigin = {origin_json};
if (window.opener) window.opener.postMessage({{type:'orange-learn-google-auth',accessToken}}, targetOrigin);
window.close();
</script><p>Autorisasi Google berhasil. Jendela ini bisa ditutup.</p></body></html>"""
    except Exception as exc:
        return f"<h3>Autorisasi Google gagal</h3><p>{escape_html_server(str(exc)[:400])}</p>", 502


def escape_html_server(value: str) -> str:
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


@app.route("/api/export/google", methods=["POST"])
def export_google():
    auth = request.headers.get("Authorization", "")
    if not auth.lower().startswith("bearer "):
        return jsonify({"success": False, "message": "Otorisasi Google belum tersedia."}), 401
    access_token = auth.split(" ", 1)[1].strip()
    if not access_token:
        return jsonify({"success": False, "message": "Token Google kosong."}), 401

    data = request.get_json(silent=True) or {}
    kind = str(data.get("kind", "sheets")).lower()
    title = str(data.get("title", "orange-learn export")).strip()[:120] or "orange-learn export"
    try:
        if kind == "docs":
            content = clean_display_text(str(data.get("content", "")))
            created = google_http_json(
                "https://docs.googleapis.com/v1/documents",
                method="POST", payload={"title": title}, access_token=access_token,
            )
            document_id = created.get("documentId")
            if not document_id:
                raise RuntimeError("Google Docs tidak mengembalikan documentId.")
            text_body = (content or "orange-learn") + "\n"
            google_http_json(
                f"https://docs.googleapis.com/v1/documents/{document_id}:batchUpdate",
                method="POST",
                payload={"requests": [{"insertText": {"location": {"index": 1}, "text": text_body}}]},
                access_token=access_token,
            )
            return jsonify({"success": True, "kind": "docs", "url": f"https://docs.google.com/document/d/{document_id}/edit", "title": title})

        headers = data.get("headers") or []
        rows = data.get("rows") or []
        if not headers and data.get("content") is not None:
            lines = clean_display_text(str(data.get("content", ""))).splitlines()
            headers = ["Bagian", "Isi"]
            rows = [[str(i + 1), line] for i, line in enumerate(lines) if line.strip()]
        if not headers:
            headers = ["orange-learn"]
        sheet = google_http_json(
            "https://sheets.googleapis.com/v4/spreadsheets",
            method="POST", payload={"properties": {"title": title}}, access_token=access_token,
        )
        spreadsheet_id = sheet.get("spreadsheetId")
        if not spreadsheet_id:
            raise RuntimeError("Google Sheets tidak mengembalikan spreadsheetId.")
        values = [headers] + rows
        end_col = google_columns(max(len(headers), 1))
        end_row = max(len(values), 1)
        range_a1 = f"Sheet1!A1:{end_col}{end_row}"
        google_http_json(
            f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{urllib.parse.quote(range_a1, safe='!')}",
            method="PUT",
            payload={"range": range_a1, "majorDimension": "ROWS", "values": values, "valueInputOption": "USER_ENTERED"},
            access_token=access_token,
        )
        # Freeze and emphasize the header row.
        first_sheet_id = ((sheet.get("sheets") or [{}])[0].get("properties") or {}).get("sheetId", 0)
        google_http_json(
            f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}:batchUpdate",
            method="POST",
            payload={"requests": [
                {"updateSheetProperties": {"properties": {"sheetId": first_sheet_id, "gridProperties": {"frozenRowCount": 1}}, "fields": "gridProperties.frozenRowCount"}},
                {"repeatCell": {"range": {"sheetId": first_sheet_id, "startRowIndex": 0, "endRowIndex": 1}, "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}}, "fields": "userEnteredFormat.textFormat.bold"}},
            ]},
            access_token=access_token,
        )
        return jsonify({"success": True, "kind": "sheets", "url": sheet.get("spreadsheetUrl") or f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit", "title": title})
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body); msg = parsed.get("error", {}).get("message") or body
        except Exception:
            msg = body
        return jsonify({"success": False, "message": f"Google API HTTP {exc.code}: {msg[:500]}"}), 502
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)[:500]}), 502


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
        for item in knowledge_result["results"][:8]
    ]
    if template:
        context_chunks.append(
            f"Workflow template: {template.get('name')} | {template.get('description')} | "
            f"{' → '.join(template.get('widgets', []))}"
        )
    feature_matches = load_orange_features()
    q_tokens = tokenise(question)
    ranked_features = []
    for feature in feature_matches:
        ft = tokenise(f"{feature.get('name','')} {feature.get('category','')} {feature.get('summary','')} {feature.get('purpose','')} {' '.join(feature.get('flow', []))}")
        score = len(q_tokens.intersection(ft))
        if score:
            ranked_features.append((score, feature))
    ranked_features.sort(key=lambda pair: pair[0], reverse=True)
    for _, feature in ranked_features[:3]:
        context_chunks.append(
            f"Feature guide: {feature.get('name')} | {feature.get('category')} | {feature.get('purpose')} | "
            f"Input: {feature.get('input')} | Output: {feature.get('output')} | "
            f"Workflow: {' → '.join(feature.get('flow', []))}"
        )
    context_text = "\n\n".join(context_chunks) or "Tidak ada konteks lokal yang cocok."

    try:
        expert_answer, ai_error = call_gemini_expert(question, history, context_text)
        if expert_answer:
            answer, mode = expert_answer, "expert"
        else:
            answer, mode = clean_ai_output(build_local_expert_answer(question, knowledge_result, template)), "local"

        return jsonify({
            "success": True,
            "answer": answer,
            "found": knowledge_result["found"],
            "score": knowledge_result["score"],
            "mode": mode,
            "workflow": ({"name": template.get("name"), "widgets": template.get("widgets", [])} if template else None),
            "ai_error": None,
            "degraded": mode == "local" and bool(ai_error),
            "degraded_reason": "provider_unavailable" if mode == "local" and ai_error else None,
        })
    except Exception as exc:
        return jsonify({
            "success": False,
            "answer": "Terjadi kesalahan pada layanan AI.",
            "error_code": "CHAT_BACKEND_ERROR",
            "message": str(exc)[:500],
        }), 500


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
