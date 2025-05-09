import os
import json
import time
from datetime import datetime, time as dtime
from dotenv import load_dotenv
from cli import ensure_note_contents_file

# Load config from .env
load_dotenv()
SIGN_START = os.getenv("SIGN_START")
SIGN_END = os.getenv("SIGN_END")
SHARE_ID = os.getenv("SHARE_ID")

SECRETS_DIR = "keys"
MESSAGES_FILE = "note_contents.txt"
LOG_FILE = "signed_notes.log"

def is_signing_allowed():
    now = datetime.now().time()
    start_hour, start_minute = map(int, SIGN_START.split(":"))
    end_hour, end_minute = map(int, SIGN_END.split(":"))
    return dtime(start_hour, start_minute) <= now <= dtime(end_hour, end_minute)

def load_note_contents():
    if not os.path.exists(MESSAGES_FILE):
        return []
    with open(MESSAGES_FILE, "r") as f:
        return [json.loads(line) for line in f if line.strip()]

def save_note_contents(note_contents):
    with open(MESSAGES_FILE, "w") as f:
        for note in note_contents:
            f.write(json.dumps(note) + "\n")

def log_action(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = "[{}] {}".format(timestamp, message)
    with open(LOG_FILE, "a") as log:
        log.write(entry + "\n")
    print(entry)

def sign_pending_notes():
    if not SHARE_ID:
        log_action("❌ SHARE_ID is not defined in .env")
        return

    share_path = os.path.join(SECRETS_DIR, SHARE_ID, "secret_share.txt")
    if not os.path.exists(share_path):
        log_action("❌ Share file not found at {}".format(share_path))
        return

    if not is_signing_allowed():
        log_action("⏳ Outside signing window. Ignoring request.")
        return

    ensure_note_contents_file()
    note_contents = load_note_contents()
    modified = False

    for note in note_contents:
        if note.get("status") != "pending":
            continue
        if any(str(sig.get("share")) == str(SHARE_ID) for sig in note.get("note_signatures", [])):
            log_action("🔁 Already signed note ID {} with share {}".format(note['id'], SHARE_ID))
            continue

        note["note_signatures"].append({
            "share": SHARE_ID,
            "signed_at": int(time.time())
        })
        log_action("✅ Signed note ID {} using share {}".format(note['id'], SHARE_ID))
        modified = True

    if modified:
        save_note_contents(note_contents)
    else:
        log_action("📭 No new notes to sign at this time.")

if __name__ == "__main__":
    try:
        log_action("🚦 Auto signer started for SHARE_ID={}".format(SHARE_ID))
        sign_pending_notes()
    except Exception as e:
        log_action("❌ UNEXPECTED ERROR: {}".format(e))