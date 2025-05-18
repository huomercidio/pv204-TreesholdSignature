import argparse
import sys
import os
import json
from keygen import generate_and_store_shares
from required_shares_sign_event import required_shares_sign_event, save_note_signature

SECRETS_DIR = "keys"
MESSAGES_FILE = "note_contents.txt"


def ensure_note_contents_file():
    if not os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, "w") as f:
            f.write("")


def submit_note_content(note_content):
    ensure_note_contents_file()
    with open(MESSAGES_FILE, "r+") as f:
        note_contents = [json.loads(line) for line in f if line.strip()]
        new_id = max([m["id"] for m in note_contents], default=0) + 1
        new_note_content = {
            "id": new_id,
            "note_content": note_content,
            "status": "pending",
            "note_signatures": []
        }
        f.write(json.dumps(new_note_content) + "\n")
    print(f"Message submitted: ID {new_id}")


def list_note_contents():
    ensure_note_contents_file()
    with open(MESSAGES_FILE, "r") as f:
        note_contents = [json.loads(line) for line in f if line.strip()]
    for m in note_contents:
        print(f"ID {m['id']}: {m['note_content']} (Signatures: {len(m['note_signatures'])})")


def broadcast(note_content_id, required_shares):
    ensure_note_contents_file()
    with open(MESSAGES_FILE, "r") as f:
        note_contents = [json.loads(line) for line in f if line.strip()]

    note_content = next((m for m in note_contents if m["id"] == note_content_id), None)
    if not note_content or note_content["status"] == "broadcasted":
        print(f"Message ID {note_content_id} not found or already broadcasted")
        return

    if len(note_content["note_signatures"]) < required_shares:
        print(f"Insufficient signatures: {len(note_content['note_signatures'])}/{required_shares}")
        return

    share_files = [
        os.path.join(SECRETS_DIR, sig["share"], "secret_share.txt")
        for sig in note_content["note_signatures"]
    ]

    note_signature = required_shares_sign_event(
        note_content["note_content"],
        share_files,
        required_shares
    )

    if note_signature:
        note_content["status"] = "broadcasted"
        with open(MESSAGES_FILE, "w") as f:
            for m in note_contents:
                f.write(json.dumps(m) + "\n")
        save_note_signature(note_signature, note_content["note_content"])
        print(f"Message ID {note_content_id} ready for broadcast")
    else:
        print("Failed to create final signature")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    generate_parser = subparsers.add_parser("generate")
    generate_parser.add_argument("--n", type=int, required=True)
    generate_parser.add_argument("--t", type=int, required=True)

    submit_parser = subparsers.add_parser("submit")
    submit_parser.add_argument("--note_content", required=True)

    list_parser = subparsers.add_parser("list")

    broadcast_parser = subparsers.add_parser("broadcast")
    broadcast_parser.add_argument("--id", type=int, required=True)
    broadcast_parser.add_argument("--required_shares", type=int, required=True)

    args = parser.parse_args()

    if args.command == "generate":
        generate_and_store_shares(args.n, args.t)
    elif args.command == "submit":
        submit_note_content(args.note_content)
    elif args.command == "list":
        list_note_contents()
    elif args.command == "broadcast":
        broadcast(args.id, args.required_shares)
    else:
        parser.print_help()
        sys.exit(1)
