# Gemini AI Fix V4

- Fixed missing `urllib.parse` import.
- Uses `x-goog-api-key` request header instead of placing the API key in the URL.
- Limits Gemini timeout/retries to stay within Vercel function duration.
- `/api/chat` returns JSON even when a backend exception occurs.
- Frontend safely parses API responses and shows server error text instead of `Unexpected token ... is not valid JSON`.
- Default model: `gemini-3.8-flash`; fallback: `gemini-3.7-flash`.
