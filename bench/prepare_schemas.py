# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 German Federal Office for Information Security (BSI) <https://www.bsi.bund.de>
# Software-Engineering: 2026 Intevation GmbH <https://intevation.de>

import copy
import json
from pathlib import Path

HERE = Path(__file__).parent


def main() -> None:
    upstream = json.loads((HERE / "base/csaf.json").read_text())
    any_of = upstream
    one_of = copy.deepcopy(any_of)
    items = one_of["$defs"]["entity_refs_t"]["items"]
    items["oneOf"] = items.pop("anyOf")
    (HERE / "schema").mkdir(exist_ok=True)
    for name, schema in (("anyOf", any_of), ("oneOf", one_of)):
        (HERE / f"schema/csaf.{name}.json").write_text(json.dumps(schema, indent=2) + "\n")
        print(name, sum(json.dumps(schema).count(f'"{name}"') for _ in [0]))


if __name__ == "__main__":
    main()
