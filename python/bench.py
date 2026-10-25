# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 German Federal Office for Information Security (BSI) <https://www.bsi.bund.de>
# Software-Engineering: 2026 Intevation GmbH <https://intevation.de>

import functools
import json
import sys
import time
import urllib.request
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.protocols import Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

LIB = "python-jsonschema"


# The Registry uses fetch() to load external schemas referenced by $ref.
# Cache each URL for this process so later benchmark runs do not repeat downloads.
# https://python-jsonschema.readthedocs.io/en/stable/referencing/#automatically-retrieving-resources-over-http
@functools.cache
def fetch(uri: str) -> Resource:
    with urllib.request.urlopen(uri, timeout=30) as response:
        return Resource.from_contents(json.load(response), default_specification=DRAFT202012)


def main() -> None:
    bench_dir = Path(sys.argv[1])
    reps = int(sys.argv[2])

    validators: dict[str, Validator] = {}
    for keyword in ("anyOf", "oneOf"):
        schema_path = bench_dir / "schema" / f"csaf.{keyword}.json"
        schema = json.loads(schema_path.read_text())
        registry = Registry(retrieve=fetch)
        validators[keyword] = Draft202012Validator(schema, registry=registry)

    for doc_path in sorted((bench_dir / "docs").glob("*.json")):
        for rep in range(reps + 1):  # rep 0 is warm-up
            # Alternate which schema runs first so cache effects do not always favor the same variant.
            order = ("anyOf", "oneOf")
            if rep % 2 == 1:
                order = ("oneOf", "anyOf")

            for keyword in order:
                load_start = time.perf_counter()
                data = json.loads(doc_path.read_text(encoding="utf-8"))
                validate_start = time.perf_counter()
                valid = validators[keyword].is_valid(data)
                validate_end = time.perf_counter()

                load_ms = (validate_start - load_start) * 1000
                validate_ms = (validate_end - validate_start) * 1000
                print(
                    f"{LIB},{keyword},{doc_path.stem},{rep},{load_ms:.3f},{validate_ms:.3f},{valid}",
                    flush=True,
                )


main()
