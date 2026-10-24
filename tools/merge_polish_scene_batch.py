"""Merge a fully read scene packet into the cumulative approved text overlay."""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import generate_payload as generator

REPO = generator.REPO
GAME = generator.SRC_GAME_DATA
AUDIT = GAME / "translation_research/quality_audit_20261023"
SNAPSHOT = GAME / "translation_research/source_update_20261015/original_table_snapshot.json"

REVIEWED_LITERAL_PASSTHROUGHS = {
    ("i18n_avg_default", "16843", "1811262444968067"): "b89281c05047fe1e56cb3e69b120e8df1a54d417bafbb7068b503c95f5445f39",
    ("i18n_avg_default", "16844", "1811262456210564"): "4236bfa63fa5952fee09e9159dbf401bae35e66b99bfd78b04455f278cb284f4",
    ("i18n_avg_default", "16845", "1811262464989317"): "c2a4f9ce2d1ff2b72e6be32a26c6e06e47bb2ac565fd1763b85b7b779bff9249",
    ("i18n_avg_default", "16846", "1811262474669190"): "99908e2b0c28971938592959e882e693d49de794300c71d0b3dc9155802919c0",
    ("i18n_avg_default", "16847", "1811262487242887"): "67d57d9c54fd6c10124baa613b04aae03d540e339c3f5962102defe824b40566",
    ("i18n_avg_default", "16848", "1811262493631624"): "106f27542037b801d0024f0c7e87d48f113e1886526f38e32bf450a9c39f6f6a",
    ("i18n_avg_default", "16849", "1811262502700169"): "d19b3188c173fab3b1cb256f046f3b6d397fe232c296c0b7f3840d4e52a69978",
    ("i18n_avg_default", "16850", "1811262444961922"): "968bf6f5dc5fb656edc06c2e193a64f28337ea3b9c3e7054c134bc5169cd8773",
}

REVIEWED_TABLE_LITERAL_PASSTHROUGHS = {
    ("promptKeys__info_i18n_code", "19", "promptKeys__info/i18n_code_38cf16f2204ffab8a6e0187070558721"): (
        ("OK", "确定", "Confirm", "Bestätigen", "Confirmer", "Confirmar"),
        "fb2c95fde180e024542ccb3081ee289b718022d2a0c9c722be96ec3b648c6069",
    ),
    ("promptKeys__info_i18n_code", "20", "promptKeys__info/i18n_code_38cf16f2204ffab8a6e0187070558721"): (
        ("OK", "确定", "Confirm", "Bestätigen", "Confirmer", "Confirmar"),
        "fb2c95fde180e024542ccb3081ee289b718022d2a0c9c722be96ec3b648c6069",
    ),
    ("promptKeys__info_i18n_code", "34", "promptKeys__info/i18n_code_38cf16f2204ffab8a6e0187070558721"): (
        ("OK", "确定", "Confirm", "Bestätigen", "Confirmer", "Confirmar"),
        "fb2c95fde180e024542ccb3081ee289b718022d2a0c9c722be96ec3b648c6069",
    ),
    ("setting__graphic_level_name", "11", "setting__graphic_level/name_752daf89c44aa831f5ee660391e1b230"): (
        ("Steam Deck", "Steam Deck", "Steam Deck", "Steam Deck", "SteamDeck", "Steam Deck"),
        "a9895cbc19bacbd565820cb79a3693a34652677f5044f1927e4be916224f1ceb",
    ),
    ("setting__key_mapping_i18n_code", "9", "setting__key_mapping/i18n_code_d523bb9d88567fec132c6d3a353f9671"): (
        ("OK", "Setting_Command_Interaction", "Setting_Command_Interaction", "", "", ""),
        "88680327b73356f3d9a816fc1350a13add525e03ec6feaa034e660a180bc1b7c",
    ),
    ("setting__key_mapping_i18n_code", "16", "setting__key_mapping/i18n_code_d523bb9d88567fec132c6d3a353f9671"): (
        ("OK", "Setting_Command_Interaction", "Setting_Command_Interaction", "", "", ""),
        "88680327b73356f3d9a816fc1350a13add525e03ec6feaa034e660a180bc1b7c",
    ),
}


