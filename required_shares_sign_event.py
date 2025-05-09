import os
import json
from frostpy import sign_message_py

SECRETS_DIR = "keys"
SIGNATURES_LOG = os.path.join(SECRETS_DIR, "note_signatures.txt")
LATEST_SIGNATURE_FILE = os.path.join(SECRETS_DIR, "latest_note_signature.txt")
PUBKEY_BUNDLE_PATH = os.path.join(SECRETS_DIR, "group_key_bundle.txt")

def read_group_pubkey_bundle():
    with open(PUBKEY_BUNDLE_PATH, "r") as f:
        return f.read().strip()

def required_shares_sign_event(note_content, share_paths, required_shares):
    shares_data = []
    for path in share_paths:
        with open(path, "r") as f:
            share = json.loads(f.read())
            shares_data.append(share)

    shares_json = json.dumps(shares_data)
    group_key_bundle = read_group_pubkey_bundle()

    try:
        signature_b64, _ = sign_message_py(note_content, shares_json, required_shares, group_key_bundle)
        return signature_b64
    except Exception as e:
        print(f"❌ Signing error: {e}")
        return None

def save_note_signature(signature_b64, note_content):
    record = {
        "note_content": note_content,
        "signature": signature_b64
    }
    try:
        os.makedirs(SECRETS_DIR, exist_ok=True)
        with open(SIGNATURES_LOG, "a") as f:
            f.write(json.dumps(record) + "\n")
        with open(LATEST_SIGNATURE_FILE, "w") as f:
            json.dump(record, f, indent=2)
        print(f"✅ Signature saved to {SIGNATURES_LOG} and {LATEST_SIGNATURE_FILE}")
    except Exception as e:
        print(f"❌ Failed to save signature: {e}")