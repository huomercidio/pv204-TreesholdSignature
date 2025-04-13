use frost_secp256k1::{
    keys::{generate_with_dealer, KeyPackage, PublicKeyPackage, VerifyingShare},
    round1, round2, SigningPackage, Signature, VerifyingKey, Identifier,
    SigningShare, SigningCommitments
};
use pyo3::prelude::*;
use rand::thread_rng;
use serde_json::{json, Value};
use hex;
use std::collections::BTreeMap;

/// Generate threshold keys (DKG)
#[pyfunction]
fn generate_keys(n: u16, t: u16) -> PyResult<String> {
    let mut rng = thread_rng();

    let (shares, pubkey_package) = generate_with_dealer(
        n,
        t,
        &mut rng
    ).map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Key generation failed: {}", e)))?;

    // Serialize shares
    let shares_json: Vec<Value> = shares.into_iter().map(|(id, share)| {
        let signing_share = share;
        let verifying_share = VerifyingShare::from(&signing_share);

        json!({
            "identifier": hex::encode(id.serialize()),
            "signing_share": hex::encode(signing_share.serialize()),
            "verifying_share": hex::encode(verifying_share.serialize()),
        })
    }).collect();

    let public_key_package_bytes = pubkey_package.serialize().map_err(|e|
        PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Serialization failed: {}", e)))?;

    let verifying_key_bytes = pubkey_package.verifying_key().serialize();

    Ok(json!({
        "shares": shares_json,
        "public_key_package": hex::encode(public_key_package_bytes),
        "verifying_key": hex::encode(verifying_key_bytes),
    }).to_string())
}

/// Threshold sign a message
#[pyfunction]
fn threshold_sign(
    message: String,
    shares_json: String,
    threshold: u16,
    pubkey_package_hex: String,
) -> PyResult<String> {
    let shares: Vec<Value> = serde_json::from_str(&shares_json)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid shares JSON: {}", e)))?;

    let pubkey_package = PublicKeyPackage::deserialize(
        &hex::decode(pubkey_package_hex)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Hex decode failed: {}", e)))?
    ).map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("PK deserialization failed: {}", e)))?;

    let mut nonces_map = BTreeMap::new();
    let mut commitments_map = BTreeMap::new();
    let mut key_packages = Vec::new();

    // Prepare signing packages
    for share in shares {
        let id_bytes = hex::decode(share["identifier"].as_str().ok_or(
            PyErr::new::<pyo3::exceptions::PyValueError, _>("Missing identifier")
        )?).map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("ID hex decode failed: {}", e)))?;

        let id = Identifier::deserialize(&id_bytes.try_into().map_err(|_|
            PyErr::new::<pyo3::exceptions::PyValueError, _>("Invalid identifier length"))?)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("ID deserialization failed: {}", e)))?;

        let signing_share_bytes = hex::decode(share["signing_share"].as_str().ok_or(
            PyErr::new::<pyo3::exceptions::PyValueError, _>("Missing signing share")
        )?).map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Share hex decode failed: {}", e)))?;

        let signing_share = SigningShare::deserialize(
            &signing_share_bytes.try_into().map_err(|_|
                PyErr::new::<pyo3::exceptions::PyValueError, _>("Invalid signing share length"))?)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Share deserialization failed: {}", e)))?;

        let verifying_share = VerifyingShare::from(&signing_share);
        let key_package = KeyPackage::new(
            id,
            signing_share,
            verifying_share,
            pubkey_package.verifying_key().clone(),
        ).map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Key package creation failed: {}", e)))?;

        let (nonces, commitments) = round1::commit(
            &key_package.signing_share(),
            &mut thread_rng()
        );
        nonces_map.insert(id, nonces);
        commitments_map.insert(id, commitments);
        key_packages.push(key_package);
    }

    // Create and verify signature
    let signing_package = SigningPackage::new(
        commitments_map.values().cloned().collect(),
        message.as_bytes()
    );
    let mut signatures = BTreeMap::new();

    for key_package in key_packages {
        let signature = round2::sign(
            &signing_package,
            &nonces_map[&key_package.identifier()],
            &key_package,
        ).map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Signing failed: {}", e)))?;

        signatures.insert(key_package.identifier(), signature);
    }

    let signature = frost_secp256k1::aggregate(&signing_package, &signatures, &pubkey_package)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Aggregation failed: {}", e)))?;

    // Verify before returning
    pubkey_package.verifying_key()
        .verify(message.as_bytes(), &signature)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Verification failed: {}", e)))?;

    Ok(hex::encode(signature.serialize()))
}

/// Verify a signature
#[pyfunction]
fn verify_signature(message: String, signature_hex: String, public_key_hex: String) -> PyResult<bool> {
    let signature_bytes: [u8; 64] = hex::decode(signature_hex)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Signature hex decode failed: {}", e)))?
        .try_into()
        .map_err(|_| PyErr::new::<pyo3::exceptions::PyValueError, _>("Invalid signature length"))?;

    let public_key_bytes: [u8; 33] = hex::decode(public_key_hex)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Public key hex decode failed: {}", e)))?
        .try_into()
        .map_err(|_| PyErr::new::<pyo3::exceptions::PyValueError, _>("Invalid public key length"))?;

    let signature = Signature::from_bytes(&signature_bytes)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Signature parse failed: {}", e)))?;

    let public_key = VerifyingKey::from_bytes(&public_key_bytes)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Public key parse failed: {}", e)))?;

    Ok(public_key.verify(message.as_bytes(), &signature).is_ok())
}

/// Python module
#[pymodule]
fn frost(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(generate_keys, m)?)?;
    m.add_function(wrap_pyfunction!(threshold_sign, m)?)?;
    m.add_function(wrap_pyfunction!(verify_signature, m)?)?;
    Ok(())
}