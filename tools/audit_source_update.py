from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
SRC_GAME_DATA = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Tales of Seikyu\Tales Of Seikyu_Data")
PREVIOUS_EXCEL_SOURCE = SRC_GAME_DATA / ".tos_korean_patch/backups/0.1.3-playtest.20260623/configs_assets_excel_f49ac7551e791fb388bd02ccb81a6a88.bundle.c7cc2e47a44f1c881c7c9c9d62d1a4b51060f061025a5f4ef663abc05bce1cc9.bak"
CURRENT_EXCEL_SOURCE = SRC_GAME_DATA / ".tos_korean_patch/baselines/0.1.6-playtest.20260625/excel.d973dcdac6fbde16.bak"
sys.path.insert(0, str(REPO / "src"))

from tos_ko_patcher.core import (  # noqa: E402
    key_column_for_schema,
    parse_string_table,
    schema_for_textasset,
    sha256_file,
    textassets_from_bundle,
)

CJK_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uf900-\ufaff\uac00-\ud7af]")
PRINTABLE_RE = re.compile(r"[\x20-\x7e\u3000-\u9fff\uf900-\ufaff\uac00-\ud7af\uff00-\uffef]{2,}")


def row_index(assets: dict[str, bytes]) -> tuple[dict[str, dict[tuple[str, str], dict[str, str]]], dict[str, str]]:
    result: dict[str, dict[tuple[str, str], dict[str, str]]] = {}
    parse_errors: dict[str, str] = {}
    for name, raw in assets.items():
        schema = schema_for_textasset(name)
        try:
            table = parse_string_table(name, raw, schema)
        except Exception as exc:  # noqa: BLE001 - audit records unparsed non-i18n tables.
            parse_errors[name] = str(exc)
            continue
        key_name = key_column_for_schema(schema)
        result[name] = {}
        for row in table.rows:
            result[name][(str(row["row_id"]), str(row.get(key_name, "")))] = {
                "row_id": str(row["row_id"]),
                "key": str(row.get(key_name, "")),
                "source_ja": str(row.get("source_ja", "")),
                "source_en": str(row.get("source_en", "")),
            }
    return result, parse_errors


def cjk_strings(raw: bytes) -> set[str]:
    values: set[str] = set()
    text = raw.decode("utf-8", "ignore")
    for match in PRINTABLE_RE.finditer(text):
        value = match.group(0).strip("\x00")
        if CJK_RE.search(value):
            values.add(value)
    return values


def raw_changed_assets(previous_assets: dict[str, bytes], current_assets: dict[str, bytes]) -> list[dict[str, Any]]:
    changed: list[dict[str, Any]] = []
    for name in sorted(set(previous_assets) & set(current_assets)):
        previous_raw = previous_assets[name]
        current_raw = current_assets[name]
        previous_hash = hashlib.sha256(previous_raw).hexdigest()
        current_hash = hashlib.sha256(current_raw).hexdigest()
        if previous_hash == current_hash:
            continue
        previous_strings = cjk_strings(previous_raw)
        current_strings = cjk_strings(current_raw)
        changed.append(
            {
                "textasset": name,
                "previous_sha256": previous_hash,
                "current_sha256": current_hash,
                "previous_len": len(previous_raw),
                "current_len": len(current_raw),
                "added_cjk_strings": sorted(current_strings - previous_strings),
                "removed_cjk_strings": sorted(previous_strings - current_strings),
            }
        )
    return changed


def main() -> int:
    previous_assets = textassets_from_bundle(PREVIOUS_EXCEL_SOURCE)
    current_assets = textassets_from_bundle(CURRENT_EXCEL_SOURCE)
    previous_rows, previous_errors = row_index(previous_assets)
    current_rows, current_errors = row_index(current_assets)

    added_rows: list[dict[str, str]] = []
    removed_rows: list[dict[str, str]] = []
    changed_rows: list[dict[str, str]] = []
    for name in sorted(set(previous_rows) | set(current_rows)):
        previous_keys = set(previous_rows.get(name, {}))
        current_keys = set(current_rows.get(name, {}))
        for key in sorted(current_keys - previous_keys):
            added_rows.append({"textasset": name, **current_rows[name][key]})
        for key in sorted(previous_keys - current_keys):
            removed_rows.append({"textasset": name, **previous_rows[name][key]})
        for key in sorted(previous_keys & current_keys):
            previous_row = previous_rows[name][key]
            current_row = current_rows[name][key]
            if previous_row["source_ja"] != current_row["source_ja"] or previous_row["source_en"] != current_row["source_en"]:
                changed_rows.append({"textasset": name, "row_id": current_row["row_id"], "key": current_row["key"]})

    changed_assets = raw_changed_assets(previous_assets, current_assets)
    assets_with_cjk_delta = [
        item
        for item in changed_assets
        if item["added_cjk_strings"] or item["removed_cjk_strings"]
    ]
    ok = not added_rows and not removed_rows and not changed_rows and not assets_with_cjk_delta
    result = {
        "status": "pass" if ok else "fail",
        "previous_source_sha256": sha256_file(PREVIOUS_EXCEL_SOURCE),
        "current_source_sha256": sha256_file(CURRENT_EXCEL_SOURCE),
        "textasset_count_previous": len(previous_assets),
        "textasset_count_current": len(current_assets),
        "added_textassets": sorted(set(current_assets) - set(previous_assets)),
        "removed_textassets": sorted(set(previous_assets) - set(current_assets)),
        "changed_textasset_count": len(changed_assets),
        "changed_textassets": [item["textasset"] for item in changed_assets],
        "assets_with_cjk_delta": assets_with_cjk_delta,
        "parse_error_count_previous": len(previous_errors),
        "parse_error_count_current": len(current_errors),
        "added_rows_count": len(added_rows),
        "removed_rows_count": len(removed_rows),
        "changed_rows_count": len(changed_rows),
        "added_rows_sample": added_rows[:20],
        "removed_rows_sample": removed_rows[:20],
        "changed_rows_sample": changed_rows[:20],
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
