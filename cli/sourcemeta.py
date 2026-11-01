# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 German Federal Office for Information Security (BSI) <https://www.bsi.bund.de>
# Software-Engineering: 2026 Intevation GmbH <https://intevation.de>

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    cli = sys.argv[1] if len(sys.argv) > 1 else "jsonschema"
    fixtures = Path(__file__).resolve().parent.parent / "fixtures/support"
    cases = json.loads((fixtures / "cases.json").read_text())
    failures = 0
    with tempfile.TemporaryDirectory() as temporary:
        instance = Path(temporary) / "instance.json"
        for keyword in ("anyOf", "oneOf"):
            for case in cases:
                instance.write_text(json.dumps(case["instance"]) + "\n")
                schema = fixtures / f"{case['schema']}.{keyword}.json"
                result = subprocess.run(
                    [cli, "validate", str(schema), str(instance), "--json"],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                if not result.stdout:
                    sys.stderr.write(result.stderr)
                    return 1
                actual = json.loads(result.stdout)["valid"]
                ok = actual == case[keyword]
                failures += not ok
                print(f"{'PASS' if ok else 'FAIL'} sourcemeta {keyword}: {case['name']}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
