# pv204-TreesholdSignature
Secure Nostr Event Signing with Threshold Cryptography

This project implements a secure and decentralized system for signing Nostr events using threshold cryptography. It is designed to work with 3 devices, where at least 2 active devices plus an Automatic Signer are required to produce valid signatures. The Automatic Signer is only available during specific hours, adding a temporal access control layer to the signing process.

# Core Features

•	Elliptic Curve: The project uses the correct curve required by Nostr: secp256k1.
•	Threshold Signing: Based on the FROST protocol (Flexible Round-Optimized Schnorr Threshold signatures).
•	Distributed Key Generation (DKG): Key shares are generated using DKG.
•	Automatic Signer: Participates in signing only during specific hours (08:00 to 15:00). If it is offline or out of schedule, signing will not proceed.
•	Nostr Integration: Events are serialized, signed, and published to the Nostr network via relays.


# Architecture

•	Device Nodes
•	3 total nodes.
•	Each holds a share of the secret key generated via DKG.
•	Any 2 devices, together with the Automatic Signer, are required to produce a valid signature.


# Threshold Signature Scheme

•	DKG: Generates shares collaboratively across devices.
•	Partial Signing: Each device creates a Schnorr partial signature using its share.
•	Aggregation: Signatures are combined to form a final valid Schnorr signature(FROST Protocol).
•	Automatic Signer
  o	Holds one of the key shares.
  o	Only signs within the window from 08:00 to 15:00 (3 PM).
  o	Outside this window, it ignores signing requests.
  o	System is configured to require this signer for valid signature generation, even if 3 devices are online.


# Event Creation Module

•	Hashes event content.
•	Serializes and formats events according to the Nostr protocol.
•	Generates event ID based on content and public key.
•	Nostr Communication
•	Signed events are sent to the decentralized Nostr network via public relays.

# Nostr Compatibility

•	Uses secp256k1 as required.
•	Compatible with NIP-01 event structure.

# Testing

•	To simulate a signing round:
•	Start all 3 devices (2 active, 1 Automatic Signer).
•	Ensure the Automatic Signer is within the time window (08:00–15:00).
•	Submit a Nostr event to be signed.
•	Verify that:
•	Only when at least 2 active devices + Automatic Signer respond, the signature is produced.
•	Requests outside time window are rejected.
