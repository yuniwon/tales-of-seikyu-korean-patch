from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from tos_ko_patcher.app import GAME_UPDATED_NOTICE, is_game_update_error, user_facing_error_message  # noqa: E402


def main() -> int:
    update_errors = [
        "지원되는 해시의 번들을 찾지 못했습니다.\n- configs_assets_excel_x.bundle: abc",
        "지원하지 않는 Excel 번들 해시입니다: abc",
        "지원하지 않는 가방 UI 번들 해시입니다: abc",
    ]
    passthrough = "Tales Of Seikyu_Data 폴더를 찾을 수 없습니다."
    checks = {
        "notice": GAME_UPDATED_NOTICE,
        "update_errors_detected": [is_game_update_error(item) for item in update_errors],
        "update_messages": [user_facing_error_message(item) for item in update_errors],
        "passthrough": user_facing_error_message(passthrough),
    }
    ok = (
        all(checks["update_errors_detected"])
        and all(item == GAME_UPDATED_NOTICE for item in checks["update_messages"])
        and checks["passthrough"] == passthrough
    )
    print(json.dumps({"status": "pass" if ok else "fail", **checks}, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
