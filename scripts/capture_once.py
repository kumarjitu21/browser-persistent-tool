#!/usr/bin/env python3
"""One-shot capture: opens a local page that tells the extension to snapshot all tabs."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import webbrowser
from pathlib import Path
from urllib.parse import urlencode

API_BASE = os.environ.get("TAB_MANAGER_API", "http://127.0.0.1:8000")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


def load_extension_id() -> str | None:
    ext_id = os.environ.get("TAB_MANAGER_EXTENSION_ID", "").strip()
    if ext_id:
        return ext_id

    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line.startswith("TAB_MANAGER_EXTENSION_ID="):
                value = line.split("=", 1)[1].strip().strip('"').strip("'")
                if value:
                    return value
    return None


def check_backend() -> None:
    try:
        import urllib.request

        with urllib.request.urlopen(f"{API_BASE}/health", timeout=3) as response:
            if response.status != 200:
                raise RuntimeError(f"Unexpected status: {response.status}")
    except Exception as exc:
        print(f"Backend not reachable at {API_BASE}: {exc}", file=sys.stderr)
        print("Start it first: cd backend && uv run python run.py")
        sys.exit(1)


def open_in_chrome(url: str) -> None:
    if sys.platform == "darwin":
        subprocess.run(["open", "-a", "Google Chrome", url], check=False)
        return
    webbrowser.open(url)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Capture all open Chrome tabs once (no background sync)."
    )
    parser.add_argument(
        "--extension-id",
        help="Chrome extension ID (from chrome://extensions). "
        "Or set TAB_MANAGER_EXTENSION_ID / .env",
    )
    parser.add_argument(
        "--page",
        action="store_true",
        help="Open extension capture-once page instead of localhost tool page",
    )
    args = parser.parse_args()

    ext_id = (args.extension_id or load_extension_id() or "").strip()
    if not ext_id:
        print("Missing extension ID.", file=sys.stderr)
        print()
        print("1. Open chrome://extensions and copy the ID under 'Workspace Memory'")
        print("2. Then either:")
        print("   export TAB_MANAGER_EXTENSION_ID=your_id_here")
        print("   echo 'TAB_MANAGER_EXTENSION_ID=your_id_here' >> .env")
        print("   python scripts/capture_once.py --extension-id your_id_here")
        sys.exit(1)

    check_backend()

    if args.page:
        url = f"chrome-extension://{ext_id}/src/capture-once.html"
        print(f"Opening extension page: {url}")
        open_in_chrome(url)
        return

    params = urlencode({"extension_id": ext_id})
    url = f"{API_BASE}/tools/capture-once?{params}"
    print(f"Opening capture tool: {url}")
    open_in_chrome(url)


if __name__ == "__main__":
    main()
