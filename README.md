# 🔐 Nostr FROST Threshold Signer

This project implements a secure, time-controlled **threshold signature system** using the [FROST protocol](https://eprint.iacr.org/2020/852) to collaboratively sign Nostr events.

---

## 🎯 Project Goal

To create a system that allows:

- ✅ **Collaborative key generation** across multiple devices
- ✅ **Threshold signing** (e.g., 3-of-5 shares) of Nostr events using FROST
- ✅ **Time-restricted automatic signers** that only sign during configured time windows
- ✅ **Verified and broadcasted Nostr events**

---
## 📁 Project Structure

| File / Folder          | Purpose                                                                 |
|------------------------|-------------------------------------------------------------------------|
| `cli.py`               | 🛠️ CLI tool: submit messages, sign manually, verify, broadcast to Nostr |
| `auto_signer.py`       | 🤖 Time-restricted automatic signer for background signing               |
| `run_signers.py`       | 🧪 Simulates multiple signer devices using `.env.*` configuration files  |
| `keygen.py`            | 🔐 Generates FROST key shares and stores the group public key            |
| `sign_message.py`      | 🧩 Aggregates shares to produce valid FROST threshold signatures         |
| `verify_signature.py`  | 🔎 Verifies signatures against the public key                            |
| `note_contents.txt`    | 📝 Stores submitted messages and collected partial signatures            |
| `keys/`                | 📂 Contains secret shares, public key, and all log files                |
| `signed_notes.log`     | 📜 Logs each auto signer's activity, per device                          |
| `.env`, `.env.1`, etc. | ⚙️ Per-device environment configs: `SIGN_START`, `SIGN_END`, `SHARE_ID` |
| `src/lib.rs`           | 🦀 Rust-based FROST logic exposed via PyO3 bindings                      |
| `frostpy/`             | 🐍 Python module compiled from Rust code (via `maturin develop`)         |

---
## 📦 Requirements

- Python 3.9+
- [Install Rust](https://www.rust-lang.org/tools/install)
- Confirm with: `rustc --version`

- Rust toolchain (`rustup`, `cargo`)
- [`maturin`](https://github.com/PyO3/maturin) for Python-Rust bindings
- Internet access (for broadcasting to Nostr relays)

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository

```bash
git clone https://github.com/yourname/pv204-TreesholdSignature
cd pv204-TreesholdSignature
```

### 2️⃣ Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # For macOS/Linux
# OR
venv\Scripts\activate   # For Windows
```

### 3️⃣ Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Build the FROST Rust bindings

```bash
maturin develop
```
---

## 🔐 Key Generation

```bash
python cli.py generate --n 5 --t 3
```

📌 What it does:
- Generates `n` FROST key shares with a signing threshold `t`
- Stores each share in `keys/<id>/secret_share.txt`
- Stores the group public key in `keys/public_key.txt`

➡️ Distribute share files to the respective signer devices.

---

## 📝 Submit a Message for Signing

```bash
python cli.py submit --note_content "teste"
```

📌 What it does:
- Adds a new message to `note_contents.txt` with status `pending`

---

## 🤖 Automatic Signing (on each device)

Configure a `.env` file per device: choose your time signing

#### Create `.env.1`, `.env.2`, `.env.3`...

```env
SIGN_START=15:00
SIGN_END=23:30
SHARE_ID=1
```

Run:

```bash
python run_signers.py
```

This simulates all signers and respects each `.env.X` time window.

Run:

```bash
python auto_signer.py
```

📌 What it does:
- Checks if current time is within `SIGN_START` and `SIGN_END`
- Loads device’s `secret_share.txt` (from `SHARE_ID`)
- Signs all pending messages it hasn’t signed yet
- Appends a timestamped signature to each message
- Logs all actions in `signed_notes.log`

➡️ Set up with `cron` or `systemd` to run every 5 mins.

---
**🧠 Concept: Simulating Multiple Devices**


In a threshold signature system, each device holds one share of the secret and should act independently—like its own signer.

To simulate this behavior on one machine (for development/testing), we use:


1️⃣ auto_signer.py → Single Device Auto Signer

This script:

Loads environment variables from .env or any .env.<id> file
.
Checks the configured SIGN_START and SIGN_END time window.


If the current time is allowed, it:
Loads the configured share (from SHARE_ID)
Signs any pending message that it hasn't signed yet
Logs the action to signed_notes.log
It represents one device participating in signing.

2️⃣ run_signers.py → Launcher for All Devices

This script:

Iterates over a list of device IDs (e.g., 1, 2, 3)

For each ID:
Temporarily sets SHARE_ID, SIGN_START, and SIGN_END via environment variables

Calls auto_signer.py in a subprocess

This simulates multiple devices running independently by 

calling auto_signer.py with different .env configurations.

📌 Example Flow
```bash
python run_signers.py
```
**Output:**

🚀 Starting multi-device auto signer simulation...

🔁 Running signer for SHARE_ID=1

[2025-05-09 00:11:28] 🚦 Auto signer started for SHARE_ID=1

[2025-05-09 00:11:28] ✅ Signed note ID 5 using share 1


🔁 Running signer for SHARE_ID=2

[2025-05-09 00:11:29] 🚦 Auto signer started for SHARE_ID=2

[2025-05-09 00:11:29] ✅ Signed note ID 5 using share 2


🔁 Running signer for SHARE_ID=3

[2025-05-09 00:11:30] 🚦 Auto signer started for SHARE_ID=3

[2025-05-09 00:11:30] ⏳ Outside signing window. Ignoring request.

Here:

Device 1 and 2 signed because they are inside the signing window.


Device 3 ignored the request because it was outside the allowed time.

✅ Summary

Script	
Role	How to Use

- auto_signer.py	Simulates one signer device	python auto_signer.py

- run_signers.py	Simulates multiple devices at once	python run_signers.py



## 📦 Broadcast a Message Once Threshold is Met

```bash
python cli.py broadcast --id 1 --required_shares 3
```

📌 What it does:
- Aggregates threshold signatures using FROST
- Verifies it
- Saves final signature to `latest_note_signature.txt`
- Triggers Nostr publishing

---

## 🌐 Publish to Nostr

Edit `nostr.py` to use your real Nostr private key (`nsec...`), then run:

```bash
python nostr.py
```

📌 What it does:
- Verifies final FROST signature
- Publishes message to `wss://nos.lol/` and `wss://relay.damus.io/`

---

## ✅ Verifying a Signature

```bash
python cli.py verify --note_content "teste"
```

---


## 🔐 Security Notes

- Never share your `secret_share.txt` files.


## 🧪 Example Workflow

1. One device runs `generate` and distributes shares
2. Devices run `auto_signer.py` every few mins
3. Once enough signatures exist, run `broadcast`
4. Signature is verified and sent to Nostr
5. Everyone sees the signed message 🎉

---

## 🔒 License

MIT — feel free to use and extend!

---

## 👨‍💻 Author

Mercídio Huo — Built for PV204 / Threshold Crypto + Nostr Systems
Benilde Nhanala — Built for PV204 / Threshold Crypto + Nostr Systems
