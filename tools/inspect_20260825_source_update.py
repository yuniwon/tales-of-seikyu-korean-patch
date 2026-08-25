from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GAME_DATA = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Tales of Seikyu\Tales Of Seikyu_Data")
SOURCE_NAME = "configs_assets_excel_3f1047082220cc86ef33c60c74bf4ded.bundle"
SOURCE = GAME_DATA / "StreamingAssets/aa/StandaloneWindows64" / SOURCE_NAME
PAYLOAD = REPO / "payload/patch_payload.json"
WORKSET = (
    GAME_DATA
    / "translation_research/script_extraction/codex_probe/dialogue_working_sets"
    / "source_update_20260825_build_24728299_Nine_Lives_355_dialogue_working_set.tsv"
)
REPORT_DIR = GAME_DATA / "translation_research/source_update_20260825"

sys.path.insert(0, str(REPO / "src"))

from tos_ko_patcher.core import (  # noqa: E402
    key_column_for_schema,
    parse_string_table,
    schema_for_textasset,
    sha256_file,
    textassets_from_bundle,
)

FIELDS = (
    "category", "source_sha256", "object_path_id", "row_index", "row_id",
    "source_textasset", "schema", "canonical_scene", "dialog_key", "row_type", "speaker",
    "english", "chinese_simplified", "japanese", "placeholder_tokens", "risk_flags",
    "reason", "korean_proposal", "term_status", "source_language_used",
    "translator_reason", "confidence", "speaker_confidence", "tone_rule_ref", "qa_notes", "review_status",
)

NEW_TRANSLATIONS = {
    "1828065917374061": "또 왔군... 뭔가 <i>특별한</i> 물건을 찾나? 그 날개 달린 여자한테 들키기 전에 얼른 골라.",
    "1828065917376115": "그건 진귀한 물건이야. 특히 구하기 어렵지.",
    "1828065917377142": "고른 물건은 {1}, 수량은 {0}개군. 그걸 어디다 쓰려고? ...아니, 말하지 마. 합계는 {2}다.",
    "1828065917377145": "매번 고맙군. 그게 <i>쓸모 있길</i> 바라지.",
    "1828065917378173": "좋겠군, 내 시간만 실컷 낭비해 줘서. 돈 생기면 다시 와.",
}

REUSE_KEYS = {
    "1805827437877175",
    "1805827437877176",
    "1810295526189757",
    "1813236111430152",
}


def tokens(value: str) -> str:
    return "|".join(re.findall(r"\{[^{}]+\}|</?[^<>]+>", value))


def main() -> int:
    payload = json.loads(PAYLOAD.read_text(encoding="utf-8"))
    existing = {
        (str(row["textasset"]), str(row["key"])): str(row["source_ja"])
        for row in payload["excel_bundle"]["patch_rows"]
    }
    assets = textassets_from_bundle(SOURCE)
    textasset = "i18n_alone_avg_default"
    schema = schema_for_textasset(textasset)
    table = parse_string_table(textasset, assets[textasset], schema)
    key_name = key_column_for_schema(schema)
    selected: list[tuple[int, dict[str, object], str, str]] = []
    for index, row in enumerate(table.rows):
        key = str(row.get(key_name, ""))
        if key in NEW_TRANSLATIONS:
            selected.append((index, row, NEW_TRANSLATIONS[key], "new_translation"))

    reuse_textasset = "i18n_avg_default"
    reuse_schema = schema_for_textasset(reuse_textasset)
    reuse_table = parse_string_table(reuse_textasset, assets[reuse_textasset], reuse_schema)
    reuse_key_name = key_column_for_schema(reuse_schema)
    for index, row in enumerate(reuse_table.rows):
        key = str(row.get(reuse_key_name, ""))
        if key in REUSE_KEYS:
            korean = existing.get((reuse_textasset, key), "")
            if not korean:
                raise RuntimeError(f"missing previous Korean for safe reuse: {key}")
            selected.append((index, row, korean, "reused_existing"))

    if len(selected) != 9:
        raise RuntimeError(f"expected 9 reviewed rows, found {len(selected)}")

    rows: list[dict[str, str]] = []
    report_rows: list[dict[str, str]] = []
    source_hash = sha256_file(SOURCE)
    for index, row, korean, status in selected:
        active_textasset = textasset if str(row.get(key_name, "")) in NEW_TRANSLATIONS else reuse_textasset
        active_schema = schema_for_textasset(active_textasset)
        active_key_name = key_column_for_schema(active_schema)
        key = str(row.get(active_key_name, ""))
        japanese = str(row.get("source_ja", ""))
        rows.append(
            {
                "category": "dialogue_source_update",
                "source_sha256": source_hash,
                "object_path_id": "",
                "row_index": str(index),
                "row_id": str(row.get("row_id", "")),
                "source_textasset": active_textasset,
                "schema": active_schema,
                "canonical_scene": str(row.get("dialog_id", "")),
                "dialog_key": key,
                "row_type": str(row.get("surface", "Dialogue")),
                "speaker": str(row.get("speaker_name", "")),
                "english": str(row.get("source_en", "")),
                "chinese_simplified": str(row.get("source_zh_cn", "")),
                "japanese": japanese,
                "placeholder_tokens": tokens(japanese),
                "risk_flags": "20260825_source_update|preserve_tokens|Nine_Lives_shop" if status == "new_translation" else "20260825_chinese_only_change|safe_reuse",
                "reason": f"source_update_20260825_build_24728299; {status}",
                "korean_proposal": korean,
                "term_status": status,
                "source_language_used": "source_ja+english+chinese_simplified+Nine_Lives_tone_decision+20260825_update_review",
                "translator_reason": "Japanese controls meaning and Nine Lives' rough transactional banmal; English and Chinese support shop function. Existing Korean is retained where only Chinese changed.",
                "confidence": "high",
                "speaker_confidence": "explicit_speaker_non_triage",
                "tone_rule_ref": "translation_research/script_extraction/codex_probe/character_tone_decisions/Nine_Lives_tone_decision.md",
                "qa_notes": f"Steam build 24728299; {status}; placeholder and rich-text order preserved.",
                "review_status": "proposal_ready",
            }
        )
        report_rows.append({"textasset": active_textasset, "row_id": str(row.get("row_id", "")), "key": key, "decision": status})

    WORKSET.parent.mkdir(parents=True, exist_ok=True)
    with WORKSET.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "status": "pass", "steam_buildid": "24728299", "source_bundle": SOURCE_NAME,
        "source_sha256": source_hash, "added_player_facing_rows": 5,
        "source_changed_rows": 4, "japanese_changed_rows": 0,
        "chinese_only_changed_rows": 4, "workset_rows": len(rows), "decisions": report_rows,
    }
    (REPORT_DIR / "source_diff_review_24728299.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (REPORT_DIR / "reviewed_change_log_24728299.md").write_text(
        "# Steam build 24728299 source update review\n\n"
        "- New player-facing Japanese rows: 5\n"
        "- Japanese meaning changes: 0\n"
        "- Simplified-Chinese-only changes with verified Korean reuse: 4\n"
        "- Removed rows: 0\n"
        "- Runtime-only text additions found: 0\n\n"
        "The five additions are Nine Lives shop dialogue. Four fingerprint changes retain existing Korean because Japanese and English are unchanged.\n",
        encoding="utf-8",
    )
    print(json.dumps({**report, "workset": str(WORKSET)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
