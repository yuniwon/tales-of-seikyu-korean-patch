from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
SRC_GAME_DATA = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Tales of Seikyu\Tales Of Seikyu_Data")
PREVIOUS_SOURCE = SRC_GAME_DATA / ".tos_korean_patch/baselines/0.1.7-playtest.20260701/excel.eefb061b2955614b.bak"
CURRENT_SOURCE = SRC_GAME_DATA / ".tos_korean_patch/backups/0.1.10-playtest.20260702/excel.6482ecc747ec57e0.bak"
sys.path.insert(0, str(REPO / "src"))

from tos_ko_patcher.core import (  # noqa: E402
    key_column_for_schema,
    parse_string_table,
    row_source_fingerprint,
    schema_for_textasset,
    sha256_file,
    textassets_from_bundle,
)


def load_previous_release_payload() -> dict[str, Any]:
    proc = subprocess.run(
        ["git", "show", "HEAD:payload/patch_payload.json"],
        cwd=str(REPO),
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode == 0 and proc.stdout.strip():
        return json.loads(proc.stdout)
    return json.loads((REPO / "payload/patch_payload.json").read_text(encoding="utf-8"))


def unique_insert(index: dict[str, dict[str, object]], duplicates: set[str], key: str, row: dict[str, object]) -> None:
    if not key:
        return
    if key in index:
        duplicates.add(key)
    index[key] = row


def build_indexes(bundle: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "identity": defaultdict(dict),
        "key": defaultdict(dict),
        "fingerprint": defaultdict(dict),
        "source_ja": defaultdict(dict),
    }
    key_dupes: dict[str, set[str]] = defaultdict(set)
    fingerprint_dupes: dict[str, set[str]] = defaultdict(set)
    source_ja_dupes: dict[str, set[str]] = defaultdict(set)
    for name, raw in textassets_from_bundle(bundle).items():
        schema = schema_for_textasset(name)
        try:
            table = parse_string_table(name, raw, schema)
        except Exception:
            continue
        key_column = key_column_for_schema(schema)
        for row in table.rows:
            row_id = str(row["row_id"])
            key = str(row.get(key_column, ""))
            result["identity"][name][(row_id, key)] = row
            unique_insert(result["key"][name], key_dupes[name], key, row)
            unique_insert(result["fingerprint"][name], fingerprint_dupes[name], row_source_fingerprint(row, schema), row)
            unique_insert(result["source_ja"][name], source_ja_dupes[name], " ".join(str(row.get("source_ja", "")).split()), row)
    for name, duplicates in key_dupes.items():
        for key in duplicates:
            result["key"][name].pop(key, None)
    for name, duplicates in fingerprint_dupes.items():
        for key in duplicates:
            result["fingerprint"][name].pop(key, None)
    for name, duplicates in source_ja_dupes.items():
        for key in duplicates:
            result["source_ja"][name].pop(key, None)
    return result


def main() -> int:
    previous_payload = load_previous_release_payload()
    previous = build_indexes(PREVIOUS_SOURCE)
    current = build_indexes(CURRENT_SOURCE)
    breakdown: Counter[str] = Counter()
    samples: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in previous_payload["excel_bundle"]["patch_rows"]:
        textasset = str(entry["textasset"])
        schema = str(entry["schema"])
        row_id = str(entry["row_id"])
        key = str(entry["key"])
        expected_fingerprint = str(entry.get("source_fingerprint") or "")
        current_row = current["identity"].get(textasset, {}).get((row_id, key))
        if current_row is not None:
            if expected_fingerprint and row_source_fingerprint(current_row, schema) != expected_fingerprint:
                breakdown["source_changed_same_identity"] += 1
                if len(samples["source_changed_same_identity"]) < 5:
                    samples["source_changed_same_identity"].append(entry)
            else:
                breakdown["identity_match"] += 1
            continue
        current_row = current["key"].get(textasset, {}).get(key)
        if current_row is not None:
            if expected_fingerprint and row_source_fingerprint(current_row, schema) != expected_fingerprint:
                breakdown["source_changed_same_key"] += 1
                if len(samples["source_changed_same_key"]) < 5:
                    samples["source_changed_same_key"].append({**entry, "new_row_id": str(current_row["row_id"])})
            else:
                breakdown["key_remap_match"] += 1
            continue
        if expected_fingerprint and current["fingerprint"].get(textasset, {}).get(expected_fingerprint) is not None:
            breakdown["fingerprint_remap_match"] += 1
            continue
        previous_row = previous["identity"].get(textasset, {}).get((row_id, key))
        previous_source_ja = " ".join(str(previous_row.get("source_ja", "")).split()) if previous_row else ""
        if previous_source_ja and current["source_ja"].get(textasset, {}).get(previous_source_ja) is not None:
            breakdown["source_ja_remap_match"] += 1
            continue
        breakdown["unmatched_or_removed"] += 1
        if len(samples["unmatched_or_removed"]) < 5:
            samples["unmatched_or_removed"].append(entry)

    safe_rows = int(breakdown["identity_match"] + breakdown["key_remap_match"] + breakdown["fingerprint_remap_match"] + breakdown["source_ja_remap_match"])
    unsafe_rows = len(previous_payload["excel_bundle"]["patch_rows"]) - safe_rows
    ok = safe_rows >= len(previous_payload["excel_bundle"]["patch_rows"]) - 50
    result = {
        "status": "pass" if ok else "fail",
        "previous_source_sha256": sha256_file(PREVIOUS_SOURCE),
        "current_source_sha256": sha256_file(CURRENT_SOURCE),
        "payload_rows": len(previous_payload["excel_bundle"]["patch_rows"]),
        "safe_rows": safe_rows,
        "unsafe_rows": unsafe_rows,
        "breakdown": dict(breakdown),
        "samples": samples,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
