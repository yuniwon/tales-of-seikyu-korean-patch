from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
SRC_GAME_DATA = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Tales of Seikyu\Tales Of Seikyu_Data")
sys.path.insert(0, str(REPO / "src"))

from tos_ko_patcher.core import (  # noqa: E402
    BAG_GLOB,
    EXCEL_GLOB,
    PATCH_VERSION,
    ensure_external,
    has_ptr,
    key_column_for_schema,
    parse_acf_field,
    parse_string_table,
    planned_excel_textassets,
    save_textassets_to_bundle,
    schema_for_textasset,
    sha256_file,
    textassets_from_bundle,
    write_string,
)

PREVIOUS_EXCEL_SOURCE = SRC_GAME_DATA / ".tos_korean_patch/backups/0.1.3-playtest.20260623/configs_assets_excel_f49ac7551e791fb388bd02ccb81a6a88.bundle.c7cc2e47a44f1c881c7c9c9d62d1a4b51060f061025a5f4ef663abc05bce1cc9.bak"
CURRENT_EXCEL_BUNDLE_NAME = "configs_assets_excel_133f2db0592e8e139c965fee90b07c1c.bundle"
EXCEL_SOURCE = SRC_GAME_DATA / ".tos_korean_patch/baselines/0.1.6-playtest.20260625/excel.d973dcdac6fbde16.bak"
BAG_SOURCE = SRC_GAME_DATA / ".korean_patch/backups/uiview_assets_bagfunctionitem_4151e323e15f7662e9ca55d7135ecfd4.bundle.43f3dbeb5cc829e9fd282b19bb3a6155de4a7769459296db8a48390be27bfc85.visual_lqa_351.bak"
BAG_CURRENT = SRC_GAME_DATA / "StreamingAssets/aa/StandaloneWindows64/uiview_assets_bagfunctionitem_4151e323e15f7662e9ca55d7135ecfd4.bundle"
PREVIOUS_PAYLOAD = REPO / "payload/patch_payload.json"
STEAM_MANIFEST = SRC_GAME_DATA.parents[2] / "appmanifest_2340520.acf"

UI_CONFIG_JAPANESE = "i18n_uiconfig_japanese"
OLD_UI_FONT_ALIAS = "line_seed_jp"
KOREAN_UI_FONT_ALIAS = "zh_cn_serif"
ZH_SERIF_CAB = "CAB-60817ce547ef0bba62727219c74c499f"
ZH_SERIF_EXTERNAL = f"archive:/{ZH_SERIF_CAB}/{ZH_SERIF_CAB}"
ZH_SERIF_FONT_PATH_ID = 3547074879389643962
LIBERATION_FONT_PATH_ID = -7997044049995672069


def current_build_id() -> str:
    if not STEAM_MANIFEST.exists():
        return ""
    return parse_acf_field(STEAM_MANIFEST.read_text(encoding="utf-8", errors="ignore"), "buildid")


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
    return json.loads(PREVIOUS_PAYLOAD.read_text(encoding="utf-8"))


def source_identity_index(bundle: Path) -> dict[str, set[tuple[str, str]]]:
    assets = textassets_from_bundle(bundle)
    identities: dict[str, set[tuple[str, str]]] = {}
    for name, raw in assets.items():
        schema = schema_for_textasset(name)
        try:
            table = parse_string_table(name, raw, schema)
        except Exception:
            continue
        key_name = key_column_for_schema(schema)
        identities[name] = {(str(row["row_id"]), str(row.get(key_name, ""))) for row in table.rows}
    return identities


def source_key_index(bundle: Path) -> dict[str, dict[str, str]]:
    assets = textassets_from_bundle(bundle)
    result: dict[str, dict[str, str]] = {}
    for name, raw in assets.items():
        schema = schema_for_textasset(name)
        try:
            table = parse_string_table(name, raw, schema)
        except Exception:
            continue
        key_name = key_column_for_schema(schema)
        by_key: dict[str, str] = {}
        duplicate_keys: set[str] = set()
        for row in table.rows:
            key = str(row.get(key_name, ""))
            if key in by_key:
                duplicate_keys.add(key)
            by_key[key] = str(row["row_id"])
        for key in duplicate_keys:
            by_key.pop(key, None)
        result[name] = by_key
    return result


def normalize_source_text(value: str) -> str:
    return " ".join(value.split())


def source_row_index(bundle: Path) -> dict[str, dict[str, dict[str, str]]]:
    assets = textassets_from_bundle(bundle)
    result: dict[str, dict[str, dict[str, str]]] = {}
    for name, raw in assets.items():
        schema = schema_for_textasset(name)
        try:
            table = parse_string_table(name, raw, schema)
        except Exception:
            continue
        key_name = key_column_for_schema(schema)
        result[name] = {
            str(row["row_id"]): {
                "key": str(row.get(key_name, "")),
                "source_ja_normalized": normalize_source_text(str(row.get("source_ja", ""))),
            }
            for row in table.rows
        }
    return result


