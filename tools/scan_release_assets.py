from __future__ import annotations

import json
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FORBIDDEN_EXT = {".bundle", ".assets", ".ress", ".resource"}
ALLOWED_EXE = {"TalesOfSeikyuKoreanPatch.exe"}


def bad_path(path: str) -> str | None:
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix in FORBIDDEN_EXT:
        return f"forbidden asset extension: {path}"
    if suffix == ".exe" and p.name not in ALLOWED_EXE:
        return f"unexpected executable: {path}"
    return None


def main() -> int:
    failures: list[str] = []
    for path in REPO.rglob("*"):
        if ".git" in path.parts or "__pycache__" in path.parts or "build" in path.parts:
            continue
        if path.is_file():
            rel = path.relative_to(REPO).as_posix()
            reason = bad_path(rel)
            if reason:
                failures.append(reason)
    for zip_path in (REPO / "dist").glob("*.zip"):
        with zipfile.ZipFile(zip_path) as zf:
            for name in zf.namelist():
                reason = bad_path(name)
                if reason:
                    failures.append(f"{zip_path.name}: {reason}")
    result = {"status": "pass" if not failures else "fail", "failure_count": len(failures), "failures": failures[:20]}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
