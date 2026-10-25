# anyOf / oneOf support test (step 1)

Tested libraries are Rust `jsonschema` 0.51.0, Go `santhosh-tekuri/jsonschema` 6.0.3,
Kotlin `networknt` 3.0.6 and `json-sKema` 0.28.0, Python `jsonschema` 4.26.0.

Run all with `make support`.

Run all commands from the repository root. Support fixtures are in
[`fixtures/support/`](fixtures/support/). each language target passes this
directory relative to its own working directory.

Benchmark inputs are [`bench/base/csaf.json`](bench/base/csaf.json) and
[`bench/base/cisco-sa-20180328-smi2.json`](bench/base/cisco-sa-20180328-smi2.json).
The schema matches [CSAF 2.1 CSD03](https://docs.oasis-open.org/csaf/csaf/v2.1/csd03/schema/csaf.json).
Generated schemas are in [`bench/schema/`](bench/schema/), generated documents
in [`bench/docs/`](bench/docs/). `make bench` creates `bench/results/` before
writing CSV files. these local measurements are ignored by Git.

The Cisco example in `bench/base/` retains its original publisher metadata.
The generated documents identify Intevation GmbH as publisher, category `other`,
and start their own revision history describing the Cisco source and the
synthetic changes. CSAF has no co-publisher property. adding one would violate
the schema. See [Publisher](https://docs.oasis-open.org/csaf/csaf/v2.1/csd03/csaf-v2.1-csd03.html#32210-document-property---publisher-)
and [Revision History](https://docs.oasis-open.org/csaf/csaf/v2.1/csd03/csaf-v2.1-csd03.html#322146-document-property---tracking---revision-history-).

# anyOf vs oneOf timing (step 2)

`make bench-docs` (re)creates schemas and documents, `make bench` runs the timing
tests, writes `bench/results/*.csv` and prints the summary tables shown below.

All times are medians per complete document.

Each test document contains 50_000 references in `acting_entity_refs`:

- `1action`, `10actions`, `100actions`: the same total number of references is
  split evenly across the actions. This tests whether one long list behaves
  differently from several shorter lists.
- `eid`, `egid`, `mixed`: references use only `EID-`, only `EGID-`, or a
  roughly equal random mix of both prefixes.

The schema checks EGID before EID. With `anyOf`, a validator may stop after a
matching EGID branch. For EID it must also check the second branch. With `oneOf`,
it must establish that exactly one branch matches. The prefix variants test how
this affects each library, while `mixed` covers a case between the two extremes.

# Results

- Python and Rust show a `oneOf` overhead for EGID and mixed references, but
  almost none for EID-only lists. This fits the possible early exit of `anyOf`.
- Python benefits strongly from splitting references across shorter lists.
- The JVM libraries show little difference. Go shows an overhead for EGID and
  mixed lists, but its individual measurements fluctuate substantially.

## JSON file read + parse + validate

| library | document | anyOf ms | oneOf ms | oneOf/anyOf |
|---|---|--:|--:|--:|
| json-sKema | csaf-100actions-egid | 49.1 | 49.1 | 1.00 |
| json-sKema | csaf-100actions-eid | 48.4 | 48.1 | 0.99 |
| json-sKema | csaf-100actions-mixed | 49.2 | 49.2 | 1.00 |
| json-sKema | csaf-10actions-egid | 47.7 | 47.1 | 0.99 |
| json-sKema | csaf-10actions-eid | 47.4 | 46.7 | 0.99 |
| json-sKema | csaf-10actions-mixed | 48.2 | 48.6 | 1.01 |
| json-sKema | csaf-1action-egid | 47.2 | 47.4 | 1.01 |
| json-sKema | csaf-1action-eid | 47.3 | 47.3 | 1.00 |
| json-sKema | csaf-1action-mixed | 48.8 | 48.7 | 1.00 |
| networknt | csaf-100actions-egid | 22.3 | 21.9 | 0.98 |
| networknt | csaf-100actions-eid | 21.8 | 21.5 | 0.99 |
| networknt | csaf-100actions-mixed | 23.1 | 23.0 | 1.00 |
| networknt | csaf-10actions-egid | 21.2 | 20.8 | 0.98 |
| networknt | csaf-10actions-eid | 21.2 | 21.1 | 0.99 |
| networknt | csaf-10actions-mixed | 22.7 | 22.2 | 0.98 |
| networknt | csaf-1action-egid | 20.7 | 20.1 | 0.97 |
| networknt | csaf-1action-eid | 21.0 | 20.2 | 0.96 |
| networknt | csaf-1action-mixed | 21.9 | 21.5 | 0.98 |
| python-jsonschema | csaf-100actions-egid | 553.6 | 1048.7 | 1.89 |
| python-jsonschema | csaf-100actions-eid | 1084.5 | 1087.5 | 1.00 |
| python-jsonschema | csaf-100actions-mixed | 827.7 | 1072.7 | 1.30 |
| python-jsonschema | csaf-10actions-egid | 869.4 | 1378.2 | 1.59 |
| python-jsonschema | csaf-10actions-eid | 1410.9 | 1414.4 | 1.00 |
| python-jsonschema | csaf-10actions-mixed | 1143.4 | 1392.2 | 1.22 |
| python-jsonschema | csaf-1action-egid | 3988.8 | 4484.6 | 1.12 |
| python-jsonschema | csaf-1action-eid | 4534.4 | 4527.3 | 1.00 |
| python-jsonschema | csaf-1action-mixed | 4275.2 | 4516.8 | 1.06 |
| rust-jsonschema | csaf-100actions-egid | 3.2 | 4.1 | 1.28 |
| rust-jsonschema | csaf-100actions-eid | 4.1 | 4.1 | 1.00 |
| rust-jsonschema | csaf-100actions-mixed | 4.0 | 4.4 | 1.11 |
| rust-jsonschema | csaf-10actions-egid | 3.0 | 3.9 | 1.29 |
| rust-jsonschema | csaf-10actions-eid | 3.8 | 3.8 | 1.00 |
| rust-jsonschema | csaf-10actions-mixed | 3.7 | 4.1 | 1.12 |
| rust-jsonschema | csaf-1action-egid | 3.1 | 3.9 | 1.27 |
| rust-jsonschema | csaf-1action-eid | 3.8 | 3.8 | 1.00 |
| rust-jsonschema | csaf-1action-mixed | 3.7 | 4.2 | 1.11 |
| santhosh-tekuri | csaf-100actions-egid | 55.1 | 92.8 | 1.68 |
| santhosh-tekuri | csaf-100actions-eid | 103.6 | 93.9 | 0.91 |
| santhosh-tekuri | csaf-100actions-mixed | 73.5 | 101.3 | 1.38 |
| santhosh-tekuri | csaf-10actions-egid | 53.4 | 77.8 | 1.46 |
| santhosh-tekuri | csaf-10actions-eid | 84.7 | 93.8 | 1.11 |
| santhosh-tekuri | csaf-10actions-mixed | 69.7 | 85.0 | 1.22 |
| santhosh-tekuri | csaf-1action-egid | 42.9 | 68.7 | 1.60 |
| santhosh-tekuri | csaf-1action-eid | 93.4 | 100.5 | 1.08 |
| santhosh-tekuri | csaf-1action-mixed | 79.4 | 97.2 | 1.22 |

## Validate only

| library | document | anyOf ms | oneOf ms | oneOf/anyOf |
|---|---|--:|--:|--:|
| json-sKema | csaf-100actions-egid | 46.2 | 45.9 | 0.99 |
| json-sKema | csaf-100actions-eid | 45.6 | 44.7 | 0.98 |
| json-sKema | csaf-100actions-mixed | 46.1 | 46.0 | 1.00 |
| json-sKema | csaf-10actions-egid | 44.8 | 44.1 | 0.99 |
| json-sKema | csaf-10actions-eid | 44.6 | 43.9 | 0.99 |
| json-sKema | csaf-10actions-mixed | 45.0 | 45.4 | 1.01 |
| json-sKema | csaf-1action-egid | 44.2 | 44.5 | 1.01 |
| json-sKema | csaf-1action-eid | 44.4 | 44.4 | 1.00 |
| json-sKema | csaf-1action-mixed | 45.7 | 45.6 | 1.00 |
| networknt | csaf-100actions-egid | 20.5 | 20.2 | 0.98 |
| networknt | csaf-100actions-eid | 20.3 | 20.0 | 0.99 |
| networknt | csaf-100actions-mixed | 21.3 | 21.1 | 0.99 |
| networknt | csaf-10actions-egid | 19.7 | 19.2 | 0.98 |
| networknt | csaf-10actions-eid | 19.7 | 19.5 | 0.99 |
| networknt | csaf-10actions-mixed | 20.9 | 20.4 | 0.98 |
| networknt | csaf-1action-egid | 19.2 | 18.6 | 0.97 |
| networknt | csaf-1action-eid | 19.5 | 18.7 | 0.96 |
| networknt | csaf-1action-mixed | 20.2 | 19.8 | 0.98 |
| python-jsonschema | csaf-100actions-egid | 551.6 | 1046.7 | 1.90 |
| python-jsonschema | csaf-100actions-eid | 1082.5 | 1085.5 | 1.00 |
| python-jsonschema | csaf-100actions-mixed | 825.4 | 1070.3 | 1.30 |
| python-jsonschema | csaf-10actions-egid | 867.4 | 1376.2 | 1.59 |
| python-jsonschema | csaf-10actions-eid | 1409.2 | 1412.5 | 1.00 |
| python-jsonschema | csaf-10actions-mixed | 1141.1 | 1389.9 | 1.22 |
| python-jsonschema | csaf-1action-egid | 3986.9 | 4482.8 | 1.12 |
| python-jsonschema | csaf-1action-eid | 4532.6 | 4525.4 | 1.00 |
| python-jsonschema | csaf-1action-mixed | 4273.1 | 4514.7 | 1.06 |
| rust-jsonschema | csaf-100actions-egid | 1.7 | 2.6 | 1.53 |
| rust-jsonschema | csaf-100actions-eid | 2.5 | 2.5 | 1.00 |
| rust-jsonschema | csaf-100actions-mixed | 2.4 | 2.9 | 1.18 |
| rust-jsonschema | csaf-10actions-egid | 1.5 | 2.4 | 1.57 |
| rust-jsonschema | csaf-10actions-eid | 2.3 | 2.3 | 1.00 |
| rust-jsonschema | csaf-10actions-mixed | 2.2 | 2.6 | 1.19 |
| rust-jsonschema | csaf-1action-egid | 1.6 | 2.4 | 1.52 |
| rust-jsonschema | csaf-1action-eid | 2.3 | 2.3 | 1.00 |
| rust-jsonschema | csaf-1action-mixed | 2.3 | 2.7 | 1.19 |
| santhosh-tekuri | csaf-100actions-egid | 45.8 | 81.2 | 1.77 |
| santhosh-tekuri | csaf-100actions-eid | 90.5 | 83.0 | 0.92 |
| santhosh-tekuri | csaf-100actions-mixed | 61.9 | 85.1 | 1.37 |
| santhosh-tekuri | csaf-10actions-egid | 40.0 | 66.9 | 1.67 |
| santhosh-tekuri | csaf-10actions-eid | 71.6 | 84.8 | 1.18 |
| santhosh-tekuri | csaf-10actions-mixed | 56.9 | 74.1 | 1.30 |
| santhosh-tekuri | csaf-1action-egid | 33.2 | 55.1 | 1.66 |
| santhosh-tekuri | csaf-1action-eid | 83.2 | 89.2 | 1.07 |
| santhosh-tekuri | csaf-1action-mixed | 67.4 | 82.5 | 1.22 |
