import os
import json
from frostpy import verify_signature_py

SECRETS_DIR = "keys"
LATEST_SIGNATURE_FILE = os.path.join(SECRETS_DIR, "latest_note_signature.txt")
PUBKEY_FILE = os.path.join(SECRETS_DIR, "public_key.txt")

def read_note_signature(note_content):
    if not os.path.exists(LATEST_SIGNATURE_FILE):
        print("❌ No signature file found.")
        return None
    with open(LATEST_SIGNATURE_FILE, "r") as f:
        data = json.load(f)
        if data["note_content"] == note_content:
            return data["signature"]
    print("❌ No matching signature for provided message.")
    return None

def read_public_key():
    if not os.path.exists(PUBKEY_FILE):
        print("❌ Public key file not found.")
        return None
    with open(PUBKEY_FILE, "r") as f:
        return f.read().strip()

def verify_note_signature(note_content, signature_b64, public_key_b64):
    try:
        return verify_signature_py(note_content, signature_b64, public_key_b64)
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return None