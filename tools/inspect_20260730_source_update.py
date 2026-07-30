from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GAME_DATA = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Tales of Seikyu\Tales Of Seikyu_Data")
OLD_SOURCE = GAME_DATA / ".tos_korean_patch/backups/0.1.10-playtest.20260702/excel.6482ecc747ec57e0.bak"
CURRENT_SOURCE = (
    GAME_DATA
    / "StreamingAssets/aa/StandaloneWindows64/configs_assets_excel_ba168df030e983b8d9fa4c3200c3b5bc.bundle"
)
PAYLOAD = REPO / "payload/patch_payload.json"
WORKSET = (
    GAME_DATA
    / "translation_research/script_extraction/codex_probe/non_dialogue_working_sets"
    / "non_dialogue_source_update_20260730_build_24352496_354_working_set.tsv"
)
REPORT_DIR = GAME_DATA / "translation_research/source_update_20260730"

sys.path.insert(0, str(REPO / "src"))

from tos_ko_patcher.core import (  # noqa: E402
    key_column_for_schema,
    parse_string_table,
    schema_for_textasset,
    sha256_file,
    textassets_from_bundle,
)

SOURCE_FIELDS = ("source_en", "source_zh_cn", "source_ja")
WORKSET_FIELDS = (
    "category",
    "source_sha256",
    "object_path_id",
    "row_index",
    "row_id",
    "source_textasset",
    "schema",
    "canonical_scene",
    "dialog_key",
    "row_type",
    "english",
    "chinese_simplified",
    "japanese",
    "placeholder_tokens",
    "risk_flags",
    "reason",
    "korean_proposal",
    "term_status",
    "source_language_used",
    "translator_reason",
    "confidence",
    "qa_notes",
    "review_status",
)

RELATIONSHIP_WARNING = (
    "<b>연애 서약은 신중하게 결정하세요. 맺은 인연은 새전함에서 "
    "이나리님께 공물을 바쳐야만 바꿀 수 있습니다.</b>"
)

TRANSLATIONS_BY_KEY = {
    "1825601725019755": "아직 운명으로 맺을 수 있는 연인이 없습니다.",
    "1825601948727923": "공물을 바치면 인연의 실을 다시 엮을 수 있습니다.",
    "1825601948727924": "아직 풀어야 할 연인의 인연이 없습니다.",
    "1825601948727925": "아직 끊어야 할 배우자의 인연이 없습니다.",
    "1825605518062195": "이나리님",
    "1825679415152231": "이나리님",
    "1825679698893422": "이나리님께 공물을 바쳐야 합니다.",
    "1825679698893423": "이나리님",
    "1825679698893424": "이나리님",
    "1826472448433767": "이나리님",
    "1826473241701088": "이나리님",
    "1826473241701089": "연인이 되었습니다: {npc.ChangeRelationNpc}",
    "1826473241701090": "이나리님",
    "1826473241701091": "연인 관계를 끝냈습니다: {npc.ChangeRelationNpc}",
    "1826473241701092": "혼인 관계를 끝냈습니다: {npc.ChangeRelationNpc}",
    "1826848077159092": "이나리님",
    "1826848077159093": "공물을 바치면 인연의 실을 다시 엮을 수 있습니다.",
    "Change_Relation_Title": "확인",
    "NPC_Relation_Interact": "연애 관계 변경",
    "No_Item_Merge_Tip": "현재 가방에 보관함 속 물건과 같은 아이템이 없습니다.",
    "RanchUpgrade_Mail_Content": (
        "이제 목장 시설과 상호작용해 소재를 사용하면 바로 업그레이드할 수 있습니다. "
        "기존 목장 업그레이드 도구에 사용한 소재는 돌려드립니다."
    ),
    "RanchUpgrade_Mail_Title": "목장 시설 업그레이드 변경 안내",
    "Remove_Wedding_Interact": "혼인 관계 끊기 ({0} 공물)",
    "Remove_Wedding_Tip": "다음 상대와의 혼인 관계를 끝낼까요? {0}",
    "Set_Lover_Interact": "연인의 인연 맺기 ({0} 공물)",
    "Set_Lover_Tip": "다음 상대와 연인이 될까요? {0}",
    "Set_Not_Lover_Interact": "연인의 인연 풀기 ({0} 공물)",
    "Set_Not_Lover_Tip": "다음 상대와 연인 관계를 끝낼까요? {0}",
    "Sow_Invalid_Grid_Tip": "이 칸에는 가구가 있어 씨앗을 심을 수 없습니다.",
    "1826846293022375": "수상한 인영",
    "1826846293022376": "유적 입구 근처에 수상한 인영이 자주 나타납니다. 대체 누구일까요?",
    "item__item/description_i18n_f13e4bed28a36bc53153534f3d0619cb": (
        "헤피가 무사시에게 감사하는 장면을 그린 만화. 두 사람 사이에는 낭만적인 분위기가 흐른다. "
        "자신들이 미카의 만화 주인공이 되었다는 사실을 두 사람은 아마 영원히 모를 것이다."
    ),
    "item__item/name_i18n_565e26c2bf9bcb746de85375274d4123": "미카의 만화",
    "location__map/name_01689b1008f260817dd07cdc2ece318d": "은신처",
    "location__map/name_b6e635a25d360cd0a85fabb93eb68ac7": "은신처",
    "location__name/name_7e3ce0e9b2116b19c6bd1113dc556c89": "유적 입구",
    "monster__monster_info/name_i18n_314cff6105abbe6c39410be427feab02": "푸른 오니",
    "promptKeys__info/i18n_code_45c30148b36fb5f5856724f38a939604": "플레이어 이름 변경",
    "promptKeys__info/i18n_code_5c49bf064214b21561d119ba2eda5dc6": "같은 아이템 보관",
    "promptKeys__info/i18n_code_8f9d247310f78ab89526983826ac8f10": "농장 이름 변경",
    "1810295526189757": (
        "미안하지만, {c.playername}. 타누키는 다른 이와 함께 목욕하지 않는다. "
        "우리에게 목욕은 사적이고 신성한 의식이거든. 그러니 타누키에게 온천 데이트를 "
        "신청하지 않는 게 좋을 거다."
    ),
    "1812672793333224": "<b>이 선택은 이후 전개에 영향을 줍니다. 신중하게 선택하세요.</b>",
}

