# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 German Federal Office for Information Security (BSI) <https://www.bsi.bund.de>
# Software-Engineering: 2026 Intevation GmbH <https://intevation.de>

import csv
import statistics
import sys
from collections import defaultdict
from pathlib import Path


def main() -> None:
    results_dir = Path(sys.argv[1])
    total_times: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    validation_times: dict[tuple[str, str, str], list[float]] = defaultdict(list)

    for csv_path in sorted(results_dir.glob("*.csv")):
        with csv_path.open() as csv_file:
            for library, keyword, document, rep, load_ms, validate_ms, valid in csv.reader(csv_file):
                assert valid in {"True", "true"}, (csv_path, document, keyword, valid)

                # Skip the warm-up run.
                if int(rep) < 1:
                    continue

                if load_ms:
                    total_ms = float(load_ms) + float(validate_ms)
                    total_times[library, document, keyword].append(total_ms)
                validation_times[library, document, keyword].append(float(validate_ms))

    for title, times in (
        ("JSON file read + parse + validate", total_times),
        ("Validate only", validation_times),
    ):
        print(f"## {title}")
        print()
        print("| library | document | anyOf ms | oneOf ms | oneOf/anyOf |")
        print("|---|---|--:|--:|--:|")
        for library, document in sorted({(library, document) for library, document, _ in times}):
            any_of_ms = statistics.median(times[library, document, "anyOf"])
            one_of_ms = statistics.median(times[library, document, "oneOf"])
            ratio = one_of_ms / any_of_ms
            print(f"| {library} | {document} | {any_of_ms:.1f} | {one_of_ms:.1f} | {ratio:.2f} |")
        print()


if __name__ == "__main__":
    main()
