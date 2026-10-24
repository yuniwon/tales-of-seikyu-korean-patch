from __future__ import annotations

import json
import csv
import re
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
    row_source_fingerprint,
    save_textassets_to_bundle,
    schema_for_textasset,
    sha256_file,
    textassets_from_bundle,
    write_string,
)

PREVIOUS_EXCEL_SOURCE = SRC_GAME_DATA / ".tos_korean_patch/backups/0.1.10-playtest.20260702/excel.6482ecc747ec57e0.bak"
CURRENT_EXCEL_BUNDLE_NAME = "configs_assets_excel_819141916302f0cf565fc9cfe6d0ffc7.bundle"
CURRENT_BAG_BUNDLE_NAME = "uiview_assets_bagfunctionitem_c03f77ea6e9f3cdb429d41f0f3886553.bundle"
EXCEL_SOURCE = SRC_GAME_DATA / "StreamingAssets/aa/StandaloneWindows64" / CURRENT_EXCEL_BUNDLE_NAME
BAG_SOURCE = SRC_GAME_DATA / ".tos_korean_patch/baselines/0.1.7-playtest.20260701/bag.e4eabffd3e04ce96.bak"
BAG_CURRENT = SRC_GAME_DATA / "StreamingAssets/aa/StandaloneWindows64" / CURRENT_BAG_BUNDLE_NAME
PREVIOUS_PAYLOAD = REPO / "payload/patch_payload.json"
STEAM_MANIFEST = SRC_GAME_DATA.parents[2] / "appmanifest_2340520.acf"
SOURCE_UPDATE_WORKSETS: list[Path] = []
REVIEWED_POLISH = REPO / "payload/reviewed_polish.tsv"

SURFACE_TEXT_OVERRIDES = {
    # This compact vertical button uses the same font asset as working item text,
    # but Korean dynamic glyphs still render as fallback squares on this surface.
    # Keep the workaround scoped to the three visible inventory sort tabs.
    ("inventory__sort_type_desc", "5", "inventory__sort_type/desc_22b777e6fcb613b8ba83ced9594cd07e"): "Normal",
    ("inventory__sort_type_desc", "6", "inventory__sort_type/desc_0e46d8d6b7a0096b06c0603c9fca9aad"): "Quest",
    ("inventory__sort_type_desc", "7", "inventory__sort_type/desc_7402599bc6350c095fb3ca545d950480"): "Gold",
}

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


def unpatched_excel_source(bundle: Path, previous_payload: dict[str, Any]) -> Path:
    excel = previous_payload["excel_bundle"]
    known_patches = set(excel.get("accepted_patched_sha256", [])) | {excel["target_sha256"]}
    if sha256_file(bundle) not in known_patches:
        return bundle
    expected = str(excel["source_sha256"])
    candidates = []
    for folder in ("baselines", "backups"):
        candidates.extend((SRC_GAME_DATA / ".tos_korean_patch" / folder).glob(f"*/excel.{expected[:16]}.bak"))
    for candidate in sorted(candidates):
        if sha256_file(candidate) == expected:
            return candidate
    raise RuntimeError("The installed Excel is patched; a hash-verified clean source backup is required to generate translations.")


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


def source_key_row_index(bundle: Path) -> dict[str, dict[str, dict[str, object]]]:
    assets = textassets_from_bundle(bundle)
    result: dict[str, dict[str, dict[str, object]]] = {}
    for name, raw in assets.items():
        schema = schema_for_textasset(name)
        try:
            table = parse_string_table(name, raw, schema)
        except Exception:
            continue
        key_name = key_column_for_schema(schema)
        by_key: dict[str, dict[str, object]] = {}
        duplicate_keys: set[str] = set()
        for row in table.rows:
            key = str(row.get(key_name, ""))
            if key in by_key:
                duplicate_keys.add(key)
            by_key[key] = row
        for key in duplicate_keys:
            by_key.pop(key, None)
        result[name] = by_key
    return result


