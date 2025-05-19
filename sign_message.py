import os
import json
from typing import List
from frostpy import required_shares_sign_event_py

SECRETS_DIR = "keys"
ALL_SIGNATURES_LOG = os.path.join(SECRETS_DIR, "note_signatures.txt")
RECENT_SIGNATURE_RECORD = os.path.join(SECRETS_DIR, "latest_note_signature.txt")

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def read_share(file_path):
    try:
        with open(file_path, "r") as f:
            share_data = json.loads(f.read())
        return share_data
    except Exception as e:
        print(f"Error reading share from {file_path}: {e}")
        return None

def collect_shares(share_files: List[str]):
    shares = []
    for path in share_files:
        share = read_share(path)
        if share:
            shares.append(share)
        else:
            print(f"Skipping invalid share at {path}")
    return shares

def read_group_key_bundle():
    file_path = os.path.join(SECRETS_DIR, "group_key_bundle.txt")
    try:
        with open(file_path, "r") as f:
            group_key_bundle = f.read()
        print(f"Public key package loaded → {file_path}")
        return group_key_bundle
    except Exception as e:
        print(f"Error reading public key package: {e}")
        return None

def save_note_signature(note_signature: str, note_content: str):
    ensure_dir(SECRETS_DIR)
    # Append to note_signatures.txt as a list
    entry = {"note_content": note_content, "note_signature": note_signature}
    if os.path.exists(ALL_SIGNATURES_LOG):
        with open(ALL_SIGNATURES_LOG, "r") as f:
            note_signatures = json.load(f)
    else:
        note_signatures = []
    note_signatures.append(entry)
    with open(ALL_SIGNATURES_LOG, "w") as f:
        json.dump(note_signatures, f)
    print(f"Signature appended to → {ALL_SIGNATURES_LOG}")
    
    # Write only the latest to latest_note_signature.txt
    with open(RECENT_SIGNATURE_RECORD, "w") as f:
        json.dump(entry, f)
    print(f"Latest note_signature saved → {RECENT_SIGNATURE_RECORD}")

def required_shares_sign_event(note_content: str, share_files: List[str], required_shares: int) -> str | None:
    print(f" Signing note_content: '{note_content}' with required_shares {required_shares}")
    shares = collect_shares(share_files)
    if len(shares) < required_shares:
        print(f"Error: Insufficient shares provided! Needed {required_shares}, got {len(shares)}.")
        return None

    group_key_bundle = read_group_key_bundle()
    if not group_key_bundle:
        print("Cannot sign note_content without the public key package.")
        return None

    shares_json = json.dumps(shares)
    try:
        note_signature_b64, signed_note_content = required_shares_sign_event_py(note_content, shares_json, required_shares, group_key_bundle)
        print("Message signed successfully!")
        save_note_signature(note_signature_b64, signed_note_content)
        return note_signature_b64
    except Exception as e:
        print(f"Error during signing: {e}")
        return None

if __name__ == "__main__":
    note_content = "Message signed in a distributed manner using threshold signatures!"
    required_shares = 2
    share_files = [
        os.path.join(SECRETS_DIR, "1", "secret_share.txt"),
        os.path.join(SECRETS_DIR, "2", "secret_share.txt"),
    ]
    note_signature = required_shares_sign_event(note_content, share_files, required_shares)
    if note_signature:
        print(f"Generated Signature: {note_signature}")
    else:
        print("Failed to generate the note_signature.")
