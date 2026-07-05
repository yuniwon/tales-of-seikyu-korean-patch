from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
GITHUB_REPO = "yuniwon/tales-of-seikyu-korean-patch"
DEFAULT_BLOG_ID = "ariwon_"
DEFAULT_BLOG_LOG_NO = "224322599998"


@dataclass(frozen=True)
class BlogNotice:
    title: str
    body: str
    metadata: dict[str, Any]


def load_payload(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def display_date_from_version(version: str) -> str:
    match = re.search(r"(20\d{6})$", version)
    if not match:
        now = datetime.now()
        return f"{now.year}년 {now.month}월 {now.day}일"
    value = match.group(1)
    year = int(value[:4])
    month = int(value[4:6])
    day = int(value[6:8])
    return f"{year}년 {month}월 {day}일"


def extract_section_lines(markdown: str, heading_prefix: str) -> list[str]:
    lines = markdown.splitlines()
    start: int | None = None
    for index, line in enumerate(lines):
        if line.startswith(heading_prefix):
            start = index + 1
            break
    if start is None:
        return []
    section: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        section.append(line.rstrip())
    return section


def extract_bullets(markdown: str, heading_prefix: str) -> list[str]:
    return [line.strip() for line in extract_section_lines(markdown, heading_prefix) if line.strip().startswith("- ")]


def zip_name(version: str) -> str:
    return f"TalesOfSeikyuKoreanPatch-v{version}.zip"


def public_version(version: str) -> str:
    return version.split("-", 1)[0]


def format_optional_hash(zip_sha256: str) -> list[str]:
    if not zip_sha256:
        return [
            "ZIP SHA256:",
            "릴리스 ZIP을 만든 뒤 --zip-sha256 값을 넣어 다시 생성해 주세요.",
        ]
    return ["ZIP SHA256:", zip_sha256.lower()]


def build_notice(
    payload: dict[str, Any],
    release_notes: str,
    *,
    zip_sha256: str = "",
    release_url: str | None = None,
    blog_id: str = DEFAULT_BLOG_ID,
    blog_log_no: str = DEFAULT_BLOG_LOG_NO,
) -> BlogNotice:
    version = str(payload["patch_version"])
    date_label = display_date_from_version(version)
    download_url = release_url or f"https://github.com/{GITHUB_REPO}/releases/latest"
    patch_rows = len(payload["excel_bundle"]["patch_rows"])
    generated_from = payload.get("generated_from") or {}
    steam_buildid = str(generated_from.get("steam_buildid") or "")
    source_update_rows = int(generated_from.get("source_update_rows") or 0)
    source_update_added = int(generated_from.get("source_update_added_rows") or 0)
    source_update_replaced = int(generated_from.get("source_update_replaced_rows") or 0)
    visible_version = public_version(version)
    title = f"세이큐이야기(Tales of Seikyu) 비공식 한글패치 v{visible_version} 배포({date_label}자)"

    change_bullets = extract_bullets(release_notes, "## 5)")
    known_bullets = extract_bullets(release_notes, "## 9)")
    if not change_bullets:
        change_bullets = [
            f"- 최신 payload 기준 총 {patch_rows:,}행을 적용합니다.",
            "- 게임이 업데이트되어도 그대로 맞는 문장은 자동으로 한국어를 적용합니다.",
            "- 새로 추가되었거나 원문이 바뀐 문장은 건드리지 않고 원문으로 남깁니다.",
        ]
    if not known_bullets:
        known_bullets = [
            "- 새로 추가되었거나 원문이 바뀐 문장은 원문으로 보일 수 있습니다.",
            "- 게임 파일 구조가 크게 바뀌면 새 패치 버전이 필요합니다.",
            "- 일부 문장/화면은 플레이테스트를 통해 계속 다듬는 중입니다.",
        ]

    body_lines = [
        "안녕하세요.",
        "",
        f"세이큐이야기 Tales of Seikyu 비공식 한글패치 v{visible_version} 배포 안내입니다.",
        "",
        f"이번 버전은 {date_label} 기준 최신 패치입니다.",
        f"최신 검토분까지 포함해 총 {patch_rows:,}행을 적용합니다.",
        "게임이 업데이트되어 파일이 조금 바뀌어도, 그대로 맞는 문장은 자동으로 한국어가 적용됩니다.",
        "새로 추가되었거나 원문이 바뀐 문장은 억지로 덮어쓰지 않고 원문으로 남겨 둡니다.",
        "",
        "1. 다운로드",
        "",
        "아래 GitHub Releases 페이지에서 최신 ZIP 파일을 받아 주세요.",
        "",
        download_url,
        "",
        "다운로드 파일:",
        zip_name(version),
        "",
        "지원 플랫폼:",
        "Steam Windows",
        "",
        "대상 게임:",
        "Tales of Seikyu",
    ]
    if steam_buildid:
        body_lines.extend(["", "대상 게임 버전/buildid:", f"Steam buildid {steam_buildid}"])

    body_lines.extend(
        [
            "",
            "2. 설치 방법",
            "",
            "1) ZIP 파일을 다운로드합니다.",
            "2) 원하는 곳에 압축을 풉니다.",
            "3) 게임을 완전히 종료합니다.",
            "4) TalesOfSeikyuKoreanPatch.exe를 실행합니다.",
            "5) 게임 폴더가 자동으로 잡히지 않으면 게임 폴더 찾기를 누릅니다.",
            "6) 한국어 패치 설치/업데이트를 누릅니다.",
            "7) 완료 메시지가 나오면 게임을 다시 실행합니다.",
            "",
            "3. 기존 패처를 쓰고 있던 분들",
            "",
            "기존 패처를 실행한 뒤 최신 패처 확인을 눌러 주세요.",
            "새 버전이 보이면 최신 패처 다운로드로 ZIP 파일을 받은 뒤, 새 EXE를 실행하면 됩니다.",
            "",
            "4. 이번 버전에서 바뀐 점",
            "",
            *change_bullets,
            "",
            "5. 문제가 생겼을 때",
            "",
            "글자가 네모로 보이면:",
            "한국어 패치 설치/업데이트를 한 번 더 눌러 주세요.",
            "",
            "일부 문장이 일본어/중국어/영어로 보이면:",
            "게임 업데이트로 원문이 바뀐 문장일 수 있습니다.",
            "화면 스크린샷과 함께 댓글로 알려 주세요.",
            "",
            "설치가 실패하면:",
            "패처의 진단 리포트 저장을 누른 뒤, 저장된 파일과 오류 화면을 함께 제보해 주세요.",
            "",
            "6. 알려진 점",
            "",
            *known_bullets,
            "",
            "7. 파일 검증값",
            "",
            *format_optional_hash(zip_sha256),
            "",
            "이 값은 파일이 정상적으로 내려받아졌는지 확인할 때 쓰는 값입니다.",
            "일반 사용자는 꼭 확인하지 않아도 됩니다.",
            "",
            "8. 후원 안내 (선택)",
            "",
            "이 프로젝트는 무료 비공식 팬 활동입니다.",
            "후원은 의무가 아니며, 패치 다운로드나 사용과는 무관합니다.",
            "작업 지속과 유지 비용 보전에 도움을 주고 싶다면 큰 힘이 됩니다.",
            "후원 계좌 QR은 기존 글의 이미지를 참고해 주세요.",
            "",
            "9. 안내 및 면책",
            "",
            "- 본 패치는 비공식 팬 번역이며 개발사/퍼블리셔와 무관합니다.",
            "- 게임 원본 파일 및 권리는 각 권리자에게 있습니다.",
            "- 정식 한국어 출시 또는 권리자 요청 시 배포를 중단하거나 수정할 수 있습니다.",
            "- 패치 파일 외 완성된 게임 원본 번들 전체는 배포하지 않습니다.",
            "- 설치 과정에서 사용자 PC에 설치된 게임의 원본 파일을 직접 패치하는 방식입니다.",
            "- 상업적 판매 및 유료 배포를 금지합니다.",
        ]
    )

    metadata = {
        "version": version,
        "public_version": visible_version,
        "tag": f"v{version}",
        "title": title,
        "release_url": download_url,
        "zip_name": zip_name(version),
        "zip_sha256": zip_sha256.lower(),
        "patch_rows": patch_rows,
        "steam_buildid": steam_buildid,
        "source_update_rows": source_update_rows,
        "source_update_added_rows": source_update_added,
        "source_update_replaced_rows": source_update_replaced,
        "excel_source_sha256": payload["excel_bundle"]["source_sha256"],
        "excel_target_sha256": payload["excel_bundle"]["target_sha256"],
        "bag_target_sha256": payload["bag_function_bundle"]["target_sha256"],
        "blog_edit_url": f"https://blog.naver.com/{blog_id}/postupdate?logNo={blog_log_no}",
        "blog_view_url": f"https://blog.naver.com/{blog_id}/{blog_log_no}",
    }
    return BlogNotice(title=title, body="\n".join(body_lines).strip() + "\n", metadata=metadata)


def write_notice(notice: BlogNotice, output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    title_path = output_dir / "title.txt"
    body_path = output_dir / "body.txt"
    metadata_path = output_dir / "metadata.json"
    combined_path = output_dir / "naver_blog_notice.md"
    title_path.write_text(notice.title + "\n", encoding="utf-8")
    body_path.write_text(notice.body, encoding="utf-8")
    metadata_path.write_text(json.dumps(notice.metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    combined_path.write_text(f"# {notice.title}\n\n{notice.body}", encoding="utf-8")
    return {
        "title": str(title_path),
        "body": str(body_path),
        "metadata": str(metadata_path),
        "combined": str(combined_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a Naver-ready blog notice draft from the current patch payload.")
    parser.add_argument("--payload", type=Path, default=REPO / "payload/patch_payload.json")
    parser.add_argument("--release-notes", type=Path, default=REPO / "RELEASE_NOTES.md")
    parser.add_argument("--output-dir", type=Path, default=REPO / "dist/blog_notice")
    parser.add_argument("--zip-sha256", default="", help="SHA256 of the release ZIP.")
    parser.add_argument("--release-url", default="", help="Override the GitHub release URL shown to users.")
    parser.add_argument("--blog-id", default=DEFAULT_BLOG_ID)
    parser.add_argument("--blog-log-no", default=DEFAULT_BLOG_LOG_NO)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = load_payload(args.payload)
    release_notes = args.release_notes.read_text(encoding="utf-8")
    notice = build_notice(
        payload,
        release_notes,
        zip_sha256=args.zip_sha256,
        release_url=args.release_url or None,
        blog_id=args.blog_id,
        blog_log_no=args.blog_log_no,
    )
    paths = write_notice(notice, args.output_dir)
    print(json.dumps({"status": "pass", **notice.metadata, "paths": paths}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
