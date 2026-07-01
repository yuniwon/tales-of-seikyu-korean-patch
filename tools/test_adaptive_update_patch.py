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
EXCEL_BUNDLE_NAME = "configs_assets_excel_future_update.bundle"
EXCEL_SOURCE = SRC_GAME_DATA / ".tos_korean_patch/baselines/0.1.7-playtest.20260701/excel.eefb061b2955614b.bak"
BAG_SOURCE = SRC_GAME_DATA / ".tos_korean_patch/baselines/0.1.7-playtest.20260701/bag.e4eabffd3e04ce96.bak"
BAG_BUNDLE_NAME = "uiview_assets_bagfunctionitem_future_update.bundle"
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


def find_row(bundle: Path, entry: dict[str, Any]) -> dict[str, object]:
    raw = textassets_from_bundle(bundle)[str(entry["textasset"])]
    schema = schema_for_textasset(str(entry["textasset"]))
    table = parse_string_table(str(entry["textasset"]), raw, schema)
    key_column = key_column_for_schema(schema)
    for row in table.rows:
        if str(row["row_id"]) == str(entry["row_id"]) and str(row.get(key_column, "")) == str(entry["key"]):
            return row
    raise AssertionError(f"row not found: {entry}")


def mutate_one_source_row(source: Path, output_dir: Path, entry: dict[str, Any]) -> tuple[Path, str]:
    raw_by_name = textassets_from_bundle(source)
    textasset = str(entry["textasset"])
    schema = schema_for_textasset(textasset)
    table = parse_string_table(textasset, raw_by_name[textasset], schema)
    key_column = key_column_for_schema(schema)
    mutated = ""
    for row in table.rows:
        if str(row["row_id"]) == str(entry["row_id"]) and str(row.get(key_column, "")) == str(entry["key"]):
            mutated = str(row.get("source_ja", "")) + " [UPDATE]"
            row["source_ja"] = mutated
            break
    if not mutated:
        raise AssertionError(f"target row not found: {entry}")
    raw_by_name[textasset] = serialize_string_table(table)
    saved = save_textassets_to_bundle(source, output_dir, {textasset: raw_by_name[textasset]})
    return saved, mutated


def main() -> int:
    payload_path = REPO / "payload/patch_payload.json"
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    if not payload["excel_bundle"]["patch_rows"][0].get("source_fingerprint"):
        print(json.dumps({"status": "fail", "reason": "payload rows have no source_fingerprint"}, ensure_ascii=False))
        return 1

    changed_entry = payload["excel_bundle"]["patch_rows"][0]
    applied_entry = payload["excel_bundle"]["patch_rows"][1]
    with tempfile.TemporaryDirectory(prefix="tos-ko-adaptive-update-", ignore_cleanup_errors=True) as temp:
        temp = Path(temp)
        source_copy = temp / "source" / EXCEL_SOURCE.name
        source_copy.parent.mkdir(parents=True)
        shutil.copy2(EXCEL_SOURCE, source_copy)
        mutated_excel, mutated_source_ja = mutate_one_source_row(source_copy, temp / "mutated", changed_entry)

        data_root = temp / "Tales Of Seikyu_Data"
        target_dir = data_root / "StreamingAssets/aa/StandaloneWindows64"
        target_dir.mkdir(parents=True)
        shutil.copy2(mutated_excel, target_dir / EXCEL_BUNDLE_NAME)
        shutil.copy2(BAG_SOURCE, target_dir / BAG_BUNDLE_NAME)
        original_unknown_hash = sha256_file(target_dir / EXCEL_BUNDLE_NAME)

        install = run([sys.executable, "-m", "tos_ko_patcher.app", "--no-gui", "--game-data", str(data_root), "--payload", str(payload_path), "--install"], REPO)
        verify = run([sys.executable, "-m", "tos_ko_patcher.app", "--no-gui", "--game-data", str(data_root), "--payload", str(payload_path), "--verify"], REPO)
        if install.returncode or verify.returncode:
            print(
                json.dumps(
                    {
                        "status": "fail",
                        "install": install.stdout + install.stderr,
                        "verify": verify.stdout + verify.stderr,
                    },
                    ensure_ascii=False,
                )
            )
            return 1

        install_result = last_json(install.stdout)
        verify_result = last_json(verify.stdout)
        patched_bundle = target_dir / EXCEL_BUNDLE_NAME
        skipped_row_after_install = find_row(patched_bundle, changed_entry)
        applied_row_after_install = find_row(patched_bundle, applied_entry)
        restore = run([sys.executable, "-m", "tos_ko_patcher.app", "--no-gui", "--game-data", str(data_root), "--payload", str(payload_path), "--restore"], REPO)
        if restore.returncode:
            print(json.dumps({"status": "fail", "restore": restore.stdout + restore.stderr}, ensure_ascii=False))
            return 1
        restored_hash = sha256_file(patched_bundle)
        restored_row = find_row(patched_bundle, changed_entry)
        report_path = Path(str(install_result.get("compatibility_report") or ""))
        report_exists = report_path.exists()

        ok = (
            install_result.get("status") == "installed_partial"
            and verify_result.get("status") == "patched_partial"
            and int(install_result.get("skipped_rows") or 0) >= 1
            and report_exists
            and str(skipped_row_after_install.get("source_ja", "")) == mutated_source_ja
            and str(applied_row_after_install.get("source_ja", "")) == str(applied_entry["source_ja"])
            and restored_hash == original_unknown_hash
            and str(restored_row.get("source_ja", "")) == mutated_source_ja
        )
        result = {
            "status": "pass" if ok else "fail",
            "unknown_source_sha256": original_unknown_hash,
            "install": install_result,
            "verify": verify_result,
            "skipped_row_preserved": str(skipped_row_after_install.get("source_ja", "")) == mutated_source_ja,
            "compatible_row_patched": str(applied_row_after_install.get("source_ja", "")) == str(applied_entry["source_ja"]),
            "restore_ok": restored_hash == original_unknown_hash,
            "report_exists": report_exists,
        }
    print(
        json.dumps(result, ensure_ascii=False)
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
