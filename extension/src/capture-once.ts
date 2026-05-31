import { captureOnce } from "./snapshot";

const status = document.getElementById("status")!;

void captureOnce()
  .then((result) => {
    status.textContent = `Saved session #${result.session_id} (${result.tab_count} tabs).`;
    status.className = "ok";
  })
  .catch((error: Error) => {
    status.textContent = error.message;
    status.className = "err";
  });
