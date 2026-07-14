from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from tos_ko_patcher.core import catalog_referenced_bundles, default_game_data, load_payload, normalize_game_data  # noqa: E402


def main() -> int:
    payload = load_payload(REPO / "payload/patch_payload.json")
    game_data = normalize_game_data(default_game_data())
    result: dict[str, object] = {"status": "pass", "game_data": str(game_data), "roles": {}}
    for role in ("excel_bundle", "bag_function_bundle"):
        pattern = str(payload[role]["glob"])
        candidates = sorted(game_data.glob(pattern))
        referenced = catalog_referenced_bundles(game_data, candidates)
        result["roles"][role] = {
            "candidate_count": len(candidates),
            "candidates": [path.name for path in candidates],
            "catalog_referenced_count": len(referenced),
            "catalog_referenced": [path.name for path in referenced],
        }
        if len(candidates) > 1 and len(referenced) != 1:
            result["status"] = "fail"
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
