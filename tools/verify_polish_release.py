"""Exercise the shipped EXE on pinned originals and a previous-release fixture."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
from tos_ko_patcher.core import (  # noqa: E402
    PATCH_VERSION,
    key_column_for_schema,
    parse_string_table,
    planned_excel_textassets,
    save_textassets_to_bundle,
    sha256_file,
    textassets_from_bundle,
)

GAME = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Tales of Seikyu\Tales Of Seikyu_Data")
REL = Path("StreamingAssets/aa/StandaloneWindows64")
NAMES = (
    "configs_assets_excel_819141916302f0cf565fc9cfe6d0ffc7.bundle",
    "uiview_assets_bagfunctionitem_c03f77ea6e9f3cdb429d41f0f3886553.bundle",
)
BASELINES = (
    GAME / ".tos_korean_patch/baselines/0.1.17-playtest.20261015/excel.5ab59347431bcbc7.bak",
    GAME / ".tos_korean_patch/baselines/0.1.7-playtest.20260701/bag.e4eabffd3e04ce96.bak",
)
POLISHED_ROWS_SHA256 = "fe451e18bb8ce514e879aaf06d0235cb7fa13e2303d0915aaa83bf47442cc4f7"
PREVIOUS_RELEASE_COMMIT = "3684408aa18ece9d01c2c053463726810f2fd419"
SORT_SURFACES = {
    "inventory__sort_type/desc_22b777e6fcb613b8ba83ced9594cd07e": ("Normal", "일반"),
    "inventory__sort_type/desc_0e46d8d6b7a0096b06c0603c9fca9aad": ("Quest", "퀘스트"),
    "inventory__sort_type/desc_7402599bc6350c095fb3ca545d950480": ("Gold", "골드"),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run(exe: Path, root: Path, *args: str) -> dict:
    result = subprocess.run(
        [str(exe), "--no-gui", "--game-data", str(root), *args],
        capture_output=True, timeout=240,
    )
    require(result.returncode == 0, f"EXE failed {args}: {result.stdout}\n{result.stderr}")
    try:
        stdout = result.stdout.decode("utf-8")
    except UnicodeDecodeError:
        stdout = result.stdout.decode("cp949")
    for line in reversed(stdout.splitlines()):
        if line.startswith("{") and line.endswith("}"):
            return json.loads(line)
    raise RuntimeError(f"No EXE JSON result: {result.stdout}")


def readback(bundle: Path, payload: dict) -> int:
    assets = textassets_from_bundle(bundle)
    tables = {}
    for entry in payload["excel_bundle"]["patch_rows"]:
        name = entry["textasset"]
        if name not in tables:
            schema = entry["schema"]
            key = key_column_for_schema(schema)
            tables[name] = {
                (str(row["row_id"]), str(row.get(key, ""))): row
                for row in parse_string_table(name, assets[name], schema).rows
            }
        row = tables[name][(str(entry["row_id"]), str(entry["key"]))]
        require(row["source_ja"] == entry["source_ja"], f"Text mismatch: {name}/{entry['row_id']}")
    return len(payload["excel_bundle"]["patch_rows"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    require(not args.report.exists(), "Do not overwrite prior release evidence")
    payload_path = REPO / "payload/patch_payload.json"
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    editorial_rows = [dict(row) for row in payload["excel_bundle"]["patch_rows"]]
    overrides = []
    for row in editorial_rows:
        if row["textasset"] == "inventory__sort_type_desc" and row["key"] in SORT_SURFACES:
            runtime, approved = SORT_SURFACES[row["key"]]
            require(row["source_ja"] == runtime, "Required bag glyph workaround missing")
            row["source_ja"] = approved
            overrides.append(row["key"])
    require(len(overrides) == 3, "Missing/duplicate surface overrides")
    rows_hash = hashlib.sha256(json.dumps(
        editorial_rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()).hexdigest()
    require(rows_hash == POLISHED_ROWS_SHA256, "Release differs from completed editorial rows")
    require(payload["patch_version"] == PATCH_VERSION, "Version mismatch")
    expected_sources = [payload[key]["source_sha256"] for key in ("excel_bundle", "bag_function_bundle")]
    require([sha256_file(p) for p in BASELINES] == expected_sources, "Clean baseline hash mismatch")
    live_before = [sha256_file(GAME / REL / name) for name in NAMES]
    archive = REPO / "dist" / f"TalesOfSeikyuKoreanPatch-v{PATCH_VERSION}.zip"
    results = {}
    with tempfile.TemporaryDirectory(prefix="tos-ko-release-") as temp:
        temp = Path(temp)
        with zipfile.ZipFile(archive) as zipped:
            require(set(zipped.namelist()) == {
                "TalesOfSeikyuKoreanPatch.exe", "README.md", "RELEASE_NOTES.md", "LICENSE"
            }, "Unexpected release contents")
            require(zipped.testzip() is None, "Broken ZIP")
            zipped.extractall(temp / "package")
        exe = temp / "package/TalesOfSeikyuKoreanPatch.exe"
        require(sha256_file(exe) == sha256_file(REPO / "dist" / exe.name), "Packaged EXE mismatch")
        for scenario in ("clean", "upgrade_v0.1.17"):
            root = temp / scenario / "Tales Of Seikyu_Data"
            (root / REL).mkdir(parents=True)
            for source, name in zip(BASELINES, NAMES):
                shutil.copy2(source, root / REL / name)
            if scenario.startswith("upgrade"):
                previous = subprocess.run(
                    ["git", "show", f"{PREVIOUS_RELEASE_COMMIT}:payload/patch_payload.json"],
                    cwd=REPO, capture_output=True, text=True, encoding="utf-8", check=True,
                )
                previous_payload = json.loads(previous.stdout)
                planned, _ = planned_excel_textassets(root / REL / NAMES[0], previous_payload)
                saved = save_textassets_to_bundle(root / REL / NAMES[0], temp / "old_patch", planned)
                require(sha256_file(saved) == previous_payload["excel_bundle"]["target_sha256"], "Old fixture mismatch")
                shutil.copy2(saved, root / REL / NAMES[0])
            installed = run(exe, root, "--install")
            require(installed["status"] == "installed" and not installed["partial_patch"], "Partial install")
            verified = run(exe, root, "--verify")
            require(verified["status"] == "patched", "EXE verification failed")
            require(all(verified[k] for k in ("font_ok", "ui_font_alias_ok", "bag_font_ok")), "Font references failed")
            require(verified["excel_sha256"] == payload["excel_bundle"]["target_sha256"], "Target hash differs")
            count = readback(root / REL / NAMES[0], payload)
            diagnostic = run(exe, root, "--diagnose")
            require(diagnostic["patcher_version"] == PATCH_VERSION, "Embedded EXE version differs")
            result = {"install": installed, "verify": verified, "readback_matches": count}
            before_restore = [
                previous_payload["excel_bundle"]["target_sha256"] if scenario.startswith("upgrade") else expected_sources[0],
                expected_sources[1],
            ]
            run(exe, root, "--restore")
            require([sha256_file(root / REL / name) for name in NAMES] == before_restore, "Restore not byte-exact")
            result["restore_byte_exact"] = True
            results[scenario] = result
    require([sha256_file(GAME / REL / name) for name in NAMES] == live_before, "Live game changed during test")
    report = {
        "status": "pass", "patch_version": PATCH_VERSION, "payload_sha256": sha256_file(payload_path),
        "editorial_rows_sha256_after_exact_surface_normalization": rows_hash,
        "runtime_surface_overrides": overrides, "zip_sha256": sha256_file(archive),
        "exe_sha256": sha256_file(REPO / "dist/TalesOfSeikyuKoreanPatch.exe"),
        "live_game_unchanged_during_test": True, "scenarios": results,
        "visual_lqa": "not_performed; font-reference checks are not glyph/render proof",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
