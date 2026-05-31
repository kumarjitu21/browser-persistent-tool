const meta = document.getElementById("meta")!;
const statusEl = document.getElementById("status")!;
const snapshotBtn = document.getElementById("snapshot") as HTMLButtonElement;
const restoreBtn = document.getElementById("restore") as HTMLButtonElement;

function setStatus(message: string, isError = false): void {
  statusEl.textContent = message;
  statusEl.style.color = isError ? "#b91c1c" : "#166534";
}

async function loadMeta(): Promise<void> {
  const stored = await chrome.storage.local.get([
    "lastSnapshotAt",
    "lastSessionId",
    "lastTabCount",
  ]);

  if (!stored.lastSnapshotAt) {
    meta.textContent = "No snapshots yet. Backend must be running on localhost:8000.";
    return;
  }

  meta.innerHTML = `
    Last snapshot: ${new Date(stored.lastSnapshotAt).toLocaleString()}<br />
    Session #${stored.lastSessionId} · ${stored.lastTabCount} tabs
  `;
}

snapshotBtn.addEventListener("click", () => {
  setStatus("Capturing snapshot…");
  chrome.runtime.sendMessage({ type: "SNAPSHOT_NOW" }, (response) => {
    if (response?.ok) {
      setStatus(`Saved session #${response.result.session_id}`);
      void loadMeta();
    } else {
      setStatus(response?.error ?? "Snapshot failed", true);
    }
  });
});

restoreBtn.addEventListener("click", () => {
  setStatus("Restoring latest session…");
  chrome.runtime.sendMessage({ type: "RESTORE_LATEST" }, (response) => {
    if (response?.ok) {
      setStatus(`Opened ${response.session.tabs.length} tabs from session #${response.session.id}`);
    } else {
      setStatus(response?.error ?? "Restore failed", true);
    }
  });
});

void loadMeta();
