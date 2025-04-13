import asyncio
import json
from typing import List, Optional
from nostr_sdk import Keys, Client, EventBuilder, NostrSigner
from .signer import FrostSigner


class NostrPublisher:
    DEFAULT_RELAYS = [
        "wss://nos.lol",
        "wss://relay.damus.io"
    ]

    def __init__(self, private_key_hex: str, relays: Optional[List[str]] = None):
        self.private_key = private_key_hex
        self.relays = relays or self.DEFAULT_RELAYS
        self.signer = FrostSigner()

    async def publish(self, message: str, signature: str) -> str:
        """Publish verified event to Nostr"""
        if len(message) > 20000:  # Roughly 20KB limit
            raise ValueError("Message too large for Nostr event")

        if not self.signer.verify(message, signature):
            raise ValueError("Invalid signature")

        keys = Keys.parse(self.private_key)
        client = Client(NostrSigner.keys(keys))

        for relay in self.relays:
            try:
                await client.add_relay(relay)
            except Exception as e:
                print(f"Warning: Failed to add relay {relay}: {str(e)}")

        await client.connect()

        content = json.dumps({
            "message": message,
            "signature": signature
        })

        event = EventBuilder.text_note(content, [])
        result = await client.send_event_builder(event)

        return result.id.to_hex()
