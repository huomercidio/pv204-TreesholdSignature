import json
import os
from datetime import time, datetime
from typing import List
from frost import threshold_sign, verify_signature
from .models import SignedMessage


class FrostSigner:
    def __init__(self, keys_dir: str = "keys", window_start: time = time(9, 0), window_end: time = time(17, 0)):
        self.keys_dir = keys_dir
        self.window_start = window_start
        self.window_end = window_end

    def check_signing_window(self) -> bool:
        now = datetime.now().time()
        if not (self.window_start <= now <= self.window_end):
            raise PermissionError(
                f"Signing only allowed between {self.window_start.strftime('%H:%M')} "
                f"and {self.window_end.strftime('%H:%M')}"
            )
        return True

    def sign(self, message: str, share_paths: List[str], threshold: int) -> SignedMessage:
        """Threshold sign with time validation"""
        self.check_signing_window()

        shares = []
        for path in share_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Share file not found: {path}")
            with open(path, "r") as f:
                shares.append(json.load(f))

        pubkey_path = f"{self.keys_dir}/public_key_package.txt"
        if not os.path.exists(pubkey_path):
            raise FileNotFoundError("Public key package not found")

        with open(pubkey_path, "r") as f:
            pubkey_package = f.read().strip()

        signature = threshold_sign(
            message,
            json.dumps(shares),
            threshold,
            pubkey_package
        )

        return SignedMessage(
            message=message,
            signature=signature,
            timestamp=datetime.now().isoformat()
        )

    def verify(self, message: str, signature: str) -> bool:
        pubkey_path = f"{self.keys_dir}/verifying_key.txt"
        if not os.path.exists(pubkey_path):
            raise FileNotFoundError("Verifying key not found")

        with open(pubkey_path, "r") as f:
            public_key = f.read().strip()
        return verify_signature(message, signature, public_key)