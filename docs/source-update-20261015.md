# Build 24948693 Maintenance Handoff

- Date: 2026-10-15 (Asia/Seoul)
- Release: `v0.1.17-playtest.20261015`
- Prior release: `v0.1.16-playtest.20260825` / build `24728299`
- Current installed Steam build: `24948693`, installed on 2026-08-28 according to Steam content log.
- Source Excel: `configs_assets_excel_819141916302f0cf565fc9cfe6d0ffc7.bundle`
- Original SHA256: `5ab59347431bcbc7d54ad1d178c1fcbaefe3e1e1060930e5746836b355cab6e8`
- Patched SHA256: `b5c886b6bc8ac22e7289fb96695612f4228177f271a5079f1f78457dcf68d114`
- Bag original SHA256: `e4eabffd3e04ce966d55bd16ce0ecdcc7fa3eed880ad99fa28de132d4747e1c0`
- Bag patched SHA256: `efc5a379999721c8935eee6fee4525e2f91764970dc056deaa897024e49f7ad4`

## Source Evidence

`python tools/audit_20261015_source_update.py` compares current Japanese, English,
and Simplified Chinese columns to the prior supported state reconstructed from
the July clean source and audited July/August deltas. The prior complete original
bundle is not available; this is a reconstructed text comparison, not a binary diff.
All 22,531 prior payload rows also independently match current source fingerprints
and exact identities, including other language and speaker fields.

- Parsed table occurrences: 23,500; non-empty unique table keys: 22,655.
- Added / removed / language-changed keys: 0 / 0 / 0.
- New translation worksets: none required.
- All 22,531 generated translation rows are identical to the preceding release.
- Previous update worksets are already incorporated in the prior payload; no stale
  overlay is re-applied to current row positions.

Local evidence lives under `translation_research/source_update_20261015/`:
`source_diff_report.json`, `original_table_snapshot.json`, and
`runtime_text_surface_inventory.{json,tsv,md}`. These contain game source material
and must not be added to the public package or repository.
A hash-verified local original backup is stored under
`.tos_korean_patch/baselines/0.1.17-playtest.20261015/`.

## Verification

- Full workset QA: 702 files, 24,092 filled rows, 0 blockers, 32 existing warnings.
- Apply-key audit: pass, 22,886 unique keys; historical duplicate/override groups remain.
- Current payload audit: pass, 22,531 rows, 0 missing identities and 0 dropped rows.
- Clean-copy export, install, font checks and restore: pass.
- Japanese UI font aliases: 95 replaced, 0 old aliases left.
- Bag font fallbacks and existing ASCII inventory category workaround: pass.
- Catalog selection, adaptive-update matching, remapping, errors and notice tests: pass.
- Ruff: pass.
- Packaged EXE export/install/font/restore smoke: pass.
- ZIP entries: patcher EXE, README, release notes and LICENSE only; no original game files.
- ZIP size: 34,307,559 bytes.
- ZIP SHA256: `5685acded05e98f9602f4d4c1f8756d6967d8a5767052b2d7cc82a172fbec99f`.
- Current fallback font target confirmed: `ZH_CN-Serif`, path ID `3547074879389643962`,
  dynamic atlas mode, CAB `60817ce547ef0bba62727219c74c499f`.

## Scope And Remaining Runtime Checks

Catalog-guided runtime inventory inspected 84 candidate bundles with 0 inspection
errors (timeline limit 30; UI limit 40), across 1,669 catalog candidates. This is
not a complete scan of all runtime bundles. There are 242 binary TextAssets that
do not parse as localization string tables; their errors are retained rather than
counted as proof of no text. No prior August runtime byte snapshot is available
for an exact runtime diff. No new runtime-only translation is inferred.

Live game files remain at their original hashes. Actual in-game visual LQA was
not performed. Watch inventory categories, dialogue, long lore pages and cutscenes
during the next playtest; automated font-pointer checks do not prove glyph rendering.
