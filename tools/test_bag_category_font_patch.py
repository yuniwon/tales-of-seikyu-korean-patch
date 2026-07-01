from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC_GAME_DATA = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Tales of Seikyu\Tales Of Seikyu_Data")
BAG_SOURCE = SRC_GAME_DATA / ".tos_korean_patch/baselines/0.1.7-playtest.20260701/bag.e4eabffd3e04ce96.bak"
BAG_BUNDLE_NAME = "uiview_assets_bagfunctionitem_c03f77ea6e9f3cdb429d41f0f3886553.bundle"
sys.path.insert(0, str(REPO / "src"))

from tos_ko_patcher.core import apply_bag_font_patch, inspect_bag_font, load_payload, sha256_file  # noqa: E402


def main() -> int:
    payload = load_payload(REPO / "payload/patch_payload.json")
    font_patch = payload["bag_function_bundle"]["font_patch"]
    expected_names = font_patch.get("local_font_names") or [font_patch["local_font_name"]]
    with tempfile.TemporaryDirectory(prefix="tos-ko-bag-category-font-", ignore_cleanup_errors=True) as temp:
        data_root = Path(temp) / "Tales Of Seikyu_Data"
        bundle_dir = data_root / "StreamingAssets/aa/StandaloneWindows64"
        bundle_dir.mkdir(parents=True)
        bundle = bundle_dir / BAG_BUNDLE_NAME
        shutil.copy2(BAG_SOURCE, bundle)
        before = inspect_bag_font(bundle, payload)
        patched_hash = apply_bag_font_patch(data_root, bundle, payload)
        after = inspect_bag_font(bundle, payload)

    hit_names = [item.get("name") for item in after.get("fallback_hits", [])]
    ok = (
        not before["font_fallback_ok"]
        and after["font_fallback_ok"]
        and sorted(hit_names) == sorted(expected_names)
        and all(item.get("has_fallback") for item in after.get("fallback_hits", []))
    )
    print(
        json.dumps(
            {
                "status": "pass" if ok else "fail",
                "source_sha256": sha256_file(BAG_SOURCE),
                "patched_sha256": patched_hash,
                "expected_names": expected_names,
                "before": before,
                "after": after,
            },
            ensure_ascii=False,
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
