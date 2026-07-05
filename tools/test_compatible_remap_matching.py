from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
SRC_GAME_DATA = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Tales of Seikyu\Tales Of Seikyu_Data")
EXCEL_SOURCE = SRC_GAME_DATA / ".tos_korean_patch/backups/0.1.10-playtest.20260702/excel.6482ecc747ec57e0.bak"
BAG_SOURCE = SRC_GAME_DATA / ".tos_korean_patch/baselines/0.1.7-playtest.20260701/bag.e4eabffd3e04ce96.bak"
EXCEL_BUNDLE_NAME = "configs_assets_excel_future_remap.bundle"
BAG_BUNDLE_NAME = "uiview_assets_bagfunctionitem_future_remap.bundle"
sys.path.insert(0, str(REPO / "src"))

from tos_ko_patcher.core import (  # noqa: E402
    key_column_for_schema,
    parse_string_table,
    save_textassets_to_bundle,
    schema_for_textasset,
    serialize_string_table,
    sha256_file,
    textassets_from_bundle,
)


def run(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO / "src")
    env["PYTHONUTF8"] = "1"
    return subprocess.run(args, cwd=str(cwd), env=env, text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def last_json(stdout: str) -> dict[str, Any]:
    for line in reversed([item.strip() for item in stdout.splitlines() if item.strip()]):
        if line.startswith("{") and line.endswith("}"):
            return json.loads(line)
    raise ValueError(f"no JSON result in stdout: {stdout[-500:]}")


def select_entries(payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    candidates = [entry for entry in payload["excel_bundle"]["patch_rows"] if entry["schema"] == "keyed_default"]
    if len(candidates) < 2:
        raise AssertionError("not enough keyed_default rows for remap test")
    return candidates[0], candidates[1]


def find_by_key(bundle: Path, entry: dict[str, Any]) -> dict[str, object]:
    textasset = str(entry["textasset"])
    schema = schema_for_textasset(textasset)
    table = parse_string_table(textasset, textassets_from_bundle(bundle)[textasset], schema)
    key_column = key_column_for_schema(schema)
    for row in table.rows:
        if str(row.get(key_column, "")) == str(entry["key"]):
            return row
    raise AssertionError(f"row not found by key: {entry}")


def mutate_unknown_update(source: Path, output_dir: Path, remap_entry: dict[str, Any], changed_entry: dict[str, Any]) -> tuple[Path, str, int]:
    raw_by_name = textassets_from_bundle(source)
    touched: dict[str, bytes] = {}
    changed_source_ja = ""
    remapped_row_id = 0
    for entry, action in [(remap_entry, "remap"), (changed_entry, "change")]:
        textasset = str(entry["textasset"])
        schema = schema_for_textasset(textasset)
        table = parse_string_table(textasset, raw_by_name[textasset], schema)
        key_column = key_column_for_schema(schema)
        max_row_id = max(int(row["row_id"]) for row in table.rows)
        found = False
        for row in table.rows:
            if str(row["row_id"]) == str(entry["row_id"]) and str(row.get(key_column, "")) == str(entry["key"]):
                if action == "remap":
                    remapped_row_id = max_row_id + 777
                    row["row_id"] = remapped_row_id
                else:
                    changed_source_ja = str(row.get("source_ja", "")) + " [UPDATE]"
                    row["source_ja"] = changed_source_ja
                found = True
                break
        if not found:
            raise AssertionError(f"target row not found: {entry}")
        touched[textasset] = serialize_string_table(table)
        raw_by_name[textasset] = touched[textasset]
    saved = save_textassets_to_bundle(source, output_dir, touched)
    return saved, changed_source_ja, remapped_row_id


def main() -> int:
    payload_path = REPO / "payload/patch_payload.json"
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    remap_entry, changed_entry = select_entries(payload)
    with tempfile.TemporaryDirectory(prefix="tos-ko-compatible-remap-", ignore_cleanup_errors=True) as temp_text:
        temp = Path(temp_text)
        source_copy = temp / "source" / EXCEL_SOURCE.name
        source_copy.parent.mkdir(parents=True)
        shutil.copy2(EXCEL_SOURCE, source_copy)
        mutated_excel, changed_source_ja, remapped_row_id = mutate_unknown_update(source_copy, temp / "mutated", remap_entry, changed_entry)
        data_root = temp / "Tales Of Seikyu_Data"
        target_dir = data_root / "StreamingAssets/aa/StandaloneWindows64"
        target_dir.mkdir(parents=True)
        shutil.copy2(mutated_excel, target_dir / EXCEL_BUNDLE_NAME)
        shutil.copy2(BAG_SOURCE, target_dir / BAG_BUNDLE_NAME)
        original_hash = sha256_file(target_dir / EXCEL_BUNDLE_NAME)

        install = run([sys.executable, "-m", "tos_ko_patcher.app", "--no-gui", "--game-data", str(data_root), "--payload", str(payload_path), "--install"], REPO)
        verify = run([sys.executable, "-m", "tos_ko_patcher.app", "--no-gui", "--game-data", str(data_root), "--payload", str(payload_path), "--verify"], REPO)
        if install.returncode or verify.returncode:
            print(json.dumps({"status": "fail", "install": install.stdout + install.stderr, "verify": verify.stdout + verify.stderr}, ensure_ascii=False))
            return 1
        install_result = last_json(install.stdout)
        verify_result = last_json(verify.stdout)
        patched_bundle = target_dir / EXCEL_BUNDLE_NAME
        remapped_row = find_by_key(patched_bundle, remap_entry)
        changed_row = find_by_key(patched_bundle, changed_entry)
        report = json.loads(Path(str(install_result["compatibility_report"])).read_text(encoding="utf-8"))

        ok = (
            install_result.get("status") == "installed_partial"
            and verify_result.get("status") == "patched_partial"
            and original_hash == str(install_result.get("excel_source_sha256_before"))
            and int(remapped_row["row_id"]) == remapped_row_id
            and str(remapped_row.get("source_ja", "")) == str(remap_entry["source_ja"])
            and str(changed_row.get("source_ja", "")) == changed_source_ja
            and int(report.get("matched_by", {}).get("key", 0)) >= 1
            and int(report.get("skipped_by_reason", {}).get("source_changed", 0)) >= 1
        )
        result = {
            "status": "pass" if ok else "fail",
            "unknown_source_sha256": original_hash,
            "install_status": install_result.get("status"),
            "verify_status": verify_result.get("status"),
            "remapped_row_id": remapped_row_id,
            "remapped_row_patched": str(remapped_row.get("source_ja", "")) == str(remap_entry["source_ja"]),
            "changed_row_preserved": str(changed_row.get("source_ja", "")) == changed_source_ja,
            "matched_by": report.get("matched_by", {}),
            "skipped_by_reason": report.get("skipped_by_reason", {}),
        }
    print(json.dumps(result, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
