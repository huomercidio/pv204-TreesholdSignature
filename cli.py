from datetime import datetime, time

def is_signing_allowed():
    now = datetime.now().time()
    return time(00, 0) <= now <= time(15, 30)

import argparse
import sys
import os
import json
from keygen import generate_and_store_shares
from required_shares_sign_event import required_shares_sign_event, save_note_signature
from verify_note_signature import verify_note_signature, read_note_signature, read_public_key

SECRETS_DIR = "keys"
MESSAGES_FILE = "note_contents.txt"
ALL_SIGNATURES_LOG = os.path.join(SECRETS_DIR, "note_signatures.txt")
RECENT_SIGNATURE_RECORD = os.path.join(SECRETS_DIR, "latest_note_signature.txt")

def ensure_note_contents_file():
    if not os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, "w") as f:
            f.write("")

def submit_note_content(note_content):
    ensure_note_contents_file()
    with open(MESSAGES_FILE, "r+") as f:
        note_contents = [json.loads(line) for line in f if line.strip()]
        new_id = max([m["id"] for m in note_contents], default=0) + 1
        new_note_content = {"id": new_id, "note_content": note_content, "status": "pending", "note_signatures": []}
        f.write(json.dumps(new_note_content) + "\n")
    print(f" Message submitted: ID {new_id} - '{note_content}'")

def list_note_contents():
    ensure_note_contents_file()
    with open(MESSAGES_FILE, "r") as f:
        note_contents = [json.loads(line) for line in f if line.strip()]
    if not note_contents:
        print("No note_contents pending.")
        return
    print("Pending Messages:")
    for m in note_contents:
        sig_count = len(m["note_signatures"])
        print(f"ID {m['id']}: '{m['note_content']}' (Signatures: {sig_count})")

def sign_partial(note_content_id, share_path):
    ensure_note_contents_file()
    with open(MESSAGES_FILE, "r") as f:
        lines = f.readlines()
    note_contents = [json.loads(line) for line in lines if line.strip()]
    note_content = next((m for m in note_contents if m["id"] == note_content_id), None)
    if not note_content or note_content["status"] != "pending":
        print(f" Message ID {note_content_id} not found or already processed.")
        return

    share_file = share_path.split("/")[-2]
    if any(sig["share"] == share_file for sig in note_content["note_signatures"]):
        print(f" Share {share_file} already signed this note_content.")
        return

    note_content["note_signatures"].append({"share": share_file})
    with open(MESSAGES_FILE, "w") as f:
        for m in note_contents:
            f.write(json.dumps(m) + "\n")
    print(f" Share {share_file} signed note_content ID {note_content_id}. Total note_signatures: {len(note_content['note_signatures'])}")

def sign(note_content, required_shares, share_files):
    note_signature = required_shares_sign_event(note_content, share_files, required_shares)
    if note_signature:
        print(f" Signature generated: {note_signature}")
        save_note_signature(note_signature, note_content)
    else:
        print(" Failed to sign the note_content.")

def verify(note_content):
    note_signature = read_note_signature(note_content)
    public_key = read_public_key()
    if note_signature and public_key:
        is_valid = verify_note_signature(note_content, note_signature, public_key)
        if is_valid is not None:
            print(" The note_signature is valid!" if is_valid else " The note_signature is invalid.")
        else:
            print(" Failed to verify the note_signature due to an error.")
    else:
        print(" Failed to load the note_signature or public key.")

def broadcast(note_content_id, required_shares):
    ensure_note_contents_file()
    with open(MESSAGES_FILE, "r") as f:
        lines = f.readlines()
    note_contents = [json.loads(line) for line in lines if line.strip()]
    note_content = next((m for m in note_contents if m["id"] == note_content_id), None)
    if not note_content or note_content["status"] != "pending":
        print(f" Message ID {note_content_id} not found or already broadcasted.")
        return

    sig_count = len(note_content["note_signatures"])
    if sig_count < required_shares:
        print(f" Insufficient note_signatures: {sig_count}/{required_shares}.")
        return

    share_files = [os.path.join(SECRETS_DIR, sig["share"], "secret_share.txt") for sig in note_content["note_signatures"]]
    note_signature = required_shares_sign_event(note_content["note_content"], share_files, required_shares)
    if note_signature:
        note_content["status"] = "broadcasted"
        with open(MESSAGES_FILE, "w") as f:
            for m in note_contents:
                f.write(json.dumps(m) + "\n")
        save_note_signature(note_signature, note_content["note_content"])
        print(f" Message ID {note_content_id} signed and ready for Nostr broadcast.")
        os.system("python nostr.py")
    else:
        print(" Failed to finalize note_signature.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    generate_parser = subparsers.add_parser("generate", help="Generate keys and shares")
    generate_parser.add_argument("--n", type=int, required=True, help="Number of participants")
    generate_parser.add_argument("--t", type=int, required=True, help="Signing required_shares")

    submit_parser = subparsers.add_parser("submit", help="Submit a new note_content")
    submit_parser.add_argument("--note_content", type=str, required=True, help="Emergency note_content")

    list_parser = subparsers.add_parser("list", help="List pending note_contents")

    sign_partial_parser = subparsers.add_parser("sign-partial", help="Sign a note_content with a share")
    sign_partial_parser.add_argument("--id", type=int, required=True, help="Message ID to sign")
    sign_partial_parser.add_argument("--share", type=str, required=True, help="Path to share file")

    sign_parser = subparsers.add_parser("sign", help="Sign a note_content with participant shares")
    sign_parser.add_argument("--note_content", type=str, required=True, help="Message to sign")
    sign_parser.add_argument("--required_shares", type=int, required=True, help="Threshold for signing")
    sign_parser.add_argument("--shares", nargs="+", required=True, help="Paths to share files")

    verify_parser = subparsers.add_parser("verify", help="Verify a note_signature")
    verify_parser.add_argument("--note_content", type=str, required=True, help="Message to verify")

    broadcast_parser = subparsers.add_parser("broadcast", help="Finalize and broadcast a note_content")
    broadcast_parser.add_argument("--id", type=int, required=True, help="Message ID to broadcast")
    broadcast_parser.add_argument("--required_shares", type=int, required=True, help="Threshold for signing")

    args = parser.parse_args()

    if args.command == "generate":
        generate_and_store_shares(args.n, args.t)
    elif args.command == "submit":
        submit_note_content(args.note_content)
    elif args.command == "list":
        list_note_contents()
    elif args.command == "sign-partial":
        sign_partial(args.id, args.share)
    elif args.command == "sign":
        sign(args.note_content, args.required_shares, args.shares)
    elif args.command == "verify":
        verify(args.note_content)
    elif args.command == "broadcast":
        broadcast(args.id, args.required_shares)
    else:
        parser.print_help()
        sys.exit(1)