REVIEWED_CUSTOM_LITERAL_PASSTHROUGHS = {
    ("i18n_custom", "1921", "Single_NEW"): (
        ("NEW", "新", "NEW", "NEU", "NOUVEAU", "NUEVO"),
        "7327d95e6a636cea1708e66537674642a37a49db8d185458fc805401bbb377e6",
    ),
    ("i18n_custom", "2092", "EA_Gift_Signature"): (
        ("ACE Entertainment", "ACE Entertainment", "ACE Entertainment", "ACE Entertainment", "ACE Entertainment", "ACE Entertainment"),
        "ebd1f9a6cb5a69821ba1ac4dbc1e9cc7aad6c966f1bec80309e5035ddc6857ea",
    ),
    ("i18n_custom", "1713", "Setting_Category_UI"): (
        ("UI", "UI", "UI", "UI", "Interface", "Interfaz de usuario"),
        "1591bf4a176a30d1596797fc084476bc96fcbdb84a9a828928850acab44871db",
    ),
    ("i18n_custom", "1824", "Experience_Up"): (
        ("EXP+{0}", "经验+{0}", "EXP + {0}", "EP + {0}", "+\u00a0{0} d’XP", "EXP +{0}"),
        "9fb9d5315a2661b9fde7ebec5b546f3a69d6cd3a75313cf78f54973521ad5ad3",
    ),
    ("i18n_custom", "1574", "Generic_LevelPrefix"): (
        ("Lv.{0}", "Lv.{0}", "Lv.{0}", "Stufe {0}", "Niveau\u00a0{0}", "Nivel {0}"),
        "e2f96442b1039da84defa825d38d8aac5923b36315de5467062561bab31838ea",
    ),
    ("i18n_custom", "1644", "Setting_Command_Confirm"): (
        ("OK", "确认", "Confirm", "Bestätigen", "Confirmer", "Confirmar"),
        "82818bbb54f4ac45580142bf2f06c2d1820294e45e4aa7d7a92ebea3ae6b298f",
    ),
    ("i18n_custom", "1253", "HP"): (
        ("HP：", "生命值：", "HP:", "LP:", "PV\u00a0:", "PV:"),
        "1bfbb8a5820d48b57b48ec1fbc026910caa0747eff682d5b77d2fa80f9cc469e",
    ),
    ("i18n_custom", "1343", "New_Sign"): (
        ("NEW!", "新！", "NEW!", "NEU!", "NOUVEAU\u00a0!", "¡NUEVO!"),
        "352e4a237e25856a801bf806b34f59f5679f4fdf5e4c003d4814ebddb5105de3",
    ),
    ("i18n_custom", "1104", "Property_Health"): (
        ("HP：", "生命值：", "HP:", "LP:", "PV :", "PV:"),
        "29f8060a959e2bc8af891bc8c537a0853765948eb8b466fe5d8c1cd59bbb631f",
    ),
    ("i18n_custom", "1134", "Shrine_Name1001"): (
        ("Shrine_Name1001", "Shrine_Name1001", "Shrine_Name1001", "Schrein_Name1001", "Shrine_Name1001", "Santuario_Nombre1001"),
        "31fd8311fda1712cfd889ec0fc00a2d93b0d10b39f816fa91725c427e03ee3f8",
    ),
    ("i18n_custom", "1135", "Shrine_Name1002"): (
        ("Shrine_Name1002", "Shrine_Name1002", "Shrine_Name1002", "Schrein_Name1002", "Shrine_Name1002", "Santuario_Nombre1002"),
        "ad561cdd384868437a8d0a64934a4d18d4a949227f99119ab52598d4be285a25",
    ),
    ("i18n_custom", "1184", "sellbox_sure"): (
        ("OK", "确定", "Confirm", "Bestätigen", "Confirmer", "Confirmar"),
        "fb2c95fde180e024542ccb3081ee289b718022d2a0c9c722be96ec3b648c6069",
    ),
    ("i18n_custom", "1000", "Code_UI"): (
        ("OK", "确定", "Confirm", "Bestätigen", "Confirmer", "Confirmar"),
        "fb2c95fde180e024542ccb3081ee289b718022d2a0c9c722be96ec3b648c6069",
    ),
    ("i18n_custom", "1034", "Setting_FOV"): (
        ("FOV", "FOV", "FOV", "Sichtfeld", "Champ de vision", "Campo de visión"),
        "8a05302255568a439cc29aa7adb1b6eba941e5f490d26eab98af147de71528d0",
    ),
    ("i18n_custom", "1078", "Map_Confirm"): (
        ("OK", "确定", "Confirm", "Bestätigen", "Confirmer", "Confirmar"),
        "fb2c95fde180e024542ccb3081ee289b718022d2a0c9c722be96ec3b648c6069",
    ),
}


