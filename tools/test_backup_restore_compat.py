from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC_GAME_DATA = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Tales of Seikyu\Tales Of Seikyu_Data")
EXCEL_BUNDLE_NAME = "configs_assets_excel_36698abb7c087ca9762cdbd1394d516f.bundle"
BAG_BUNDLE_NAME = "uiview_assets_bagfunctionitem_c03f77ea6e9f3cdb429d41f0f3886553.bundle"
EXCEL_CURRENT = SRC_GAME_DATA / "StreamingAssets/aa/StandaloneWindows64" / EXCEL_BUNDLE_NAME
BAG_CURRENT = SRC_GAME_DATA / "StreamingAssets/aa/StandaloneWindows64" / BAG_BUNDLE_NAME
EXCEL_SOURCE = SRC_GAME_DATA / ".tos_korean_patch/baselines/0.1.7-playtest.20260701/excel.eefb061b2955614b.bak"
BAG_SOURCE = SRC_GAME_DATA / ".tos_korean_patch/baselines/0.1.7-playtest.20260701/bag.e4eabffd3e04ce96.bak"
sys.path.insert(0, str(REPO / "src"))

from tos_ko_patcher.core import (  # noqa: E402
    backup_path_for,
    legacy_backup_name,
    restore_patch,
    sha256_file,
)


def main() -> int:
    payload_path = REPO / "payload/patch_payload.json"
    with tempfile.TemporaryDirectory(prefix="tos-ko-restore-compat-", ignore_cleanup_errors=True) as temp:
        data_root = Path(temp) / "Tales Of Seikyu_Data"
        target_dir = data_root / "StreamingAssets/aa/StandaloneWindows64"
        target_dir.mkdir(parents=True)
        excel_target = target_dir / EXCEL_BUNDLE_NAME
        bag_target = target_dir / BAG_BUNDLE_NAME
        shutil.copy2(EXCEL_CURRENT, excel_target)
        shutil.copy2(BAG_CURRENT, bag_target)

        excel_legacy = data_root / ".tos_korean_patch/backups/0.1.4-playtest.20260623" / legacy_backup_name(excel_target, sha256_file(EXCEL_SOURCE))
        excel_legacy.parent.mkdir(parents=True)
        shutil.copy2(EXCEL_SOURCE, excel_legacy)

        bag_short = backup_path_for(data_root, bag_target, sha256_file(BAG_SOURCE))
        bag_short.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(BAG_SOURCE, bag_short)

        result = restore_patch(data_root, payload_path)
        excel_after = sha256_file(excel_target)
        bag_after = sha256_file(bag_target)

    ok = excel_after == sha256_file(EXCEL_SOURCE) and bag_after == sha256_file(BAG_SOURCE)
    print(
        json.dumps(
            {
                "status": "pass" if ok else "fail",
                "restore_result": result,
                "excel_after": excel_after,
                "bag_after": bag_after,
                "excel_legacy_backup_name": excel_legacy.name,
                "bag_short_backup_name": bag_short.name,
            },
            ensure_ascii=False,
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
