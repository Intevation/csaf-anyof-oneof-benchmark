// SPDX-License-Identifier: Apache-2.0
use std::{
    env,
    error::Error,
    fs,
    path::{Path, PathBuf},
    process::ExitCode,
};

use serde_json::Value;

fn read_json(path: &Path) -> Result<Value, Box<dyn Error>> {
    Ok(serde_json::from_str(&fs::read_to_string(path)?)?)
}

fn main() -> Result<ExitCode, Box<dyn Error>> {
    let fixtures = env::args_os()
        .nth(1)
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("../fixtures/support"));
    let cases = read_json(&fixtures.join("cases.json"))?;
    let mut failures = 0;
    for keyword in ["anyOf", "oneOf"] {
        for case in cases.as_array().ok_or("cases.json is not an array")? {
            let name = case["schema"].as_str().ok_or("missing schema")?;
            let schema = read_json(&fixtures.join(format!("{name}.{keyword}.json")))?;
            let validator = jsonschema::validator_for(&schema)?;
            let actual = validator.is_valid(&case["instance"]);
            let expected = case[keyword].as_bool().ok_or("missing expectation")?;
            let ok = actual == expected;
            if !ok {
                failures += 1;
            }
            println!(
                "{} rust-jsonschema {keyword} {name}: {} (expected {expected}, got {actual})",
                if ok { "PASS" } else { "FAIL" },
                case["name"].as_str().unwrap_or("?"),
            );
        }
    }
    Ok(if failures == 0 { ExitCode::SUCCESS } else { ExitCode::FAILURE })
}
