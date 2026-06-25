from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC_GAME_DATA = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Tales of Seikyu\Tales Of Seikyu_Data")
EXCEL_BUNDLE_NAME = "configs_assets_excel_133f2db0592e8e139c965fee90b07c1c.bundle"
EXCEL_SOURCE = SRC_GAME_DATA / ".tos_korean_patch/baselines/0.1.6-playtest.20260625/excel.d973dcdac6fbde16.bak"
sys.path.insert(0, str(REPO / "src"))

from tos_ko_patcher.core import (  # noqa: E402
    inspect_excel_ui_font,
    planned_excel_textassets,
    save_textassets_to_bundle,
    sha256_file,
    textassets_from_bundle,
    write_string,
)


def main() -> int:
    payload = json.loads((REPO / "payload/patch_payload.json").read_text(encoding="utf-8"))
    font_patch = payload["excel_bundle"]["ui_font_patch"]
    source_raw = textassets_from_bundle(EXCEL_SOURCE)[font_patch["textasset"]]
    source_old_count = source_raw.count(write_string(font_patch["old_alias"]))
    source_new_count = source_raw.count(write_string(font_patch["new_alias"]))

    with tempfile.TemporaryDirectory(prefix="tos-ko-ui-font-unit-", ignore_cleanup_errors=True) as temp:
        temp = Path(temp)
        source = temp / EXCEL_BUNDLE_NAME
        shutil.copy2(EXCEL_SOURCE, source)
        planned, changed = planned_excel_textassets(source, payload)
        patched_raw = planned[font_patch["textasset"]]
        patched_old_count = patched_raw.count(write_string(font_patch["old_alias"]))
        patched_new_count = patched_raw.count(write_string(font_patch["new_alias"]))
        saved = save_textassets_to_bundle(source, temp / "out", planned)
        inspection = inspect_excel_ui_font(saved, payload)

    ok = (
        source_old_count == font_patch["expected_replacements"]
        and source_new_count == 0
        and patched_old_count == 0
        and patched_new_count >= font_patch["expected_replacements"]
        and inspection["ui_font_alias_ok"]
    )
    result = {
        "status": "pass" if ok else "fail",
        "source_sha256": sha256_file(EXCEL_SOURCE),
        "changed_units": changed,
        "source_old_alias_count": source_old_count,
        "source_new_alias_count": source_new_count,
        "patched_old_alias_count": patched_old_count,
        "patched_new_alias_count": patched_new_count,
        "inspection": inspection,
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