def source_fingerprint_index(bundle: Path) -> dict[str, dict[str, dict[str, object]]]:
    assets = textassets_from_bundle(bundle)
    result: dict[str, dict[str, dict[str, object]]] = {}
    for name, raw in assets.items():
        schema = schema_for_textasset(name)
        try:
            table = parse_string_table(name, raw, schema)
        except Exception:
            continue
        by_fingerprint: dict[str, dict[str, object]] = {}
        duplicate_fingerprints: set[str] = set()
        for row in table.rows:
            fingerprint = row_source_fingerprint(row, schema)
            if fingerprint in by_fingerprint:
                duplicate_fingerprints.add(fingerprint)
            by_fingerprint[fingerprint] = row
        for fingerprint in duplicate_fingerprints:
            by_fingerprint.pop(fingerprint, None)
        result[name] = by_fingerprint
    return result


def source_ja_text_index(bundle: Path) -> dict[str, dict[str, dict[str, object]]]:
    assets = textassets_from_bundle(bundle)
    result: dict[str, dict[str, dict[str, object]]] = {}
    for name, raw in assets.items():
        schema = schema_for_textasset(name)
        try:
            table = parse_string_table(name, raw, schema)
        except Exception:
            continue
        by_source_ja: dict[str, dict[str, object]] = {}
        duplicate_source_ja: set[str] = set()
        for row in table.rows:
            source_ja = normalize_source_text(str(row.get("source_ja", "")))
            if not source_ja:
                continue
            if source_ja in by_source_ja:
                duplicate_source_ja.add(source_ja)
            by_source_ja[source_ja] = row
        for source_ja in duplicate_source_ja:
            by_source_ja.pop(source_ja, None)
        result[name] = by_source_ja
    return result


def normalize_source_text(value: str) -> str:
    return " ".join(value.split())


def source_languages_match(left: dict[str, object], right: dict[str, object]) -> bool:
    return all(
        normalize_source_text(str(left.get(field, ""))) == normalize_source_text(str(right.get(field, "")))
        for field in ("source_en", "source_zh_cn", "source_ja")
    )


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


def source_row_lookup(bundle: Path) -> dict[tuple[str, str, str], dict[str, object]]:
    assets = textassets_from_bundle(bundle)
    result: dict[tuple[str, str, str], dict[str, object]] = {}
    for name, raw in assets.items():
        schema = schema_for_textasset(name)
        try:
            table = parse_string_table(name, raw, schema)
        except Exception:
            continue
        key_name = key_column_for_schema(schema)
        for row in table.rows:
            result[(name, str(row["row_id"]), str(row.get(key_name, "")))] = row
    return result


def enrich_rows_with_source_fingerprints(rows: list[dict[str, Any]], source_bundle: Path) -> list[dict[str, Any]]:
    lookup = source_row_lookup(source_bundle)
    enriched: list[dict[str, Any]] = []
    for entry in rows:
        key = (str(entry["textasset"]), str(entry["row_id"]), str(entry["key"]))
        source_row = lookup.get(key)
        if source_row is None:
            raise RuntimeError(f"cannot fingerprint missing source row: {key}")
        schema = str(entry["schema"])
        updated = dict(entry)
        updated["source_fingerprint"] = row_source_fingerprint(source_row, schema)
        enriched.append(updated)
    return enriched


