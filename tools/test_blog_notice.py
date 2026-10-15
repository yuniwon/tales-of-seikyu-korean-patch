from __future__ import annotations

import json
import tempfile
from pathlib import Path

from build_blog_notice import build_notice, load_payload, write_notice

REPO = Path(__file__).resolve().parents[1]
ZIP_SHA256 = "564455da53d8da00e392f5574272b5c1bc1e419fb2ae2d3ed098c7cb8933e5de"


def main() -> int:
    payload = load_payload(REPO / "payload/patch_payload.json")
    release_notes = (REPO / "RELEASE_NOTES.md").read_text(encoding="utf-8")
    notice = build_notice(payload, release_notes, zip_sha256=ZIP_SHA256)

    checks = {
        "title_has_public_version": "v0.1.17 배포" in notice.title,
        "title_hides_internal_version": "playtest" not in notice.title,
        "metadata_has_full_version": notice.metadata["version"] == "0.1.17-playtest.20261015",
        "body_has_zip": "TalesOfSeikyuKoreanPatch-v0.1.17-playtest.20261015.zip" in notice.body,
        "body_has_sha": ZIP_SHA256 in notice.body,
        "body_has_row_count": "22,531행" in notice.body,
        "body_has_buildid": "24948693" in notice.body,
        "metadata_patch_rows": notice.metadata["patch_rows"] == 22531,
        "metadata_edit_url": notice.metadata["blog_edit_url"].endswith("/postupdate?logNo=224322599998"),
    }
    with tempfile.TemporaryDirectory(prefix="tos-ko-blog-notice-test-") as temp:
        paths = write_notice(notice, Path(temp))
        files_exist = all(Path(path).exists() for path in paths.values())
        metadata = json.loads(Path(paths["metadata"]).read_text(encoding="utf-8"))
        checks["files_exist"] = files_exist
        checks["metadata_roundtrip"] = metadata["zip_sha256"] == ZIP_SHA256

    ok = all(checks.values())
    print(json.dumps({"status": "pass" if ok else "fail", **checks}, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
