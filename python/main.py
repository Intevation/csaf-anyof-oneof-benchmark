# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 German Federal Office for Information Security (BSI) <https://www.bsi.bund.de>
# Software-Engineering: 2026 Intevation GmbH <https://intevation.de>

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    fixtures = Path(sys.argv[1] if len(sys.argv) > 1 else "../fixtures/support")
    failures = 0
    for keyword in ("anyOf", "oneOf"):
        validators: dict[str, Draft202012Validator] = {}
        for case in read_json(fixtures / "cases.json"):
            name = case["schema"]
            if name not in validators:
                schema = read_json(fixtures / f"{name}.{keyword}.json")
                Draft202012Validator.check_schema(schema)
                validators[name] = Draft202012Validator(schema)
            actual = validators[name].is_valid(case["instance"])
            ok = actual == case[keyword]
            failures += not ok
            print(f"{'PASS' if ok else 'FAIL'} python-jsonschema {keyword} {name}: {case['name']} (expected {case[keyword]}, got {actual})")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
