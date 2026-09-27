# Google Docs & Google Sheets Export

Orange Learn can export AI answers to Google Docs and workflow datasets/results to Google Sheets.

## Required Google Cloud setup
1. Enable **Google Docs API** and **Google Sheets API** in the same Google Cloud project as the OAuth client.
2. Configure an OAuth consent screen.
3. Create an OAuth 2.0 Client ID for a **Web application**.
4. Add the exact authorized redirect URI:
   `https://orangelearn.vercel.app/api/google/oauth/callback`
5. Add these Vercel environment variables:
   - `GOOGLE_CLIENT_ID` (Config)
   - `GOOGLE_CLIENT_SECRET` (Secret)
   - `GOOGLE_OAUTH_REDIRECT_URI` (Config)
   - `FLASK_SECRET_KEY` (Secret)

The app uses Google OAuth to request permission for the Docs and Sheets APIs, then keeps the short-lived access token in browser memory for the current session. The application does not write a Google API key into the source code.

## In the app
- AI Tutor: each AI answer has **Google Docs** and **Google Sheets** export buttons.
- Workflow Builder: the toolbar has **Google Sheets** for the current dataset and **Google Docs** for a workflow report.

Google Docs creation uses `documents.create` then `documents.batchUpdate`, while Sheets creation and cell writing use the Sheets API.
