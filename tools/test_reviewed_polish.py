from __future__ import annotations

import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import generate_payload as generator
import merge_polish_scene_batch as scene_batch


class ReviewedPolishTests(unittest.TestCase):
    def test_structural_reference_requires_exact_original_record(self):
        row = dict(textasset="interest_info", schema="keyed_default", row_id="1", row_key="LifeSkill",
                   source_zh_cn="ui_livinglevel_icon_02", source_ja="ui_livinglevel_frame_02",
                   source_en="interest__info/level_point_up_tip_0134b2d4194f2646a48100c2926e668b",
                   source_de="interest__info/level_up_tip_a915717928f78750f7790f18c9890771",
                   source_fr="interest__info/name_4d56b826549730e78ae5cb3530c2f02f",
                   source_es="ui_stats_frame_15")
        self.assertTrue(scene_batch.reviewed_reference_passthrough(row))
        for field in row:
            with self.subTest(field=field):
                self.assertFalse(scene_batch.reviewed_reference_passthrough({**row, field: "changed"}))

    def test_reference_exception_does_not_accept_generic_identifiers(self):
        row = dict(textasset="other_table", schema="keyed_default", row_id="1", row_key="LifeSkill",
                   source_ja="ui_livinglevel_frame_02")
        self.assertFalse(scene_batch.reviewed_reference_passthrough(row))
        self.assertFalse(scene_batch.reviewed_reference_passthrough({**row, "textasset": "interest_info"}))

    def test_custom_keyed_packet_selects_exact_identity(self):
        row = dict(textasset="i18n_custom", row_id="1", row_key="Button", schema="keyed_custom")
        ref = {k: row[k] for k in ("textasset", "row_id", "row_key")}
        config = {"keyed_rows_read_in_full": [ref], "expected_rows": 1}
        other = {**row, "row_id": "2", "row_key": "Other"}
        self.assertEqual(scene_batch.select_review_rows([row, other], config),
                         ([row], {"table:i18n_custom"}))
        for mutation in ({"row_key": "changed"}, {"row_id": "2"}, {"schema": "unknown"}):
            with self.subTest(mutation=mutation), self.assertRaises(RuntimeError):
                scene_batch.select_review_rows([{**row, **mutation}, other], config)

    def test_custom_literal_requires_every_locale_identity_and_schema(self):
        for identity, (sources, _) in scene_batch.REVIEWED_CUSTOM_LITERAL_PASSTHROUGHS.items():
            row = dict(textasset=identity[0], row_id=identity[1], row_key=identity[2], schema="keyed_custom")
            source_fields = ["source_" + locale for locale in ("ja", "zh_cn", "en", "de", "fr", "es")]
            row.update(dict(zip(source_fields, sources)))
            self.assertTrue(scene_batch.reviewed_literal_passthrough(row))
            for field in ["textasset", "row_id", "row_key", "schema", *source_fields]:
                with self.subTest(identity=identity, field=field):
                    self.assertFalse(scene_batch.reviewed_literal_passthrough({**row, field: "changed"}))

    def test_keyed_packet_selects_exact_pairs_not_whole_tables(self):
        rows = [dict(textasset=table, row_id=str(i), row_key=f"{table}-{i}", schema="keyed_default")
                for table in ("names", "descriptions") for i in (1, 2)]
        manifest = [{k: row[k] for k in ("textasset", "row_id", "row_key")} for row in rows if row["row_id"] == "1"]
        selected, groups = scene_batch.select_review_rows(rows, {
            "keyed_rows_read_in_full": manifest, "expected_rows": 2,
        })
        self.assertEqual(selected, [rows[0], rows[2]])
        self.assertEqual(groups, {"table:names", "table:descriptions"})

    def test_keyed_packet_rejects_changed_missing_duplicate_and_mixed_manifest(self):
        row = dict(textasset="names", row_id="1", row_key="original", schema="keyed_default")
        ref = {k: row[k] for k in ("textasset", "row_id", "row_key")}
        base = {"keyed_rows_read_in_full": [ref], "expected_rows": 1}
        invalid = [{**base, "expected_rows": 2},
                   {**base, "keyed_rows_read_in_full": [ref, ref]},
                   {**base, "tables_read_in_full": ["names"]},
                   {**base, "scenes_read_in_full": ["scene"]},
                   {**base, "context_flows_read_in_full": [{"textasset": "q", "story_id": "s"}]}]
        for field in ref:
            invalid.extend([{**base, "keyed_rows_read_in_full": [{**ref, field: value}]}
                            for value in ("changed", "", 1)])
        invalid.extend([{**base, "keyed_rows_read_in_full": [{**ref, "extra": "x"}]},
                        {**base, "keyed_rows_read_in_full": ["not-a-triple"]},
                        {**base, "keyed_rows_read_in_full": {"bad": "mapping"}}])
        for config in invalid:
            with self.subTest(config=config), self.assertRaises(RuntimeError):
                scene_batch.select_review_rows([row], config)

    def test_keyed_packet_rejects_wrong_schema_or_duplicate_source_reference(self):
        row = dict(textasset="names", row_id="1", row_key="original", schema="keyed_default")
        ref = {k: row[k] for k in ("textasset", "row_id", "row_key")}
        config = {"keyed_rows_read_in_full": [ref], "expected_rows": 1}
        for rows in ([{**row, "schema": "avg"}], [{**row, "schema": "context"}], [row, dict(row)]):
            with self.subTest(rows=rows), self.assertRaises(RuntimeError):
                scene_batch.select_review_rows(rows, config)

    def test_scene_selection_preserves_existing_avg_contract(self):
        row = dict(textasset="avg", row_id="1", text_id="a", schema="avg", dialog_id="Scene")
        other = dict(textasset="table", row_id="1", row_key="b", schema="keyed_default")
        self.assertEqual(scene_batch.select_review_rows([row, other], {
            "scenes_read_in_full": ["Scene"], "expected_rows": 1,
        }), ([row], {"Scene"}))

    def test_table_selection_namespaces_same_row_number(self):
        rows = [dict(textasset=table, row_id="1", row_key=table + "-key", schema="keyed_default")
                for table in ("names", "locations")]
        selected, groups = scene_batch.select_review_rows(rows, {
            "tables_read_in_full": ["names", "locations"], "expected_rows": 2,
        })
        self.assertEqual(selected, rows)
        self.assertEqual(groups, {"table:names", "table:locations"})
        self.assertEqual([scene_batch.review_reference(r) for r in rows], ["names:1", "locations:1"])

    def test_review_selection_rejects_incomplete_or_mixed_manifest(self):
        rows = [dict(textasset="names", row_id=str(i), row_key=str(i), schema="keyed_default") for i in (1, 2)]
        for config in ({"tables_read_in_full": ["names"], "expected_rows": 1},
                       {"tables_read_in_full": ["missing"], "expected_rows": 0},
                       {"tables_read_in_full": ["names", "names"], "expected_rows": 2},
                       {"tables_read_in_full": ["names"], "scenes_read_in_full": ["Scene"], "expected_rows": 2},
                       {"expected_rows": 0}):
            with self.subTest(config=config), self.assertRaises(RuntimeError):
                scene_batch.select_review_rows(rows, config)

    def test_review_selection_rejects_duplicate_identity_or_reference(self):
        row = dict(textasset="names", row_id="1", row_key="a", schema="keyed_default")
        for second in (dict(row), {**row, "row_key": "other"}):
            with self.subTest(second=second), self.assertRaises(RuntimeError):
                scene_batch.select_review_rows([row, second], {"tables_read_in_full": ["names"], "expected_rows": 2})

    def test_literal_passthrough_requires_exact_source_contract(self):
        for identity, fingerprint in scene_batch.REVIEWED_LITERAL_PASSTHROUGHS.items():
            for mutation in ("none", "row_id", "textasset", "text_id", "schema", "surface", "speaker_id",
                             "source_ja", "source_zh_cn", "source_en", "source_de", "source_fr", "source_es", "fingerprint"):
                with self.subTest(identity=identity, mutation=mutation):
                    table, row_id, key = identity
                    row = dict(textasset=table, row_id=row_id, text_id=key, schema="avg",
                               surface="InteractionTitle", speaker_id="DateTest#fixture")
                    row.update({"source_" + locale: "Test_Lover" for locale in ("ja", "zh_cn", "en", "de", "fr", "es")})
                    if mutation not in {"none", "fingerprint"}:
                        row[mutation] = "changed"
                    with patch.object(generator, "row_source_fingerprint",
                                      return_value="changed" if mutation == "fingerprint" else fingerprint):
                        self.assertEqual(scene_batch.reviewed_literal_passthrough(row), mutation == "none")

    def test_context_flow_selects_all_surfaces_without_claiming_whole_table(self):
        rows = [dict(textasset="quests", row_id=str(i), text_id=str(i), schema="context",
                     story_id="Start" if i < 3 else "Later", surface="Title" if i == 1 else "Description")
                for i in (1, 2, 3)]
        selected, groups = scene_batch.select_review_rows(rows, {
            "context_flows_read_in_full": [{"textasset": "quests", "story_id": "Start"}], "expected_rows": 2,
        })
        self.assertEqual(selected, rows[:2])
        self.assertEqual(groups, {"table:quests"})

    def test_context_flow_rejects_missing_partial_duplicate_and_mixed_modes(self):
        flow = dict(textasset="quests", story_id="Start")
        rows = [dict(textasset="quests", row_id=str(i), text_id=str(i), schema="context", story_id="Start")
                for i in (1, 2)]
        for config in (
            {"context_flows_read_in_full": [flow], "expected_rows": 1},
            {"context_flows_read_in_full": [dict(textasset="quests", story_id="Missing")], "expected_rows": 0},
            {"context_flows_read_in_full": [flow, flow], "expected_rows": 2},
            {"context_flows_read_in_full": [flow], "tables_read_in_full": ["quests"], "expected_rows": 2},
            {"context_flows_read_in_full": [flow], "scenes_read_in_full": ["Start"], "expected_rows": 2},
            {"context_flows_read_in_full": [dict(textasset="quests", story_id="")], "expected_rows": 0},
            {"context_flows_read_in_full": [{**flow, "row_id": "1"}], "expected_rows": 1},
        ):
            with self.subTest(config=config), self.assertRaises(RuntimeError):
                scene_batch.select_review_rows(rows, config)

    def test_context_flow_rejects_duplicate_references_and_wrong_schema(self):
        row = dict(textasset="quests", row_id="1", text_id="a", schema="context", story_id="Start")
        config = {"context_flows_read_in_full": [{"textasset": "quests", "story_id": "Start"}], "expected_rows": 2}
        for second in (dict(row), {**row, "text_id": "b"}, {**row, "row_id": "2", "schema": "keyed_default"}):
            with self.subTest(second=second), self.assertRaises(RuntimeError):
                scene_batch.select_review_rows([row, second], config)

    def test_table_literals_require_exact_locale_identity_and_fingerprint(self):
        locales = ("ja", "zh_cn", "en", "de", "fr", "es")
        for identity, (sources, fingerprint) in scene_batch.REVIEWED_TABLE_LITERAL_PASSTHROUGHS.items():
            for mutation in ("none", "row_id", "textasset", "row_key", "schema", "fingerprint",
                             *("source_" + locale for locale in locales)):
                with self.subTest(identity=identity, mutation=mutation):
                    table, row_id, key = identity
                    row = dict(textasset=table, row_id=row_id, row_key=key, schema="keyed_default")
                    row.update({"source_" + locale: text for locale, text in zip(locales, sources)})
                    if mutation not in {"none", "fingerprint"}:
                        row[mutation] = "changed"
                    with patch.object(generator, "row_source_fingerprint",
                                      return_value="changed" if mutation == "fingerprint" else fingerprint):
                        self.assertEqual(scene_batch.reviewed_literal_passthrough(row), mutation == "none")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workset = Path(self.temp.name) / "reviewed.tsv"
        self.entry = {"textasset": "dialogue", "row_id": "1", "key": "stable", "schema": "avg", "source_ja": "old {name}"}
        self.proposal = {
            "source_textasset": "dialogue", "row_id": "1", "dialog_key": "stable", "source_fingerprint": "fp",
            "old_target": "old {name}", "korean_proposal": "new {name}", "review_status": "approved",
        }
        self.source = {("dialogue", "1", "stable"): {"original": True}}

    def apply(self, proposals=None, rows=None):
        proposals = [self.proposal] if proposals is None else proposals
        with self.workset.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(self.proposal), delimiter="\t")
            writer.writeheader()
            writer.writerows(proposals)
        with patch.object(generator, "source_row_lookup", return_value=self.source), patch.object(
            generator, "row_source_fingerprint", return_value="fp",
        ):
            return generator.apply_reviewed_polish([self.entry] if rows is None else rows, Path("source"), self.workset)

    def test_apply_preserves_input_and_outside_rows(self):
        outside = {**self.entry, "row_id": "2", "key": "other"}
        result, count = self.apply(rows=[self.entry, outside])
        self.assertEqual(count, 1)
        self.assertEqual(result[0]["source_ja"], "new {name}")
        self.assertEqual(self.entry["source_ja"], "old {name}")
        self.assertEqual(result[1], outside)

    def test_idempotent(self):
        result, _ = self.apply()
        self.assertEqual(self.apply(rows=result)[0], result)

    def test_unique_stable_key_can_move(self):
        self.proposal["row_id"] = "99"
        self.assertEqual(self.apply()[1], 1)

    def test_source_change_rejected(self):
        self.proposal["source_fingerprint"] = "changed"
        with self.assertRaisesRegex(RuntimeError, "source changed"):
            self.apply()

    def test_korean_conflict_rejected(self):
        self.entry["source_ja"] = "concurrent edit {name}"
        with self.assertRaisesRegex(RuntimeError, "Korean conflict"):
            self.apply()

    def test_duplicate_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "duplicate"):
            self.apply([self.proposal, self.proposal])

    def test_ambiguous_key_rejected(self):
        self.proposal["row_id"] = "99"
        with self.assertRaisesRegex(RuntimeError, "ambiguous"):
            self.apply(rows=[self.entry, {**self.entry, "row_id": "2"}])

    def test_missing_key_rejected(self):
        self.proposal["dialog_key"] = "missing"
        with self.assertRaisesRegex(RuntimeError, "missing"):
            self.apply()

    def test_token_loss_rejected(self):
        self.proposal["korean_proposal"] = "no placeholder"
        with self.assertRaisesRegex(RuntimeError, "token contract"):
            self.apply()

    def test_unapproved_rejected(self):
        self.proposal["review_status"] = "hold"
        with self.assertRaisesRegex(RuntimeError, "unapproved"):
            self.apply()

    def configure_source_token_repair(self, stable="1813236122144653", textasset="i18n_avg_default"):
        contaminated, canonical = generator.REVIEWED_SOURCE_TOKEN_REPAIRS[(textasset, stable)]
        old = "old " + " ".join(contaminated)
        new = "new " + " ".join(canonical)
        self.entry.update(textasset=textasset, key=stable, source_ja=old)
        self.proposal.update(source_textasset=textasset, dialog_key=stable, old_target=old, korean_proposal=new)
        self.source = {(textasset, "1", stable): {"source_ja": "original " + " ".join(canonical)}}

    def test_audited_source_token_repairs_and_idempotence(self):
        for textasset, stable in generator.REVIEWED_SOURCE_TOKEN_REPAIRS:
            with self.subTest(stable=stable):
                self.configure_source_token_repair(stable, textasset)
                result, count = self.apply()
                self.assertEqual(count, 1)
                self.assertEqual(result[0]["source_ja"], self.proposal["korean_proposal"])
                self.assertEqual(self.apply(rows=result)[0], result)

    def test_repair_rejects_wrong_canonical_source(self):
        self.configure_source_token_repair()
        self.source[("i18n_avg_default", "1", self.entry["key"])]["source_ja"] = "changed source {other}"
        with self.assertRaisesRegex(RuntimeError, "source-token repair"):
            self.apply()

    def test_repair_rejects_other_token_loss_or_reordering(self):
        for new in ("lost {c.playername}", "extra {c.playername} {npc.WeddingNPC} {other}",
                    "reordered {npc.WeddingNPC} {c.playername}"):
            with self.subTest(new=new):
                self.configure_source_token_repair()
                self.proposal["korean_proposal"] = new
                with self.assertRaisesRegex(RuntimeError, "source-token repair"):
                    self.apply()

    def test_repair_rejects_rich_text_loss(self):
        self.configure_source_token_repair()
        old = "<i>" + self.proposal["old_target"] + "</i>"
        self.proposal["old_target"] = self.entry["source_ja"] = old
        with self.assertRaisesRegex(RuntimeError, "source-token repair"):
            self.apply()

    def test_repair_cannot_be_used_on_other_rows(self):
        self.configure_source_token_repair()
        stable = "unreviewed"
        self.entry["key"] = self.proposal["dialog_key"] = stable
        self.source = {("i18n_avg_default", "1", stable): {"source_ja": "source {c.playername} {npc.WeddingNPC}"}}
        with self.assertRaisesRegex(RuntimeError, "token contract"):
            self.apply()

    def test_repair_rejects_return_to_mixed_locale_tokens(self):
        self.configure_source_token_repair()
        self.proposal["korean_proposal"] = self.proposal["old_target"]
        with self.assertRaisesRegex(RuntimeError, "source-token repair"):
            self.apply()

    def test_copied_trial_repair_rejects_source_or_target_tokens(self):
        for mutate in ("source", "target", "return_to_copy"):
            with self.subTest(mutate=mutate):
                self.configure_source_token_repair("1809595912229486")
                if mutate == "source":
                    self.source[("i18n_avg_default", "1", self.entry["key"])]["source_ja"] += " {new}"
                elif mutate == "target":
                    self.proposal["korean_proposal"] += " {npc.BestLoverNpc}"
                else:
                    self.proposal["korean_proposal"] = self.proposal["old_target"]
                with self.assertRaisesRegex(RuntimeError, "source-token repair"):
                    self.apply()

    def test_copied_trial_repair_rejects_other_contamination(self):
        for old in ("old {npc.BestLoverNpc}", "old {other} {other}", "<i>old</i>"):
            with self.subTest(old=old):
                self.configure_source_token_repair("1809595912229486")
                self.proposal["old_target"] = self.entry["source_ja"] = old
                with self.assertRaisesRegex(RuntimeError, "source-token repair"):
                    self.apply()

    def test_copied_trial_repair_is_not_generic_token_removal(self):
        self.configure_source_token_repair("1809595912229486")
        stable = "unreviewed-trial"
        self.entry["key"] = self.proposal["dialog_key"] = stable
        self.source = {("i18n_avg_default", "1", stable): {"source_ja": "no source tokens"}}
        with self.assertRaisesRegex(RuntimeError, "token contract"):
            self.apply()

    def test_audited_repairs_reject_changed_source_or_target(self):
        for textasset, stable in generator.REVIEWED_SOURCE_TOKEN_REPAIRS:
            for mutate in ("source", "target", "return_to_copy"):
                with self.subTest(stable=stable, mutate=mutate):
                    self.configure_source_token_repair(stable, textasset)
                    if mutate == "source":
                        self.source[(textasset, "1", stable)]["source_ja"] += " {unexpected}"
                    elif mutate == "target":
                        self.proposal["korean_proposal"] += " <b>new</b>"
                    else:
                        self.proposal["korean_proposal"] = self.proposal["old_target"]
                    with self.assertRaisesRegex(RuntimeError, "source-token repair"):
                        self.apply()

    def test_audited_patterns_do_not_transfer_to_other_identities(self):
        for textasset, stable in generator.REVIEWED_SOURCE_TOKEN_REPAIRS:
            with self.subTest(stable=stable):
                self.configure_source_token_repair(stable, textasset)
                unknown = "unreviewed-copy"
                self.entry["key"] = self.proposal["dialog_key"] = unknown
                self.source = {(textasset, "1", unknown): {"source_ja": "original"}}
                with self.assertRaisesRegex(RuntimeError, "token contract"):
                    self.apply()

    def test_copied_hotspring_invitation_requires_both_name_tokens(self):
        for old in ("old {c.playername}", "old {c.playername} {c.playername} {c.playername}"):
            with self.subTest(old=old):
                self.configure_source_token_repair("1804899039517200")
                self.proposal["old_target"] = self.entry["source_ja"] = old
                with self.assertRaisesRegex(RuntimeError, "source-token repair"):
                    self.apply()

    def test_copied_birthday_repair_does_not_transfer_between_tables(self):
        self.configure_source_token_repair("1806646314739610", "i18n_alone_avg_default")
        self.entry["textasset"] = self.proposal["source_textasset"] = "i18n_avg_default"
        self.source = {("i18n_avg_default", "1", self.entry["key"]): {"source_ja": "original"}}
        with self.assertRaisesRegex(RuntimeError, "token contract"):
            self.apply()

    def configure_original_markup_repair(self):
        textasset, stable = "i18n_avg_default", "1773671128313092"
        source, _, _ = generator.REVIEWED_ORIGINAL_MARKUP_REPAIRS[(textasset, stable)]
        old, new = "old <b>text<b>", "new <b>text</b>"
        self.entry.update(textasset=textasset, key=stable, source_ja=old)
        self.proposal.update(source_textasset=textasset, dialog_key=stable, old_target=old, korean_proposal=new)
        self.source = {(textasset, "1", stable): {"source_ja": source}}

    def test_all_original_markup_repairs_are_exact_and_idempotent(self):
        for (table, key), (ja, malformed, canonical) in generator.REVIEWED_ORIGINAL_MARKUP_REPAIRS.items():
            for mutation in ("none", "source", "old", "target", "table", "key"):
                with self.subTest(table=table, key=key, mutation=mutation):
                    old, new = "old" + "text".join(malformed), "new" + "text".join(canonical)
                    self.entry.update(textasset=table, key=key, source_ja=old)
                    self.proposal.update(source_textasset=table, dialog_key=key, old_target=old, korean_proposal=new)
                    original = {"source_ja": ja}
                    if mutation == "source":
                        original["source_ja"] += "changed"
                    elif mutation == "old":
                        self.proposal["old_target"] = self.entry["source_ja"] = old + "{unexpected}"
                    elif mutation == "target":
                        self.proposal["korean_proposal"] += "{unexpected}"
                    elif mutation == "table":
                        self.proposal["source_textasset"] = self.entry["textasset"] = "other"
                    elif mutation == "key":
                        self.proposal["dialog_key"] = self.entry["key"] = "other"
                    self.source = {(self.entry["textasset"], "1", self.entry["key"]): original}
                    if mutation == "none":
                        result, count = self.apply()
                        self.assertEqual(count, 1)
                        self.assertEqual(result[0]["source_ja"], new)
                        self.assertEqual(self.apply(rows=result)[0], result)
                    else:
                        with self.assertRaisesRegex(RuntimeError, "repair contract|token contract"):
                            self.apply()

    def configure_original_token_repair(self):
        table, key = "i18n_avg_default", "1820218594496168"
        ja, zh, en, _, _ = generator.REVIEWED_ORIGINAL_TOKEN_REPAIRS[(table, key)]
        old = "검은 여우와 싸우다가 {c.playername}, 기절해 버렸어!"
        self.entry.update(textasset=table, key=key, source_ja=old)
        self.proposal.update(source_textasset=table, dialog_key=key, old_target=old,
                             korean_proposal="검은 여우와 싸우다가 정신을 잃었어!")
        self.source = {(table, "1", key): {"source_ja": ja, "source_zh_cn": zh, "source_en": en}}

    def configure_dye_tutorial_repair(self):
        table = "tutorial__ui_tutorial_desc"
        key = "tutorial__ui_tutorial/desc_0a87ea42380b270dff34a3bee3299d06"
        ja, zh, en, _, _ = generator.REVIEWED_ORIGINAL_TOKEN_REPAIRS[(table, key)]
        old = "다른 색이 필요하면 {item.3444}를 사용하세요."
        self.entry.update(textasset=table, key=key, schema="keyed_default", source_ja=old)
        self.proposal.update(source_textasset=table, dialog_key=key, old_target=old,
                             korean_proposal="원하는 색은 {item.25125}로 골라 보세요.")
        self.source = {(table, "1", key): {"source_ja": ja, "source_zh_cn": zh, "source_en": en}}

    def test_dye_tutorial_repair_and_idempotence(self):
        self.configure_dye_tutorial_repair()
        result, count = self.apply()
        self.assertEqual(count, 1)
        self.assertEqual(result[0]["source_ja"], self.proposal["korean_proposal"])
        self.assertEqual(self.apply(rows=result)[0], result)

    def test_dye_tutorial_rejects_source_and_token_mutations(self):
        for change in ("source_ja", "source_zh_cn", "source_en", "old", "missing", "wrong", "extra"):
            with self.subTest(change=change):
                self.configure_dye_tutorial_repair()
                if change.startswith("source_"):
                    next(iter(self.source.values()))[change] += "changed"
                elif change == "old":
                    self.proposal["old_target"] = self.entry["source_ja"] = "{item.3445}"
                elif change == "missing":
                    self.proposal["korean_proposal"] = "만능 염료"
                elif change == "wrong":
                    self.proposal["korean_proposal"] = "{item.3444}"
                else:
                    self.proposal["korean_proposal"] += " {item.25125}"
                with self.assertRaisesRegex(RuntimeError, "original-token repair"):
                    self.apply()

    def test_dye_tutorial_repair_cannot_transfer_identity(self):
        for change in ("table", "key"):
            with self.subTest(change=change):
                self.configure_dye_tutorial_repair()
                original = next(iter(self.source.values()))
                if change == "table":
                    self.entry["textasset"] = self.proposal["source_textasset"] = "other"
                else:
                    self.entry["key"] = self.proposal["dialog_key"] = "other"
                self.source = {(self.entry["textasset"], "1", self.entry["key"]): original}
                with self.assertRaisesRegex(RuntimeError, "token contract"):
                    self.apply()

    def test_original_token_repair_and_idempotence(self):
        self.configure_original_token_repair()
        result, count = self.apply()
        self.assertEqual(count, 1)
        self.assertEqual(result[0]["source_ja"], self.proposal["korean_proposal"])
        self.assertEqual(self.apply(rows=result)[0], result)

    def test_original_token_repair_rejects_changed_contract(self):
        for change in ("source_ja", "source_zh_cn", "source_en", "old", "target", "retained_name"):
            with self.subTest(change=change):
                self.configure_original_token_repair()
                if change.startswith("source_"):
                    next(iter(self.source.values()))[change] += "changed"
                elif change == "old":
                    self.proposal["old_target"] = self.entry["source_ja"] = "old {other}"
                elif change == "target":
                    self.proposal["korean_proposal"] += " {unexpected}"
                else:
                    self.proposal["korean_proposal"] += " {c.playername}"
                with self.assertRaisesRegex(RuntimeError, "original-token repair"):
                    self.apply()

    def test_original_token_repair_cannot_transfer_identity(self):
        for change in ("table", "key"):
            with self.subTest(change=change):
                self.configure_original_token_repair()
                original = next(iter(self.source.values()))
                if change == "table":
                    self.entry["textasset"] = self.proposal["source_textasset"] = "other"
                else:
                    self.entry["key"] = self.proposal["dialog_key"] = "other"
                self.source = {(self.entry["textasset"], "1", self.entry["key"]): original}
                with self.assertRaisesRegex(RuntimeError, "token contract"):
                    self.apply()

    def test_original_markup_repair_and_idempotence(self):
        self.configure_original_markup_repair()
        result, count = self.apply()
        self.assertEqual(count, 1)
        self.assertEqual(result[0]["source_ja"], "new <b>text</b>")
        self.assertEqual(self.apply(rows=result)[0], result)

    def test_original_markup_repair_rejects_changed_contract(self):
        for mutate in ("source", "old", "target", "return_to_malformed"):
            with self.subTest(mutate=mutate):
                self.configure_original_markup_repair()
                if mutate == "source":
                    next(iter(self.source.values()))["source_ja"] += "changed"
                elif mutate == "old":
                    self.proposal["old_target"] = self.entry["source_ja"] = "old <i>text</i>"
                elif mutate == "target":
                    self.proposal["korean_proposal"] += " {unexpected}"
                else:
                    self.proposal["korean_proposal"] = self.proposal["old_target"]
                with self.assertRaisesRegex(RuntimeError, "original-markup repair"):
                    self.apply()

    def test_original_markup_repair_cannot_transfer_identity(self):
        for change in ("table", "key"):
            with self.subTest(change=change):
                self.configure_original_markup_repair()
                if change == "table":
                    self.entry["textasset"] = self.proposal["source_textasset"] = "other"
                else:
                    self.entry["key"] = self.proposal["dialog_key"] = "other"
                self.source = {(self.entry["textasset"], "1", self.entry["key"]): {"source_ja": "source"}}
                with self.assertRaisesRegex(RuntimeError, "token contract"):
                    self.apply()

    def test_missing_workset_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "workset missing"):
            generator.apply_reviewed_polish([], Path("source"), self.workset)

    def test_known_patch_requires_verified_original(self):
        root = Path(self.temp.name)
        live = root / "live.bundle"
        live.write_bytes(b"patched")
        expected = hashlib.sha256(b"original").hexdigest()
        previous = {"excel_bundle": {"source_sha256": expected, "target_sha256": hashlib.sha256(b"patched").hexdigest()}}
        folder = root / ".tos_korean_patch/baselines/version"
        folder.mkdir(parents=True)
        backup = folder / f"excel.{expected[:16]}.bak"
        backup.write_bytes(b"corrupt")
        with patch.object(generator, "SRC_GAME_DATA", root):
            with self.assertRaisesRegex(RuntimeError, "hash-verified"):
                generator.unpatched_excel_source(live, previous)
            backup.write_bytes(b"original")
            self.assertEqual(generator.unpatched_excel_source(live, previous), backup)

    def test_unknown_source_not_silently_replaced(self):
        live = Path(self.temp.name) / "live.bundle"
        live.write_bytes(b"new-game-update")
        previous = {"excel_bundle": {"source_sha256": "old-source", "target_sha256": "old-patch"}}
        self.assertEqual(generator.unpatched_excel_source(live, previous), live)


class ReviewedAdditionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.registry = Path(self.temp.name) / "additions.json"
        self.workset = Path(self.temp.name) / "approved.tsv"
        self.entry = {"textasset": "dialogue", "schema": "avg", "row_id": "1", "key": "stable",
                      "source_fingerprint": "fp", "source_ja": "original {name}"}
        self.contracts = [dict(self.entry)]
        self.proposal = {"source_textasset": "dialogue", "row_id": "1", "dialog_key": "stable",
                         "source_fingerprint": "fp", "old_target": "original {name}",
                         "korean_proposal": "translated {name}", "review_status": "approved"}
        self.proposals = [self.proposal]
        self.source = {("dialogue", "1", "stable"): {"source_ja": "original {name}"}}

    def seed(self, rows=None, apply=False):
        self.registry.write_text(json.dumps(self.contracts), encoding="utf-8")
        with self.workset.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(self.proposal), delimiter="\t")
            writer.writeheader()
            writer.writerows(self.proposals)
        with (patch.object(generator, "source_row_lookup", return_value=self.source),
              patch.object(generator, "row_source_fingerprint", return_value="fp"),
              patch.object(generator, "schema_for_textasset", return_value="avg")):
            result, count = generator.seed_reviewed_additions(
                [] if rows is None else rows, Path("source"), self.workset, self.registry,
            )
            if apply:
                result, _ = generator.apply_reviewed_polish(result, Path("source"), self.workset)
            return result, count

    def test_exact_approved_addition_and_idempotence(self):
        original = []
        result, count = self.seed(original, apply=True)
        self.assertEqual(count, 1)
        self.assertEqual(original, [])
        self.assertEqual(result, [{**self.entry, "source_ja": "translated {name}"}])
        repeated, count = self.seed(result, apply=True)
        self.assertEqual(repeated, result)
        self.assertEqual(count, 0)

    def test_missing_or_unapproved_translation_rejected(self):
        self.proposals = []
        with self.assertRaisesRegex(RuntimeError, "exact approved"):
            self.seed()
        self.proposals = [self.proposal]
        self.proposal["review_status"] = "hold"
        with self.assertRaisesRegex(RuntimeError, "exact approved"):
            self.seed()

    def test_duplicate_contract_rejected(self):
        self.contracts.append(dict(self.entry))
        with self.assertRaisesRegex(RuntimeError, "duplicate"):
            self.seed()

    def test_contract_cannot_duplicate_korean_authority(self):
        self.contracts[0]["korean_proposal"] = "other"
        with self.assertRaisesRegex(RuntimeError, "fields invalid"):
            self.seed()

    def test_missing_original_rejected(self):
        self.source = {}
        with self.assertRaisesRegex(RuntimeError, "original source changed"):
            self.seed()

    def test_changed_original_japanese_rejected(self):
        self.source[("dialogue", "1", "stable")]["source_ja"] = "changed {name}"
        with self.assertRaisesRegex(RuntimeError, "original source changed"):
            self.seed()

    def test_changed_fingerprint_or_schema_rejected(self):
        for field in ("source_fingerprint", "schema"):
            with self.subTest(field=field):
                self.contracts = [{**self.entry, field: "changed"}]
                with self.assertRaisesRegex(RuntimeError, "original source changed"):
                    self.seed()

    def test_approval_contract_changes_rejected(self):
        for field in ("source_fingerprint", "row_id", "old_target", "korean_proposal"):
            with self.subTest(field=field):
                self.proposals = [{**self.proposal, field: ""}]
                with self.assertRaisesRegex(RuntimeError, "exact approved"):
                    self.seed()

    def test_duplicate_approval_rejected(self):
        self.proposals.append(dict(self.proposal))
        with self.assertRaisesRegex(RuntimeError, "exact approved"):
            self.seed()

    def test_stable_key_move_or_duplicate_not_guessed(self):
        for rows in ([{**self.entry, "row_id": "2"}], [self.entry, dict(self.entry)]):
            with self.subTest(rows=rows):
                with self.assertRaisesRegex(RuntimeError, "identity collision"):
                    self.seed(rows)

    def test_concurrent_korean_not_reset_to_seed(self):
        current = {**self.entry, "source_ja": "concurrent {name}"}
        self.assertEqual(self.seed([current])[0], [current])
        with self.assertRaisesRegex(RuntimeError, "Korean conflict"):
            self.seed([current], apply=True)

    def test_token_loss_still_rejected(self):
        self.proposal["korean_proposal"] = "missing placeholder"
        with self.assertRaisesRegex(RuntimeError, "token contract"):
            self.seed(apply=True)

    def test_unregistered_missing_target_still_rejected(self):
        self.contracts = []
        with self.assertRaisesRegex(RuntimeError, "missing or ambiguous"):
            self.seed(apply=True)


if __name__ == "__main__":
    unittest.main()