def build_rows(
    previous_payload: dict[str, Any],
    source_bundle: Path,
    previous_source_bundle: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    source_identities = source_identity_index(source_bundle)
    source_keys = source_key_index(source_bundle)
    current_rows = source_row_index(source_bundle)
    previous_rows = source_row_index(previous_source_bundle)
    rows: list[dict[str, Any]] = []
    dropped: list[dict[str, Any]] = []
    remapped: list[dict[str, Any]] = []
    source_text_remapped: list[dict[str, Any]] = []
    for entry in previous_payload["excel_bundle"]["patch_rows"]:
        identity = (str(entry["row_id"]), str(entry["key"]))
        textasset = str(entry["textasset"])
        if identity in source_identities.get(textasset, set()):
            rows.append(entry)
            continue
        current_row_id = source_keys.get(textasset, {}).get(str(entry["key"]))
        if current_row_id:
            updated = dict(entry)
            updated["row_id"] = current_row_id
            rows.append(updated)
            remapped.append({**entry, "new_row_id": current_row_id})
            continue
        previous_row = previous_rows.get(textasset, {}).get(str(entry["row_id"]))
        current_row = current_rows.get(textasset, {}).get(str(entry["row_id"]))
        if previous_row and current_row and previous_row["source_ja_normalized"] == current_row["source_ja_normalized"]:
            updated = dict(entry)
            updated["key"] = current_row["key"]
            rows.append(updated)
            source_text_remapped.append({**entry, "new_key": current_row["key"]})
            continue
        dropped.append(entry)
    return rows, dropped, remapped, source_text_remapped


def source_diff(previous_source: Path, current_source: Path) -> dict[str, Any]:
    previous = source_identity_index(previous_source)
    current = source_identity_index(current_source)
    removed = []
    added = []
    for textasset in sorted(set(previous) | set(current)):
        previous_keys = previous.get(textasset, set())
        current_keys = current.get(textasset, set())
        for row_id, key in sorted(previous_keys - current_keys):
            removed.append({"textasset": textasset, "row_id": row_id, "key": key})
        for row_id, key in sorted(current_keys - previous_keys):
            added.append({"textasset": textasset, "row_id": row_id, "key": key})
    return {
        "previous_source_sha256": sha256_file(previous_source),
        "current_source_sha256": sha256_file(current_source),
        "removed_row_count": len(removed),
        "added_row_count": len(added),
        "removed_rows_sample": removed[:20],
        "added_rows_sample": added[:20],
    }


def ui_font_alias_source_count(source_bundle: Path) -> int:
    raw = textassets_from_bundle(source_bundle)[UI_CONFIG_JAPANESE]
    return raw.count(write_string(OLD_UI_FONT_ALIAS))


def previous_accepted_hashes(previous_payload: dict[str, Any], bundle_key: str) -> list[str]:
    bundle = previous_payload[bundle_key]
    hashes = set(bundle.get("accepted_patched_sha256", []))
    if bundle.get("target_sha256"):
        hashes.add(str(bundle["target_sha256"]))
    return sorted(item for item in hashes if item)


def write_payload(payload: dict[str, Any]) -> Path:
    out = REPO / "payload/patch_payload.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out


def apply_bag_to_temp(source: Path, payload: dict[str, Any]) -> str:
    import UnityPy

    with tempfile.TemporaryDirectory(prefix="tos-ko-bag-payload-", ignore_cleanup_errors=True) as temp:
        temp = Path(temp)
        target = temp / source.name
        shutil.copy2(source, target)
        bag = payload["bag_function_bundle"]
        font_patch = bag["font_patch"]
        env = UnityPy.load(str(target))
        asset = env.assets[0]
        file_id, _ = ensure_external(asset, font_patch["external_path"])
        for obj in env.objects:
            if obj.type.name != "MonoBehaviour":
                continue
            try:
                tree = obj.read_typetree()
            except Exception:
                continue
            if tree.get("m_Name") != font_patch["local_font_name"]:
                continue
            table = tree.setdefault("m_FallbackFontAssetTable", [])
            if not has_ptr(table, file_id, int(font_patch["fallback_font_path_id"])):
                table.append({"m_FileID": file_id, "m_PathID": int(font_patch["fallback_font_path_id"])})
                obj.save_typetree(tree)
        out_dir = temp / "out"
        out_dir.mkdir()
        env.save(out_path=str(out_dir))
        return sha256_file(out_dir / source.name)


def main() -> int:
    previous_payload = load_previous_release_payload()
    rows, dropped_rows, remapped_rows, source_text_remapped_rows = build_rows(previous_payload, EXCEL_SOURCE, PREVIOUS_EXCEL_SOURCE)
    diff = source_diff(PREVIOUS_EXCEL_SOURCE, EXCEL_SOURCE)
    payload: dict[str, Any] = {
        "patch_version": PATCH_VERSION,
        "game": "Tales of Seikyu",
        "language": "ko",
        "supported_platform": "Steam Windows",
        "generated_from": {
            "steam_buildid": current_build_id(),
            "excel_source_sha256": sha256_file(EXCEL_SOURCE),
            "previous_excel_source_sha256": sha256_file(PREVIOUS_EXCEL_SOURCE),
            "previous_payload_rows": len(previous_payload["excel_bundle"]["patch_rows"]),
            "dropped_previous_payload_rows": len(dropped_rows),
            "dropped_previous_payload_rows_sample": dropped_rows[:20],
            "remapped_previous_payload_rows": len(remapped_rows),
            "remapped_previous_payload_rows_sample": remapped_rows[:20],
            "source_text_remapped_previous_payload_rows": len(source_text_remapped_rows),
            "source_text_remapped_previous_payload_rows_sample": source_text_remapped_rows[:20],
            "source_diff_from_previous_build": diff,
            "bag_source_sha256": sha256_file(BAG_SOURCE),
            "bag_reference_current_sha256": sha256_file(BAG_CURRENT),
        },
        "excel_bundle": {
            "glob": EXCEL_GLOB,
            "source_sha256": sha256_file(EXCEL_SOURCE),
            "target_sha256": "",
            "accepted_patched_sha256": previous_accepted_hashes(previous_payload, "excel_bundle"),
            "ui_font_patch": {
                "textasset": UI_CONFIG_JAPANESE,
                "old_alias": OLD_UI_FONT_ALIAS,
                "new_alias": KOREAN_UI_FONT_ALIAS,
                "expected_replacements": ui_font_alias_source_count(EXCEL_SOURCE),
            },
            "patch_rows": rows,
        },
        "bag_function_bundle": {
            "glob": BAG_GLOB,
            "source_sha256": sha256_file(BAG_SOURCE),
            "target_sha256": sha256_file(BAG_CURRENT),
            "accepted_patched_sha256": sorted(set(previous_accepted_hashes(previous_payload, "bag_function_bundle") + [sha256_file(BAG_CURRENT)])),
            "font_patch": {
                "local_font_name": "LiberationSans SDF",
                "local_font_path_id": LIBERATION_FONT_PATH_ID,
                "external_path": ZH_SERIF_EXTERNAL,
                "fallback_font_path_id": ZH_SERIF_FONT_PATH_ID,
            },
        },
    }
    payload_path = write_payload(payload)

    with tempfile.TemporaryDirectory(prefix="tos-ko-excel-payload-", ignore_cleanup_errors=True) as temp:
        temp = Path(temp)
        data_root = temp / "Tales Of Seikyu_Data"
        target_dir = data_root / "StreamingAssets/aa/StandaloneWindows64"
        target_dir.mkdir(parents=True)
        temp_excel = target_dir / CURRENT_EXCEL_BUNDLE_NAME
        shutil.copy2(EXCEL_SOURCE, temp_excel)
        planned, _ = planned_excel_textassets(temp_excel, payload)
        saved = save_textassets_to_bundle(temp_excel, temp / "out", planned)
        excel_hash = sha256_file(saved)
    bag_hash = apply_bag_to_temp(BAG_SOURCE, payload)

    if excel_hash != payload["excel_bundle"]["target_sha256"]:
        payload["excel_bundle"]["target_sha256"] = excel_hash
        payload["excel_bundle"]["accepted_patched_sha256"] = sorted(set(payload["excel_bundle"]["accepted_patched_sha256"] + [excel_hash]))
    if bag_hash != payload["bag_function_bundle"]["target_sha256"]:
        payload["bag_function_bundle"]["target_sha256"] = bag_hash
        payload["bag_function_bundle"]["accepted_patched_sha256"] = sorted(set(payload["bag_function_bundle"]["accepted_patched_sha256"] + [bag_hash]))
    payload_path = write_payload(payload)
    print(
        json.dumps(
            {
                "status": "pass",
                "payload": str(payload_path),
                "patch_rows": len(rows),
                "dropped_previous_payload_rows": len(dropped_rows),
                "remapped_previous_payload_rows": len(remapped_rows),
                "source_text_remapped_previous_payload_rows": len(source_text_remapped_rows),
                "steam_buildid": current_build_id(),
                "excel_source_sha256": payload["excel_bundle"]["source_sha256"],
                "excel_target_sha256": payload["excel_bundle"]["target_sha256"],
                "bag_source_sha256": payload["bag_function_bundle"]["source_sha256"],
                "bag_target_sha256": payload["bag_function_bundle"]["target_sha256"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
