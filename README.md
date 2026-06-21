# Tales of Seikyu 비공식 한글패치

Tales of Seikyu Steam Windows판용 비공식 한국어 패처입니다.

이 저장소에는 게임 원본 번들, 실행 파일, 전체 데이터 폴더가 들어 있지 않습니다. 패처는 사용자의 PC에 설치된 원본 게임 파일을 확인한 뒤, 지원되는 해시일 때만 한국어 텍스트와 필요한 폰트 fallback을 적용합니다.

## 지원 대상

- 게임: Tales of Seikyu
- 플랫폼: Steam Windows
- 패치 버전: `0.1.2-playtest.20260621`
- 지원 방식: 로컬 원본 파일에 패치 적용, 설치 전 자동 백업, GUI 복구, GitHub 최신 패처 확인/다운로드, 진단 리포트 저장

## 설치

1. GitHub Releases에서 최신 ZIP을 다운로드합니다.
2. 압축을 풉니다.
3. `TalesOfSeikyuKoreanPatch.exe`를 실행합니다.
4. 게임 폴더가 자동으로 잡히지 않으면 `게임 폴더 찾기`로 `Tales Of Seikyu_Data` 폴더 또는 게임 설치 폴더를 선택합니다. Steam 추가 라이브러리도 자동 탐색합니다.
5. `한국어 패치 설치/업데이트`를 누릅니다.
6. 완료 후 게임을 완전히 다시 실행합니다.

패처 첫 화면에서는 게임 경로, 패치 적용 상태, 폰트 fallback 상태, 최신 패처 릴리스 상태를 자동으로 확인합니다.

## 폰트 적용 방식

현재 배포본은 별도 폰트 파일을 재배포하지 않습니다. 게임에 이미 포함된 CJK 폰트를 가방 UI의 TextMeshPro fallback으로 연결하고, `폰트 상태` 카드와 검증 결과의 `font_ok` 값으로 적용 여부를 확인합니다.

폰트 상태가 `Fallback 미적용`으로 보이면 `한국어 패치 설치/업데이트`를 다시 실행해 주세요.

Steam 경로 확인:

- Steam 라이브러리 -> Tales of Seikyu 우클릭 -> 관리 -> 로컬 파일 보기

## 최신 패처 확인

`최신 패처 확인`은 GitHub Releases의 최신 릴리스를 조회합니다.

`최신 패처 다운로드`는 최신 ZIP 파일을 사용자 다운로드 폴더에 저장하고 폴더를 엽니다. 실행 중인 패처 EXE를 자동으로 덮어쓰거나, 다운로드한 파일을 자동 실행하지 않습니다. 새 ZIP을 받은 뒤에는 압축을 풀고 새 `TalesOfSeikyuKoreanPatch.exe`를 실행해 주세요.

## 편의 기능

- `게임 실행`: Steam을 통해 Tales of Seikyu 실행을 요청합니다.
- `진단 리포트 저장`: 게임 경로, 패치 해시, 폰트 fallback 상태, 오류 메시지를 JSON으로 저장합니다.
- `오프라인 패치 파일 만들기`: 게임 폴더를 직접 수정하지 않고, 현재 PC의 원본 파일에서 패치된 번들을 별도 폴더에 생성합니다. 보안 프로그램이나 샌드박스 환경에서 결과물을 먼저 확인하고 싶을 때 쓰는 개발/고급 사용자용 기능입니다.

## 복구

1. `TalesOfSeikyuKoreanPatch.exe`를 실행합니다.
2. 같은 게임 폴더를 선택합니다.
3. `원본 복구`를 누릅니다.

백업이 없거나 게임 업데이트로 파일 구조가 바뀐 경우 Steam의 파일 무결성 검사를 사용해 주세요.

## 알려진 이슈

- 현재 배포본은 Steam Windows의 확인된 번들 해시에만 적용됩니다.
- 게임 업데이트로 번들 해시가 바뀌면 패처가 설치를 거부할 수 있습니다. 이 경우 새 패치 버전이 필요합니다.
- 일부 문장/화면은 플레이테스트를 통해 계속 다듬는 중입니다.

## 개발자용 명령

```powershell
$env:PYTHONUTF8='1'
python tools\generate_payload.py
python tools\test_patcher_features.py
python tools\test_update_logic.py
python tools\run_temp_baseline_test.py
python tools\build_release.py
python tools\run_exe_temp_test.py
python tools\scan_release_assets.py
```

소스 실행:

```powershell
$env:PYTHONPATH='src'
python -m tos_ko_patcher.app --no-gui --game-data "C:\Program Files (x86)\Steam\steamapps\common\Tales of Seikyu\Tales Of Seikyu_Data" --verify
python -m tos_ko_patcher.app --no-gui --check-update
python -m tos_ko_patcher.app --no-gui --diagnose --diagnostic-out ".\tos-ko-diagnostic.json"
```

## 면책

- 본 패치는 비공식 팬 번역이며 개발사/퍼블리셔와 무관합니다.
- 게임 원본 파일 및 권리는 각 권리자에게 있습니다.
- 이 저장소와 배포 ZIP은 게임 원본 자산 전체를 포함하지 않습니다.
- 상업적 판매/유료 배포를 금지합니다.
