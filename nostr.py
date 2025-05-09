import asyncio
from nostr_sdk import Keys, Client, EventBuilder, NostrSigner
import os
import json
import frostpy

SECRETS_DIR = "keys"
RECENT_SIGNATURE_RECORD = os.path.join(SECRETS_DIR, "latest_note_signature.txt")

async def publish_frost_event():
    try:
        private_key_hex = "nsec1j25teydgjpg32wke38zjl8ar3kvskjye63924h9rpt2mzekgep0smrx2kv"
        note_signature_file = RECENT_SIGNATURE_RECORD
        public_key_file = os.path.join(SECRETS_DIR, "public_key.txt")
        if not os.path.exists(note_signature_file):
            raise FileNotFoundError(f"Signature file not found at {note_signature_file}. Run 'python cli.py broadcast' first.")
        with open(note_signature_file, "r") as f:
            data = json.load(f)
            frost_note_signature_b64 = data["signature"]
            frost_note_content = data["note_content"]

        if not os.path.exists(public_key_file):
            raise FileNotFoundError(f"Public key file not found at {public_key_file}. Run 'python cli.py generate' first.")
        with open(public_key_file, "r") as f:
            public_key_b64 = f.read().strip()

        if not frostpy.verify_signature_py(frost_note_content, frost_note_signature_b64, public_key_b64):
            raise ValueError("FROST note_signature verification failed.")
        print("✅ FROST note_signature verified successfully")

        keys = Keys.parse(private_key_hex)
        signer = NostrSigner.keys(keys)
        client = Client(signer)

        await client.add_relay("wss://nos.lol/")
        await client.add_relay("wss://relay.damus.io/")
        await client.connect()
        await asyncio.sleep(1)

        note_content = f"{frost_note_content}\nFROST Signature: {frost_note_signature_b64}"
        event_builder = EventBuilder.text_note(note_content)

        res = await client.send_event_builder(event_builder)
        event_id = res.id.to_bech32() if res.id else "Failed to get ID"
        print(f"FROST Message: {frost_note_content}")
        print(f"FROST Signature: {frost_note_signature_b64}")
        print(f"Nostr Event ID: {event_id}")
        print(f"Sent to: {res.success}")
        print(f"Not sent to: {res.failed}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(publish_frost_event())
