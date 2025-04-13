import argparse
import asyncio
import json
import os
from typing import List
from .keygen import KeyGenerator
from .signer import FrostSigner
from .nostr import NostrPublisher
from .models import SignedMessage


def generate_keys(args):
    generator = KeyGenerator()
    try:
        shares = generator.generate(args.n, args.t)
        print(f"Generated {args.n}-of-{args.t} threshold keys")
        print(f"Group public key saved to keys/verifying_key.txt")
    except ValueError as e:
        print(f"❌ Error generating keys: {e}")


def sign_message(args):
    signer = FrostSigner()
    try:
        # Validate shares exist
        for share in args.shares:
            if not os.path.exists(share):
                raise FileNotFoundError(f"Share file not found: {share}")

        signed = signer.sign(args.message, args.shares, args.threshold)
        os.makedirs("keys", exist_ok=True)
        with open("keys/latest_signature.txt", "w") as f:
            json.dump({
                "message": signed.message,
                "signature": signed.signature,
                "timestamp": signed.timestamp
            }, f)
        print(f"✅ Signed message saved to keys/latest_signature.txt")
    except Exception as e:
        print(f"❌ Signing failed: {e}")


async def publish_message(args):
    try:
        if not os.path.exists("keys/latest_signature.txt"):
            raise FileNotFoundError("No signature found. Please sign a message first.")

        with open("keys/latest_signature.txt", "r") as f:
            data = json.load(f)

        publisher = NostrPublisher(args.private_key)
        event_id = await publisher.publish(data["message"], data["signature"])
        print(f"📨 Published event ID: {event_id}")
    except Exception as e:
        print(f"❌ Publish failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="Nostr Threshold Signer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Key generation
    keygen_parser = subparsers.add_parser("generate")
    keygen_parser.add_argument("-n", type=int, required=True, help="Number of participants (must be ≥ threshold)")
    keygen_parser.add_argument("-t", type=int, required=True, help="Signing threshold (must be ≥ 1)")
    keygen_parser.set_defaults(func=generate_keys)

    # Signing
    sign_parser = subparsers.add_parser("sign")
    sign_parser.add_argument("-m", "--message", required=True)
    sign_parser.add_argument("-s", "--shares", nargs="+", required=True)
    sign_parser.add_argument("-t", "--threshold", type=int, required=True)
    sign_parser.set_defaults(func=sign_message)

    # Publish
    publish_parser = subparsers.add_parser("publish")
    publish_parser.add_argument("-k", "--private-key", required=True)
    publish_parser.set_defaults(func=lambda args: asyncio.run(publish_message(args)))

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
