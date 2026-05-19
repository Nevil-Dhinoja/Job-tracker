import time
import os
import shutil
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ── Config ────────────────────────────────────────────────────────────────────
WATCH_DIR     = r"G:\Achivements and Projects\Job-tracker\watch"
PROCESSED_DIR = r"G:\Achivements and Projects\Job-tracker\watch\processed"
N8N_WEBHOOK   = "http://localhost:5678/webhook/job-tracker"   # production URL (workflow must be ACTIVE)

os.makedirs(PROCESSED_DIR, exist_ok=True)


# ── File parser ───────────────────────────────────────────────────────────────
def parse_job_file(filepath: str) -> dict:
    data = {}
    with open(filepath, "r", encoding="utf-8-sig") as f:  # utf-8-sig strips BOM
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key, _, value = line.partition(":")
                key   = key.strip().lower()
                value = value.strip()
                if key and value:
                    data[key] = value
    return data


# ── Webhook sender ────────────────────────────────────────────────────────────
def send_to_n8n(data: dict, filename: str):
    if not data.get("url"):
        print(f"[SKIP] {filename} has no URL — skipping.")
        return False

    print(f"[SEND] Processing: {filename}")
    print(f"       → {data}")

    try:
        response = requests.post(N8N_WEBHOOK, json=data, timeout=60)
        if response.status_code == 200:
            print(f"[OK]   n8n accepted {filename}")
            return True
        else:
            print(f"[ERR]  n8n returned {response.status_code}: {response.text[:200]}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"[ERR]  Cannot reach n8n at {N8N_WEBHOOK} — is it running?")
        return False
    except Exception as e:
        print(f"[ERR]  {e}")
        return False


# ── File event handler ────────────────────────────────────────────────────────
class JobFileHandler(FileSystemEventHandler):

    def on_created(self, event):
        if event.is_directory:
            return

        filepath = event.src_path
        filename = os.path.basename(filepath)

        # Only process .txt files
        if not filename.endswith(".txt"):
            return

        # Small delay — wait for file to finish writing
        time.sleep(0.5)

        print(f"\n[NEW]  Detected: {filename}")

        data    = parse_job_file(filepath)
        success = send_to_n8n(data, filename)

        # Move to processed/ regardless of success
        dest = os.path.join(PROCESSED_DIR, filename)

        # Avoid overwrite — add timestamp if file already exists
        if os.path.exists(dest):
            ts   = time.strftime("%Y%m%d_%H%M%S")
            name, ext = os.path.splitext(filename)
            dest = os.path.join(PROCESSED_DIR, f"{name}_{ts}{ext}")

        shutil.move(filepath, dest)
        status = "done" if success else "failed"
        print(f"[MOVE] {filename} → processed/ ({status})\n")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  Job Tracker — File Watcher")
    print(f"  Watching: {WATCH_DIR}")
    print(f"  Webhook:  {N8N_WEBHOOK}")
    print("=" * 50)
    print("\nDrop a .txt file into the watch/ folder to start.\n")

    handler  = JobFileHandler()
    observer = Observer()
    observer.schedule(handler, WATCH_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[STOP] Watcher stopped.")

    observer.join()