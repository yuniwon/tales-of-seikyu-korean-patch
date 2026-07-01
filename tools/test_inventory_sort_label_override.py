from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from tos_ko_patcher.core import load_payload  # noqa: E402


EXPECTED = {
    ("inventory__sort_type_desc", "5", "inventory__sort_type/desc_22b777e6fcb613b8ba83ced9594cd07e"): "Normal",
    ("inventory__sort_type_desc", "6", "inventory__sort_type/desc_0e46d8d6b7a0096b06c0603c9fca9aad"): "Quest",
    ("inventory__sort_type_desc", "7", "inventory__sort_type/desc_7402599bc6350c095fb3ca545d950480"): "Gold",
}


def main() -> int:
    payload = load_payload(REPO / "payload/patch_payload.json")
    rows = payload["excel_bundle"]["patch_rows"]
    actual = {
        (str(row["textasset"]), str(row["row_id"]), str(row["key"])): str(row["source_ja"])
        for row in rows
        if str(row["textasset"]) == "inventory__sort_type_desc"
    }
    mismatches = []
    for key, expected in EXPECTED.items():
        if actual.get(key) != expected:
            mismatches.append({"key": key, "expected": expected, "actual": actual.get(key)})
    unexpected_ascii_scope = [
        {"key": key, "value": value}
        for key, value in sorted(actual.items())
        if key not in EXPECTED and value in set(EXPECTED.values())
    ]
    status = "pass" if not mismatches and not unexpected_ascii_scope else "fail"
    print(
        json.dumps(
            {
                "status": status,
                "expected": [{"key": key, "value": value} for key, value in sorted(EXPECTED.items())],
                "actual_inventory_sort_rows": [{"key": key, "value": value} for key, value in sorted(actual.items())],
                "mismatches": mismatches,
                "unexpected_ascii_scope": unexpected_ascii_scope,
            },
            ensure_ascii=False,
        )
    )
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