REVIEWED_REFERENCE_PASSTHROUGHS = {
    ("interest_info", "1", "LifeSkill"): "a27fd446eee1c5d4668548cace0ed02b20f26e155fb966572d03acb07b377b01",
    ("interest_info", "2", "LifeSkill"): "eeadecb6127ef8e1b95950ec28843e83eb315d12a1a1851c10ea38e8852b93ac",
    ("interest_info", "3", "LifeSkill"): "1ea5ec1db73b465e86b01549795f4e3486ba44933474579f133c54095b1d50d4",
    ("interest_info", "4", "LifeSkill"): "97bc7d11d12ba39132a73c0d32fa1f6364816ba5f47357888745c61705d49073",
    ("interest_info", "5", "LifeSkill"): "678a398fab7973778a24f59b238c9d796c525d48a743a2e4b4c55a90ce26bd8e",
    ("interest_info", "6", "LifeSkill"): "34975b1e0d6040fe5e0e7ccb86fb93b34a57181deb79b51e361455b2ec6302bf",
    ("interest_info", "7", "LifeSkill"): "494eacdc0a806c647c65f3de20a0139fe2a2607820f68fb18db4dc05d40bdfbb",
}


def reviewed_reference_passthrough(row: dict) -> bool:
    expected = REVIEWED_REFERENCE_PASSTHROUGHS.get(identity(row))
    return bool(expected and row.get("schema") == "keyed_default"
                and generator.row_source_fingerprint(row, "keyed_default") == expected)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tokens(text: str) -> list[str]:
    return re.findall(r"\{[^{}]*\}|</?[^>]+>", text)


def identity(row: dict) -> tuple[str, str, str]:
    return str(row["textasset"]), str(row["row_id"]), str(row.get("key", row.get("text_id", row.get("row_key", ""))))


def review_group(row: dict) -> str:
    return row["dialog_id"] if row["schema"] == "avg" else "table:" + row["textasset"]


def review_reference(row: dict) -> str:
    return str(row["row_id"]) if row["schema"] == "avg" else f"{row['textasset']}:{row['row_id']}"


