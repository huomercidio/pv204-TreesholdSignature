# 🔐 Threshold Signature

**Threshold Signature** is a Rust-powered Python extension that provides **real key generation for threshold signatures** using the [FROST](https://eprint.iacr.org/2020/852) protocol over the **secp256k1** elliptic curve.

This tool enables decentralized signing setups, supporting secure generation of cryptographic key shares for a specified number of participants with a configurable threshold.

---

## ✨ Features

- ✅ Generates real FROST key shares for `n` participants and threshold `t`
- ✅ Outputs group public key and per-participant signing shares
- ✅ Full Python integration via [PyO3](https://github.com/PyO3/pyo3) and [maturin](https://github.com/PyO3/maturin)
- ✅ Secure cryptographic operations over the widely used `secp256k1` curve
- ✅ Implements `generate_keys_py()` via `frost_secp256k1::keys::generate_with_dealer`
- ✅ Shares are returned as JSON using `Identifier`, `SecretShare`, and `PublicKeyPackage`

---

## 📦 Installation

### 1. Requirements

- Python 3.8+
- Rust and Cargo installed
- [maturin](https://github.com/PyO3/maturin): install with `pip install maturin`

### 2. Setup

```bash
git clone https://github.com/YOUR_USERNAME/pv204-TreesholdSignature.git
cd pv204-TreesholdSignature/frost

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate   # On Linux/macOS: source .venv/bin/activate

# Compile the Rust crate and install as a Python module
maturin develop
```

---

## 🔮 Usage (Python)

```python
from thresholdfrost import generate_keys_py

# Generate key shares for 5 participants with threshold 3
print(generate_keys_py(n=5, t=3))
```

This returns a JSON string with:

- `group_public_key`: hex-encoded group key
- `group_verifying_key`: hex-encoded verifying key
- `shares`: list of signing shares per participant

---

## 📚 Internals

This crate exposes the following:

- `generate_keys_py(n, t)`
  - Uses `frost_secp256k1::keys::generate_with_dealer`
  - Handles conversion between `usize` and `u16`
  - Serializes identifiers and signing shares with `hex`

---

## 👩‍💻 Authors

This project was developed as part of the **PV204 - TreesholdSignature** assignment by:

- **Benilde Nhanala** — [565303@mail.muni.cz]
- **Mercídio Huo** — [565299@mail.muni.cz]