def build_rows(
    previous_payload: dict[str, Any],
    source_bundle: Path,
    previous_source_bundle: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    source_lookup = source_row_lookup(source_bundle)
    source_keys = source_key_row_index(source_bundle)
    source_fingerprints = source_fingerprint_index(source_bundle)
    source_ja_texts = source_ja_text_index(source_bundle)
    current_rows = source_row_index(source_bundle)
    previous_rows = source_row_index(previous_source_bundle)
    previous_source_lookup = source_row_lookup(previous_source_bundle)
    rows: list[dict[str, Any]] = []
    dropped: list[dict[str, Any]] = []
    remapped: list[dict[str, Any]] = []
    fingerprint_remapped: list[dict[str, Any]] = []
    source_text_remapped: list[dict[str, Any]] = []
    for entry in previous_payload["excel_bundle"]["patch_rows"]:
        textasset = str(entry["textasset"])
        schema = str(entry["schema"])
        row_id = str(entry["row_id"])
        key = str(entry["key"])
        expected_fingerprint = str(entry.get("source_fingerprint") or "")
        identity = (textasset, row_id, key)
        source_row = source_lookup.get(identity)
        if source_row is not None:
            if not expected_fingerprint or row_source_fingerprint(source_row, schema) == expected_fingerprint:
                rows.append(entry)
            elif (previous_source_row := previous_source_lookup.get(identity)) is not None and source_languages_match(
                previous_source_row, source_row
            ):
                rows.append(entry)
            else:
                dropped.append({**entry, "drop_reason": "source_changed"})
            continue
        source_row = source_keys.get(textasset, {}).get(key)
        if source_row is not None:
            current_fingerprint = row_source_fingerprint(source_row, schema)
            previous_source_row = previous_source_lookup.get(identity)
            if (
                expected_fingerprint
                and current_fingerprint != expected_fingerprint
                and not (previous_source_row and source_languages_match(previous_source_row, source_row))
            ):
                dropped.append({**entry, "drop_reason": "key_remap_source_changed", "new_row_id": str(source_row["row_id"])})
                continue
            updated = dict(entry)
            updated["row_id"] = str(source_row["row_id"])
            rows.append(updated)
            remapped.append({**entry, "new_row_id": str(source_row["row_id"])})
            continue
        if expected_fingerprint:
            source_row = source_fingerprints.get(textasset, {}).get(expected_fingerprint)
            if source_row is not None:
                key_name = key_column_for_schema(schema)
                updated = dict(entry)
                updated["row_id"] = str(source_row["row_id"])
                updated["key"] = str(source_row.get(key_name, ""))
                rows.append(updated)
                fingerprint_remapped.append({**entry, "new_row_id": updated["row_id"], "new_key": updated["key"]})
                continue
        previous_row = previous_rows.get(textasset, {}).get(row_id)
        previous_source_ja = previous_row["source_ja_normalized"] if previous_row else ""
        source_row = source_ja_texts.get(textasset, {}).get(previous_source_ja) if previous_source_ja else None
        if source_row is not None:
            key_name = key_column_for_schema(schema)
            updated = dict(entry)
            updated["row_id"] = str(source_row["row_id"])
            updated["key"] = str(source_row.get(key_name, ""))
            rows.append(updated)
            source_text_remapped.append({**entry, "new_row_id": updated["row_id"], "new_key": updated["key"]})
            continue
        previous_row = previous_rows.get(textasset, {}).get(str(entry["row_id"]))
        current_row = current_rows.get(textasset, {}).get(str(entry["row_id"]))
        if previous_row and current_row and previous_row["source_ja_normalized"] == current_row["source_ja_normalized"]:
            updated = dict(entry)
            updated["key"] = current_row["key"]
            rows.append(updated)
            source_text_remapped.append({**entry, "new_key": current_row["key"]})
            continue
        dropped.append({**entry, "drop_reason": "missing_or_changed"})
    return rows, dropped, remapped, fingerprint_remapped, source_text_remapped


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def source_update_rows(source_bundle: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    source_identities = source_identity_index(source_bundle)
    current_rows = source_row_index(source_bundle)
    rows: list[dict[str, Any]] = []
    remapped: list[dict[str, Any]] = []
    for workset in SOURCE_UPDATE_WORKSETS:
        for row in read_tsv(workset):
            if (row.get("review_status") or "").strip() != "proposal_ready":
                continue
            textasset = (row.get("source_textasset") or "").strip()
            row_id = (row.get("row_id") or "").strip()
            key = (row.get("dialog_key") or "").strip()
            korean = (row.get("korean_proposal") or "").strip()
            if not textasset or not row_id or not key or not korean:
                raise RuntimeError(f"incomplete source-update row in {workset}: row_id={row_id!r}")
            if "귀허" in korean:
                raise RuntimeError(f"forbidden legacy term remains in source-update row: {workset} row_id={row_id}")
            if (row_id, key) not in source_identities.get(textasset, set()):
                current_row = current_rows.get(textasset, {}).get(row_id)
                if not current_row:
                    raise RuntimeError(f"source-update row does not match current source: {textasset} {(row_id, key)}")
                remapped.append({"textasset": textasset, "row_id": row_id, "old_key": key, "new_key": current_row["key"]})
                key = current_row["key"]
            rows.append(
                {
                    "textasset": textasset,
                    "schema": schema_for_textasset(textasset),
                    "row_id": row_id,
                    "key": key,
                    "source_ja": korean,
                }
            )
    return rows, remapped


def merge_patch_rows(base_rows: list[dict[str, Any]], overlay_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int, int]:
    merged: list[dict[str, Any]] = []
    indexes: dict[tuple[str, str, str], int] = {}
    for row in base_rows:
        key = (str(row["textasset"]), str(row["row_id"]), str(row["key"]))
        indexes[key] = len(merged)
        merged.append(row)
    added = 0
    replaced = 0
    for row in overlay_rows:
        key = (str(row["textasset"]), str(row["row_id"]), str(row["key"]))
        if key in indexes:
            merged[indexes[key]] = row
            replaced += 1
        else:
            indexes[key] = len(merged)
            merged.append(row)
            added += 1
    return merged, added, replaced


def apply_surface_text_overrides(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    expected = set(SURFACE_TEXT_OVERRIDES)
    seen: set[tuple[str, str, str]] = set()
    updated_rows: list[dict[str, Any]] = []
    for row in rows:
        key = (str(row["textasset"]), str(row["row_id"]), str(row["key"]))
        if key in SURFACE_TEXT_OVERRIDES:
            updated = dict(row)
            updated["source_ja"] = SURFACE_TEXT_OVERRIDES[key]
            updated_rows.append(updated)
            seen.add(key)
        else:
            updated_rows.append(row)
    missing = sorted(expected - seen)
    if missing:
        raise RuntimeError(f"surface text override target rows missing: {missing}")
    return updated_rows


REVIEWED_SOURCE_TOKEN_REPAIRS = {
    ("i18n_custom", "Game_Name_CDJump"): (
        ("<i>", "</i>"),
        (),
    ),
    ("i18n_custom", "StoryBook_Collect"): (
        ("<i>", "</i>"),
        (),
    ),
    ("story_book__main_content_i18n", "story_book__main/content_i18n_e469a042375efc7baf91d715eafc3ba9"): (
        ("<b>", "<i>", "</i>", "</b>"),
        (),
    ),
    ("i18n_avg_default", "1818885489140342"): (
        ("<i>", "</i>"),
        (),
    ),
    ("i18n_avg_default", "1773671126447212"): (
        ("{highlight.default}", "{location.21}", "{highlight}"),
        ("{location.21}",),
    ),
    ("i18n_avg_default", "1773671126617422"): (
        ("{highlight}", "{location.16}", "{highlight.default}"),
        (),
    ),
    ("i18n_avg_default", "1813236155477442"): (
        ("{start_wedding_npc}", "{c.playername}", "{npc.WeddingNPC}"),
        ("{start_wedding_npc}",),
    ),
    ("i18n_avg_default", "1813236122144653"): (
        ("{start_wedding_npc}", "{c.playername}", "{npc.WeddingNPC}"),
        ("{c.playername}", "{npc.WeddingNPC}"),
    ),
    ("i18n_avg_default", "1809595912229486"): (
        ("{npc.BestLoverNpc}", "{npc.BestLoverNpc}"),
        (),
    ),
    ("i18n_avg_default", "1814629625282673"): (
        ("<shiver>", "</shiver>"),
        (),
    ),
    ("i18n_avg_default", "1814630351499405"): (
        ("{c.playername}",),
        (),
    ),
    ("i18n_avg_default", "1814630351499407"): (
        (),
        ("{c.playername}",),
    ),
    ("i18n_avg_default", "1814712403374107"): (
        (),
        ("<shiver>", "</shiver>"),
    ),
    ("i18n_avg_default", "1814712404686878"): (
        ("{c.playername}",),
        (),
    ),
    ("i18n_avg_default", "1814712406960167"): (
        ("<i>", "</i>"),
        (),
    ),
    ("i18n_avg_default", "1816057644940794"): (
        ("{c.playername}",),
        (),
    ),
    ("i18n_avg_default", "1794817603263553"): (
        ("{c.playername}",),
        (),
    ),
    ("i18n_avg_default", "1794817603263559"): (
        ("{c.playername}",),
        (),
    ),
    ("i18n_avg_default", "1795328179342409"): (
        ("{sw.Ninja}",),
        (),
    ),
    ("i18n_avg_default", "1813236083654884"): (
        ("{start_wedding_npc}", "{c.playername}", "{npc.WeddingNPC}"),
        ("{c.playername}", "{npc.WeddingNPC}"),
    ),
    ("i18n_avg_default", "1813235503409711"): (
        ("{start_wedding_npc}", "{c.playername}", "{npc.WeddingNPC}"),
        ("{start_wedding_npc}",),
    ),
    ("i18n_avg_default", "1813236151020540"): (
        ("{start_wedding_npc}", "{c.playername}", "{npc.WeddingNPC}"),
        ("{c.playername}", "{npc.WeddingNPC}"),
    ),
    ("i18n_avg_default", "1813236133572947"): (
        ("{start_wedding_npc}", "{c.playername}", "{npc.WeddingNPC}"),
        ("{c.playername}", "{npc.WeddingNPC}"),
    ),
    ("i18n_avg_default", "1795425752449203"): (
        ("<i>", "<I>", "</i>"),
        (),
    ),
    ("i18n_avg_default", "1813236111417799"): (
        ("{start_wedding_npc}", "{c.playername}", "{npc.WeddingNPC}"),
        ("{c.playername}", "{npc.WeddingNPC}"),
    ),
    ("i18n_alone_avg_default", "1806646314739610"): (
        ("<i>", "{c.playername}", "</i>"),
        (),
    ),
    ("i18n_avg_default", "1821352528199317"): (
        ("{c.playername}",),
        (),
    ),
    ("i18n_avg_default", "1776325335605723"): (
        ("<b>", "<i>", "{highlight.default}", "{highlight}", "</i>", "</b>"),
        (),
    ),
    ("i18n_avg_default", "1776325385311710"): (
        ("{c.playername}", "{highlight.default}", "<i>", "</i>", "{highlight}"),
        (),
    ),
    ("i18n_avg_default", "1776325508172271"): (
        ("<b>", "</b>"),
        (),
    ),
    ("i18n_avg_default", "1776325612988920"): (
        ("{c.playername}", "<i>", "</i>"),
        (),
    ),
    ("i18n_avg_default", "1777656980360898"): (
        ("{c.playername}", "{npc.4101}"),
        (),
    ),
    ("i18n_avg_default", "1777662268200786"): (
        ("{c.playername}",),
        (),
    ),
    ("i18n_avg_default", "1777662185212747"): (
        ("{c.playername}",),
        (),
    ),
    ("i18n_avg_default", "1776321964130778"): (
        ("<b>", "{highlight.default}", "{highlight}", "</b>"),
        (),
    ),
    ("i18n_avg_default", "1776321995108828"): (
        ("{highlight.default}", "<b>", "</b>", "{highlight}", "<i>", "</i>"),
        (),
    ),
    ("i18n_avg_default", "1804899039517200"): (
        ("{c.playername}", "{c.playername}"),
        (),
    ),
}


REVIEWED_ORIGINAL_MARKUP_REPAIRS = {
    ("i18n_avg_default", "1775429067206302"): (
        "</shiver>ゴロゴロ…</shiver>",
        ("</shiver>", "</shiver>"),
        ("<shiver>", "</shiver>"),
    ),
    ("i18n_avg_default", "1805256890597686"): (
        "<shiver>もっと食わせろぉぉぉ！！！</ishiver>",
        ("<shiver>", "</ishiver>"),
        ("<shiver>", "</shiver>"),
    ),
    ("i18n_avg_default", "1773671128313092"): (
        "刮目せよ～！\n<b>全能にして無敵の戦士…<b>",
        ("<b>", "<b>"),
        ("<b>", "</b>"),
    ),
}


REVIEWED_ORIGINAL_TOKEN_REPAIRS = {
    ("tutorial__ui_tutorial_desc", "tutorial__ui_tutorial/desc_0a87ea42380b270dff34a3bee3299d06"): (
        "より多くの色が必要の場合、{item.3444}を使います。\nカラースペクトルをスライドして、お気に入りの色を選んでください。",
        "如果这些预设颜色都不是你想要的，不妨来试试{item.25125}。\n滑动色谱，挑选你心仪的颜色。",
        "If you would like more colors, try using the {item.3444}.\nUse the slider to pick the perfect shade for you.",
        ("{item.3444}",),
        ("{item.25125}",),
    ),
    ("i18n_avg_default", "1820218594496168"): (
        "黒狐と戦ってたら、{c.playername}、\n気を失っちゃったんだよ！",
        "我当时在和黑暗狐狸战斗，然后就失去意识了！",
        "I was fighting the Dark Fox, then I blacked out!",
        ("{c.playername}",),
        (),
    ),
}


def validate_reviewed_tokens(identity: tuple[str, str], old: str, new: str, original: dict[str, Any]) -> None:
    """Restore exact audited contamination patterns to their Japanese slot contract."""
    pattern = r"\{[^{}]*\}|</?[^>]+>"
    old_tokens, new_tokens = tuple(re.findall(pattern, old)), tuple(re.findall(pattern, new))
    original_repair = REVIEWED_ORIGINAL_TOKEN_REPAIRS.get(identity)
    if original_repair is not None:
        source_ja, source_zh, source_en, malformed, canonical = original_repair
        if (original.get("source_ja") == source_ja
                and original.get("source_zh_cn") == source_zh
                and original.get("source_en") == source_en
                and old_tokens in {malformed, canonical} and new_tokens == canonical):
            return
        raise RuntimeError(f"reviewed polish original-token repair contract changed: {identity}")
    markup_repair = REVIEWED_ORIGINAL_MARKUP_REPAIRS.get(identity)
    if markup_repair is not None:
        source_ja, malformed, canonical = markup_repair
        if (original.get("source_ja") == source_ja
                and old_tokens in {malformed, canonical} and new_tokens == canonical):
            return
        raise RuntimeError(f"reviewed polish original-markup repair contract changed: {identity}")
    repair = REVIEWED_SOURCE_TOKEN_REPAIRS.get(identity)
    if repair is not None:
        contaminated, canonical = repair
        if (tuple(re.findall(pattern, str(original.get("source_ja", "")))) == canonical
                and new_tokens == canonical and old_tokens in {contaminated, canonical}):
            return
        raise RuntimeError(f"reviewed polish source-token repair contract changed: {identity}")
    if old_tokens != new_tokens:
        raise RuntimeError(f"reviewed polish token contract changed: {identity}")


REVIEWED_ADDITIONS = REPO / "payload/reviewed_additions.json"


def reviewed_addition_seeds(
    source_bundle: Path, registry: Path = REVIEWED_ADDITIONS,
) -> list[dict[str, Any]]:
    """Validate exact original rows; Korean remains in the approved TSV only."""
    contracts = json.loads(registry.read_text(encoding="utf-8"))
    if not isinstance(contracts, list):
        raise RuntimeError("reviewed addition registry must be a list")
    source = source_row_lookup(source_bundle)
    seen: set[tuple[str, str]] = set()
    for entry in contracts:
        required = {"textasset", "schema", "row_id", "key", "source_fingerprint", "source_ja"}
        if not isinstance(entry, dict) or set(entry) != required or not all(isinstance(v, str) for v in entry.values()):
            raise RuntimeError("reviewed addition contract fields invalid")
        identity = (entry["textasset"], entry["key"])
        if identity in seen:
            raise RuntimeError(f"duplicate reviewed addition contract: {identity}")
        seen.add(identity)
        original = source.get((entry["textasset"], entry["row_id"], entry["key"]))
        if (original is None or schema_for_textasset(entry["textasset"]) != entry["schema"]
                or row_source_fingerprint(original, entry["schema"]) != entry["source_fingerprint"]
                or original.get("source_ja") != entry["source_ja"]):
            raise RuntimeError(f"reviewed addition original source changed: {identity}")
    return contracts


def seed_reviewed_additions(
    rows: list[dict[str, Any]], source_bundle: Path, workset: Path = REVIEWED_POLISH,
    registry: Path = REVIEWED_ADDITIONS,
) -> tuple[list[dict[str, Any]], int]:
    contracts = reviewed_addition_seeds(source_bundle, registry)
    proposals = read_tsv(workset)
    result = [dict(row) for row in rows]
    added = 0
    for entry in contracts:
        identity = (entry["textasset"], entry["row_id"], entry["key"])
        approved = [p for p in proposals
                    if (p["source_textasset"], p["row_id"], p["dialog_key"]) == identity]
        if (len(approved) != 1 or approved[0].get("review_status") != "approved"
                or approved[0]["source_fingerprint"] != entry["source_fingerprint"]
                or approved[0]["old_target"] != entry["source_ja"]
                or not approved[0]["korean_proposal"].strip()):
            raise RuntimeError(f"reviewed addition requires exact approved translation: {identity}")
        candidates = [r for r in result if (r["textasset"], r["key"]) == (identity[0], identity[2])]
        if candidates:
            if (len(candidates) != 1 or str(candidates[0]["row_id"]) != identity[1]
                    or candidates[0]["schema"] != entry["schema"]
                    or candidates[0]["source_fingerprint"] != entry["source_fingerprint"]):
                raise RuntimeError(f"reviewed addition identity collision: {identity}")
            # Never reset an existing Korean row: the ordinary overlay checks conflicts.
        else:
            result.append(dict(entry))
            added += 1
    return result, added


def apply_reviewed_polish(
    rows: list[dict[str, Any]], source_bundle: Path, workset: Path = REVIEWED_POLISH,
) -> tuple[list[dict[str, Any]], int]:
    """Apply accepted text only while source and previous Korean still agree."""
    if not workset.exists():
        raise RuntimeError(f"reviewed polish workset missing: {workset}")
    proposals = read_tsv(workset)
    source = source_row_lookup(source_bundle)
    indexes: dict[tuple[str, str], list[int]] = {}
    for index, row in enumerate(rows):
        indexes.setdefault((str(row["textasset"]), str(row["key"])), []).append(index)
    result = [dict(row) for row in rows]
    seen: set[int] = set()
    for proposal in proposals:
        if proposal.get("review_status") != "approved":
            raise RuntimeError("reviewed polish contains an unapproved row")
        identity = (proposal["source_textasset"], proposal["dialog_key"])
        candidates = indexes.get(identity, [])
        exact = [i for i in candidates if str(rows[i]["row_id"]) == proposal["row_id"]]
        matches = exact or candidates
        if len(matches) != 1:
            raise RuntimeError(f"reviewed polish target missing or ambiguous: {identity}")
        index = matches[0]
        if index in seen:
            raise RuntimeError(f"duplicate reviewed polish target: {identity}")
        seen.add(index)
        entry = rows[index]
        key = (str(entry["textasset"]), str(entry["row_id"]), str(entry["key"]))
        original = source.get(key)
        if original is None or row_source_fingerprint(original, entry["schema"]) != proposal["source_fingerprint"]:
            raise RuntimeError(f"reviewed polish source changed: {identity}")
        old, new = proposal["old_target"], proposal["korean_proposal"]
        if not new.strip() or str(entry["source_ja"]) not in {old, new}:
            raise RuntimeError(f"reviewed polish Korean conflict: {identity}")
        validate_reviewed_tokens(identity, old, new, original)
        result[index]["source_ja"] = new
    return result, len(seen)


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
        local_font_names = {str(name) for name in font_patch.get("local_font_names") or [font_patch["local_font_name"]]}
        env = UnityPy.load(str(target))
        asset = env.assets[0]
        file_id, _ = ensure_external(asset, font_patch["external_path"])
        seen_names: set[str] = set()
        for obj in env.objects:
            if obj.type.name != "MonoBehaviour":
                continue
            try:
                tree = obj.read_typetree()
            except Exception:
                continue
            if tree.get("m_Name") not in local_font_names:
                continue
            seen_names.add(str(tree.get("m_Name") or ""))
            table = tree.setdefault("m_FallbackFontAssetTable", [])
            if not has_ptr(table, file_id, int(font_patch["fallback_font_path_id"])):
                table.append({"m_FileID": file_id, "m_PathID": int(font_patch["fallback_font_path_id"])})
                obj.save_typetree(tree)
        missing_names = sorted(local_font_names - seen_names)
        if missing_names:
            raise RuntimeError(f"bag font targets missing: {missing_names}")
        out_dir = temp / "out"
        out_dir.mkdir()
        env.save(out_path=str(out_dir))
        return sha256_file(out_dir / source.name)


def main() -> int:
    previous_payload = load_previous_release_payload()
    excel_source = unpatched_excel_source(EXCEL_SOURCE, previous_payload)
    rows, dropped_rows, remapped_rows, fingerprint_remapped_rows, source_text_remapped_rows = build_rows(
        previous_payload, excel_source, PREVIOUS_EXCEL_SOURCE
    )
    overlay_rows, source_update_remapped_rows = source_update_rows(excel_source)
    rows, source_update_added_rows, source_update_replaced_rows = merge_patch_rows(rows, overlay_rows)
    rows = apply_surface_text_overrides(rows)
    rows = enrich_rows_with_source_fingerprints(rows, excel_source)
    rows, reviewed_addition_count = seed_reviewed_additions(rows, excel_source)
    rows, reviewed_polish_count = apply_reviewed_polish(rows, excel_source)
    # Keep the three known broken-glyph surfaces safe in the shipped build;
    # their approved Korean remains in the editorial TSV for future font work.
    rows = apply_surface_text_overrides(rows)
    diff = source_diff(PREVIOUS_EXCEL_SOURCE, excel_source)
    payload: dict[str, Any] = {
        "patch_version": PATCH_VERSION,
        "game": "Tales of Seikyu",
        "language": "ko",
        "supported_platform": "Steam Windows",
        "generated_from": {
            "steam_buildid": current_build_id(),
            "excel_source_sha256": sha256_file(excel_source),
            "previous_excel_source_sha256": sha256_file(PREVIOUS_EXCEL_SOURCE),
            "previous_payload_rows": len(previous_payload["excel_bundle"]["patch_rows"]),
            "dropped_previous_payload_rows": len(dropped_rows),
            "dropped_previous_payload_rows_sample": dropped_rows[:20],
            "remapped_previous_payload_rows": len(remapped_rows),
            "remapped_previous_payload_rows_sample": remapped_rows[:20],
            "fingerprint_remapped_previous_payload_rows": len(fingerprint_remapped_rows),
            "fingerprint_remapped_previous_payload_rows_sample": fingerprint_remapped_rows[:20],
            "source_text_remapped_previous_payload_rows": len(source_text_remapped_rows),
            "source_text_remapped_previous_payload_rows_sample": source_text_remapped_rows[:20],
            "source_update_worksets": [str(path) for path in SOURCE_UPDATE_WORKSETS],
            "source_update_rows": len(overlay_rows),
            "source_update_remapped_rows": len(source_update_remapped_rows),
            "source_update_remapped_rows_sample": source_update_remapped_rows[:20],
            "source_update_added_rows": source_update_added_rows,
            "source_update_replaced_rows": source_update_replaced_rows,
            "reviewed_polish_rows": reviewed_polish_count,
            "reviewed_addition_rows": reviewed_addition_count,
            "reviewed_additions_registry": str(REVIEWED_ADDITIONS.relative_to(REPO)),
            "reviewed_additions_sha256": sha256_file(REVIEWED_ADDITIONS),
            "reviewed_polish_workset": str(REVIEWED_POLISH.relative_to(REPO)),
            "reviewed_polish_sha256": sha256_file(REVIEWED_POLISH),
            "source_diff_from_previous_build": diff,
            "bag_source_sha256": sha256_file(BAG_SOURCE),
            "bag_reference_current_sha256": sha256_file(BAG_CURRENT),
        },
        "excel_bundle": {
            "glob": EXCEL_GLOB,
            "source_sha256": sha256_file(excel_source),
            "target_sha256": "",
            "accepted_patched_sha256": previous_accepted_hashes(previous_payload, "excel_bundle"),
            "ui_font_patch": {
                "textasset": UI_CONFIG_JAPANESE,
                "old_alias": OLD_UI_FONT_ALIAS,
                "new_alias": KOREAN_UI_FONT_ALIAS,
                "expected_replacements": ui_font_alias_source_count(excel_source),
                "minimum_replacements": 1,
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
                "local_font_names": ["LiberationSans SDF", "LiberationSans SDF - Fallback"],
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
        shutil.copy2(excel_source, temp_excel)
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
                "fingerprint_remapped_previous_payload_rows": len(fingerprint_remapped_rows),
                "source_text_remapped_previous_payload_rows": len(source_text_remapped_rows),
                "source_update_rows": len(overlay_rows),
                "source_update_remapped_rows": len(source_update_remapped_rows),
                "source_update_added_rows": source_update_added_rows,
                "source_update_replaced_rows": source_update_replaced_rows,
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
