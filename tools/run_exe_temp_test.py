from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC_GAME_DATA = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Tales of Seikyu\Tales Of Seikyu_Data")
EXE = REPO / "dist/TalesOfSeikyuKoreanPatch.exe"
EXCEL_BUNDLE_NAME = "configs_assets_excel_36698abb7c087ca9762cdbd1394d516f.bundle"
EXCEL_SOURCE = SRC_GAME_DATA / ".tos_korean_patch/baselines/0.1.7-playtest.20260701/excel.eefb061b2955614b.bak"
BAG_SOURCE = SRC_GAME_DATA / ".tos_korean_patch/baselines/0.1.7-playtest.20260701/bag.e4eabffd3e04ce96.bak"


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=str(REPO), text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def last_json(stdout: str) -> dict[str, object]:
    for line in reversed([item.strip() for item in stdout.splitlines() if item.strip()]):
        if line.startswith("{") and line.endswith("}"):
            return json.loads(line)
    raise ValueError(f"no JSON result in stdout: {stdout[-500:]}")


def main() -> int:
    if not EXE.exists():
        print(json.dumps({"status": "fail", "reason": f"missing {EXE}"}, ensure_ascii=False))
        return 1
    with tempfile.TemporaryDirectory(prefix="tos-ko-exe-test-") as temp:
        data_root = Path(temp) / "Tales Of Seikyu_Data"
        target_dir = data_root / "StreamingAssets/aa/StandaloneWindows64"
        target_dir.mkdir(parents=True)
        shutil.copy2(EXCEL_SOURCE, target_dir / EXCEL_BUNDLE_NAME)
        shutil.copy2(BAG_SOURCE, target_dir / "uiview_assets_bagfunctionitem_c03f77ea6e9f3cdb429d41f0f3886553.bundle")
        export_dir = Path(temp) / "exported_patch"
        export = run([str(EXE), "--no-gui", "--game-data", str(data_root), "--export-patch", "--export-dir", str(export_dir)])
        install = run([str(EXE), "--no-gui", "--game-data", str(data_root), "--install"])
        verify = run([str(EXE), "--no-gui", "--game-data", str(data_root), "--verify"])
        restore = run([str(EXE), "--no-gui", "--game-data", str(data_root), "--restore"])
        if export.returncode or install.returncode or verify.returncode or restore.returncode:
            print(
                json.dumps(
                    {
                        "status": "fail",
                        "export": export.stdout + export.stderr,
                        "install": install.stdout + install.stderr,
                        "verify": verify.stdout + verify.stderr,
                        "restore": restore.stdout + restore.stderr,
                    },
                    ensure_ascii=False,
                )
            )
            return 1
        export_result = last_json(export.stdout)
        manifest = Path(str(export_result.get("manifest", "")))
        if not manifest.exists() or len(export_result.get("files", [])) != 2:
            print(json.dumps({"status": "fail", "reason": "export manifest/files missing", "export": export_result}, ensure_ascii=False))
            return 1
        verify_result = last_json(verify.stdout)
        if not verify_result.get("font_ok") or not verify_result.get("ui_font_alias_ok"):
            print(json.dumps({"status": "fail", "reason": "font_ok was not true", "verify": verify_result}, ensure_ascii=False))
            return 1
    print(json.dumps({"status": "pass", "exe": str(EXE), "font_ok": True, "ui_font_alias_ok": True}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
