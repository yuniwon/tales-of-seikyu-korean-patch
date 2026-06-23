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
EXCEL_BUNDLE_NAME = "configs_assets_excel_f49ac7551e791fb388bd02ccb81a6a88.bundle"
EXCEL_SOURCE = SRC_GAME_DATA / ".tos_korean_patch/backups/0.1.3-playtest.20260623/configs_assets_excel_f49ac7551e791fb388bd02ccb81a6a88.bundle.c7cc2e47a44f1c881c7c9c9d62d1a4b51060f061025a5f4ef663abc05bce1cc9.bak"
BAG_SOURCE = SRC_GAME_DATA / ".korean_patch/backups/uiview_assets_bagfunctionitem_4151e323e15f7662e9ca55d7135ecfd4.bundle.43f3dbeb5cc829e9fd282b19bb3a6155de4a7769459296db8a48390be27bfc85.visual_lqa_351.bak"
sys.path.insert(0, str(REPO / "src"))

from tos_ko_patcher.core import (  # noqa: E402
    inspect_excel_ui_font,
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


def build_text_only_excel(source: Path, payload: dict[str, Any], output_dir: Path) -> Path:
    raw_by_name = textassets_from_bundle(source)
    by_textasset: dict[str, list[dict[str, Any]]] = {}
    for entry in payload["excel_bundle"]["patch_rows"]:
        by_textasset.setdefault(entry["textasset"], []).append(entry)

    planned: dict[str, bytes] = {}
    for textasset, entries in sorted(by_textasset.items()):
        schema = schema_for_textasset(textasset)
        table = parse_string_table(textasset, raw_by_name[textasset], schema)
        key_column = key_column_for_schema(schema)
        lookup = {(str(row["row_id"]), str(row.get(key_column, ""))): row for row in table.rows}
        for entry in entries:
            lookup[(str(entry["row_id"]), str(entry["key"]))]["source_ja"] = entry["source_ja"]
        planned[textasset] = serialize_string_table(table)
    return save_textassets_to_bundle(source, output_dir, planned)


def main() -> int:
    payload_path = REPO / "payload/patch_payload.json"
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="tos-ko-repair-text-only-", ignore_cleanup_errors=True) as temp:
        temp = Path(temp)
        source = temp / EXCEL_BUNDLE_NAME
        shutil.copy2(EXCEL_SOURCE, source)
        text_only = build_text_only_excel(source, payload, temp / "text_only")
        text_only_hash = sha256_file(text_only)

        data_root = temp / "Tales Of Seikyu_Data"
        target_dir = data_root / "StreamingAssets/aa/StandaloneWindows64"
        target_dir.mkdir(parents=True)
        shutil.copy2(text_only, target_dir / EXCEL_BUNDLE_NAME)
        shutil.copy2(BAG_SOURCE, target_dir / "uiview_assets_bagfunctionitem_4151e323e15f7662e9ca55d7135ecfd4.bundle")
        before = inspect_excel_ui_font(target_dir / EXCEL_BUNDLE_NAME, payload)
        install = run([sys.executable, "-m", "tos_ko_patcher.app", "--no-gui", "--game-data", str(data_root), "--payload", str(payload_path), "--install"], REPO)
        verify = run([sys.executable, "-m", "tos_ko_patcher.app", "--no-gui", "--game-data", str(data_root), "--payload", str(payload_path), "--verify"], REPO)
        if install.returncode or verify.returncode:
            print(
                json.dumps(
                    {
                        "status": "fail",
                        "text_only_hash": text_only_hash,
                        "before": before,
                        "install": install.stdout + install.stderr,
                        "verify": verify.stdout + verify.stderr,
                    },
                    ensure_ascii=False,
                )
            )
            return 1
        verify_result = last_json(verify.stdout)
        after = inspect_excel_ui_font(target_dir / EXCEL_BUNDLE_NAME, payload)

    ok = (
        text_only_hash in set(payload["excel_bundle"].get("accepted_patched_sha256", []))
        and not before["ui_font_alias_ok"]
        and after["ui_font_alias_ok"]
        and verify_result.get("font_ok")
        and verify_result.get("ui_font_alias_ok")
    )
    print(
        json.dumps(
            {
                "status": "pass" if ok else "fail",
                "text_only_hash": text_only_hash,
                "target_sha256": payload["excel_bundle"]["target_sha256"],
                "before": before,
                "after": after,
                "verify": verify_result,
            },
            ensure_ascii=False,
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
