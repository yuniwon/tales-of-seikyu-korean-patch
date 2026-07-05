# 블로그 글 수정 자동화 프로세스

패치 릴리스를 만든 뒤 네이버 블로그 글을 갱신할 때 쓰는 절차입니다.

이 자동화는 네이버 계정 정보를 저장하지 않습니다. 대신 릴리스 정보로 제목과 본문 초안을 만들고, 로그인된 브라우저에서 사람이 확인한 뒤 발행합니다.

## 1. 릴리스 ZIP 해시 확인

```powershell
$zip = "dist\TalesOfSeikyuKoreanPatch-v0.1.12-playtest.20260705.zip"
$zipHash = (Get-FileHash $zip -Algorithm SHA256).Hash.ToLower()
```

## 2. 블로그 초안 생성

```powershell
$env:PYTHONUTF8='1'
python tools\build_blog_notice.py --zip-sha256 $zipHash
```

생성 위치:

- `dist\blog_notice\title.txt`
- `dist\blog_notice\body.txt`
- `dist\blog_notice\naver_blog_notice.md`
- `dist\blog_notice\metadata.json`

`metadata.json`에는 블로그 편집 URL, GitHub 릴리스 URL, ZIP 파일명, ZIP 해시, 적용 행 수, 대상 buildid가 들어 있습니다.

## 3. 네이버 블로그 글 수정

1. 브라우저에서 네이버에 로그인합니다.
2. `metadata.json`의 `blog_edit_url`을 엽니다.
3. `title.txt`의 제목과 `body.txt`의 본문을 기존 글에 반영합니다.
4. 하단 후원 이미지처럼 유지해야 할 기존 구성요소가 있으면 삭제하지 않았는지 확인합니다.
5. `발행`을 눌러 저장합니다.
6. 게시 화면에서 제목, 파일명, ZIP SHA256, 변경 사항이 최신 릴리스와 맞는지 확인합니다.

## 4. 에이전트에게 맡길 때

에이전트가 브라우저를 조작할 수 있고 사용자가 이미 로그인해 둔 상태라면 다음처럼 지시하면 됩니다.

```text
dist\blog_notice의 title/body/metadata를 기준으로 네이버 블로그 기존 세이큐이야기 한글패치 글을 수정해줘.
후원 이미지는 유지하고, 제목/버전/파일명/SHA256/변경점만 최신 릴리스 기준으로 반영한 뒤 게시 화면에서 확인해줘.
```

완전 무인 게시를 목표로 하지 않습니다. 네이버 로그인, 보안 확인, 최종 발행은 항상 사용자 소유 브라우저에서 눈에 보이게 진행합니다.
