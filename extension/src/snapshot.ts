import type { SnapshotPayload, SnapshotResponse } from "./types";

export const API_BASE = "http://127.0.0.1:8000";

export async function captureSnapshot(): Promise<SnapshotPayload> {
  const tabs = await chrome.tabs.query({});

  return {
    browser: "chrome",
    tabs: tabs
      .filter((tab) => tab.url && !tab.url.startsWith("chrome://"))
      .map((tab) => ({
        window_id: tab.windowId ?? 0,
        url: tab.url ?? "",
        title: tab.title ?? "",
        active: tab.active ?? false,
        pinned: tab.pinned ?? false,
        index: tab.index ?? 0,
      })),
  };
}

export async function captureOnce(): Promise<SnapshotResponse> {
  const payload = await captureSnapshot();
  if (payload.tabs.length === 0) {
    throw new Error("No capturable tabs found (chrome:// pages are skipped)");
  }

  const response = await fetch(`${API_BASE}/snapshot`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Snapshot failed (${response.status}): ${detail}`);
  }

  const result = (await response.json()) as SnapshotResponse;
  await chrome.storage.local.set({
    lastSnapshotAt: new Date().toISOString(),
    lastSessionId: result.session_id,
    lastTabCount: result.tab_count,
  });

  console.info(
    `[Workspace Memory] Saved session ${result.session_id} (${result.tab_count} tabs)`
  );
  return result;
}
