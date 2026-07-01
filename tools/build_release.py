from __future__ import annotations

import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VERSION = "0.1.8-playtest.20260701"
EXE_NAME = "TalesOfSeikyuKoreanPatch.exe"


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=str(REPO), text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def main() -> int:
    shutil.rmtree(REPO / "build", ignore_errors=True)
    shutil.rmtree(REPO / "dist", ignore_errors=True)
    args = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        "--onefile",
        "--name",
        "TalesOfSeikyuKoreanPatch",
        "--paths",
        "src",
        "--hidden-import",
        "UnityPy.resources",
        "--collect-data",
        "UnityPy",
        "--exclude-module",
        "pandas",
        "--exclude-module",
        "pyarrow",
        "--exclude-module",
        "sqlalchemy",
        "--exclude-module",
        "numpy",
        "--exclude-module",
        "matplotlib",
        "--add-data",
        "payload/patch_payload.json;payload",
        "src/tos_ko_patcher/app.py",
    ]
    proc = run(args)
    if proc.returncode:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        return proc.returncode
    dist = REPO / "dist"
    exe = dist / EXE_NAME
    if not exe.exists():
        print(json.dumps({"status": "fail", "reason": f"missing {exe}"}, ensure_ascii=False))
        return 1
    zip_path = dist / f"TalesOfSeikyuKoreanPatch-v{VERSION}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.write(exe, EXE_NAME)
        for name in ["README.md", "RELEASE_NOTES.md", "LICENSE"]:
            zf.write(REPO / name, name)
    print(json.dumps({"status": "pass", "exe": str(exe), "zip": str(zip_path), "zip_size": zip_path.stat().st_size}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
