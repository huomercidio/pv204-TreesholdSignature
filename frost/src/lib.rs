use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use pyo3::exceptions::PyValueError;

use frost_secp256k1::{
    keys::{generate_with_dealer},
    Identifier,
    rand_core::OsRng,
};
use std::collections::BTreeMap;
use std::convert::TryFrom;
use serde_json::json;
use hex;

#[pyfunction]
fn generate_keys_py(n: usize, t: usize) -> PyResult<String> {
    if t < 2 || t > n {
        return Err(PyValueError::new_err("min_signers must be at least 2 and not larger than max_signers"));
    }

    let identifiers: Vec<Identifier> = (1..=n)
        .map(|i| Identifier::try_from(i as u16).unwrap())
        .collect();

    let (secret_shares, pubkey_package) =
        generate_with_dealer(t as u16, n as u16, &mut OsRng)
            .map_err(|e| PyValueError::new_err(format!("Key generation failed: {e}")))?;

    let shares = identifiers.iter().map(|id| {
        let share = secret_shares.get(id).unwrap();
        json!({
            "participant_id": hex::encode(id.serialize()),
            "share": hex::encode(share.secret().to_bytes()),
        })
    }).collect::<Vec<_>>();

    let pubkey_bytes = pubkey_package.group_public().to_bytes();
    let verifying_key_bytes = pubkey_package.group_public().to_bytes();

    let result = json!({
        "shares": shares,
        "group_public_key": hex::encode(pubkey_bytes),
        "group_verifying_key": hex::encode(verifying_key_bytes),
    });

    Ok(result.to_string())
}

#[pymodule]
fn thresholdfrost(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(generate_keys_py, m)?)?;
    Ok(())
}
