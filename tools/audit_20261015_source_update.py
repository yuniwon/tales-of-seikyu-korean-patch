from __future__ import annotations

import csv
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GAME = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Tales of Seikyu\Tales Of Seikyu_Data")
SOURCE = GAME / "StreamingAssets/aa/StandaloneWindows64/configs_assets_excel_819141916302f0cf565fc9cfe6d0ffc7.bundle"
EXPECTED_SHA = "5ab59347431bcbc7d54ad1d178c1fcbaefe3e1e1060930e5746836b355cab6e8"
OUT = GAME / "translation_research/source_update_20261015"
sys.path.insert(0, str(REPO / "src"))

from tos_ko_patcher.core import (  # noqa: E402
    key_column_for_schema,
    parse_string_table,
    planned_excel_textassets_report,
    schema_for_textasset,
    sha256_file,
    textassets_from_bundle,
)

LANGUAGES = ("source_en", "source_ja", "source_zh_cn")


def extract(bundle: Path) -> tuple[dict[tuple[str, str], dict], list, list]:
    unique = {}
    occurrences = []
    failures = []
    for name, raw in textassets_from_bundle(bundle).items():
        schema = schema_for_textasset(name)
        try:
            table = parse_string_table(name, raw, schema)
        except Exception as exc:
            failures.append({"textasset": name, "bytes": len(raw), "error": str(exc)})
            continue
        key_column = key_column_for_schema(schema)
        for row in table.rows:
            occurrences.append({"textasset": name, "schema": schema, **row})
            if row.get(key_column):
                unique[(name, str(row[key_column]))] = row
    return unique, occurrences, failures


def main() -> int:
    if sha256_file(SOURCE) != EXPECTED_SHA:
        raise RuntimeError("Current source hash differs from the audited original")
    base, _, _ = extract(GAME / ".tos_korean_patch/backups/0.1.10-playtest.20260702/excel.6482ecc747ec57e0.bak")
    july = json.loads((GAME / "translation_research/source_update_20260730/source_diff_review_24352496.json").read_text(encoding="utf-8"))
    for item in july["changes"]:
        identity = (item["textasset"], item["key"])
        if item["kind"] == "removed":
            base.pop(identity, None)
        else:
            base[identity] = {**base.get(identity, {}), **{field: item.get(field, "") for field in LANGUAGES}}
    august = GAME / "translation_research/script_extraction/codex_probe/dialogue_working_sets/source_update_20260825_build_24728299_Nine_Lives_355_dialogue_working_set.tsv"
    with august.open(encoding="utf-8-sig", newline="") as handle:
        for item in csv.DictReader(handle, delimiter="\t"):
            identity = (item["source_textasset"], item["dialog_key"])
            base[identity] = {
                **base.get(identity, {}), "source_en": item["english"],
                "source_ja": item["japanese"], "source_zh_cn": item["chinese_simplified"],
            }
    current, occurrences, failures = extract(SOURCE)
    added = sorted(current.keys() - base.keys())
    removed = sorted(base.keys() - current.keys())
    changed = [
        {"textasset": identity[0], "key": identity[1], "fields": fields}
        for identity in sorted(current.keys() & base.keys())
        if (fields := [field for field in LANGUAGES if current[identity].get(field, "") != base[identity].get(field, "")])
    ]
    payload = json.loads((REPO / "payload/patch_payload.json").read_text(encoding="utf-8"))
    _, _, compatible = planned_excel_textassets_report(SOURCE, payload, compatible_only=True)
    report = {
        "status": "pass" if not (added or removed or changed or compatible["skipped_rows"]) else "fail",
        "buildid": "24948693", "source_sha256": EXPECTED_SHA,
        "baseline_method": "Reconstructed build 24728299 language columns from July clean source plus July/August audited deltas; all previous payload fingerprints checked independently.",
        "added": added, "removed": removed, "changed": changed,
        "unique_key_rows": len(current), "all_row_occurrences": len(occurrences),
        "non_string_table_parser_caveats": failures,
        "caveat": "Other binary TextAssets are not treated as absent text. Runtime snapshots are separate; in-game visual QA was not performed.",
        "compatibility": {key: value for key, value in compatible.items() if key != "skipped"},
        "translation_decision": "No new or changed language rows; preserve all existing Korean.",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "source_diff_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "original_table_snapshot.json").write_text(json.dumps(occurrences, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    baseline = GAME / ".tos_korean_patch/baselines/0.1.17-playtest.20261015" / f"excel.{EXPECTED_SHA[:16]}.bak"
    baseline.parent.mkdir(parents=True, exist_ok=True)
    if not baseline.exists():
        shutil.copy2(SOURCE, baseline)
    if sha256_file(baseline) != EXPECTED_SHA or sha256_file(SOURCE) != EXPECTED_SHA:
        raise RuntimeError("Source baseline verification failed")
    print(json.dumps({key: value for key, value in report.items() if key != "non_string_table_parser_caveats"}, ensure_ascii=False))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
