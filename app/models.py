from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict

@dataclass
class KeyShare:
    participant_id: int
    identifier: str
    signing_share: str
    verifying_share: str

@dataclass
class SignedMessage:
    message: str
    signature: str
    timestamp: str
