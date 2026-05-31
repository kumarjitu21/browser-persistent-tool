# Workspace Memory

Local browser workspace persistence: automatic tab snapshots, searchable session history, and one-click recovery.

## Architecture

```text
Chrome Extension (TypeScript)
    ↓  POST /snapshot every 60s
Local FastAPI Service (Python)
    ↓
SQLite (backend/data/workspace.db)
    ↓
Restore / History APIs
```

## Quick Start

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

API docs: http://127.0.0.1:8000/docs

SQLite (`backend/data/workspace.db` by default; set `TAB_MANAGER_USE_HOME=1` for `~/.tab-manager/workspace.db`).

### 2. Extension

```bash
cd extension
npm install
npm run build
```

Load in Chrome:

1. Open `chrome://extensions`
2. Enable **Developer mode**
3. Click **Load unpacked**
4. Select `extension/dist`

### 3. Verify

1. Open several tabs
2. Wait 60 seconds (or click **Snapshot Now** in the popup)
3. Check backend logs or `GET /sessions`
4. Click **Restore Latest Session** to reopen tabs

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/snapshot` | Store a tab snapshot |
| GET | `/sessions` | List recent sessions |
| GET | `/sessions/{id}` | Get session detail |
| GET | `/restore/latest` | Latest session for recovery |
| GET | `/restore/{id}` | Specific session for recovery |

## Snapshot Payload

```json
{
  "browser": "chrome",
  "tabs": [
    {
      "window_id": 123,
      "url": "https://example.com",
      "title": "Example",
      "active": true,
      "pinned": false,
      "index": 0
    }
  ]
}
```

## What's Next

- Named workspaces ("Production Incident Investigation")
- Deduplication (skip identical consecutive snapshots)
- Timeline UI
- Firefox support
- FTS5 search over titles/URLs
- Semantic search with local embeddings

## Project Structure

```text
backend/
  app/
    main.py       # FastAPI routes
    models.py     # SQLAlchemy models
    schemas.py    # Pydantic schemas
    database.py   # SQLite setup
extension/
  src/
    background.ts # Snapshot scheduler
    popup.ts      # Manual snapshot / restore
```