def select_review_rows(source_rows: list[dict], config: dict) -> tuple[list[dict], set[str]]:
    scene_names = config.get("scenes_read_in_full", [])
    table_names = config.get("tables_read_in_full", [])
    context_flows = config.get("context_flows_read_in_full", [])
    keyed_rows = config.get("keyed_rows_read_in_full", [])
    if sum(map(bool, (scene_names, table_names, context_flows, keyed_rows))) != 1:
        raise RuntimeError("Select one AVG-scene, table, context-flow or exact keyed-row mode.")
    if keyed_rows:
        if not isinstance(keyed_rows, list) or any(
            not isinstance(row, dict) or set(row) != {"textasset", "row_id", "row_key"}
            or not all(isinstance(value, str) and value for value in row.values())
            for row in keyed_rows
        ):
            raise RuntimeError("Keyed rows require exact nonempty textasset/row_id/row_key triples.")
        requested = {identity(row) for row in keyed_rows}
        if len(requested) != len(keyed_rows):
            raise RuntimeError("Duplicate keyed row identities.")
        selected = [row for row in source_rows
                    if row["schema"] in {"keyed_default", "keyed_custom"} and identity(row) in requested]
        if {identity(row) for row in selected} != requested:
            raise RuntimeError("A requested keyed row was not found in the original source.")
        groups = {review_group(row) for row in selected}
    elif context_flows:
        if not isinstance(context_flows, list) or any(
            not isinstance(flow, dict) or set(flow) != {"textasset", "story_id"}
            or not all(isinstance(value, str) and value for value in flow.values())
            for flow in context_flows
        ):
            raise RuntimeError("Context flows require exact nonempty textasset/story_id pairs.")
        flow_ids = {(flow["textasset"], flow["story_id"]) for flow in context_flows}
        if len(flow_ids) != len(context_flows):
            raise RuntimeError("Duplicate context flow names.")
        selected = [r for r in source_rows if r["schema"] == "context"
                    and (r["textasset"], r.get("story_id")) in flow_ids]
        if {(r["textasset"], r["story_id"]) for r in selected} != flow_ids:
            raise RuntimeError("A requested context flow was not found.")
        groups = {review_group(r) for r in selected}
    else:
        names = scene_names or table_names
        if len(names) != len(set(names)):
            raise RuntimeError("Duplicate review group names.")
        groups = set(scene_names) if scene_names else {"table:" + name for name in table_names}
        selected = [r for r in source_rows if (r["schema"] == "avg") == bool(scene_names)
                    and review_group(r) in groups]
    if (len(selected) != config["expected_rows"] or {review_group(r) for r in selected} != groups
            or len({identity(r) for r in selected}) != len(selected)
            or len({review_reference(r) for r in selected}) != len(selected)):
        raise RuntimeError("Scene/table row coverage does not match the reviewed manifest.")
    return selected, groups


def reviewed_literal_passthrough(row: dict) -> bool:
    custom_contract = REVIEWED_CUSTOM_LITERAL_PASSTHROUGHS.get(identity(row))
    if custom_contract is not None:
        sources, fingerprint = custom_contract
        return (row.get("schema") == "keyed_custom"
                and tuple(row.get("source_" + locale) for locale in ("ja", "zh_cn", "en", "de", "fr", "es")) == sources
                and generator.row_source_fingerprint(row, "keyed_custom") == fingerprint)
    table_contract = REVIEWED_TABLE_LITERAL_PASSTHROUGHS.get(identity(row))
    if table_contract is not None:
        sources, fingerprint = table_contract
        return (row.get("schema") == "keyed_default"
                and tuple(row.get("source_" + locale) for locale in ("ja", "zh_cn", "en", "de", "fr", "es")) == sources
                and generator.row_source_fingerprint(row, "keyed_default") == fingerprint)
    expected = REVIEWED_LITERAL_PASSTHROUGHS.get(identity(row))
    return bool(expected and row.get("schema") == "avg" and row.get("surface") == "InteractionTitle"
                and str(row.get("speaker_id", "")).startswith("DateTest#")
                and all(row.get("source_" + locale) == "Test_Lover"
                        for locale in ("ja", "zh_cn", "en", "de", "fr", "es"))
                and generator.row_source_fingerprint(row, "avg") == expected)


