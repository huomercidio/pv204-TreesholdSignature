pv204-TreesholdSignature

🚀 Secure Nostr Event Signing with Threshold Cryptography

Overview

This project implements a secure and decentralized signature system for Nostr events using threshold cryptography.

The protocol ensures that no single device holds the full private key. Instead, the private key is distributed among 4 participants via Distributed Key Generation (DKG), and an Automatic Signer is only available from 08:00 to 15:00.

A valid signature requires collaboration from at least 2 participant devices and the AutoSigner, achieving a 3-of-5 threshold.

All logic is implemented in Python using real cryptographic primitives.

**Core Features**

- Elliptic Curve: Uses the Nostr-compatible curve secp256k1

- Threshold Signing: Based on the structure of the FROST protocol

- Distributed Key Generation (DKG): Secret key is never revealed; shares are generated collaboratively

- Automatic Signer: Time-restricted signer only active between 08:00–15:00

- Nostr Integration: Events are serialized, signed, and broadcast to public Nostr relays

**Architecture**

- 4 participant devices (💻💻💻💻)

- 1 AutoSigner (⏱️ automatic signer)

- Threshold = 3 of 5

- Key shares and operations follow modular cryptographic logic using coincurve, hashlib, and bech32

**Security Benefits**

- Private key never reconstructed or revealed

- Signature is only possible via collaborative partial signatures

- Time-limited access via AutoSigner increases operational security

- Supports secure decentralized signing for Nostr messages

**How to Test**

- Run threshold.py

- Simulates DKG and generates key_shares/ and partial_sigs/

- Verifies if AutoSigner is within allowed window

- Combines valid partials into a full hash-based signature

- Displays npub of the final signer

⚠️ **Note:** This is a secure simulation using real EC keypairs, but simplified Schnorr aggregation. 


**Authors**

👩 Benilde Nhanala – 565303

👨 Mercidio Huo – 565299

