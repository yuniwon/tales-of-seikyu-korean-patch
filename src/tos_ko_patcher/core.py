from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import sys
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import UnityPy
from UnityPy.files.SerializedFile import FileIdentifier


PATCH_VERSION = "0.1.4-playtest.20260623"
PATCH_TAG = f"v{PATCH_VERSION}"
GITHUB_REPO = "yuniwon/tales-of-seikyu-korean-patch"
LATEST_RELEASE_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
RELEASES_URL = f"https://github.com/{GITHUB_REPO}/releases/latest"
STEAM_APP_ID = "2340520"
STEAM_APP_URL = f"steam://rungameid/{STEAM_APP_ID}"
GAME_EXE_NAME = "Tales Of Seikyu.exe"
DEFAULT_STEAM_DATA = Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Steam/steamapps/common/Tales of Seikyu/Tales Of Seikyu_Data"
EXCEL_GLOB = "StreamingAssets/aa/StandaloneWindows64/configs_assets_excel_*.bundle"
BAG_GLOB = "StreamingAssets/aa/StandaloneWindows64/uiview_assets_bagfunctionitem_*.bundle"
PATCH_STATE_DIR = ".tos_korean_patch"
PAYLOAD_RELATIVE = Path("payload/patch_payload.json")
RELEASE_ASSET_PREFIX = "TalesOfSeikyuKoreanPatch"
USER_AGENT = f"tos-ko-patcher/{PATCH_VERSION}"

AVG_COLUMNS = [
    "text_id",
    "speaker_id",
    "dialog_id",
    "surface",
    "speaker_name",
    "source_en",
    "source_de",
    "source_zh_cn",
    "source_unused",
    "source_ja",
    "source_fr",
    "source_es",
]

CONTEXT_COLUMNS = [
    "text_id",
    "story_id",
    "node_id",
    "surface",
    "source_en",
    "source_de",
    "source_zh_cn",
    "source_unused",
    "source_ja",
    "source_fr",
    "source_es",
]

KEYED_DEFAULT_COLUMNS = [
    "row_key",
    "source_zh_cn",
    "source_ja",
    "source_en",
    "source_de",
    "source_fr",
    "source_es",
]

KEYED_CUSTOM_COLUMNS = [
    "row_key",
    "source_en",
    "source_zh_cn",
    "source_ja",
    "source_de",
    "source_fr",
    "source_es",
]

SCHEMA_COLUMNS = {
    "avg": AVG_COLUMNS,
    "context": CONTEXT_COLUMNS,
    "keyed_default": KEYED_DEFAULT_COLUMNS,
    "keyed_custom": KEYED_CUSTOM_COLUMNS,
}

AVG_TABLES = {"i18n_avg_default", "i18n_alone_avg_default"}
CONTEXT_TABLES = {"i18n_quest_default"}
KEYED_CUSTOM_TABLES = {
    "i18n_custom",
    "i18n_birthday_options",
    "i18n_npc_invitation",
    "i18n_quest_related",
}


class PatchError(RuntimeError):
    """User-facing patcher error."""


@dataclass
class ParsedTable:
    name: str
    schema: str
    count: int
    rows: list[dict[str, object]]


def log_noop(message: str) -> None:
    del message


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def default_download_dir() -> Path:
    downloads = Path.home() / "Downloads"
    return downloads if downloads.exists() else Path.home()


def default_export_dir() -> Path:
    return default_download_dir() / "TalesOfSeikyuKoreanPatch-export"


def parse_acf_field(text: str, field: str) -> str:
    match = re.search(rf'"{re.escape(field)}"\s+"([^"]+)"', text)
    return match.group(1).replace("\\\\", "\\") if match else ""


def steam_root_candidates() -> list[Path]:
    candidates = [
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Steam",
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Steam",
    ]
    local = os.environ.get("LOCALAPPDATA")
    if local:
        candidates.append(Path(local) / "Steam")
    seen: set[Path] = set()
    result: list[Path] = []
    for candidate in candidates:
        resolved = candidate.expanduser()
        if resolved not in seen:
            seen.add(resolved)
            result.append(resolved)
    return result


def steamapps_from_root(steam_root: Path) -> list[Path]:
    steamapps = steam_root / "steamapps"
    candidates = [steamapps]
    libraryfolders = steamapps / "libraryfolders.vdf"
    if libraryfolders.exists():
        text = libraryfolders.read_text(encoding="utf-8", errors="ignore")
        for path_text in re.findall(r'"path"\s+"([^"]+)"', text):
            candidates.append(Path(path_text.replace("\\\\", "\\")) / "steamapps")
    seen: set[Path] = set()
    result: list[Path] = []
    for candidate in candidates:
        try:
            resolved = candidate.expanduser().resolve()
        except OSError:
            resolved = candidate.expanduser()
        if resolved not in seen:
            seen.add(resolved)
            result.append(resolved)
    return result


def discover_steam_game_data(steam_roots: list[Path] | None = None) -> Path | None:
    for steam_root in steam_roots or steam_root_candidates():
        for steamapps in steamapps_from_root(steam_root):
            manifest = steamapps / f"appmanifest_{STEAM_APP_ID}.acf"
            if not manifest.exists():
                continue
            text = manifest.read_text(encoding="utf-8", errors="ignore")
            install_dir = parse_acf_field(text, "installdir") or "Tales of Seikyu"
            game_root = steamapps / "common" / install_dir
            data_dir = game_root / "Tales Of Seikyu_Data"
            if (data_dir / "StreamingAssets").exists():
                return data_dir.resolve()
    return None


