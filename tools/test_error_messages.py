from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from tos_ko_patcher.app import (  # noqa: E402
    GAME_UPDATED_NOTICE,
    PATH_ERROR_NOTICE,
    is_game_update_error,
    user_facing_error_message,
    verify_error_status,
)


def main() -> int:
    update_errors = [
        "지원되는 해시의 번들을 찾지 못했습니다.\n- configs_assets_excel_x.bundle: abc",
        "지원하지 않는 Excel 번들 해시입니다: abc",
        "지원하지 않는 가방 UI 번들 해시입니다: abc",
    ]
    path_error = "[WinError 3] 지정된 경로를 찾을 수 없습니다: 'C:\\very\\long\\path'"
    passthrough = "Tales Of Seikyu_Data 폴더를 찾을 수 없습니다."
    checks = {
        "notice": GAME_UPDATED_NOTICE,
        "update_errors_detected": [is_game_update_error(item) for item in update_errors],
        "update_messages": [user_facing_error_message(item) for item in update_errors],
        "path_message": user_facing_error_message(path_error),
        "passthrough": user_facing_error_message(passthrough),
        "valid_path_update_status": verify_error_status(update_errors[0], path_valid=True),
        "valid_path_file_status": verify_error_status("Unity bundle parse failed", path_valid=True),
        "invalid_path_status": verify_error_status(path_error, path_valid=False),
    }
    ok = (
        all(checks["update_errors_detected"])
        and all(item == GAME_UPDATED_NOTICE for item in checks["update_messages"])
        and checks["path_message"].startswith(PATH_ERROR_NOTICE)
        and checks["passthrough"] == passthrough
        and checks["valid_path_update_status"]["path"] == "경로 확인됨"
        and checks["valid_path_update_status"]["patch"] == "게임 업데이트 확인 필요"
        and checks["valid_path_file_status"]["path"] == "경로 확인됨"
        and checks["valid_path_file_status"]["patch"] == "게임 파일 확인 필요"
        and checks["invalid_path_status"]["path"] == "경로 확인 실패"
    )
    print(json.dumps({"status": "pass" if ok else "fail", **checks}, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
