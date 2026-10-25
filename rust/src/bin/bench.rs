// SPDX-License-Identifier: Apache-2.0
use std::{
    env,
    error::Error,
    fs,
    path::{Path, PathBuf},
    time::Instant,
};

use serde_json::Value;

fn read_json(path: &Path) -> Result<Value, Box<dyn Error>> {
    Ok(serde_json::from_str(&fs::read_to_string(path)?)?)
}

fn main() -> Result<(), Box<dyn Error>> {
    let bench = PathBuf::from(env::args().nth(1).ok_or("BENCH_DIR")?);
    let reps: usize = env::args().nth(2).ok_or("REPS")?.parse()?;
    let mut validators = Vec::new();
    for keyword in ["anyOf", "oneOf"] {
        let schema = read_json(&bench.join(format!("schema/csaf.{keyword}.json")))?;
        let validator = jsonschema::validator_for(&schema)?;
        validators.push((keyword, validator));
    }
    let mut docs: Vec<PathBuf> = fs::read_dir(bench.join("docs"))?
        .map(|e| e.map(|e| e.path()))
        .collect::<Result<_, _>>()?;
    docs.sort();
    for doc in docs {
        let stem = doc.file_stem().unwrap().to_string_lossy().into_owned();
        for rep in 0..=reps {
            let order: Vec<usize> = if rep % 2 == 0 { vec![0, 1] } else { vec![1, 0] };
            for i in order {
                let (keyword, validator) = &validators[i];
                let t0 = Instant::now();
                let data = read_json(&doc)?;
                let t1 = Instant::now();
                let valid = validator.is_valid(&data);
                let t2 = Instant::now();
                println!(
                    "rust-jsonschema,{keyword},{stem},{rep},{:.3},{:.3},{valid}",
                    (t1 - t0).as_secs_f64() * 1e3,
                    (t2 - t1).as_secs_f64() * 1e3
                );
            }
        }
    }
    Ok(())
}
