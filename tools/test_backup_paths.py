from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from tos_ko_patcher.core import backup_path_for, legacy_backup_name, short_backup_name  # noqa: E402


def main() -> int:
    game_data = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Tales of Seikyu\Tales Of Seikyu_Data")
    digest = "c6607bdea4519e5cc516b920ab520c90ab6ad0566f2ac0fcdb5ee3813ba03711"
    excel = game_data / "StreamingAssets/aa/StandaloneWindows64/configs_assets_excel_36698abb7c087ca9762cdbd1394d516f.bundle"
    bag = game_data / "StreamingAssets/aa/StandaloneWindows64/uiview_assets_bagfunctionitem_c03f77ea6e9f3cdb429d41f0f3886553.bundle"
    excel_short = backup_path_for(game_data, excel, digest)
    excel_legacy = excel_short.parent / legacy_backup_name(excel, digest)
    checks = {
        "excel_short_name": short_backup_name(excel, digest),
        "bag_short_name": short_backup_name(bag, digest),
        "excel_short_path_length": len(str(excel_short)),
        "excel_legacy_path_length": len(str(excel_legacy)),
        "excel_short_path": str(excel_short),
        "excel_legacy_path": str(excel_legacy),
    }
    ok = (
        checks["excel_short_name"] == "excel.c6607bdea4519e5c.bak"
        and checks["bag_short_name"] == "bag.c6607bdea4519e5c.bak"
        and checks["excel_short_path_length"] < 220
        and checks["excel_legacy_path_length"] > 260
    )
    print(json.dumps({"status": "pass" if ok else "fail", **checks}, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
