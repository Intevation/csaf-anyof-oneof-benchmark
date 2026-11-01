# anyOf / oneOf comparison

Tested libraries: Rust `jsonschema` 0.51.0, Go `santhosh-tekuri/jsonschema` 6.0.3,
Kotlin `networknt` 3.0.6 and `json-sKema` 0.28.0, Python `jsonschema` 4.26.0,
and Sourcemeta JSON Schema CLI 16.9.0.

- `make support`: support tests from `fixtures/support/`.
- `make bench-docs`: generate schemas in `bench/schema/` and documents in `bench/docs/`.
- `make bench`: write CSV files to `bench/results/` and print timing tables.
- `make bench-sourcemeta`: run only the CLI benchmarks with `jsonschema` on `PATH`.

Inputs: [CSAF schema](https://github.com/oasis-tcs/csaf/blob/e0da5a98af185acce66e1ef4c2686c8f215703b2/csaf_2.1/json_schema/csaf.json)
and [Cisco document](https://github.com/oasis-tcs/csaf/blob/e0da5a98af185acce66e1ef4c2686c8f215703b2/csaf_2.1/examples/csaf/cisco-sa-20180328-smi2.json).
The documents are modified with synthetic involvement data for benchmarking.

## Batches

Each batch has `eid`, `egid` and seeded random `mixed` variants.

Combining 100_000 actions with 40_000 references (the maximum recommended value
for each action) would produce a formatted JSON file exceeding 100 GB. We
therefore test the recommended upper limits separately. 100_000 total references
distributed across different action counts, including 100_000 actions, plus an
explicit single-action batch with 40_000 references.

| Batch | Actions | References per action | Total references |
|---|--:|--:|--:|
| `1action-40000refs` | 1 | 40_000 | 40_000 |
| `1action` | 1 | 100_000 | 100_000 |
| `10actions` | 10 | 10_000 | 100_000 |
| `100actions` | 100 | 1_000 | 100_000 |
| `1000actions` | 1_000 | 100 | 100_000 |
| `10000actions` | 10_000 | 10 | 100_000 |
| `100000actions` | 100_000 | 1 | 100_000 |

The schemas differ only in `entity_refs_t/items`: `anyOf` versus `oneOf`.
Both `acting_entity_refs` and `receiving_entity_refs` use that type. The default
is `acting_entity_refs`. Generate the receiving variant with:

```sh
make bench-docs DOC_FLAGS=--receiving
make bench
```

## Results

- `anyOf` is generally faster than `oneOf` for EGID and mixed references in
  Python, Rust and Go.
- For EID-only lists, Python and Rust perform about equally with either keyword.
- The JVM libraries perform about equally with `anyOf` and `oneOf`.

The values below omit the Python values for 100_000-action, as the
projected time to run those benchmarks would haven taken more than 24 hours.

Times are milliseconds per document, excluding schema compilation.

## JSON file read + parse + validate

| library | document | anyOf ms | oneOf ms | oneOf/anyOf |
|---|---|--:|--:|--:|
| json-sKema | csaf-100000actions-egid | 627.1 | 648.0 | 1.03 |
| json-sKema | csaf-100000actions-eid | 641.3 | 636.2 | 0.99 |
| json-sKema | csaf-100000actions-mixed | 599.5 | 620.4 | 1.03 |
| json-sKema | csaf-10000actions-egid | 137.0 | 137.9 | 1.01 |
| json-sKema | csaf-10000actions-eid | 136.0 | 138.6 | 1.02 |
| json-sKema | csaf-10000actions-mixed | 137.5 | 138.2 | 1.00 |
| json-sKema | csaf-1000actions-egid | 96.2 | 99.8 | 1.04 |
| json-sKema | csaf-1000actions-eid | 95.6 | 97.8 | 1.02 |
| json-sKema | csaf-1000actions-mixed | 97.8 | 99.4 | 1.02 |
| json-sKema | csaf-100actions-egid | 92.2 | 92.6 | 1.00 |
| json-sKema | csaf-100actions-eid | 90.8 | 91.5 | 1.01 |
| json-sKema | csaf-100actions-mixed | 93.6 | 94.9 | 1.01 |
| json-sKema | csaf-10actions-egid | 91.8 | 92.0 | 1.00 |
| json-sKema | csaf-10actions-eid | 90.3 | 90.5 | 1.00 |
| json-sKema | csaf-10actions-mixed | 94.2 | 93.3 | 0.99 |
| json-sKema | csaf-1action-40000refs-egid | 37.2 | 37.5 | 1.01 |
| json-sKema | csaf-1action-40000refs-eid | 36.9 | 37.0 | 1.00 |
| json-sKema | csaf-1action-40000refs-mixed | 37.8 | 38.1 | 1.01 |
| json-sKema | csaf-1action-egid | 92.9 | 92.2 | 0.99 |
| json-sKema | csaf-1action-eid | 90.9 | 91.9 | 1.01 |
| json-sKema | csaf-1action-mixed | 95.2 | 98.2 | 1.03 |
| networknt | csaf-100000actions-egid | 256.7 | 258.2 | 1.01 |
| networknt | csaf-100000actions-eid | 239.4 | 235.1 | 0.98 |
| networknt | csaf-100000actions-mixed | 242.6 | 232.5 | 0.96 |
| networknt | csaf-10000actions-egid | 64.5 | 63.3 | 0.98 |
| networknt | csaf-10000actions-eid | 64.3 | 64.0 | 0.99 |
| networknt | csaf-10000actions-mixed | 66.4 | 65.1 | 0.98 |
| networknt | csaf-1000actions-egid | 48.3 | 46.7 | 0.97 |
| networknt | csaf-1000actions-eid | 48.1 | 47.3 | 0.98 |
| networknt | csaf-1000actions-mixed | 51.0 | 49.7 | 0.97 |
| networknt | csaf-100actions-egid | 46.3 | 44.4 | 0.96 |
| networknt | csaf-100actions-eid | 46.0 | 44.7 | 0.97 |
| networknt | csaf-100actions-mixed | 48.8 | 47.8 | 0.98 |
| networknt | csaf-10actions-egid | 45.2 | 43.7 | 0.97 |
| networknt | csaf-10actions-eid | 45.0 | 43.8 | 0.97 |
| networknt | csaf-10actions-mixed | 48.0 | 46.6 | 0.97 |
| networknt | csaf-1action-40000refs-egid | 17.6 | 17.2 | 0.98 |
| networknt | csaf-1action-40000refs-eid | 17.7 | 17.3 | 0.98 |
| networknt | csaf-1action-40000refs-mixed | 18.8 | 18.5 | 0.98 |
| networknt | csaf-1action-egid | 43.8 | 42.3 | 0.97 |
| networknt | csaf-1action-eid | 43.7 | 42.5 | 0.97 |
| networknt | csaf-1action-mixed | 47.0 | 45.9 | 0.98 |
| python-jsonschema | csaf-10000actions-egid | 25462.4 | 26447.7 | 1.04 |
| python-jsonschema | csaf-10000actions-eid | 26560.2 | 26648.8 | 1.00 |
| python-jsonschema | csaf-10000actions-mixed | 25701.2 | 26291.3 | 1.02 |
| python-jsonschema | csaf-1000actions-egid | 1262.5 | 2220.3 | 1.76 |
| python-jsonschema | csaf-1000actions-eid | 2335.8 | 2305.2 | 0.99 |
| python-jsonschema | csaf-1000actions-mixed | 1796.6 | 2288.5 | 1.27 |
| python-jsonschema | csaf-100actions-egid | 1141.5 | 2091.8 | 1.83 |
| python-jsonschema | csaf-100actions-eid | 2185.4 | 2176.2 | 1.00 |
| python-jsonschema | csaf-100actions-mixed | 1681.1 | 2139.7 | 1.27 |
| python-jsonschema | csaf-10actions-egid | 2408.8 | 3361.5 | 1.40 |
| python-jsonschema | csaf-10actions-eid | 3464.3 | 3436.8 | 0.99 |
| python-jsonschema | csaf-10actions-mixed | 2937.6 | 3417.2 | 1.16 |
| python-jsonschema | csaf-1action-40000refs-egid | 2646.8 | 3023.1 | 1.14 |
| python-jsonschema | csaf-1action-40000refs-eid | 3062.9 | 3064.2 | 1.00 |
| python-jsonschema | csaf-1action-40000refs-mixed | 2865.2 | 3029.2 | 1.06 |
| python-jsonschema | csaf-1action-egid | 14786.8 | 15738.9 | 1.06 |
| python-jsonschema | csaf-1action-eid | 15824.2 | 15841.7 | 1.00 |
| python-jsonschema | csaf-1action-mixed | 15299.8 | 15817.9 | 1.03 |
| rust-jsonschema | csaf-100000actions-egid | 63.7 | 65.9 | 1.03 |
| rust-jsonschema | csaf-100000actions-eid | 66.0 | 67.0 | 1.01 |
| rust-jsonschema | csaf-100000actions-mixed | 64.7 | 65.8 | 1.02 |
| rust-jsonschema | csaf-10000actions-egid | 14.0 | 15.9 | 1.14 |
| rust-jsonschema | csaf-10000actions-eid | 15.9 | 15.9 | 1.00 |
| rust-jsonschema | csaf-10000actions-mixed | 16.6 | 17.4 | 1.05 |
| rust-jsonschema | csaf-1000actions-egid | 7.7 | 9.7 | 1.25 |
| rust-jsonschema | csaf-1000actions-eid | 9.6 | 9.7 | 1.01 |
| rust-jsonschema | csaf-1000actions-mixed | 9.4 | 10.3 | 1.10 |
| rust-jsonschema | csaf-100actions-egid | 6.7 | 8.4 | 1.24 |
| rust-jsonschema | csaf-100actions-eid | 8.4 | 8.5 | 1.01 |
| rust-jsonschema | csaf-100actions-mixed | 8.4 | 9.1 | 1.09 |
| rust-jsonschema | csaf-10actions-egid | 6.5 | 8.2 | 1.26 |
| rust-jsonschema | csaf-10actions-eid | 8.1 | 8.2 | 1.01 |
| rust-jsonschema | csaf-10actions-mixed | 7.9 | 8.8 | 1.11 |
| rust-jsonschema | csaf-1action-40000refs-egid | 2.7 | 3.4 | 1.24 |
| rust-jsonschema | csaf-1action-40000refs-eid | 3.4 | 3.3 | 0.98 |
| rust-jsonschema | csaf-1action-40000refs-mixed | 3.3 | 3.6 | 1.11 |
| rust-jsonschema | csaf-1action-egid | 6.7 | 8.4 | 1.26 |
| rust-jsonschema | csaf-1action-eid | 8.1 | 8.2 | 1.01 |
| rust-jsonschema | csaf-1action-mixed | 8.0 | 8.9 | 1.11 |
| santhosh-tekuri | csaf-100000actions-egid | 392.3 | 420.1 | 1.07 |
| santhosh-tekuri | csaf-100000actions-eid | 426.4 | 420.4 | 0.99 |
| santhosh-tekuri | csaf-100000actions-mixed | 400.2 | 416.7 | 1.04 |
| santhosh-tekuri | csaf-10000actions-egid | 110.4 | 162.5 | 1.47 |
| santhosh-tekuri | csaf-10000actions-eid | 166.4 | 159.3 | 0.96 |
| santhosh-tekuri | csaf-10000actions-mixed | 138.2 | 158.1 | 1.14 |
| santhosh-tekuri | csaf-1000actions-egid | 88.5 | 119.0 | 1.34 |
| santhosh-tekuri | csaf-1000actions-eid | 137.4 | 130.3 | 0.95 |
| santhosh-tekuri | csaf-1000actions-mixed | 110.8 | 153.7 | 1.39 |
| santhosh-tekuri | csaf-100actions-egid | 79.7 | 127.7 | 1.60 |
| santhosh-tekuri | csaf-100actions-eid | 167.1 | 142.6 | 0.85 |
| santhosh-tekuri | csaf-100actions-mixed | 136.7 | 165.3 | 1.21 |
| santhosh-tekuri | csaf-10actions-egid | 97.2 | 134.4 | 1.38 |
| santhosh-tekuri | csaf-10actions-eid | 171.8 | 171.3 | 1.00 |
| santhosh-tekuri | csaf-10actions-mixed | 139.3 | 163.5 | 1.17 |
| santhosh-tekuri | csaf-1action-40000refs-egid | 45.2 | 76.7 | 1.70 |
| santhosh-tekuri | csaf-1action-40000refs-eid | 68.4 | 71.6 | 1.05 |
| santhosh-tekuri | csaf-1action-40000refs-mixed | 54.3 | 78.0 | 1.44 |
| santhosh-tekuri | csaf-1action-egid | 87.6 | 140.2 | 1.60 |
| santhosh-tekuri | csaf-1action-eid | 157.1 | 171.3 | 1.09 |
| santhosh-tekuri | csaf-1action-mixed | 120.8 | 167.8 | 1.39 |

## Validate only

| library | document | anyOf ms | oneOf ms | oneOf/anyOf |
|---|---|--:|--:|--:|
| json-sKema | csaf-100000actions-egid | 567.0 | 573.5 | 1.01 |
| json-sKema | csaf-100000actions-eid | 579.4 | 556.8 | 0.96 |
| json-sKema | csaf-100000actions-mixed | 539.2 | 551.2 | 1.02 |
| json-sKema | csaf-10000actions-egid | 124.8 | 125.6 | 1.01 |
| json-sKema | csaf-10000actions-eid | 123.9 | 125.2 | 1.01 |
| json-sKema | csaf-10000actions-mixed | 124.9 | 125.3 | 1.00 |
| json-sKema | csaf-1000actions-egid | 89.1 | 92.6 | 1.04 |
| json-sKema | csaf-1000actions-eid | 88.7 | 90.9 | 1.02 |
| json-sKema | csaf-1000actions-mixed | 90.4 | 91.7 | 1.01 |
| json-sKema | csaf-100actions-egid | 85.6 | 86.1 | 1.01 |
| json-sKema | csaf-100actions-eid | 84.4 | 85.2 | 1.01 |
| json-sKema | csaf-100actions-mixed | 86.7 | 88.0 | 1.01 |
| json-sKema | csaf-10actions-egid | 85.3 | 85.5 | 1.00 |
| json-sKema | csaf-10actions-eid | 84.0 | 84.2 | 1.00 |
| json-sKema | csaf-10actions-mixed | 87.3 | 86.4 | 0.99 |
| json-sKema | csaf-1action-40000refs-egid | 34.4 | 34.7 | 1.01 |
| json-sKema | csaf-1action-40000refs-eid | 34.1 | 34.2 | 1.00 |
| json-sKema | csaf-1action-40000refs-mixed | 34.8 | 35.0 | 1.01 |
| json-sKema | csaf-1action-egid | 86.3 | 85.5 | 0.99 |
| json-sKema | csaf-1action-eid | 84.4 | 84.8 | 1.01 |
| json-sKema | csaf-1action-mixed | 88.2 | 90.6 | 1.03 |
| networknt | csaf-100000actions-egid | 218.7 | 220.6 | 1.01 |
| networknt | csaf-100000actions-eid | 203.3 | 199.4 | 0.98 |
| networknt | csaf-100000actions-mixed | 199.3 | 196.6 | 0.99 |
| networknt | csaf-10000actions-egid | 57.5 | 56.4 | 0.98 |
| networknt | csaf-10000actions-eid | 57.5 | 57.2 | 0.99 |
| networknt | csaf-10000actions-mixed | 59.4 | 57.5 | 0.97 |
| networknt | csaf-1000actions-egid | 44.2 | 42.7 | 0.97 |
| networknt | csaf-1000actions-eid | 44.2 | 43.3 | 0.98 |
| networknt | csaf-1000actions-mixed | 46.7 | 45.3 | 0.97 |
| networknt | csaf-100actions-egid | 42.8 | 40.8 | 0.95 |
| networknt | csaf-100actions-eid | 42.6 | 41.3 | 0.97 |
| networknt | csaf-100actions-mixed | 44.8 | 43.8 | 0.98 |
| networknt | csaf-10actions-egid | 41.7 | 40.2 | 0.97 |
| networknt | csaf-10actions-eid | 41.6 | 40.4 | 0.97 |
| networknt | csaf-10actions-mixed | 44.0 | 42.7 | 0.97 |
| networknt | csaf-1action-40000refs-egid | 16.0 | 15.6 | 0.97 |
| networknt | csaf-1action-40000refs-eid | 16.1 | 15.7 | 0.98 |
| networknt | csaf-1action-40000refs-mixed | 17.0 | 16.7 | 0.98 |
| networknt | csaf-1action-egid | 40.3 | 38.9 | 0.96 |
| networknt | csaf-1action-eid | 40.3 | 39.1 | 0.97 |
| networknt | csaf-1action-mixed | 43.1 | 41.9 | 0.97 |
| python-jsonschema | csaf-10000actions-egid | 25449.6 | 26434.2 | 1.04 |
| python-jsonschema | csaf-10000actions-eid | 26549.6 | 26638.1 | 1.00 |
| python-jsonschema | csaf-10000actions-mixed | 25689.7 | 26279.9 | 1.02 |
| python-jsonschema | csaf-1000actions-egid | 1256.7 | 2214.6 | 1.76 |
| python-jsonschema | csaf-1000actions-eid | 2330.2 | 2299.5 | 0.99 |
| python-jsonschema | csaf-1000actions-mixed | 1790.4 | 2282.2 | 1.27 |
| python-jsonschema | csaf-100actions-egid | 1137.1 | 2087.5 | 1.84 |
| python-jsonschema | csaf-100actions-eid | 2181.1 | 2171.8 | 1.00 |
| python-jsonschema | csaf-100actions-mixed | 1676.3 | 2134.9 | 1.27 |
| python-jsonschema | csaf-10actions-egid | 2404.4 | 3357.1 | 1.40 |
| python-jsonschema | csaf-10actions-eid | 3460.1 | 3432.6 | 0.99 |
| python-jsonschema | csaf-10actions-mixed | 2933.1 | 3412.6 | 1.16 |
| python-jsonschema | csaf-1action-40000refs-egid | 2644.7 | 3021.1 | 1.14 |
| python-jsonschema | csaf-1action-40000refs-eid | 3060.8 | 3062.2 | 1.00 |
| python-jsonschema | csaf-1action-40000refs-mixed | 2863.0 | 3027.0 | 1.06 |
| python-jsonschema | csaf-1action-egid | 14782.9 | 15734.9 | 1.06 |
| python-jsonschema | csaf-1action-eid | 15818.7 | 15837.7 | 1.00 |
| python-jsonschema | csaf-1action-mixed | 15295.5 | 15813.7 | 1.03 |
| rust-jsonschema | csaf-100000actions-egid | 25.2 | 27.5 | 1.09 |
| rust-jsonschema | csaf-100000actions-eid | 27.1 | 27.8 | 1.03 |
| rust-jsonschema | csaf-100000actions-mixed | 26.4 | 27.7 | 1.05 |
| rust-jsonschema | csaf-10000actions-egid | 6.8 | 8.7 | 1.28 |
| rust-jsonschema | csaf-10000actions-eid | 8.5 | 8.6 | 1.01 |
| rust-jsonschema | csaf-10000actions-mixed | 9.4 | 10.1 | 1.08 |
| rust-jsonschema | csaf-1000actions-egid | 3.7 | 5.6 | 1.51 |
| rust-jsonschema | csaf-1000actions-eid | 5.5 | 5.6 | 1.02 |
| rust-jsonschema | csaf-1000actions-mixed | 5.3 | 6.2 | 1.17 |
| rust-jsonschema | csaf-100actions-egid | 3.3 | 5.0 | 1.53 |
| rust-jsonschema | csaf-100actions-eid | 4.9 | 5.0 | 1.01 |
| rust-jsonschema | csaf-100actions-mixed | 4.8 | 5.7 | 1.17 |
| rust-jsonschema | csaf-10actions-egid | 3.1 | 4.8 | 1.55 |
| rust-jsonschema | csaf-10actions-eid | 4.7 | 4.7 | 1.01 |
| rust-jsonschema | csaf-10actions-mixed | 4.5 | 5.4 | 1.19 |
| rust-jsonschema | csaf-1action-40000refs-egid | 1.3 | 2.0 | 1.56 |
| rust-jsonschema | csaf-1action-40000refs-eid | 2.0 | 1.9 | 0.97 |
| rust-jsonschema | csaf-1action-40000refs-mixed | 1.8 | 2.2 | 1.20 |
| rust-jsonschema | csaf-1action-egid | 3.3 | 5.0 | 1.52 |
| rust-jsonschema | csaf-1action-eid | 4.8 | 4.9 | 1.01 |
| rust-jsonschema | csaf-1action-mixed | 4.7 | 5.5 | 1.18 |
| santhosh-tekuri | csaf-100000actions-egid | 224.0 | 258.1 | 1.15 |
| santhosh-tekuri | csaf-100000actions-eid | 264.6 | 264.9 | 1.00 |
| santhosh-tekuri | csaf-100000actions-mixed | 242.1 | 260.1 | 1.07 |
| santhosh-tekuri | csaf-10000actions-egid | 76.2 | 119.3 | 1.56 |
| santhosh-tekuri | csaf-10000actions-eid | 125.3 | 125.8 | 1.00 |
| santhosh-tekuri | csaf-10000actions-mixed | 102.7 | 124.0 | 1.21 |
| santhosh-tekuri | csaf-1000actions-egid | 67.6 | 99.0 | 1.46 |
| santhosh-tekuri | csaf-1000actions-eid | 114.5 | 110.2 | 0.96 |
| santhosh-tekuri | csaf-1000actions-mixed | 90.7 | 134.2 | 1.48 |
| santhosh-tekuri | csaf-100actions-egid | 62.4 | 110.9 | 1.78 |
| santhosh-tekuri | csaf-100actions-eid | 140.6 | 122.9 | 0.87 |
| santhosh-tekuri | csaf-100actions-mixed | 113.0 | 146.3 | 1.29 |
| santhosh-tekuri | csaf-10actions-egid | 72.0 | 116.4 | 1.62 |
| santhosh-tekuri | csaf-10actions-eid | 155.8 | 135.7 | 0.87 |
| santhosh-tekuri | csaf-10actions-mixed | 119.2 | 143.6 | 1.20 |
| santhosh-tekuri | csaf-1action-40000refs-egid | 35.2 | 61.3 | 1.74 |
| santhosh-tekuri | csaf-1action-40000refs-eid | 60.3 | 58.8 | 0.98 |
| santhosh-tekuri | csaf-1action-40000refs-mixed | 44.6 | 62.5 | 1.40 |
| santhosh-tekuri | csaf-1action-egid | 67.7 | 116.7 | 1.72 |
| santhosh-tekuri | csaf-1action-eid | 133.7 | 147.7 | 1.11 |
| santhosh-tekuri | csaf-1action-mixed | 97.9 | 146.4 | 1.50 |
| sourcemeta-cli | csaf-100000actions-egid | 38992.2 | 39594.3 | 1.02 |
| sourcemeta-cli | csaf-100000actions-eid | 39617.3 | 40668.0 | 1.03 |
| sourcemeta-cli | csaf-100000actions-mixed | 50022.2 | 50829.7 | 1.02 |
| sourcemeta-cli | csaf-10000actions-egid | 373.3 | 376.3 | 1.01 |
| sourcemeta-cli | csaf-10000actions-eid | 374.1 | 373.6 | 1.00 |
| sourcemeta-cli | csaf-10000actions-mixed | 126.9 | 127.4 | 1.00 |
| sourcemeta-cli | csaf-1000actions-egid | 31.7 | 33.8 | 1.07 |
| sourcemeta-cli | csaf-1000actions-eid | 34.0 | 33.8 | 0.99 |
| sourcemeta-cli | csaf-1000actions-mixed | 25.7 | 27.0 | 1.05 |
| sourcemeta-cli | csaf-100actions-egid | 231.4 | 234.2 | 1.01 |
| sourcemeta-cli | csaf-100actions-eid | 235.2 | 235.1 | 1.00 |
| sourcemeta-cli | csaf-100actions-mixed | 162.8 | 164.4 | 1.01 |
| sourcemeta-cli | csaf-10actions-egid | 2224.3 | 2228.2 | 1.00 |
| sourcemeta-cli | csaf-10actions-eid | 2221.4 | 2219.1 | 1.00 |
| sourcemeta-cli | csaf-10actions-mixed | 2298.2 | 2295.2 | 1.00 |
| sourcemeta-cli | csaf-1action-40000refs-egid | 3528.1 | 3539.1 | 1.00 |
| sourcemeta-cli | csaf-1action-40000refs-eid | 3515.4 | 3525.2 | 1.00 |
| sourcemeta-cli | csaf-1action-40000refs-mixed | 4151.8 | 4160.0 | 1.00 |
| sourcemeta-cli | csaf-1action-egid | 21991.7 | 22000.3 | 1.00 |
| sourcemeta-cli | csaf-1action-eid | 21990.9 | 21959.9 | 1.00 |
| sourcemeta-cli | csaf-1action-mixed | 26613.1 | 26587.5 | 1.00 |

## SSVC namespace-pattern regression notes

Sourcemeta JSON Schema CLI 16.9.0 fails when compiling the SSVC
pattern introduced by [commit `44cc49e`](https://github.com/CERTCC/SSVC/commit/44cc49e3f7316a8ba58fefb4de81ad582e0bfb0c).
We therefore use a local copy of the [SSVC schema from `7782fb1`](https://github.com/CERTCC/SSVC/blob/7782fb1a44841b175c3b4610d4d583a3b5d1343b/data/schema/v2/SelectionList_2_0_0.schema.json).

Without that local SSVC override, this command fetches the external schema:

```sh
jsonschema validate bench/schema/csaf.anyOf.json bench/docs/csaf-1action-40000refs-egid.json \
  --resolve bench/metaschemas --http
```

```text
error: Invalid regular expression
  at location "/$defs/https:~1~1certcc.github.io~1SSVC~1data~1schema~1v2~1SelectionList_2_0_0.schema.json/$defs/Selection/properties/namespace/pattern"
  at base uri https://certcc.github.io/SSVC/data/schema/v2/SelectionList_2_0_0.schema.json
```
