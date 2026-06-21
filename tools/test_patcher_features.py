from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from tos_ko_patcher.core import discover_steam_game_data, font_status_from_inspection, parse_acf_field  # noqa: E402


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="tos-ko-feature-test-") as temp:
        root = Path(temp)
        steam_root = root / "Steam"
        steamapps = steam_root / "steamapps"
        library = root / "SteamLibrary"
        library_steamapps = library / "steamapps"
        data_dir = library_steamapps / "common" / "Tales of Seikyu" / "Tales Of Seikyu_Data" / "StreamingAssets"
        data_dir.mkdir(parents=True)
        steamapps.mkdir(parents=True, exist_ok=True)
        library_steamapps.mkdir(parents=True, exist_ok=True)
        escaped_library = str(library).replace("\\", "\\\\")
        (steamapps / "libraryfolders.vdf").write_text(f'"libraryfolders"\n{{\n  "0"\n  {{\n    "path" "{escaped_library}"\n  }}\n}}\n', encoding="utf-8")
        manifest = library_steamapps / "appmanifest_2340520.acf"
        manifest.write_text('"AppState"\n{\n  "appid" "2340520"\n  "installdir" "Tales of Seikyu"\n  "buildid" "123"\n}\n', encoding="utf-8")

        discovered = discover_steam_game_data([steam_root])
        expected = data_dir.parent.resolve()
        checks = {
            "acf_installdir": parse_acf_field(manifest.read_text(encoding="utf-8"), "installdir"),
            "steam_discovery": str(discovered),
            "steam_discovery_expected": str(expected),
            "font_ok": font_status_from_inspection(
                {
                    "font_fallback_ok": True,
                    "local_font_name": "LiberationSans SDF",
                    "external_file_id": 4,
                    "fallback_font_path_id": 99,
                    "fallback_hits": [{"has_fallback": True}, {"has_fallback": False}],
                }
            ),
        }
    if checks["acf_installdir"] != "Tales of Seikyu" or checks["steam_discovery"] != checks["steam_discovery_expected"]:
        print(json.dumps({"status": "fail", **checks}, ensure_ascii=False))
        return 1
    if checks["font_ok"]["font_fallback_hit_count"] != 1 or checks["font_ok"]["font_fallback_candidate_count"] != 2:
        print(json.dumps({"status": "fail", **checks}, ensure_ascii=False))
        return 1
    print(json.dumps({"status": "pass", **checks}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
