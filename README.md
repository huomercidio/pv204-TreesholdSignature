#pv204-TreesholdSignature
🚀 #Secure Nostr Event Signing with Threshold Cryptography
🔍 #Overview
This project implements a secure and decentralized signature system for Nostr events using threshold cryptography.

The protocol ensures that no single device holds the full private key. Instead, the private key is distributed among 4 participants via Distributed Key Generation (DKG), and an Automatic Signer is only available from 08:00 to 15:00.

A valid signature requires collaboration from at least 2 participant devices and the AutoSigner, achieving a 3-of-5 threshold.

🔐 #Core Features
✅ **Elliptic Curve: Uses the Nostr-compatible curve secp256k1

🔁 Threshold Signing: Based on the structure of the FROST protocol (Flexible Round-Optimized Schnorr Threshold signatures)

🧩 Distributed Key Generation (DKG): Secret key is never revealed; shares are generated collaboratively

⏰ Automatic Signer: Time-restricted signer only active between 08:00–15:00

📡 Nostr Integration: Events are serialized, signed, and broadcast to public Nostr relays (e.g., wss://relay.damus.io, wss://purplerelay.com, wss://nos.lol)

⚙️ Architecture
4 participant devices (💻💻💻💻)

1 AutoSigner (⏱️ automatic ♂️ or ♀️)

Threshold = 3 of 5

All key shares and operations follow modular cryptographic logic using coincurve, hashlib, and bech32
