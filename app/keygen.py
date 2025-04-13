import os
import json
from typing import List
from frost import generate_keys
from .models import KeyShare


class KeyGenerator:
    def __init__(self, keys_dir: str = "keys"):
        self.keys_dir = keys_dir
        os.makedirs(keys_dir, exist_ok=True)

    def generate(self, n: int, t: int) -> List[KeyShare]:
        """Generate and save threshold keys"""
        if t > n:
            raise ValueError("Threshold t cannot be greater than number of participants n")
        if t < 1:
            raise ValueError("Threshold must be at least 1")

        result = json.loads(generate_keys(n, t))

        # Save public keys
        with open(f"{self.keys_dir}/public_key_package.txt", "w") as f:
            f.write(result["public_key_package"])

        with open(f"{self.keys_dir}/verifying_key.txt", "w") as f:
            f.write(result["verifying_key"])

        # Save and return shares
        shares = []
        for share_data in result["shares"]:
            share = KeyShare(
                participant_id=int(share_data["identifier"], 16),  # Use identifier as participant_id
                identifier=share_data["identifier"],
                signing_share=share_data["signing_share"],
                verifying_share=share_data["verifying_share"]
            )
            share_dir = f"{self.keys_dir}/participant_{share.participant_id}"
            os.makedirs(share_dir, exist_ok=True)
            with open(f"{share_dir}/share.json", "w") as f:
                json.dump(share_data, f)
            shares.append(share)

        return shares