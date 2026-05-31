# Workspace Memory

Local browser workspace persistence: automatic tab snapshots, searchable session history, and one-click recovery.

## Architecture

```text
Chrome Extension (TypeScript)
    ↓  POST /snapshot on demand (one-shot)
Local FastAPI Service (Python)
    ↓
SQLite (backend/data/workspace.db)
    ↓
Restore / History APIs
```

## Quick Start

### 1. Backend (uv)

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if needed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then:

```bash
cd backend
uv sync
uv run python run.py
```

From the repo root without `cd`:

```bash
uv run --project backend python run.py
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

### 3. One-shot capture (no background sync)

Copy your extension ID from `chrome://extensions`, then:

```bash
export TAB_MANAGER_EXTENSION_ID=your_extension_id_here
uv run --project backend python scripts/capture_once.py
```

Or save it once in `.env`:

```env
TAB_MANAGER_EXTENSION_ID=your_extension_id_here
```

Other ways to capture once:

| Method | How |
|--------|-----|
| **CLI** | `uv run --project backend python scripts/capture_once.py` |
| **Popup** | Click extension icon → **Capture Once** |
| **Keyboard** | `Cmd+Shift+Y` (Mac) / `Ctrl+Shift+Y` |
| **Extension page** | `uv run --project backend python scripts/capture_once.py --page` |

### 4. Verify

1. Open several normal tabs (http/https)
2. Run `uv run --project backend python scripts/capture_once.py`
3. Check `GET /sessions` or the popup status
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
  pyproject.toml  # uv dependencies
  uv.lock
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