def launch_game(log: Callable[[str], None] = log_noop) -> dict[str, Any]:
    import webbrowser

    opened = webbrowser.open(STEAM_APP_URL)
    log(f"Steam 실행 요청: {STEAM_APP_URL}")
    return {"status": "launch_requested" if opened else "launch_request_failed", "steam_url": STEAM_APP_URL, "appid": STEAM_APP_ID}


def release_tag_key(tag: str) -> list[tuple[int, int | str]]:
    tokens = re.findall(r"\d+|[A-Za-z]+", tag.lstrip("vV"))
    key: list[tuple[int, int | str]] = []
    for token in tokens:
        if token.isdigit():
            key.append((1, int(token)))
        else:
            key.append((0, token.lower()))
    return key


def compare_release_tags(left: str, right: str) -> int:
    left_key = release_tag_key(left)
    right_key = release_tag_key(right)
    return (left_key > right_key) - (left_key < right_key)


def fetch_latest_release(api_url: str = LATEST_RELEASE_API, timeout: int = 10) -> dict[str, Any]:
    request = urllib.request.Request(
        api_url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        raise PatchError(f"GitHub 최신 릴리스 확인에 실패했습니다: {exc}") from exc


def select_release_asset(release: dict[str, Any]) -> dict[str, Any] | None:
    assets = release.get("assets") or []
    if not isinstance(assets, list):
        return None

    def is_zip(asset: dict[str, Any]) -> bool:
        name = str(asset.get("name") or "")
        return name.lower().endswith(".zip") and bool(asset.get("browser_download_url"))

    preferred = [
        asset
        for asset in assets
        if isinstance(asset, dict) and is_zip(asset) and str(asset.get("name") or "").startswith(RELEASE_ASSET_PREFIX)
    ]
    if preferred:
        return preferred[0]
    fallback = [asset for asset in assets if isinstance(asset, dict) and is_zip(asset)]
    return fallback[0] if fallback else None


def release_update_status(release: dict[str, Any], current_tag: str = PATCH_TAG) -> dict[str, Any]:
    latest_tag = str(release.get("tag_name") or "")
    if not latest_tag:
        raise PatchError("GitHub 릴리스 응답에 tag_name이 없습니다.")
    asset = select_release_asset(release)
    comparison = compare_release_tags(latest_tag, current_tag)
    if comparison > 0:
        status = "update_available"
    elif comparison == 0:
        status = "current"
    else:
        status = "ahead"
    return {
        "status": status,
        "current_tag": current_tag,
        "latest_tag": latest_tag,
        "is_newer": comparison > 0,
        "release_url": release.get("html_url") or RELEASES_URL,
        "published_at": release.get("published_at") or "",
        "asset_name": asset.get("name") if asset else "",
        "asset_size": asset.get("size") if asset else 0,
        "asset_digest": asset.get("digest") if asset else "",
        "asset": asset,
    }


def check_latest_release(timeout: int = 10) -> dict[str, Any]:
    return release_update_status(fetch_latest_release(timeout=timeout))


def expected_asset_sha256(asset: dict[str, Any]) -> str:
    digest = str(asset.get("digest") or "")
    if digest.lower().startswith("sha256:"):
        return digest.split(":", 1)[1].lower()
    return ""


def download_release_asset(
    asset: dict[str, Any],
    dest_dir: Path | None = None,
    log: Callable[[str], None] = log_noop,
    progress: Callable[[int, int], None] | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    url = str(asset.get("browser_download_url") or "")
    name = Path(str(asset.get("name") or "")).name
    if not url or not name.lower().endswith(".zip"):
        raise PatchError("다운로드 가능한 ZIP 릴리스 자산을 찾지 못했습니다.")

    target_dir = (dest_dir or default_download_dir()).expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / name
    part = target.with_name(f"{target.name}.part")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    expected_hash = expected_asset_sha256(asset)

    log(f"다운로드 시작: {name}")
    h = hashlib.sha256()
    downloaded = 0
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            total = int(response.headers.get("Content-Length") or asset.get("size") or 0)
            with part.open("wb") as handle:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    handle.write(chunk)
                    h.update(chunk)
                    downloaded += len(chunk)
                    if progress:
                        progress(downloaded, total)
        actual_hash = h.hexdigest()
        if expected_hash and actual_hash.lower() != expected_hash:
            raise PatchError(f"다운로드 해시 검증 실패: expected={expected_hash}, actual={actual_hash}")
        if target.exists():
            target.unlink()
        part.replace(target)
    except Exception:
        part.unlink(missing_ok=True)
        raise

    log(f"다운로드 완료: {target}")
    return {
        "status": "downloaded",
        "path": str(target),
        "sha256": actual_hash,
        "expected_sha256": expected_hash,
        "size": downloaded,
    }


def download_latest_release(
    dest_dir: Path | None = None,
    log: Callable[[str], None] = log_noop,
    progress: Callable[[int, int], None] | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    release = fetch_latest_release(timeout=timeout)
    status = release_update_status(release)
    asset = status.get("asset")
    if not isinstance(asset, dict):
        raise PatchError("최신 릴리스에 다운로드 가능한 ZIP 자산이 없습니다.")
    result = download_release_asset(asset, dest_dir, log, progress, timeout)
    return {**status, **result, "asset": None}


def read_u32(raw: bytes, pos: int) -> tuple[int, int]:
    return struct.unpack_from("<I", raw, pos)[0], pos + 4


def write_u32(value: int) -> bytes:
    return struct.pack("<I", value)


def read_7bit_int(raw: bytes, pos: int) -> tuple[int, int]:
    count = 0
    shift = 0
    while True:
        if pos >= len(raw):
            raise ValueError("unterminated 7-bit integer")
        byte = raw[pos]
        pos += 1
        count |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return count, pos
        shift += 7
        if shift > 35:
            raise ValueError("7-bit integer is too long")


def write_7bit_int(value: int) -> bytes:
    if value < 0:
        raise ValueError("negative 7-bit integer")
    out = bytearray()
    while value >= 0x80:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    out.append(value)
    return bytes(out)


def read_string(raw: bytes, pos: int) -> tuple[str, int]:
    length, pos = read_7bit_int(raw, pos)
    data = raw[pos : pos + length]
    if len(data) != length:
        raise ValueError("string exceeds table length")
    return data.decode("utf-8"), pos + length


def write_string(value: str) -> bytes:
    data = value.encode("utf-8")
    return write_7bit_int(len(data)) + data


def script_to_raw(value: str) -> bytes:
    return value.encode("utf-8", "surrogateescape")


def raw_to_script(value: bytes) -> str:
    return value.decode("utf-8", "surrogateescape")


def schema_for_textasset(name: str) -> str:
    lowered = name.lower()
    if lowered in AVG_TABLES:
        return "avg"
    if lowered in CONTEXT_TABLES:
        return "context"
    if lowered in KEYED_CUSTOM_TABLES:
        return "keyed_custom"
    return "keyed_default"


def key_column_for_schema(schema: str) -> str:
    return "text_id" if "text_id" in SCHEMA_COLUMNS[schema] else "row_key"


def parse_string_table(name: str, raw: bytes, schema: str) -> ParsedTable:
    columns = SCHEMA_COLUMNS[schema]
    pos = 0
    count, pos = read_u32(raw, pos)
    rows: list[dict[str, object]] = []
    for _ in range(count):
        row_id, pos = read_u32(raw, pos)
        row: dict[str, object] = {"row_id": row_id}
        for column in columns:
            value, pos = read_string(raw, pos)
            row[column] = value
        rows.append(row)
    if pos != len(raw):
        raise ValueError(f"{name} trailing bytes: {len(raw) - pos}")
    return ParsedTable(name=name, schema=schema, count=count, rows=rows)


def serialize_string_table(table: ParsedTable) -> bytes:
    columns = SCHEMA_COLUMNS[table.schema]
    out = bytearray(write_u32(table.count))
    for row in table.rows:
        out += write_u32(int(row["row_id"]))
        for column in columns:
            out += write_string(str(row[column]))
    return bytes(out)


def textassets_from_bundle(bundle_path: Path) -> dict[str, bytes]:
    env = UnityPy.load(str(bundle_path))
    result: dict[str, bytes] = {}
    for obj in env.objects:
        if obj.type.name != "TextAsset":
            continue
        data = obj.read()
        name = getattr(data, "name", "") or getattr(data, "m_Name", "")
        tree = obj.read_typetree()
        result[name] = script_to_raw(tree.get("m_Script") or "")
    return result


def save_textassets_to_bundle(source_bundle: Path, out_dir: Path, new_raw_by_name: dict[str, bytes]) -> Path:
    env = UnityPy.load(str(source_bundle))
    seen: set[str] = set()
    for obj in env.objects:
        if obj.type.name != "TextAsset":
            continue
        data = obj.read()
        name = getattr(data, "name", "") or getattr(data, "m_Name", "")
        if name not in new_raw_by_name:
            continue
        tree = obj.read_typetree()
        tree["m_Script"] = raw_to_script(new_raw_by_name[name])
        obj.save_typetree(tree)
        seen.add(name)
    missing = set(new_raw_by_name) - seen
    if missing:
        raise PatchError(f"TextAsset not found while saving: {sorted(missing)}")
    out_dir.mkdir(parents=True, exist_ok=True)
    env.save(out_path=str(out_dir))
    saved = out_dir / source_bundle.name
    if not saved.exists():
        raise PatchError(f"UnityPy did not create expected bundle: {saved}")
    return saved


def resource_path(relative: Path = PAYLOAD_RELATIVE) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
    return base / relative


def load_payload(path: Path | None = None) -> dict[str, Any]:
    payload_path = path or resource_path()
    return json.loads(payload_path.read_text(encoding="utf-8"))


def normalize_game_data(path: Path) -> Path:
    path = path.expanduser().resolve()
    if (path / "StreamingAssets").exists():
        return path
    nested = path / "Tales Of Seikyu_Data"
    if (nested / "StreamingAssets").exists():
        return nested.resolve()
    raise PatchError("Tales Of Seikyu_Data 폴더를 찾을 수 없습니다.")


def default_game_data() -> Path:
    return discover_steam_game_data() or DEFAULT_STEAM_DATA


def find_single_bundle(game_data: Path, pattern: str, expected_hashes: set[str]) -> Path:
    matches = sorted(game_data.glob(pattern))
    if not matches:
        raise PatchError(f"대상 번들을 찾을 수 없습니다: {pattern}")
    hashed: list[tuple[Path, str]] = [(path, sha256_file(path)) for path in matches]
    for path, digest in hashed:
        if digest in expected_hashes:
            return path
    if len(matches) == 1:
        return matches[0]
    details = "\n".join(f"- {path.name}: {digest}" for path, digest in hashed)
    raise PatchError(f"지원되는 해시의 번들을 찾지 못했습니다.\n{details}")


def state_dir(game_data: Path) -> Path:
    return game_data / PATCH_STATE_DIR


def backup_file(game_data: Path, source: Path, digest: str, log: Callable[[str], None]) -> Path:
    backup = state_dir(game_data) / "backups" / PATCH_VERSION / f"{source.name}.{digest}.bak"
    if not backup.exists():
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, backup)
        log(f"백업 생성: {backup}")
    else:
        log(f"기존 백업 사용: {backup}")
    return backup


def copy_with_parent(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def excel_ui_font_patch(payload: dict[str, Any]) -> dict[str, Any]:
    patch = payload.get("excel_bundle", {}).get("ui_font_patch") or {}
    return patch if isinstance(patch, dict) else {}


def font_alias_token(alias: str) -> bytes:
    return write_string(alias)


def apply_excel_ui_font_alias_patch(raw: bytes, payload: dict[str, Any]) -> tuple[bytes, int]:
    patch = excel_ui_font_patch(payload)
    if not patch:
        return raw, 0
    old_alias = str(patch["old_alias"])
    new_alias = str(patch["new_alias"])
    old_token = font_alias_token(old_alias)
    new_token = font_alias_token(new_alias)
    replacements = raw.count(old_token)
    if not replacements:
        return raw, 0
    return raw.replace(old_token, new_token), replacements


def inspect_excel_ui_font(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    patch = excel_ui_font_patch(payload)
    if not patch:
        return {"ui_font_patch_configured": False, "ui_font_alias_ok": True}
    textasset = str(patch["textasset"])
    old_alias = str(patch["old_alias"])
    new_alias = str(patch["new_alias"])
    expected = int(patch.get("expected_replacements") or 1)
    raw_by_name = textassets_from_bundle(path)
    raw = raw_by_name.get(textasset)
    if raw is None:
        return {
            "ui_font_patch_configured": True,
            "ui_font_textasset": textasset,
            "ui_font_alias_ok": False,
            "ui_font_alias_error": "textasset_missing",
            "old_ui_font_alias": old_alias,
            "old_ui_font_alias_count": 0,
            "korean_ui_font_alias": new_alias,
            "korean_ui_font_alias_count": 0,
            "expected_ui_font_alias_count": expected,
        }
    old_count = raw.count(font_alias_token(old_alias))
    new_count = raw.count(font_alias_token(new_alias))
    return {
        "ui_font_patch_configured": True,
        "ui_font_textasset": textasset,
        "ui_font_alias_ok": old_count == 0 and new_count >= expected,
        "old_ui_font_alias": old_alias,
        "old_ui_font_alias_count": old_count,
        "korean_ui_font_alias": new_alias,
        "korean_ui_font_alias_count": new_count,
        "expected_ui_font_alias_count": expected,
    }


def planned_excel_textassets(bundle: Path, payload: dict[str, Any]) -> tuple[dict[str, bytes], int]:
    raw_by_name = textassets_from_bundle(bundle)
    by_textasset: dict[str, list[dict[str, Any]]] = {}
    for entry in payload["excel_bundle"]["patch_rows"]:
        by_textasset.setdefault(entry["textasset"], []).append(entry)

    planned: dict[str, bytes] = {}
    changed = 0
    for textasset, entries in sorted(by_textasset.items()):
        if textasset not in raw_by_name:
            raise PatchError(f"TextAsset missing in bundle: {textasset}")
        schema = entries[0]["schema"]
        table = parse_string_table(textasset, raw_by_name[textasset], schema)
        key_column = key_column_for_schema(schema)
        lookup = {(str(row["row_id"]), str(row.get(key_column, ""))): row for row in table.rows}
        for entry in entries:
            key = (str(entry["row_id"]), str(entry["key"]))
            row = lookup.get(key)
            if row is None:
                raise PatchError(f"패치 대상 행을 찾지 못했습니다: {textasset} {key}")
            if str(row.get("source_ja", "")) != entry["source_ja"]:
                row["source_ja"] = entry["source_ja"]
                changed += 1
        planned[textasset] = serialize_string_table(table)

    font_patch = excel_ui_font_patch(payload)
    if font_patch:
        textasset = str(font_patch["textasset"])
        if textasset not in raw_by_name:
            raise PatchError(f"UI font TextAsset missing in bundle: {textasset}")
        base_raw = planned.get(textasset, raw_by_name[textasset])
        patched_raw, replacements = apply_excel_ui_font_alias_patch(base_raw, payload)
        if replacements:
            planned[textasset] = patched_raw
            changed += replacements
    return planned, changed


def apply_excel_patch(game_data: Path, bundle: Path, payload: dict[str, Any], log: Callable[[str], None] = log_noop) -> str:
    digest = sha256_file(bundle)
    excel = payload["excel_bundle"]
    accepted = set(excel.get("accepted_patched_sha256", [])) | {excel.get("target_sha256", "")}
    ui_font_status = inspect_excel_ui_font(bundle, payload)
    if digest in accepted and ui_font_status["ui_font_alias_ok"]:
        log("Excel 번들은 이미 패치되어 있습니다.")
        return digest
    if digest != excel["source_sha256"] and digest not in accepted:
        raise PatchError(f"지원하지 않는 Excel 번들 해시입니다: {digest}")
    backup_file(game_data, bundle, digest, log)
    planned, changed = planned_excel_textassets(bundle, payload)
    log(f"Excel TextAsset 변경 행: {changed}")
    with tempfile.TemporaryDirectory(prefix="tos-ko-excel-") as temp:
        saved = save_textassets_to_bundle(bundle, Path(temp), planned)
        copy_with_parent(saved, bundle)
    new_digest = sha256_file(bundle)
    accepted_after = set(excel.get("accepted_patched_sha256", [])) | {excel["target_sha256"]}
    if new_digest not in accepted_after:
        raise PatchError(f"Excel 패치 후 해시 검증 실패: {new_digest}")
    return new_digest


def external_index(asset: Any, external_path: str) -> int | None:
    for index, item in enumerate(asset.externals, start=1):
        if item.path == external_path:
            return index
    return None


def make_file_identifier(external_path: str) -> FileIdentifier:
    identifier = FileIdentifier.__new__(FileIdentifier)
    FileIdentifier.__attrs_init__(identifier, external_path, "", b"\x00" * 16, 0)
    return identifier


def ensure_external(asset: Any, external_path: str) -> tuple[int, bool]:
    existing = external_index(asset, external_path)
    if existing is not None:
        return existing, False
    asset.externals.append(make_file_identifier(external_path))
    return len(asset.externals), True


def has_ptr(items: list[dict[str, int]], file_id: int, path_id: int) -> bool:
    return any(int(item.get("m_FileID", -1)) == file_id and int(item.get("m_PathID", 0)) == path_id for item in items)


def inspect_bag_font(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    font_patch = payload["bag_function_bundle"]["font_patch"]
    env = UnityPy.load(str(path))
    asset = env.assets[0]
    file_id = external_index(asset, font_patch["external_path"])
    fallback_hits: list[dict[str, Any]] = []
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        try:
            tree = obj.read_typetree()
        except Exception:
            continue
        if tree.get("m_Name") == font_patch["local_font_name"]:
            table = tree.get("m_FallbackFontAssetTable") or []
            fallback_hits.append(
                {
                    "path_id": obj.path_id,
                    "has_fallback": file_id is not None and has_ptr(table, file_id, int(font_patch["fallback_font_path_id"])),
                    "fallback_count": len(table),
                }
            )
    return {
        "external_file_id": file_id,
        "fallback_hits": fallback_hits,
        "font_fallback_ok": file_id is not None and any(item["has_fallback"] for item in fallback_hits),
        "local_font_name": font_patch["local_font_name"],
        "external_path": font_patch["external_path"],
        "fallback_font_path_id": int(font_patch["fallback_font_path_id"]),
    }


def font_status_from_inspection(inspection: dict[str, Any]) -> dict[str, Any]:
    fallback_hits = inspection.get("fallback_hits") or []
    fallback_count = sum(1 for item in fallback_hits if item.get("has_fallback"))
    return {
        "font_ok": bool(inspection.get("font_fallback_ok")),
        "font_local_name": inspection.get("local_font_name") or "",
        "font_external_file_id": inspection.get("external_file_id"),
        "font_fallback_hit_count": fallback_count,
        "font_fallback_candidate_count": len(fallback_hits),
        "font_fallback_path_id": inspection.get("fallback_font_path_id"),
    }


def font_status_from_excel_ui(inspection: dict[str, Any]) -> dict[str, Any]:
    return {
        "ui_font_alias_ok": bool(inspection.get("ui_font_alias_ok")),
        "ui_font_textasset": inspection.get("ui_font_textasset", ""),
        "old_ui_font_alias": inspection.get("old_ui_font_alias", ""),
        "old_ui_font_alias_count": int(inspection.get("old_ui_font_alias_count", 0)),
        "korean_ui_font_alias": inspection.get("korean_ui_font_alias", ""),
        "korean_ui_font_alias_count": int(inspection.get("korean_ui_font_alias_count", 0)),
        "expected_ui_font_alias_count": int(inspection.get("expected_ui_font_alias_count", 0)),
    }


def combined_font_status(bag_inspection: dict[str, Any], excel_ui_inspection: dict[str, Any]) -> dict[str, Any]:
    bag_status = font_status_from_inspection(bag_inspection)
    excel_status = font_status_from_excel_ui(excel_ui_inspection)
    bag_font_ok = bool(bag_status["font_ok"])
    ui_font_alias_ok = bool(excel_status["ui_font_alias_ok"])
    return {
        **bag_status,
        **excel_status,
        "bag_font_ok": bag_font_ok,
        "font_ok": bag_font_ok and ui_font_alias_ok,
    }


def apply_bag_font_patch(game_data: Path, bundle: Path, payload: dict[str, Any], log: Callable[[str], None] = log_noop) -> str:
    digest = sha256_file(bundle)
    bag = payload["bag_function_bundle"]
    accepted = set(bag.get("accepted_patched_sha256", [])) | {bag.get("target_sha256", "")}
    if digest in accepted:
        if inspect_bag_font(bundle, payload)["font_fallback_ok"]:
            log("가방 UI 폰트 번들은 이미 패치되어 있습니다.")
            return digest
    if digest != bag["source_sha256"]:
        raise PatchError(f"지원하지 않는 가방 UI 번들 해시입니다: {digest}")
    backup_file(game_data, bundle, digest, log)

    font_patch = bag["font_patch"]
    env = UnityPy.load(str(bundle))
    asset = env.assets[0]
    file_id, external_added = ensure_external(asset, font_patch["external_path"])
    fallback_changed = 0
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        try:
            tree = obj.read_typetree()
        except Exception:
            continue
        if tree.get("m_Name") != font_patch["local_font_name"]:
            continue
        table = tree.setdefault("m_FallbackFontAssetTable", [])
        if has_ptr(table, file_id, int(font_patch["fallback_font_path_id"])):
            continue
        table.append({"m_FileID": file_id, "m_PathID": int(font_patch["fallback_font_path_id"])})
        obj.save_typetree(tree)
        fallback_changed += 1
    log(f"가방 UI 폰트 fallback 변경: {fallback_changed}, external_added={external_added}")
    with tempfile.TemporaryDirectory(prefix="tos-ko-bag-") as temp:
        env.save(out_path=temp)
        saved = Path(temp) / bundle.name
        if not saved.exists():
            raise PatchError("가방 UI 번들 저장 결과를 찾지 못했습니다.")
        copy_with_parent(saved, bundle)
    new_digest = sha256_file(bundle)
    accepted_after = set(bag.get("accepted_patched_sha256", [])) | {bag["target_sha256"]}
    if new_digest not in accepted_after:
        raise PatchError(f"가방 UI 패치 후 해시 검증 실패: {new_digest}")
    return new_digest


def build_patched_excel_copy(bundle: Path, output_bundle: Path, payload: dict[str, Any], log: Callable[[str], None] = log_noop) -> str:
    digest = sha256_file(bundle)
    excel = payload["excel_bundle"]
    accepted = set(excel.get("accepted_patched_sha256", [])) | {excel.get("target_sha256", "")}
    if digest in accepted and inspect_excel_ui_font(bundle, payload)["ui_font_alias_ok"]:
        copy_with_parent(bundle, output_bundle)
        return sha256_file(output_bundle)
    if digest != excel["source_sha256"] and digest not in accepted:
        raise PatchError(f"지원하지 않는 Excel 번들 해시입니다: {digest}")
    planned, changed = planned_excel_textassets(bundle, payload)
    log(f"오프라인 Excel TextAsset 변경 행: {changed}")
    with tempfile.TemporaryDirectory(prefix="tos-ko-export-excel-") as temp:
        saved = save_textassets_to_bundle(bundle, Path(temp), planned)
        copy_with_parent(saved, output_bundle)
    new_digest = sha256_file(output_bundle)
    accepted_after = set(excel.get("accepted_patched_sha256", [])) | {excel["target_sha256"]}
    if new_digest not in accepted_after:
        raise PatchError(f"오프라인 Excel 출력 해시 검증 실패: {new_digest}")
    return new_digest


def build_patched_bag_copy(bundle: Path, output_bundle: Path, payload: dict[str, Any], log: Callable[[str], None] = log_noop) -> str:
    digest = sha256_file(bundle)
    bag = payload["bag_function_bundle"]
    accepted = set(bag.get("accepted_patched_sha256", [])) | {bag.get("target_sha256", "")}
    if digest in accepted and inspect_bag_font(bundle, payload)["font_fallback_ok"]:
        copy_with_parent(bundle, output_bundle)
        return sha256_file(output_bundle)
    if digest != bag["source_sha256"]:
        raise PatchError(f"지원하지 않는 가방 UI 번들 해시입니다: {digest}")

    font_patch = bag["font_patch"]
    env = UnityPy.load(str(bundle))
    asset = env.assets[0]
    file_id, external_added = ensure_external(asset, font_patch["external_path"])
    fallback_changed = 0
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        try:
            tree = obj.read_typetree()
        except Exception:
            continue
        if tree.get("m_Name") != font_patch["local_font_name"]:
            continue
        table = tree.setdefault("m_FallbackFontAssetTable", [])
        if has_ptr(table, file_id, int(font_patch["fallback_font_path_id"])):
            continue
        table.append({"m_FileID": file_id, "m_PathID": int(font_patch["fallback_font_path_id"])})
        obj.save_typetree(tree)
        fallback_changed += 1
    log(f"오프라인 가방 UI 폰트 fallback 변경: {fallback_changed}, external_added={external_added}")
    with tempfile.TemporaryDirectory(prefix="tos-ko-export-bag-") as temp:
        env.save(out_path=temp)
        saved = Path(temp) / bundle.name
        if not saved.exists():
            raise PatchError("오프라인 가방 UI 번들 저장 결과를 찾지 못했습니다.")
        copy_with_parent(saved, output_bundle)
    new_digest = sha256_file(output_bundle)
    accepted_after = set(bag.get("accepted_patched_sha256", [])) | {bag["target_sha256"]}
    if new_digest not in accepted_after:
        raise PatchError(f"오프라인 가방 UI 출력 해시 검증 실패: {new_digest}")
    return new_digest


def export_patch_files(
    game_data_path: Path,
    output_dir: Path | None = None,
    payload_path: Path | None = None,
    log: Callable[[str], None] = log_noop,
) -> dict[str, Any]:
    payload = load_payload(payload_path)
    game_data = normalize_game_data(game_data_path)
    target_root = (output_dir or default_export_dir()).expanduser().resolve()
    excel_hashes = {payload["excel_bundle"]["source_sha256"], payload["excel_bundle"]["target_sha256"], *payload["excel_bundle"].get("accepted_patched_sha256", [])}
    bag_hashes = {payload["bag_function_bundle"]["source_sha256"], payload["bag_function_bundle"]["target_sha256"], *payload["bag_function_bundle"].get("accepted_patched_sha256", [])}
    excel_bundle = find_single_bundle(game_data, payload["excel_bundle"]["glob"], excel_hashes)
    bag_bundle = find_single_bundle(game_data, payload["bag_function_bundle"]["glob"], bag_hashes)
    excel_rel = excel_bundle.relative_to(game_data)
    bag_rel = bag_bundle.relative_to(game_data)
    excel_out = target_root / excel_rel
    bag_out = target_root / bag_rel
    excel_hash = build_patched_excel_copy(excel_bundle, excel_out, payload, log)
    bag_hash = build_patched_bag_copy(bag_bundle, bag_out, payload, log)
    manifest = {
        "status": "exported",
        "patch_version": payload["patch_version"],
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "source_game_data": str(game_data),
        "output_dir": str(target_root),
        "files": [
            {"relative_path": str(excel_rel).replace("\\", "/"), "sha256": excel_hash},
            {"relative_path": str(bag_rel).replace("\\", "/"), "sha256": bag_hash},
        ],
        "note": "사용자 PC의 원본 게임 파일에서 생성한 패치 결과입니다. 이 폴더를 그대로 재배포하지 마세요.",
    }
    manifest_path = target_root / "PATCH_EXPORT_MANIFEST.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {**manifest, "manifest": str(manifest_path)}


def install_patch(game_data_path: Path, payload_path: Path | None = None, log: Callable[[str], None] = log_noop) -> dict[str, Any]:
    payload = load_payload(payload_path)
    game_data = normalize_game_data(game_data_path)
    log(f"게임 데이터 폴더: {game_data}")
    excel_hashes = {payload["excel_bundle"]["source_sha256"], payload["excel_bundle"]["target_sha256"], *payload["excel_bundle"].get("accepted_patched_sha256", [])}
    bag_hashes = {payload["bag_function_bundle"]["source_sha256"], payload["bag_function_bundle"]["target_sha256"], *payload["bag_function_bundle"].get("accepted_patched_sha256", [])}
    excel_bundle = find_single_bundle(game_data, payload["excel_bundle"]["glob"], excel_hashes)
    bag_bundle = find_single_bundle(game_data, payload["bag_function_bundle"]["glob"], bag_hashes)
    excel_after = apply_excel_patch(game_data, excel_bundle, payload, log)
    bag_after = apply_bag_font_patch(game_data, bag_bundle, payload, log)
    font_status = combined_font_status(inspect_bag_font(bag_bundle, payload), inspect_excel_ui_font(excel_bundle, payload))
    write_state(game_data, payload, excel_bundle, bag_bundle, excel_after, bag_after)
    return {"status": "installed", "excel_sha256": excel_after, "bag_sha256": bag_after, "game_data": str(game_data), **font_status}


def write_state(game_data: Path, payload: dict[str, Any], excel_bundle: Path, bag_bundle: Path, excel_hash: str, bag_hash: str) -> None:
    state = {
        "patch_version": payload["patch_version"],
        "installed_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "excel_bundle": str(excel_bundle.relative_to(game_data)).replace("\\", "/"),
        "bag_function_bundle": str(bag_bundle.relative_to(game_data)).replace("\\", "/"),
        "excel_sha256": excel_hash,
        "bag_sha256": bag_hash,
    }
    path = state_dir(game_data) / "install_state.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def verify_patch(game_data_path: Path, payload_path: Path | None = None, log: Callable[[str], None] = log_noop) -> dict[str, Any]:
    payload = load_payload(payload_path)
    game_data = normalize_game_data(game_data_path)
    excel_hashes = {payload["excel_bundle"]["source_sha256"], payload["excel_bundle"]["target_sha256"], *payload["excel_bundle"].get("accepted_patched_sha256", [])}
    bag_hashes = {payload["bag_function_bundle"]["source_sha256"], payload["bag_function_bundle"]["target_sha256"], *payload["bag_function_bundle"].get("accepted_patched_sha256", [])}
    excel_bundle = find_single_bundle(game_data, payload["excel_bundle"]["glob"], excel_hashes)
    bag_bundle = find_single_bundle(game_data, payload["bag_function_bundle"]["glob"], bag_hashes)
    excel_hash = sha256_file(excel_bundle)
    bag_hash = sha256_file(bag_bundle)
    font_status = combined_font_status(inspect_bag_font(bag_bundle, payload), inspect_excel_ui_font(excel_bundle, payload))
    excel_ok = excel_hash in ({payload["excel_bundle"]["target_sha256"]} | set(payload["excel_bundle"].get("accepted_patched_sha256", []))) and bool(
        font_status["ui_font_alias_ok"]
    )
    bag_ok = bag_hash in ({payload["bag_function_bundle"]["target_sha256"]} | set(payload["bag_function_bundle"].get("accepted_patched_sha256", []))) and bool(
        font_status["bag_font_ok"]
    )
    result = {
        "status": "patched" if excel_ok and bag_ok else "not_patched",
        "excel_sha256": excel_hash,
        "bag_sha256": bag_hash,
        "excel_ok": excel_ok,
        "bag_ok": bag_ok,
        **font_status,
        "game_data": str(game_data),
    }
    log(json.dumps(result, ensure_ascii=False))
    return result


def build_diagnostic_report(game_data_path: Path, payload_path: Path | None = None) -> dict[str, Any]:
    payload = load_payload(payload_path)
    report: dict[str, Any] = {
        "patcher_version": PATCH_VERSION,
        "patcher_tag": PATCH_TAG,
        "payload_version": payload.get("patch_version", ""),
        "steam_app_id": STEAM_APP_ID,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "requested_game_data": str(game_data_path),
        "discovered_steam_game_data": str(discover_steam_game_data() or ""),
    }
    try:
        report["verify"] = verify_patch(game_data_path, payload_path)
        report["status"] = "ok"
    except Exception as exc:  # noqa: BLE001 - diagnostics should capture user-facing failures.
        report["status"] = "error"
        report["error"] = str(exc)
    return report


def write_diagnostic_report(game_data_path: Path, output_path: Path, payload_path: Path | None = None) -> dict[str, Any]:
    report = build_diagnostic_report(game_data_path, payload_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {**report, "path": str(output_path)}


def restore_patch(game_data_path: Path, payload_path: Path | None = None, log: Callable[[str], None] = log_noop) -> dict[str, Any]:
    payload = load_payload(payload_path)
    game_data = normalize_game_data(game_data_path)
    excel_bundle = find_single_bundle(
        game_data,
        payload["excel_bundle"]["glob"],
        {payload["excel_bundle"]["source_sha256"], payload["excel_bundle"]["target_sha256"], *payload["excel_bundle"].get("accepted_patched_sha256", [])},
    )
    bag_bundle = find_single_bundle(
        game_data,
        payload["bag_function_bundle"]["glob"],
        {payload["bag_function_bundle"]["source_sha256"], payload["bag_function_bundle"]["target_sha256"], *payload["bag_function_bundle"].get("accepted_patched_sha256", [])},
    )
    restored: dict[str, str] = {}
    for key, bundle, expected in [
        ("excel", excel_bundle, payload["excel_bundle"]["source_sha256"]),
        ("bag", bag_bundle, payload["bag_function_bundle"]["source_sha256"]),
    ]:
        candidates = sorted((state_dir(game_data) / "backups").glob(f"**/{bundle.name}.{expected}.bak"))
        if not candidates:
            raise PatchError(f"{key} 원본 백업을 찾지 못했습니다. Steam 파일 무결성 검사를 사용해 주세요.")
        copy_with_parent(candidates[-1], bundle)
        digest = sha256_file(bundle)
        if digest != expected:
            raise PatchError(f"{key} 복구 해시 검증 실패: {digest}")
        restored[key] = digest
        log(f"{key} 복구 완료: {digest}")
    return {"status": "restored", **restored, "game_data": str(game_data)}


def build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Tales of Seikyu Korean patcher")
    parser.add_argument("--game-data", default=str(default_game_data()), help="Tales Of Seikyu_Data 또는 게임 설치 폴더 경로")
    parser.add_argument("--payload", default="", help="개발/테스트용 payload JSON 경로")
    parser.add_argument("--install", action="store_true", help="한국어 패치를 설치합니다.")
    parser.add_argument("--restore", action="store_true", help="설치 시 만든 백업으로 복구합니다.")
    parser.add_argument("--verify", action="store_true", help="현재 패치 적용 상태를 확인합니다.")
    parser.add_argument("--check-update", action="store_true", help="GitHub 최신 패처 릴리스를 확인합니다.")
    parser.add_argument("--download-update", action="store_true", help="GitHub 최신 패처 ZIP을 다운로드합니다.")
    parser.add_argument("--download-dir", default="", help="최신 패처 ZIP을 저장할 폴더")
    parser.add_argument("--diagnose", action="store_true", help="진단 리포트를 출력하거나 저장합니다.")
    parser.add_argument("--diagnostic-out", default="", help="진단 리포트 JSON 저장 경로")
    parser.add_argument("--export-patch", action="store_true", help="게임 폴더를 직접 수정하지 않고 패치된 파일을 별도 폴더에 생성합니다.")
    parser.add_argument("--export-dir", default="", help="오프라인 패치 파일 출력 폴더")
    parser.add_argument("--launch-game", action="store_true", help="Steam을 통해 Tales of Seikyu 실행을 요청합니다.")
    parser.add_argument("--no-gui", action="store_true", help="GUI 없이 명령줄 결과만 출력합니다.")
    return parser


def cli_main(argv: list[str] | None = None) -> int:
    parser = build_cli_parser()
    args = parser.parse_args(argv)
    payload = Path(args.payload).resolve() if args.payload else None

    def log(message: str) -> None:
        print(message)

    try:
        game_data = Path(args.game_data)
        if args.install:
            result = install_patch(game_data, payload, log)
        elif args.restore:
            result = restore_patch(game_data, payload, log)
        elif args.verify:
            result = verify_patch(game_data, payload, log)
        elif args.check_update:
            result = check_latest_release()
            result.pop("asset", None)
        elif args.download_update:
            download_dir = Path(args.download_dir).resolve() if args.download_dir else None
            result = download_latest_release(download_dir, log)
        elif args.diagnose:
            if args.diagnostic_out:
                result = write_diagnostic_report(game_data, Path(args.diagnostic_out).resolve(), payload)
            else:
                result = build_diagnostic_report(game_data, payload)
        elif args.export_patch:
            export_dir = Path(args.export_dir).resolve() if args.export_dir else None
            result = export_patch_files(game_data, export_dir, payload, log)
        elif args.launch_game:
            result = launch_game(log)
        else:
            parser.error(
                "one of --install, --restore, --verify, --check-update, --download-update, --diagnose, --export-patch, or --launch-game is required when --no-gui is used"
            )
            return 2
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except Exception as exc:  # noqa: BLE001 - CLI should surface clean message.
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
