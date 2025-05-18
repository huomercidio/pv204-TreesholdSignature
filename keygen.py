import json
import os
import shutil
from frostpy import generate_keys_py

SECRETS_DIR = "keys"
ENV_TEMPLATE = """SHARE_ID={participant_id}
THRESHOLD={threshold}
SIGN_START=08:00
SIGN_END=22:00
POLL_INTERVAL=60
"""


def generate_and_store_shares(n: int, t: int) -> None:
    if t > n:
        raise ValueError(f"Threshold {t} cannot exceed participants {n}")

    print(f"Generating {n} shares (threshold {t})...")

    # Clear old state
    if os.path.exists(SECRETS_DIR):
        shutil.rmtree(SECRETS_DIR)
    for f in os.listdir('.'):
        if f.startswith('.env.share'):
            os.remove(f)

    # Generate new keys
    result = json.loads(generate_keys_py(n, t))

    os.makedirs(SECRETS_DIR, exist_ok=True)

    # Save group keys
    with open(os.path.join(SECRETS_DIR, "group_key_bundle.txt"), 'w') as f:
        f.write(result["group_public_key"])

    with open(os.path.join(SECRETS_DIR, "public_key.txt"), 'w') as f:
        f.write(result["group_verifying_key"])

    # Save participant shares
    for share in result["shares"]:
        pid = share["participant_id"]
        share_dir = os.path.join(SECRETS_DIR, str(pid))
        os.makedirs(share_dir, exist_ok=True)

        with open(os.path.join(share_dir, "secret_share.txt"), 'w') as f:
            json.dump(share["share"], f)

        with open(f".env.share{pid}", 'w') as f:
            f.write(ENV_TEMPLATE.format(
                participant_id=pid,
                threshold=t
            ))

    print(f"Successfully generated {n} shares")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--t", type=int, required=True)
    args = parser.parse_args()
    generate_and_store_shares(args.n, args.t)
