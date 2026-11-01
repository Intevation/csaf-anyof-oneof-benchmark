# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 German Federal Office for Information Security (BSI) <https://www.bsi.bund.de>
# Software-Engineering: 2026 Intevation GmbH <https://intevation.de>

import argparse
import copy
import json
import random
from pathlib import Path

HERE = Path(__file__).parent
TOTAL = 100_000
SEED = 19991001
# (number of actions, references per action)
BATCHES = {
    "1action-40000refs": (1, 40_000),
    "1action": (1, TOTAL),
    "10actions": (10, TOTAL // 10),
    "100actions": (100, TOTAL // 100),
    "1000actions": (1_000, TOTAL // 1_000),
    "10000actions": (10_000, TOTAL // 10_000),
    "100000actions": (100_000, 1),
}
MIXES = ("eid", "egid", "mixed")
DATE = "2026-10-29T12:00:00Z"
SOURCE = (
    "https://raw.githubusercontent.com/oasis-tcs/csaf/e0da5a98af185acce66e1ef4c2686c8f215703b2/"
    "csaf_2.1/examples/csaf/cisco-sa-20180328-smi2.json"
)


def refs(mix: str, n: int, rng: random.Random, offset: int) -> list[str]:
    out = []
    for i in range(offset, offset + n):
        kind = {"eid": "EID", "egid": "EGID"}.get(mix) or rng.choice(("EID", "EGID"))
        out.append(f"{kind}-{i:06d}")
    return out


def main(*, receiving: bool = False) -> None:
    base = json.loads((HERE / "base/cisco-sa-20180328-smi2.json").read_text())
    (HERE / "docs").mkdir(exist_ok=True)
    for sname, (n_actions, per) in BATCHES.items():
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
                        "summary": "Added synthetic involvement data for benchmarking.",
                    }
                ],
            }
            for reference in document.get("references", []):
                if reference.get("category") == "self":
                    reference["category"] = "external"
            document.setdefault("references", []).append(
                {"category": "external", "summary": "Original Cisco PSIRT document", "url": SOURCE}
            )
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
            if receiving:
                for action in actions:
                    action["receiving_entity_refs"] = action["acting_entity_refs"]
                    action["acting_entity_refs"] = ["EID-000001"]
                document["tracking"]["revision_history"][0]["summary"] = (
                    "Added synthetic receiving entity references for benchmarking."
                )
            doc["document"]["involvement"] = {
                "entities": [
                    {"category": "vendor", "entity_id": "EID-000001", "name": "Vendor"},
                ],
                "actions": actions,
            }
            path = HERE / "docs" / f"{name}.json"
            content = json.dumps(doc, indent=2)
            path.write_text(content + "\n")
            print(f"Created {path.name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--receiving", action="store_true", help="Benchmark receiving_entity_refs instead of acting_entity_refs"
    )
    main(receiving=parser.parse_args().receiving)
