from __future__ import annotations

import csv
import json
from pathlib import Path

SRC_GAME_DATA = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Tales of Seikyu\Tales Of Seikyu_Data")
WORKSET = (
    SRC_GAME_DATA
    / "translation_research/script_extraction/codex_probe/non_dialogue_working_sets/non_dialogue_source_update_20260705_changed_rows_353_working_set.tsv"
)
REVIEW_LOG = SRC_GAME_DATA / "translation_research/source_update_20260705/reviewed_change_log_353.md"
REQUIRED_FIELDS = ["source_textasset", "row_id", "dialog_key", "korean_proposal", "review_status"]


def main() -> int:
    rows = list(csv.DictReader(WORKSET.open("r", encoding="utf-8-sig", newline=""), delimiter="\t"))
    proposal_rows = [row for row in rows if (row.get("review_status") or "").strip() == "proposal_ready"]
    missing_core_fields = [
        {"row_index": index, "missing": [field for field in REQUIRED_FIELDS if not (row.get(field) or "").strip()]}
        for index, row in enumerate(proposal_rows, start=1)
        if any(not (row.get(field) or "").strip() for field in REQUIRED_FIELDS)
    ]
    duplicate_apply_keys: set[tuple[str, str, str]] = set()
    seen: set[tuple[str, str, str]] = set()
    for row in proposal_rows:
        key = (str(row.get("source_textasset") or ""), str(row.get("row_id") or ""), str(row.get("dialog_key") or ""))
        if key in seen:
            duplicate_apply_keys.add(key)
        seen.add(key)
    contains_forbidden = any("귀허" in str(row.get("korean_proposal") or "") for row in proposal_rows)
    result = {
        "status": "pass",
        "workset": str(WORKSET),
        "review_log": str(REVIEW_LOG),
        "review_log_exists": REVIEW_LOG.exists(),
        "rows": len(rows),
        "proposal_ready": len(proposal_rows),
        "missing_core_fields": missing_core_fields[:20],
        "duplicate_apply_keys": sorted("|".join(key) for key in duplicate_apply_keys)[:20],
        "contains_forbidden_귀허": contains_forbidden,
        "term_status": sorted({str(row.get("term_status") or "") for row in proposal_rows}),
    }
    ok = (
        WORKSET.exists()
        and REVIEW_LOG.exists()
        and len(rows) == 27
        and len(proposal_rows) == 27
        and not missing_core_fields
        and not duplicate_apply_keys
        and not contains_forbidden
    )
    result["status"] = "pass" if ok else "fail"
    print(json.dumps(result, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
