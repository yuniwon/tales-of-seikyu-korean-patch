from __future__ import annotations

import json
import shutil
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
    SCHEMA_COLUMNS,
    ensure_external,
    has_ptr,
    parse_string_table,
    planned_excel_textassets,
    save_textassets_to_bundle,
    schema_for_textasset,
    sha256_file,
    textassets_from_bundle,
)

EXCEL_SOURCE = SRC_GAME_DATA / ".korean_patch/backups/configs_assets_excel_faab60dac21aead7056d09e73c9da19c.bundle.5d50ce6257b1d8ca8231f59abe183da0968fd4297d943f1527a7e523be291595.bak"
EXCEL_CURRENT = SRC_GAME_DATA / "StreamingAssets/aa/StandaloneWindows64/configs_assets_excel_faab60dac21aead7056d09e73c9da19c.bundle"
BAG_SOURCE = SRC_GAME_DATA / ".korean_patch/backups/uiview_assets_bagfunctionitem_4151e323e15f7662e9ca55d7135ecfd4.bundle.43f3dbeb5cc829e9fd282b19bb3a6155de4a7769459296db8a48390be27bfc85.visual_lqa_351.bak"
BAG_CURRENT = SRC_GAME_DATA / "StreamingAssets/aa/StandaloneWindows64/uiview_assets_bagfunctionitem_4151e323e15f7662e9ca55d7135ecfd4.bundle"

ZH_SERIF_CAB = "CAB-60817ce547ef0bba62727219c74c499f"
ZH_SERIF_EXTERNAL = f"archive:/{ZH_SERIF_CAB}/{ZH_SERIF_CAB}"
ZH_SERIF_FONT_PATH_ID = 3547074879389643962
LIBERATION_FONT_PATH_ID = -7997044049995672069


def key_column(schema: str) -> str:
    return "text_id" if "text_id" in SCHEMA_COLUMNS[schema] else "row_key"


def build_rows() -> list[dict[str, Any]]:
    source_assets = textassets_from_bundle(EXCEL_SOURCE)
    current_assets = textassets_from_bundle(EXCEL_CURRENT)
    rows: list[dict[str, Any]] = []
    for name in sorted(set(source_assets) & set(current_assets)):
        schema = schema_for_textasset(name)
        try:
            source_table = parse_string_table(name, source_assets[name], schema)
            current_table = parse_string_table(name, current_assets[name], schema)
        except Exception:
            continue
        key_name = key_column(schema)
        source_by_key = {(str(row["row_id"]), str(row.get(key_name, ""))): row for row in source_table.rows}
        current_by_key = {(str(row["row_id"]), str(row.get(key_name, ""))): row for row in current_table.rows}
        for identity, current_row in sorted(current_by_key.items()):
            source_row = source_by_key.get(identity)
            if source_row is None:
                continue
            if str(source_row.get("source_ja", "")) == str(current_row.get("source_ja", "")):
                continue
            rows.append(
                {
                    "textasset": name,
                    "schema": schema,
                    "row_id": identity[0],
                    "key": identity[1],
                    "source_ja": str(current_row.get("source_ja", "")),
                }
            )
    return rows


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
    rows = build_rows()
    payload: dict[str, Any] = {
        "patch_version": PATCH_VERSION,
        "game": "Tales of Seikyu",
        "language": "ko",
        "supported_platform": "Steam Windows",
        "generated_from": {
            "excel_source_sha256": sha256_file(EXCEL_SOURCE),
            "excel_reference_current_sha256": sha256_file(EXCEL_CURRENT),
            "bag_source_sha256": sha256_file(BAG_SOURCE),
            "bag_reference_current_sha256": sha256_file(BAG_CURRENT),
        },
        "excel_bundle": {
            "glob": EXCEL_GLOB,
            "source_sha256": sha256_file(EXCEL_SOURCE),
            "target_sha256": sha256_file(EXCEL_CURRENT),
            "accepted_patched_sha256": [sha256_file(EXCEL_CURRENT)],
            "patch_rows": rows,
        },
        "bag_function_bundle": {
            "glob": BAG_GLOB,
            "source_sha256": sha256_file(BAG_SOURCE),
            "target_sha256": sha256_file(BAG_CURRENT),
            "accepted_patched_sha256": [sha256_file(BAG_CURRENT)],
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
        temp_excel = target_dir / EXCEL_CURRENT.name
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