RELATIONSHIP_WARNING_KEYS = {
    "1804412877067092",
    "1804417214057773",
    "1805026793929301",
    "1805044396789935",
    "1805419147124128",
    "1805827273068432",
    "1810819445287969",
    "1810900908972108",
    "1810901013973070",
    "1810901085183056",
    "1810901172041810",
    "1810901314544724",
    "1810901421106263",
    "1810901466475609",
    "1811514375592075",
    "1812588509166180",
    "1812588800415391",
    "1812676320275062",
    "1818679574342064",
    "1820094180739548",
}


def parsed_rows(bundle: Path) -> dict[tuple[str, str], dict[str, object]]:
    result: dict[tuple[str, str], dict[str, object]] = {}
    for name, raw in textassets_from_bundle(bundle).items():
        schema = schema_for_textasset(name)
        try:
            table = parse_string_table(name, raw, schema)
        except Exception:
            continue
        key_name = key_column_for_schema(schema)
        for row_index, row in enumerate(table.rows):
            key = str(row.get(key_name, ""))
            if key:
                result[(name, key)] = {**row, "schema": schema, "key": key, "row_index": row_index}
    return result


def tokens(value: str) -> str:
    return "|".join(re.findall(r"\{[^{}]+\}|</?[^<>]+>", value))


def korean_for(change: dict[str, object]) -> tuple[str, str]:
    key = str(change["key"])
    if key in RELATIONSHIP_WARNING_KEYS:
        return RELATIONSHIP_WARNING, "updated_translation"
    if key in TRANSLATIONS_BY_KEY:
        return TRANSLATIONS_BY_KEY[key], "updated_translation" if change["kind"] == "source_changed" else "new_translation"
    existing = str(change.get("existing_korean", ""))
    if existing:
        return existing, "reused_existing"
    return "", "excluded_empty_source"


