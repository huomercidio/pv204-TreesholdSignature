# ❄️ pv204-TreesholdSignature

**Secure Nostr Event Signing with Threshold Cryptography**

This project implements a secure and decentralized threshold signature system using the **FROST** protocol over the **secp256k1** curve, fully compatible with the **Nostr** network. It ensures that only a subset of devices can jointly sign a message, with the addition of a time-restricted **Automatic Signer** for added control.

---

## ✨ **Features**

- **Elliptic Curve**: Uses the required curve for Nostr (**secp256k1**).
- **Threshold Signing**: Based on the real **FROST** protocol with t-of-n configuration.
- **Distributed Key Generation (DKG)**: Devices collaboratively generate key shares.
- **Automatic Signer**: Only active during specific hours (08:00–15:00), it holds a key share required for signing.
- **Event Signing**: Events are hashed, signed by multiple participants, and sent to the **Nostr** relays.
- **Language**: Implemented in **Rust** (signing backend) + **Python** (event serialization and publication).

---

## 🧠 **How It Works**

1. **Keygen**: Run DKG with `cargo run -- keygen` to generate `n` key shares.
2. **Partial Signing**: Devices run `sign` individually to create partial signatures.
3. **Combination**: A third party combines valid partials using the `combine` command.
4. **Python**: The combined signature is used to create a valid **Nostr** event and publish it through relays.

---

## 🚀 **Command Line Interface (Rust)**

```sh
cargo run -- keygen --output shares --participants 5 --threshold 3
cargo run -- sign --share shares/share_1.json --message HASH --output sig_1.json
cargo run -- combine --signatures sig_1.json sig_2.json sig_5.json --output final_sig.json
```

---

## 🛰️ **Send Signed Event to Nostr (Python)**

Use the provided `send_to_nostr.py` to:
- Load the `final_sig.json`
- Create a valid Nostr event
- Send it to public relays like Damus and Nos.lol

---

## 👩🏾‍💻👨🏽‍💻 **Authors**

- **Benilde Nhanala – 565303** 👩🏾‍💻  
- **Mercidio Huo – 565299** 👨🏽‍💻

---

## 📁 **Source Code**

Below is the core logic of the Rust CLI implementation:

```rust
use clap::{Parser, Subcommand};
use frost_secp256k1 as frost;
use rand::thread_rng;
use serde::{Deserialize, Serialize};
use std::{fs, path::Path};

#[derive(Parser)]
#[command(author, version, about)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    Keygen {
        #[arg(short, long)]
        output: String,
        #[arg(short, long, default_value_t = 5)]
        participants: u16,
        #[arg(short, long, default_value_t = 3)]
        threshold: u16,
    },
    Sign {
        #[arg(short, long)]
        share: String,
        #[arg(short, long)]
        message: String,
        #[arg(short, long)]
        output: String,
    },
    Combine {
        #[arg(short, long)]
        signatures: Vec<String>,
        #[arg(short, long)]
        output: String,
    },
}

#[derive(Serialize, Deserialize)]
struct KeyShare {
    identifier: frost::Identifier,
    share: frost::SecretShare,
    public: frost::PublicKeyPackage,
}

#[derive(Serialize, Deserialize)]
struct PartialSig {
    identifier: frost::Identifier,
    signature: frost::round1::SignatureShare,
}

#[derive(Serialize, Deserialize)]
struct CombinedSig {
    signature: frost::Signature,
    pubkey: frost::PublicKeyPackage,
}

fn main() {
    let cli = Cli::parse();

    match cli.command {
        Commands::Keygen {
            output,
            participants,
            threshold,
        } => {
            let mut rng = thread_rng();
            let (shares, pubkey_package) = frost::keys::generate_with_dealer(
                participants,
                threshold,
                frost::keys::IdentifierList::Default,
                &mut rng,
            )
            .unwrap();

            for (identifier, secret_share) in shares {
                let share = KeyShare {
                    identifier,
                    share: secret_share,
                    public: pubkey_package.clone(),
                };
                let path = format!("{}/share_{}.json", output, identifier);
                fs::write(path, serde_json::to_string(&share).unwrap()).unwrap();
            }
            println!("Generated {} key shares", participants);
        }
        Commands::Sign {
            share,
            message,
            output,
        } => {
            let share: KeyShare = serde_json::from_str(&fs::read_to_string(share).unwrap()).unwrap();
            let msg = hex::decode(message).unwrap();
            let nonce = frost::round1::SigningNonces::new(&mut thread_rng());
            let partial = frost::round1::commit(
                share.identifier,
                &share.share,
                &nonce,
                &msg,
                &share.public,
            )
            .unwrap();

            let partial_sig = PartialSig {
                identifier: share.identifier,
                signature: partial,
            };
            fs::write(output, serde_json::to_string(&partial_sig).unwrap()).unwrap();
            println!("Generated partial signature");
        }
        Commands::Combine {
            signatures,
            output,
        } => {
            let mut sigs = Vec::new();
            let mut pubkey_package = None;

            for path in signatures {
                let partial: PartialSig = serde_json::from_str(&fs::read_to_string(path).unwrap()).unwrap();
                sigs.push(partial.signature);
                if pubkey_package.is_none() {
                    let share: KeyShare = serde_json::from_str(&fs::read_to_string(path).unwrap()).unwrap();
                    pubkey_package = Some(share.public);
                }
            }

            let combined = frost::aggregate(&sigs, &pubkey_package.unwrap()).unwrap();
            let result = CombinedSig {
                signature: combined,
                pubkey: pubkey_package.unwrap(),
            };
            fs::write(output, serde_json::to_string(&result).unwrap()).unwrap();
            println!("Combined signatures successfully");
        }
    }
}
```



