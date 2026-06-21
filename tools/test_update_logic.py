from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from tos_ko_patcher.core import expected_asset_sha256, release_update_status, select_release_asset  # noqa: E402


def main() -> int:
    release = {
        "tag_name": "v0.1.2-playtest.20260621",
        "html_url": "https://github.com/yuniwon/tales-of-seikyu-korean-patch/releases/tag/v0.1.2-playtest.20260621",
        "published_at": "2026-06-21T00:00:00Z",
        "assets": [
            {
                "name": "notes.txt",
                "browser_download_url": "https://example.invalid/notes.txt",
                "size": 10,
            },
            {
                "name": "TalesOfSeikyuKoreanPatch-v0.1.2.zip",
                "browser_download_url": "https://example.invalid/TalesOfSeikyuKoreanPatch-v0.1.2.zip",
                "size": 123,
                "digest": "sha256:abc123",
            },
        ],
    }
    asset = select_release_asset(release)
    status = release_update_status(release, current_tag="v0.1.1-playtest.20260621")
    checks = {
        "selected_asset": asset["name"] if asset else "",
        "update_status": status["status"],
        "is_newer": status["is_newer"],
        "digest": expected_asset_sha256(asset or {}),
        "ahead_status": release_update_status(release, current_tag="v0.1.3-playtest.20260621")["status"],
        "missing_asset": select_release_asset({"assets": [{"name": "README.md"}]}) is None,
    }
    expected = {
        "selected_asset": "TalesOfSeikyuKoreanPatch-v0.1.2.zip",
        "update_status": "update_available",
        "is_newer": True,
        "digest": "abc123",
        "ahead_status": "ahead",
        "missing_asset": True,
    }
    if checks != expected:
        print(json.dumps({"status": "fail", "checks": checks, "expected": expected}, ensure_ascii=False))
        return 1
    print(json.dumps({"status": "pass", **checks}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
