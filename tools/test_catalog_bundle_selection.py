from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from tos_ko_patcher.core import PatchError, find_single_bundle, sha256_file  # noqa: E402


PATTERN = "StreamingAssets/aa/StandaloneWindows64/uiview_assets_bagfunctionitem_*.bundle"


def write_catalog(game_data: Path, *bundle_names: str) -> None:
    catalog = game_data / "StreamingAssets/aa/catalog.bin"
    catalog.parent.mkdir(parents=True, exist_ok=True)
    locations = [
        f"{{UnityEngine.AddressableAssets.Addressables.RuntimePath}}\\StandaloneWindows64\\{name}.bundle"
        for name in bundle_names
    ]
    catalog.write_bytes(("\x00".join(locations) + "\x00").encode("utf-8"))


def selection_error(game_data: Path) -> bool:
    try:
        find_single_bundle(game_data, PATTERN, set())
    except PatchError as exc:
        return "지원되는 해시의 번들을 찾지 못했습니다" in str(exc)
    return False


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="tos-ko-catalog-selection-") as temp:
        game_data = Path(temp) / "Tales Of Seikyu_Data"
        bundle_dir = game_data / "StreamingAssets/aa/StandaloneWindows64"
        bundle_dir.mkdir(parents=True)
        stale = bundle_dir / "uiview_assets_bagfunctionitem_stale.bundle"
        active = bundle_dir / "uiview_assets_bagfunctionitem_active.bundle"
        stale.write_bytes(b"stale")
        active.write_bytes(b"active-original")

        write_catalog(game_data, active.stem)
        stale_known_hash = sha256_file(stale)
        selected_before = find_single_bundle(game_data, PATTERN, {stale_known_hash})
        active.write_bytes(b"active-patched")
        selected_after = find_single_bundle(game_data, PATTERN, {stale_known_hash})

        (game_data / "StreamingAssets/aa/catalog.bin").unlink()
        missing_catalog_rejected = selection_error(game_data)
        write_catalog(game_data, stale.stem, active.stem)
        ambiguous_catalog_rejected = selection_error(game_data)

    ok = (
        selected_before.name == active.name
        and selected_after.name == active.name
        and missing_catalog_rejected
        and ambiguous_catalog_rejected
    )
    print(
        json.dumps(
            {
                "status": "pass" if ok else "fail",
                "selected_before": selected_before.name,
                "selected_after": selected_after.name,
                "missing_catalog_rejected": missing_catalog_rejected,
                "ambiguous_catalog_rejected": ambiguous_catalog_rejected,
            },
            ensure_ascii=False,
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
