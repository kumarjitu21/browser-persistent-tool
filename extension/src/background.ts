import type { SnapshotPayload, SnapshotResponse } from "./types";

const API_BASE = "http://127.0.0.1:8000";
const SNAPSHOT_ALARM = "workspace-snapshot";
const SNAPSHOT_INTERVAL_MINUTES = 1;

async function captureSnapshot(): Promise<SnapshotPayload> {
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

async function sendSnapshot(): Promise<SnapshotResponse | null> {
  const payload = await captureSnapshot();
  if (payload.tabs.length === 0) {
    console.warn("[Workspace Memory] No capturable tabs found");
    return null;
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

function scheduleSnapshots(): void {
  chrome.alarms.create(SNAPSHOT_ALARM, {
    periodInMinutes: SNAPSHOT_INTERVAL_MINUTES,
  });
}

chrome.runtime.onInstalled.addListener(() => {
  scheduleSnapshots();
  void sendSnapshot().catch((error) => {
    console.error("[Workspace Memory] Initial snapshot failed:", error);
  });
});

chrome.runtime.onStartup.addListener(() => {
  scheduleSnapshots();
});

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === SNAPSHOT_ALARM) {
    void sendSnapshot().catch((error) => {
      console.error("[Workspace Memory] Scheduled snapshot failed:", error);
    });
  }
});

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.type === "SNAPSHOT_NOW") {
    void sendSnapshot()
      .then((result) => sendResponse({ ok: true, result }))
      .catch((error: Error) => sendResponse({ ok: false, error: error.message }));
    return true;
  }

  if (message.type === "RESTORE_LATEST") {
    void fetch(`${API_BASE}/restore/latest`)
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(`Restore failed (${response.status})`);
        }
        const session = await response.json();
        const urls = session.tabs.map((tab: { url: string }) => tab.url);

        for (const url of urls) {
          await chrome.tabs.create({ url, active: false });
        }

        sendResponse({ ok: true, session });
      })
      .catch((error: Error) => sendResponse({ ok: false, error: error.message }));
    return true;
  }

  return false;
});
