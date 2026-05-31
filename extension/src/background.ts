import { captureOnce } from "./snapshot";

function handleSnapshot(
  sendResponse: (response: { ok: boolean; result?: unknown; error?: string }) => void
): boolean {
  void captureOnce()
    .then((result) => sendResponse({ ok: true, result }))
    .catch((error: Error) => sendResponse({ ok: false, error: error.message }));
  return true;
}

chrome.runtime.onInstalled.addListener(() => {
  console.info(
    `[Workspace Memory] Extension ready (ID: ${chrome.runtime.id}). ` +
      "Capture is manual only — run scripts/capture_once.py or use the popup."
  );
});

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.type === "SNAPSHOT_NOW") {
    return handleSnapshot(sendResponse);
  }

  if (message.type === "RESTORE_LATEST") {
    void fetch("http://127.0.0.1:8000/restore/latest")
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

chrome.runtime.onMessageExternal.addListener((message, _sender, sendResponse) => {
  if (message.type === "SNAPSHOT_NOW") {
    return handleSnapshot(sendResponse);
  }
  return false;
});

chrome.commands.onCommand.addListener((command) => {
  if (command === "capture-once") {
    void captureOnce().catch((error) => {
      console.error("[Workspace Memory] Capture failed:", error);
    });
  }
});
