import os
import json
import time
import logging
import sys
from datetime import datetime, time as dt_time
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    handlers=[
        logging.FileHandler('signer.log'),
        logging.StreamHandler()
    ]
)


class AutoSigner:
    def __init__(self, env_file: str):
        load_dotenv(env_file)
        self.participant_id = os.getenv("SHARE_ID", "")
        self.threshold = int(os.getenv("THRESHOLD", "0"))
        self.sign_start, self.sign_end = self.parse_time_window(
            os.getenv("SIGN_START", "00:00"),
            os.getenv("SIGN_END", "00:00")
        )
        self.poll_interval = int(os.getenv("POLL_INTERVAL", "60"))
        self.share_path = os.path.join("keys", self.participant_id, "secret_share.txt")
        self.messages_file = "note_contents.txt"
        self.signatures_log = os.path.join("keys", "note_signatures.txt")

        if not self.participant_id:
            logging.error("❌ SHARE_ID is not defined in .env")
            sys.exit(1)

        logging.info(f"🚦 Auto signer started for SHARE_ID={self.participant_id}")

    def parse_time_window(self, start_str: str, end_str: str) -> Tuple[dt_time, dt_time]:
        try:
            start = dt_time(*map(int, start_str.split(':')))
            end = dt_time(*map(int, end_str.split(':')))
            return start, end
        except ValueError:
            return dt_time(0, 0), dt_time(23, 59)

    def is_active_window(self) -> bool:
        now = datetime.now().time()
        if self.sign_start < self.sign_end:
            return self.sign_start <= now <= self.sign_end
        return now >= self.sign_start or now <= self.sign_end

    def load_share(self) -> Optional[Dict]:
        try:
            with open(self.share_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"❌ Share file not found at {self.share_path}")
            return None

    def load_note_contents(self) -> List[Dict]:
        if not os.path.exists(self.messages_file):
            return []

        try:
            with open(self.messages_file, 'r', encoding='utf-8') as f:
                return [json.loads(line) for line in f if line.strip()]
        except (IOError, json.JSONDecodeError) as e:
            logging.error(f"❌ Failed to load notes: {e}")
            return []

    def save_note_contents(self, notes: List[Dict]) -> bool:
        try:
            with open(self.messages_file, 'w', encoding='utf-8') as f:
                for note in notes:
                    f.write(json.dumps(note) + "\n")
            return True
        except IOError as e:
            logging.error(f"❌ Failed to save notes: {e}")
            return False

    def check_all_notes_signed(self) -> bool:
        """Check if all pending notes have reached threshold"""
        notes = self.load_note_contents()
        if not notes:
            return False

        return all(
            len(note.get("note_signatures", [])) >= self.threshold
            for note in notes
            if note.get("status") == "pending"
        )

    def participate_in_signing(self) -> bool:
        if not self.is_active_window():
            logging.info("⏳ Outside signing window. Ignoring request.")
            return False

        share = self.load_share()
        if not share:
            return False

        note_contents = self.load_note_contents()
        modified = False

        for note in note_contents:
            if note.get("status") != "pending":
                continue

            if len(note.get("note_signatures", [])) >= self.threshold:
                continue

            if any(str(sig.get("share")) == self.participant_id
                   for sig in note.get("note_signatures", [])):
                logging.info(f"🔁 Already signed note ID {note['id']} with share {self.participant_id}")
                continue

            note["note_signatures"].append({
                "share": self.participant_id,
                "signed_at": int(time.time())
            })
            logging.info(f"✅ Signed note ID {note['id']} using share {self.participant_id}")

            if len(note["note_signatures"]) >= self.threshold:
                note["status"] = "signed"
                logging.info(f"✔️ Threshold reached for note ID {note['id']}")

            modified = True

        if modified:
            if self.save_note_contents(note_contents):
                # Check if all notes are now signed
                if self.check_all_notes_signed():
                    logging.info("All notes fully signed - shutting down")
                    return True
            return False

        logging.info("📭 No new notes to sign at this time.")
        return False

    def run(self):
        try:
            while True:
                should_exit = self.participate_in_signing()
                if should_exit:
                    break
                time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            logging.info("Shutting down...")
        except Exception as e:
            logging.error(f"❌ UNEXPECTED ERROR: {e}")
        finally:
            sys.exit(0)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True)
    args = parser.parse_args()
    AutoSigner(args.env).run()
