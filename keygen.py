import os
import json
from frostpy import generate_keys_py

SECRETS_DIR = "keys"

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def store_individual_share(participant_id, encoded_share):
    dir_path = os.path.join(SECRETS_DIR, f"{participant_id}")
    ensure_dir(dir_path)
    file_path = os.path.join(dir_path, "secret_share.txt")
    with open(file_path, "w") as f:
        f.write(encoded_share)
    print(f"✅ Saved share for participant {participant_id} → {file_path}")

def store_pubkey_bundle(group_key_bundle):
    ensure_dir(SECRETS_DIR)
    file_path = os.path.join(SECRETS_DIR, "group_key_bundle.txt")
    try:
        with open(file_path, "w") as f:
            f.write(group_key_bundle)
        print(f"✅ Group public key package saved → {file_path}")
    except Exception as e:
        print(f"❌ Error saving public key package: {e}")

def store_nostr_pubkey(group_key_bundle):
    ensure_dir(SECRETS_DIR)
    nostr_key_path = os.path.join(SECRETS_DIR, "public_key.txt")
    try:
        with open(nostr_key_path, "w") as f:
            f.write(group_key_bundle)
        print(f"✅ Group verifying key saved → {nostr_key_path}")
    except Exception as e:
        print(f"❌ Error saving Nostr public key: {e}")

def generate_and_store_shares(n: int, t: int):
    print(f"🚀 Generating {n} FROST shares with threshold {t}...")
    try:
        raw_json = generate_keys_py(n, t)
    except Exception as e:
        print(f"❌ Error during key generation: {e}")
        return

    try:
        result = json.loads(raw_json)
        shares = result["shares"]
        group_key_bundle = result["group_public_key"]
        group_verifying_key = result["group_verifying_key"]
    except Exception as e:
        print(f"❌ JSON parsing error: {e}")
        return

    store_pubkey_bundle(group_key_bundle)
    store_nostr_pubkey(group_verifying_key)

    for share in shares:
        pid = share["participant_id"]
        encoded = json.dumps(share["share"])
        store_individual_share(pid, encoded)

    print("✅ All shares and public key data saved successfully.")

if __name__ == "__main__":
    generate_and_store_shares(n=5, t=3)