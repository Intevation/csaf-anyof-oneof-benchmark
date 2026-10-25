# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 German Federal Office for Information Security (BSI) <https://www.bsi.bund.de>
# Software-Engineering: 2026 Intevation GmbH <https://intevation.de>

import copy
import json
import random
from pathlib import Path

HERE = Path(__file__).parent
TOTAL = 50_000
SEED = 19991001
STRUCTURES = {"1action": 1, "10actions": 10, "100actions": 100}
MIXES = ("eid", "egid", "mixed")
DATE = "2026-10-29T12:00:00Z"


def refs(mix: str, n: int, rng: random.Random, offset: int) -> list[str]:
    out = []
    for i in range(offset, offset + n):
        kind = {"eid": "EID", "egid": "EGID"}.get(mix) or rng.choice(("EID", "EGID"))
        out.append(f"{kind}-{i:06d}")
    return out


def main() -> None:
    base = json.loads((HERE / "base/cisco-sa-20180328-smi2.json").read_text())
    (HERE / "docs").mkdir(exist_ok=True)
    for sname, n_actions in STRUCTURES.items():
        for mix in MIXES:
            rng = random.Random(SEED)
            doc = copy.deepcopy(base)
            name = f"csaf-{sname}-{mix}"
            document = doc["document"]
            document["title"] = f"Synthetic benchmark: {document['title']}"
            document["publisher"] = {
                "category": "other",
                "name": "Intevation GmbH",
                "namespace": "https://intevation.de",
                "issuing_authority": (
                    "Creates synthetic CSAF benchmark documents derived from the Cisco PSIRT example. "
                    "Not a Cisco advisory release."
                ),
            }
            document["tracking"] = {
                "id": name,
                "status": "final",
                "version": "1.0.0",
                "initial_release_date": DATE,
                "current_release_date": DATE,
                "revision_history": [
                    {
                        "number": "1.0.0",
                        "date": DATE,
                        "summary": (
                            "Intevation GmbH created a synthetic benchmark from Cisco PSIRT advisory "
                            "cisco-sa-20180328-smi2, version 3.0.0, adding generated involvement data. "
                            "Original publisher and revision history are preserved in "
                            "bench/base/cisco-sa-20180328-smi2.json."
                        ),
                    }
                ],
            }
            for reference in document.get("references", []):
                if reference.get("category") == "self":
                    reference["category"] = "external"
            per = TOTAL // n_actions
            actions = [
                {
                    "action_id": f"AID-{a + 1:04d}",
                    "category": "coordination",
                    "date": "2026-10-01T12:00:00Z",
                    "status": "completed",
                    "acting_entity_refs": refs(mix, per, rng, a * per),
                }
                for a in range(n_actions)
            ]
            doc["document"]["involvement"] = {
                "entities": [
                    {"category": "vendor", "entity_id": "EID-000001", "name": "Vendor"},
                ],
                "actions": actions,
            }
            path = HERE / "docs" / f"{name}.json"
            content = json.dumps(doc)
            path.write_text(content + "\n")
            print(f"Created {path.name}")


if __name__ == "__main__":
    main()
