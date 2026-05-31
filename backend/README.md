# Workspace Memory — Backend

Python API backed by SQLite. Managed with [uv](https://docs.astral.sh/uv/).

## Setup

```bash
cd backend
uv sync
```

## Run API server

```bash
uv run python run.py
```

Or:

```bash
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API docs: http://127.0.0.1:8000/docs

## One-shot capture (from repo root)

```bash
export TAB_MANAGER_EXTENSION_ID=your_extension_id
uv run --project backend python ../scripts/capture_once.py
```

## Inspect SQLite

```bash
sqlite3 data/workspace.db "SELECT id, created_at FROM sessions ORDER BY id DESC LIMIT 5;"
```
