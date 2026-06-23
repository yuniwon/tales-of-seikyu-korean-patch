from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from tos_ko_patcher.core import backup_path_for, legacy_backup_name, short_backup_name  # noqa: E402


def main() -> int:
    game_data = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Tales of Seikyu\Tales Of Seikyu_Data")
    digest = "5defc6d90de95fbfa8e691f3f9136f4bd5c9d6d9571613ba7f2e869c29d21453"
    excel = game_data / "StreamingAssets/aa/StandaloneWindows64/configs_assets_excel_f49ac7551e791fb388bd02ccb81a6a88.bundle"
    bag = game_data / "StreamingAssets/aa/StandaloneWindows64/uiview_assets_bagfunctionitem_4151e323e15f7662e9ca55d7135ecfd4.bundle"
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
        checks["excel_short_name"] == "excel.5defc6d90de95fbf.bak"
        and checks["bag_short_name"] == "bag.5defc6d90de95fbf.bak"
        and checks["excel_short_path_length"] < 220
        and checks["excel_legacy_path_length"] > 260
    )
    print(json.dumps({"status": "pass" if ok else "fail", **checks}, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