def write_tsv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("batch", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    config_bytes = args.batch.read_bytes()
    config = json.loads(config_bytes)
    payload_path = REPO / "payload/patch_payload.json"
    overlay_path = REPO / "payload/reviewed_polish.tsv"
    payload_bytes = payload_path.read_bytes()
    overlay_bytes = overlay_path.read_bytes()
    if digest(payload_bytes) != config["input_payload_sha256"]:
        raise RuntimeError("Scene review baseline changed; reread before merging.")
    payload = json.loads(payload_bytes)
    before = {identity(row): row for row in payload["excel_bundle"]["patch_rows"]}
    source_rows = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    selected, scenes = select_review_rows(source_rows, config)
    revisions = config["revisions"]
    addition_ids = config.get("additions", [])
    if len(addition_ids) != len(set(addition_ids)) or not set(addition_ids).issubset(revisions):
        raise RuntimeError("Additions must be unique explicit revisions.")
    registry_bytes = generator.REVIEWED_ADDITIONS.read_bytes()
    seeds = {}
    if addition_ids:
        source = generator.unpatched_excel_source(generator.EXCEL_SOURCE, payload)
        seeds = {identity(r): r for r in generator.reviewed_addition_seeds(source)}
    additions = {}
    holds = config.get("holds", {})
    row_ids = {review_reference(r) for r in selected}
    if not set(revisions).issubset(row_ids) or not set(holds).issubset(row_ids) or set(revisions) & set(holds):
        raise RuntimeError("Out-of-scene or conflicting decisions.")
    controls = {path: digest((GAME / path).read_bytes()) for path in config["control_refs"]}
    approved = generator.read_tsv(overlay_path)
    fields = list(approved[0])
    indexes = {(r["source_textasset"], r["row_id"], r["dialog_key"]): i for i, r in enumerate(approved)}
    if len(indexes) != len(approved):
        raise RuntimeError("Existing approved overlay has duplicate occurrences.")
    decisions = []
    changes = {}
    for row in selected:
        key = identity(row)
        current = before.get(key)
        ref = review_reference(row)
        if ref in addition_ids:
            if current is not None or key not in seeds:
                raise RuntimeError(f"Addition must be missing and explicitly registered: {key}")
            current = seeds[key]
            additions[key] = current
        reason = "Full scene, choices and source languages checked; meaning, voice, state and terminology retained."
        old = str(current["source_ja"]) if current else ""
        final = old
        decision = "keep_verified"
        if current and generator.row_source_fingerprint(row, row["schema"]) != current["source_fingerprint"]:
            raise RuntimeError(f"Snapshot/source fingerprint changed: {key}")
        if ref in holds:
            decision, reason = "hold", holds[ref]
        elif ref in revisions:
            if current is None:
                raise RuntimeError(f"New translation requires an explicit addition contract: {key}")
            final, reason = revisions[ref]
            if not final.strip() or final == old:
                raise RuntimeError(f"Empty or unchanged revision: {key}")
            generator.validate_reviewed_tokens((key[0], key[2]), old, final, row)
            decision = "revised"
            changes[key] = final
            entry = {
                "source_textasset": key[0], "row_id": key[1], "dialog_key": key[2],
                "source_fingerprint": current["source_fingerprint"], "old_target": old,
                "korean_proposal": final, "review_status": "approved", "batch_id": config["batch_id"], "reason": reason,
            }
            if key in indexes:
                previous = approved[indexes[key]]
                if previous["korean_proposal"] != old or previous["source_fingerprint"] != current["source_fingerprint"]:
                    raise RuntimeError(f"Concurrent approved text changed: {key}")
                entry["old_target"] = previous["old_target"]
                approved[indexes[key]] = entry
            else:
                indexes[key] = len(approved)
                approved.append(entry)
        elif current is None:
            stripped = re.sub(r"\{[^{}]*\}|</?[^>]+>", "", str(row["source_ja"]))
            literal_passthrough = reviewed_literal_passthrough(row)
            reference_passthrough = reviewed_reference_passthrough(row)
            if any(c.isalpha() for c in stripped) and not (literal_passthrough or reference_passthrough):
                raise RuntimeError(f"Untranslated source cannot silently pass: {key}")
            reason = "Verified original-text passthrough: only numerals/punctuation/placeholders, no Korean payload entry required."
            if reference_passthrough:
                reason = ("Exact source-verified structural asset/localization reference record, not language text. "
                          "Whole original table1824 bytes consumed; all21 referenced localized rows have Korean. "
                          "Keep original identifiers under exact schema/identity/all-fields fingerprint contract.")
            elif literal_passthrough:
                reason = ("Exact source-verified table literal: preserve Steam Deck brand or OK confirmation label, "
                          "with complete locale/identity/fingerprint contract; not omitted Japanese dialogue."
                          if key in REVIEWED_TABLE_LITERAL_PASSTHROUGHS else
                          "Exact source-verified custom UI literal: preserve the pinned original label, abbreviation or source placeholder with complete locale/identity/fingerprint contract; runtime visibility not inferred."
                          if key in REVIEWED_CUSTOM_LITERAL_PASSTHROUGHS else
                          "Exact source-verified DateTest literal Test_Lover identical in six locales; preserve identifier, not omitted Japanese dialogue. Runtime reachability not inferred.")
            final = str(row["source_ja"])
        decisions.append({
            "textasset": key[0], "row_id": key[1], "stable_key": key[2], "scene": review_group(row),
            "speaker": row.get("speaker_name", ""), "surface": row.get("surface", "TableText"), "decision": decision,
            "old_ko": old, "final_ko": final, "reason": reason,
            "source_ja": row["source_ja"], "source_zh_cn": row["source_zh_cn"], "source_en": row["source_en"],
        })
    counts = dict(collections.Counter(r["decision"] for r in decisions))
    if len(additions) != len(addition_ids):
        raise RuntimeError("Addition scope did not match the selected source rows.")
    summary = {"batch_id": config["batch_id"], "rows": len(decisions), "scenes": sorted(scenes),
               "decisions": counts, "approved_overlay_rows": len(approved), "outside_batch_changes": 0,
               "controls_sha256": controls, "config_sha256": digest(config_bytes),
               "added_patch_rows": len(additions), "additions_registry_sha256": digest(registry_bytes),
               "status": "dry_run_pass"}
    if not args.apply:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    folder = args.batch.with_suffix("")
    folder.mkdir(exist_ok=False)
    (folder / "payload_before.json").write_bytes(payload_bytes)
    (folder / "approved_before.tsv").write_bytes(overlay_bytes)
    (folder / "additions_registry.json").write_bytes(registry_bytes)
    (folder / "decisions.json").write_text(json.dumps(decisions, ensure_ascii=False, indent=2), encoding="utf-8")
    (folder / "review_config.json").write_bytes(config_bytes)
    staged = folder / "approved_after.tsv"
    write_tsv(staged, approved, fields)
    if (payload_path.read_bytes() != payload_bytes or overlay_path.read_bytes() != overlay_bytes
            or generator.REVIEWED_ADDITIONS.read_bytes() != registry_bytes):
        raise RuntimeError("Inputs changed during preparation; no canonical write performed.")
    overlay_path.write_bytes(staged.read_bytes())
    subprocess.run([sys.executable, "-X", "utf8", str(REPO / "tools/generate_payload.py")], cwd=REPO, check=True)
    updated_bytes = payload_path.read_bytes()
    updated = json.loads(updated_bytes)
    after = {identity(row): row for row in updated["excel_bundle"]["patch_rows"]}
    if set(after) != set(before) | set(additions):
        raise RuntimeError("Generated payload changed identities outside the reviewed scope.")
    actual = {key for key in before if before[key]["source_ja"] != after[key]["source_ja"]} | set(additions)
    if actual != set(changes):
        raise RuntimeError("Generated payload changed outside the reviewed scope.")
    for key, original in (before | additions).items():
        expected = {**original, "source_ja": changes.get(key, original["source_ja"])}
        if after[key] != expected:
            raise RuntimeError(f"Generated row contract mismatch: {key}")
    summary.update(status="merged_pass", payload_sha256_after=digest(updated_bytes), approved_sha256_after=digest(staged.read_bytes()))
    (folder / "receipt.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
