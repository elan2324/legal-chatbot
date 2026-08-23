# Legal Guidance AI Chatbot

A Flask-based legal-information chatbot. Stage 1A focuses on stabilizing the existing application, securing authentication, and separating the chat API from the UI. The current chatbot engine is still the legacy rule-based `bot.json` matcher; the LLM + RAG layer will be added in a later stage.

## Stage 1A setup

### 1. Create and activate a virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure the environment

Copy `.env.example` to `.env` and replace `SECRET_KEY` with a long random value.

### 4. Start the application

For a new clone with no existing database:

```powershell
python app.py
```

The application creates `signup.db` locally on first startup.

For an existing database created by the old version, run the one-time migration first:

```powershell
python migrate_db.py
python app.py
```

### 5. Open the application

Open `http://127.0.0.1:5000/login`.

## Security changes in Stage 1A

- Passwords are hashed with Werkzeug instead of stored as plaintext.
- Flask sessions protect the application and chat API.
- The hard-coded admin/admin login is removed.
- The Flask secret is loaded from `.env`.
- SQLite databases are ignored by Git.
- Chat messages are rendered with `textContent` rather than injected as HTML.
- The chat API uses `POST /api/chat` and validates input length.
- Debug mode is controlled by `FLASK_DEBUG` and defaults to off.

## Important

`signup.db` contains local user data and must never be committed to Git. The legacy `bot.json` matcher is intentionally retained for now only as a temporary chatbot engine; it will be replaced by the LLM + RAG pipeline in a later stage.