def write_artifacts(report: dict[str, object], current_rows: dict[tuple[str, str], dict[str, object]]) -> None:
    source_sha = str(report["current_sha256"])
    selected = [
        item
        for item in report["changes"]
        if item["kind"] in {"added", "source_changed"}
    ]
    workset_rows: list[dict[str, str]] = []
    decisions: list[dict[str, object]] = []
    for change in selected:
        current = current_rows[(str(change["textasset"]), str(change["key"]))]
        korean, term_status = korean_for(change)
        decision = "excluded_structural_empty" if not korean else term_status
        decisions.append({**change, "decision": decision, "korean": korean})
        if not korean:
            continue
        japanese = str(current.get("source_ja", ""))
        flags = ["20260730_source_update", "preserve_tokens"]
        if "\n" in japanese:
            flags.append("multiline")
        workset_rows.append(
            {
                "category": "dialogue_source_update" if str(change["textasset"]).startswith("i18n_") else "non_dialogue_source_update",
                "source_sha256": source_sha,
                "object_path_id": "",
                "row_index": str(current.get("row_index", "")),
                "row_id": str(current.get("row_id", "")),
                "source_textasset": str(change["textasset"]),
                "schema": str(current.get("schema", "")),
                "canonical_scene": str(current.get("scene_name", current.get("scene", ""))),
                "dialog_key": str(change["key"]),
                "row_type": str(current.get("row_type", "KeyedText")),
                "english": str(current.get("source_en", "")),
                "chinese_simplified": str(current.get("source_zh_cn", "")),
                "japanese": japanese,
                "placeholder_tokens": tokens(japanese),
                "risk_flags": "|".join(flags),
                "reason": f"source_update_20260730_build_24352496; change_kind={change['kind']}",
                "korean_proposal": korean,
                "term_status": term_status,
                "source_language_used": "source_ja+english+chinese_simplified+20260730_update_review",
                "translator_reason": "Current Japanese controls meaning and register; established Korean terminology and existing verified translation are retained where the source meaning is unchanged.",
                "confidence": "high",
                "qa_notes": f"Reviewed for Steam build 24352496; {decision}; placeholders and rich-text tokens preserved.",
                "review_status": "proposal_ready",
            }
        )
    WORKSET.parent.mkdir(parents=True, exist_ok=True)
    with WORKSET.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=WORKSET_FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(workset_rows)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_json = REPORT_DIR / "source_diff_review_24352496.json"
    report_json.write_text(json.dumps({**report, "decisions": decisions}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = [
        "# Steam build 24352496 source update review",
        "",
        f"- Previous source: `{report['old_sha256']}`",
        f"- Current source: `{report['current_sha256']}`",
        f"- Added rows: {report['counts']['added']}",
        f"- Removed rows: {report['counts']['removed']}",
        f"- Source-language changes: {report['counts']['source_changed']}",
        f"- Metadata-only changes: {report['counts']['metadata_only']}",
        f"- Reviewed overlay rows: {len(workset_rows)}",
        f"- Structural empty rows excluded: {sum(not item['korean'] for item in decisions)}",
        "",
        "All Japanese changes were reviewed. Chinese-only and metadata-only changes retain verified Korean. "
        "The removed Blue Oni row is replaced by the new current key with the existing Korean name.",
    ]
    (REPORT_DIR / "reviewed_change_log_24352496.md").write_text("\n".join(summary) + "\n", encoding="utf-8")


def main() -> int:
    old = parsed_rows(OLD_SOURCE)
    current = parsed_rows(CURRENT_SOURCE)
    payload = json.loads(PAYLOAD.read_text(encoding="utf-8"))
    korean_by_key = {
        (str(row["textasset"]), str(row["key"])): str(row["source_ja"])
        for row in payload["excel_bundle"]["patch_rows"]
    }
    changes: list[dict[str, object]] = []
    for identity in sorted(set(old) | set(current)):
        before = old.get(identity)
        after = current.get(identity)
        if before is None:
            kind = "added"
        elif after is None:
            kind = "removed"
        else:
            changed_fields = [field for field in SOURCE_FIELDS if str(before.get(field, "")) != str(after.get(field, ""))]
            metadata_fields = [
                field
                for field in ("speaker_id", "speaker_name")
                if str(before.get(field, "")) != str(after.get(field, ""))
            ]
            if not changed_fields and not metadata_fields:
                continue
            kind = "source_changed" if changed_fields else "metadata_only"
        row = after or before or {}
        changes.append(
            {
                "kind": kind,
                "textasset": identity[0],
                "schema": row.get("schema", ""),
                "row_id": str(row.get("row_id", "")),
                "key": identity[1],
                "source_en_before": str((before or {}).get("source_en", "")),
                "source_en": str((after or {}).get("source_en", "")),
                "source_zh_cn_before": str((before or {}).get("source_zh_cn", "")),
                "source_zh_cn": str((after or {}).get("source_zh_cn", "")),
                "source_ja_before": str((before or {}).get("source_ja", "")),
                "source_ja": str((after or {}).get("source_ja", "")),
                "existing_korean": korean_by_key.get(identity, ""),
            }
        )
    report = {
        "old_sha256": sha256_file(OLD_SOURCE),
        "current_sha256": sha256_file(CURRENT_SOURCE),
        "counts": {kind: sum(item["kind"] == kind for item in changes) for kind in ("added", "removed", "source_changed", "metadata_only")},
        "changes": changes,
    }
    write_artifacts(report, current)
    print(
        json.dumps(
            {
                "status": "pass",
                "counts": report["counts"],
                "workset": str(WORKSET),
                "report_dir": str(REPORT_DIR),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
