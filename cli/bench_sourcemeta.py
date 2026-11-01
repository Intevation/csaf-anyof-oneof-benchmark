# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 German Federal Office for Information Security (BSI) <https://www.bsi.bund.de>
# Software-Engineering: 2026 Intevation GmbH <https://intevation.de>

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> None:
    bench = Path(sys.argv[1]).resolve()
    reps = int(sys.argv[2])
    with tempfile.TemporaryDirectory() as temporary:
        instances = Path(temporary) / "instances.jsonl"
        for index, document in enumerate(sorted((bench / "docs").glob("*.json"))):
            content = json.dumps(json.loads(document.read_text())) + "\n"
            with instances.open("w") as output:
                for _ in range(reps + 1):
                    output.write(content)
            order = ("anyOf", "oneOf") if index % 2 == 0 else ("oneOf", "anyOf")
            for keyword in order:
                print(f"Benchmarking sourcemeta-cli {keyword} {document.stem}", file=sys.stderr, flush=True)
                result = subprocess.run(
                    [
                        "jsonschema",
                        "validate",
                        str(bench / "schema" / f"csaf.{keyword}.json"),
                        str(instances),
                        "--resolve",
                        str(bench / "metaschemas"),
                        "--resolve",
                        str(bench / "base/SelectionList_2_0_0.schema.json"),
                        "--http",
                        "--fast",
                        "--benchmark",
                        "--loop",
                        "1",
                    ],
                    stdout=subprocess.PIPE,
                    text=True,
                    check=True,
                )
                lines = result.stdout.splitlines()
                if len(lines) != reps + 1:
                    message = f"Expected {reps + 1} CLI measurements, got {len(lines)}"
                    raise ValueError(message)
                for rep, line in enumerate(lines):
                    match = re.fullmatch(r".+\[(\d+)\]: PASS ([\d.]+) \+- [\d.]+ us \([\d.]+\)", line)
                    if match is None or int(match[1]) != rep + 1:
                        message = f"Unexpected CLI benchmark output: {line}"
                        raise ValueError(message)
                    validate_ms = float(match[2]) / 1000
                    # Empty load time, the native CLI timer covers validation only.
                    print(f"sourcemeta-cli,{keyword},{document.stem},{rep},,{validate_ms:.6f},True", flush=True)


if __name__ == "__main__":
    main()
