import secrets
import hashlib
import json

from ecdsa import SigningKey, SECP256k1

def generate_frost_shares(n=5, t=3):
    if not (2 <= t <= n):
        raise ValueError("Threshold t must be at least 2 and at most n")

    # Gera chaves privadas aleatórias
    secret_keys = [secrets.token_bytes(32) for _ in range(n)]
    signing_keys = [SigningKey.from_string(sk, curve=SECP256k1) for sk in secret_keys]
    verifying_keys = [sk.verifying_key for sk in signing_keys]

    shares = []
    for i in range(n):
        share_hex = secret_keys[i].hex()
        pubkey_hex = verifying_keys[i].to_string().hex()
        shares.append({
            "id": i + 1,
            "private_share": share_hex,
            "public_share": pubkey_hex
        })

    group_pubkey_hash = hashlib.sha256(b''.join(vk.to_string() for vk in verifying_keys)).hexdigest()

    return {
        "group_public_key": group_pubkey_hash,
        "shares": shares
    }


if __name__ == '__main__':
    result = generate_frost_shares(n=5, t=3)
    print(json.dumps(result, indent=2))
