from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC_GAME_DATA = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Tales of Seikyu\Tales Of Seikyu_Data")
EXCEL_SOURCE = SRC_GAME_DATA / ".tos_korean_patch/baselines/0.1.7-playtest.20260701/excel.eefb061b2955614b.bak"
sys.path.insert(0, str(REPO / "src"))

from tos_ko_patcher.core import (  # noqa: E402
    EXCEL_GLOB,
    key_column_for_schema,
    parse_acf_field,
    parse_string_table,
    schema_for_textasset,
    sha256_file,
    textassets_from_bundle,
)


def main() -> int:
    payload_path = REPO / "payload/patch_payload.json"
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    matches = sorted(SRC_GAME_DATA.glob(EXCEL_GLOB))
    if len(matches) != 1:
        print(json.dumps({"status": "fail", "reason": "expected one current Excel bundle", "matches": [str(item) for item in matches]}, ensure_ascii=False))
        return 1
    current_bundle = matches[0]
    raw_by_name = textassets_from_bundle(EXCEL_SOURCE)
    bundle_identities: dict[str, set[tuple[str, str]]] = {}
    for name, raw in raw_by_name.items():
        schema = schema_for_textasset(name)
        try:
            table = parse_string_table(name, raw, schema)
        except Exception:
            continue
        key_name = key_column_for_schema(schema)
        bundle_identities[name] = {(str(row["row_id"]), str(row.get(key_name, ""))) for row in table.rows}

    missing_rows = []
    for entry in payload["excel_bundle"]["patch_rows"]:
        identity = (str(entry["row_id"]), str(entry["key"]))
        if identity not in bundle_identities.get(str(entry["textasset"]), set()):
            missing_rows.append({"textasset": entry["textasset"], "row_id": entry["row_id"], "key": entry["key"]})

    manifest = SRC_GAME_DATA.parents[2] / "appmanifest_2340520.acf"
    buildid = ""
    if manifest.exists():
        buildid = parse_acf_field(manifest.read_text(encoding="utf-8", errors="ignore"), "buildid")
    result = {
        "status": "pass" if not missing_rows else "fail",
        "steam_buildid": buildid,
        "current_excel_bundle": current_bundle.name,
        "current_excel_sha256": sha256_file(current_bundle),
        "audited_source_bundle": str(EXCEL_SOURCE),
        "audited_source_sha256": sha256_file(EXCEL_SOURCE),
        "payload_source_sha256": payload["excel_bundle"]["source_sha256"],
        "payload_target_sha256": payload["excel_bundle"]["target_sha256"],
        "payload_rows": len(payload["excel_bundle"]["patch_rows"]),
        "missing_rows_count": len(missing_rows),
        "missing_rows_sample": missing_rows[:20],
        "dropped_previous_payload_rows": payload.get("generated_from", {}).get("dropped_previous_payload_rows"),
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "pass" and result["audited_source_sha256"] == result["payload_source_sha256"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
