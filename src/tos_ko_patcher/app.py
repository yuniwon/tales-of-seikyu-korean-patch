from __future__ import annotations

import json
import os
import queue
import sys
import threading
import webbrowser
from pathlib import Path
from tkinter import BOTH, END, LEFT, RIGHT, X, StringVar, Text, Tk, filedialog, messagebox
from tkinter import ttk
from typing import Any, Callable

from tos_ko_patcher.core import (
    PATCH_TAG,
    PATCH_VERSION,
    RELEASES_URL,
    PatchError,
    check_latest_release,
    cli_main,
    default_download_dir,
    default_game_data,
    download_latest_release,
    install_patch,
    restore_patch,
    verify_patch,
)


BG = "#0f1117"
PANEL = "#171a22"
PANEL_ALT = "#1d212b"
BORDER = "#2a2f3a"
FG = "#edf0f5"
MUTED = "#99a1b3"
ACCENT = "#5b8cff"
ACCENT_HOVER = "#719cff"
DANGER = "#ef6461"
SUCCESS = "#59c27d"
WARN = "#f0b45a"


class PatcherGui:
    def __init__(self) -> None:
        self.root = Tk()
        self.root.title("Tales of Seikyu 비공식 한글패치")
        self.root.geometry("920x680")
        self.root.minsize(840, 620)
        self.root.configure(bg=BG)

        self.path_var = StringVar(value=str(default_game_data()))
        self.path_status_var = StringVar(value="경로 확인 대기")
        self.patch_status_var = StringVar(value="패치 상태 확인 대기")
        self.update_status_var = StringVar(value="최신 릴리스 확인 대기")
        self.progress_var = StringVar(value="게임을 종료한 뒤 설치/복구를 진행해 주세요.")
        self.version_var = StringVar(value=f"현재 패처 {PATCH_VERSION}")

        self.queue: queue.Queue[tuple[str, Any]] = queue.Queue()
        self.buttons: list[ttk.Button] = []
        self.download_button: ttk.Button | None = None
        self.latest_release: dict[str, Any] | None = None
        self.busy = False

        self._configure_style()
        self._build()
        self._pump()
        self.root.after(250, lambda: self._verify(notify=False))
        self.root.after(1800, lambda: self._check_update(notify=False))

    def _configure_style(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        base_font = ("Malgun Gothic", 10)
        style.configure(".", font=base_font, background=BG, foreground=FG)
        style.configure("Root.TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL, borderwidth=1, relief="solid")
        style.configure("SubPanel.TFrame", background=PANEL_ALT, borderwidth=1, relief="solid")
        style.configure("TLabel", background=BG, foreground=FG)
        style.configure("Panel.TLabel", background=PANEL, foreground=FG)
        style.configure("Muted.TLabel", background=BG, foreground=MUTED)
        style.configure("PanelMuted.TLabel", background=PANEL, foreground=MUTED)
        style.configure("Title.TLabel", background=BG, foreground=FG, font=("Malgun Gothic", 20, "bold"))
        style.configure("Subtitle.TLabel", background=BG, foreground=MUTED)
        style.configure("CardTitle.TLabel", background=PANEL, foreground=MUTED, font=("Malgun Gothic", 9))
        style.configure("CardValue.TLabel", background=PANEL, foreground=FG, font=("Malgun Gothic", 12, "bold"))
        style.configure("Status.TLabel", background=PANEL_ALT, foreground=FG, padding=(10, 5), font=("Malgun Gothic", 9, "bold"))
        style.configure("TEntry", fieldbackground="#0c0e13", foreground=FG, insertcolor=FG, bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER)
        style.map("TEntry", fieldbackground=[("disabled", "#151820")])
        style.configure("TButton", background=PANEL_ALT, foreground=FG, bordercolor=BORDER, focusthickness=0, padding=(12, 8))
        style.map("TButton", background=[("active", "#272c38"), ("disabled", "#161922")], foreground=[("disabled", "#697084")])
        style.configure("Accent.TButton", background=ACCENT, foreground="#ffffff", bordercolor=ACCENT, padding=(14, 9))
        style.map("Accent.TButton", background=[("active", ACCENT_HOVER), ("disabled", "#28344e")])
        style.configure("Danger.TButton", background="#3a2025", foreground="#ffd7d5", bordercolor="#5c3038", padding=(12, 8))
        style.map("Danger.TButton", background=[("active", "#4b2930"), ("disabled", "#21181c")])

    def _build(self) -> None:
        outer = ttk.Frame(self.root, style="Root.TFrame", padding=20)
        outer.pack(fill=BOTH, expand=True)

        header = ttk.Frame(outer, style="Root.TFrame")
        header.pack(fill=X, pady=(0, 16))
        title_col = ttk.Frame(header, style="Root.TFrame")
        title_col.pack(side=LEFT, fill=X, expand=True)
        ttk.Label(title_col, text="Tales of Seikyu Korean Patch", style="Title.TLabel").pack(anchor="w")
        ttk.Label(title_col, text="비공식 한글패치 설치, 복구, 최신 패처 확인", style="Subtitle.TLabel").pack(anchor="w", pady=(4, 0))
        ttk.Label(header, textvariable=self.version_var, style="Status.TLabel").pack(side=RIGHT)

        status_row = ttk.Frame(outer, style="Root.TFrame")
        status_row.pack(fill=X, pady=(0, 14))
        self._status_card(status_row, "게임 경로", self.path_status_var).pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        self._status_card(status_row, "패치 상태", self.patch_status_var).pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        self._status_card(status_row, "업데이트", self.update_status_var).pack(side=LEFT, fill=X, expand=True)

        path_panel = ttk.Frame(outer, style="Panel.TFrame", padding=14)
        path_panel.pack(fill=X, pady=(0, 14))
        ttk.Label(path_panel, text="게임 폴더 또는 Tales Of Seikyu_Data 경로", style="PanelMuted.TLabel").pack(anchor="w")
        path_row = ttk.Frame(path_panel, style="Panel.TFrame")
        path_row.pack(fill=X, pady=(8, 0))
        ttk.Entry(path_row, textvariable=self.path_var).pack(side=LEFT, fill=X, expand=True)
        browse = ttk.Button(path_row, text="게임 폴더 찾기", command=self._browse)
        browse.pack(side=RIGHT, padx=(8, 0))
        self.buttons.append(browse)

        action_panel = ttk.Frame(outer, style="Panel.TFrame", padding=14)
        action_panel.pack(fill=X, pady=(0, 14))
        primary_row = ttk.Frame(action_panel, style="Panel.TFrame")
        primary_row.pack(fill=X)
        self._add_button(primary_row, "한국어 패치 설치/업데이트", lambda: self._install(), style="Accent.TButton").pack(side=LEFT, padx=(0, 8))
        self._add_button(primary_row, "상태 새로고침", lambda: self._verify()).pack(side=LEFT, padx=(0, 8))
        self._add_button(primary_row, "원본 복구", lambda: self._restore(), style="Danger.TButton").pack(side=LEFT, padx=(0, 8))
        self._add_button(primary_row, "최신 패처 확인", lambda: self._check_update()).pack(side=LEFT, padx=(0, 8))
        self.download_button = self._add_button(primary_row, "최신 패처 다운로드", lambda: self._download_update())
        self.download_button.pack(side=LEFT)
        self.download_button.state(["disabled"])

        secondary_row = ttk.Frame(action_panel, style="Panel.TFrame")
        secondary_row.pack(fill=X, pady=(10, 0))
        self._add_button(secondary_row, "릴리스 페이지 열기", self._open_releases).pack(side=LEFT, padx=(0, 8))
        self._add_button(secondary_row, "로그 저장", self._save_log).pack(side=LEFT)
        ttk.Label(secondary_row, textvariable=self.progress_var, style="PanelMuted.TLabel").pack(side=RIGHT)

        log_panel = ttk.Frame(outer, style="Panel.TFrame", padding=12)
        log_panel.pack(fill=BOTH, expand=True)
        ttk.Label(log_panel, text="작업 로그", style="PanelMuted.TLabel").pack(anchor="w", pady=(0, 8))
        self.log = Text(
            log_panel,
            wrap="word",
            height=16,
            bg="#0c0e13",
            fg="#d8dce7",
            insertbackground=FG,
            relief="flat",
            padx=10,
            pady=10,
            font=("Consolas", 10),
        )
        self.log.pack(fill=BOTH, expand=True)
        self._log("게임을 완전히 종료한 뒤 설치/복구를 진행해 주세요.")
        self._log("최신 패처 확인은 GitHub Releases를 조회하고, 다운로드는 ZIP 파일 저장까지만 진행합니다.")

    def _status_card(self, parent: ttk.Frame, title: str, variable: StringVar) -> ttk.Frame:
        frame = ttk.Frame(parent, style="Panel.TFrame", padding=14)
        ttk.Label(frame, text=title, style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(frame, textvariable=variable, style="CardValue.TLabel", wraplength=245).pack(anchor="w", pady=(6, 0))
        return frame

    def _add_button(
        self,
        parent: ttk.Frame,
        text: str,
        command: Callable[[], None],
        style: str = "TButton",
    ) -> ttk.Button:
        button = ttk.Button(parent, text=text, command=command, style=style)
        self.buttons.append(button)
        return button

    def _browse(self) -> None:
        selected = filedialog.askdirectory(title="Tales of Seikyu 설치 폴더 선택")
        if selected:
            self.path_var.set(selected)
            self._verify(notify=False)

    def _open_releases(self) -> None:
        webbrowser.open(RELEASES_URL)

    def _save_log(self) -> None:
        target = filedialog.asksaveasfilename(
            title="패처 로그 저장",
            defaultextension=".txt",
            filetypes=[("Text log", "*.txt"), ("All files", "*.*")],
        )
        if not target:
            return
        Path(target).write_text(self.log.get("1.0", END), encoding="utf-8")
        self._log(f"로그 저장: {target}")

    def _log(self, message: str) -> None:
        self.log.insert(END, message + "\n")
        self.log.see(END)

    def _queue_log(self, message: str) -> None:
        self.queue.put(("log", message))

    def _queue_dialog(self, kind: str, title: str, message: str) -> None:
        self.queue.put(("dialog", (kind, title, message)))

    def _pump(self) -> None:
        try:
            while True:
                kind, payload = self.queue.get_nowait()
                if kind == "log":
                    self._log(str(payload))
                elif kind == "busy":
                    self._set_busy(bool(payload))
                elif kind == "result":
                    action, result, notify = payload
                    self._handle_result(str(action), result, bool(notify))
                elif kind == "error":
                    action, message, notify = payload
                    self._handle_error(str(action), str(message), bool(notify))
                elif kind == "dialog":
                    level, title, message = payload
                    if level == "error":
                        messagebox.showerror(title, message)
                    else:
                        messagebox.showinfo(title, message)
        except queue.Empty:
            pass
        self.root.after(100, self._pump)

    def _set_busy(self, busy: bool) -> None:
        self.busy = busy
        state = ["disabled"] if busy else ["!disabled"]
        for button in self.buttons:
            button.state(state)
        self._sync_download_button()

    def _sync_download_button(self) -> None:
        if not self.download_button:
            return
        if self.busy:
            self.download_button.state(["disabled"])
            return
        has_asset = bool(
            self.latest_release
            and self.latest_release.get("asset_name")
            and self.latest_release.get("status") in {"update_available", "current"}
        )
        self.download_button.state(["!disabled"] if has_asset else ["disabled"])

    def _path(self) -> Path:
        return Path(self.path_var.get())

    def _run_worker(self, action: str, label: str, target: Callable[[], dict[str, Any]], notify: bool = True) -> None:
        if self.busy:
            self._log("다른 작업이 진행 중입니다. 잠시 후 다시 시도해 주세요.")
            return

        def worker() -> None:
            self.queue.put(("busy", True))
            self._queue_log("")
            self._queue_log(f"[{label}] 시작")
            try:
                result = target()
                self._queue_log(json.dumps({k: v for k, v in result.items() if k != "asset"}, ensure_ascii=False, indent=2))
                self.queue.put(("result", (action, result, notify)))
            except PatchError as exc:
                self._queue_log(f"오류: {exc}")
                self.queue.put(("error", (action, str(exc), notify)))
            except Exception as exc:  # noqa: BLE001 - GUI should not crash silently.
                self._queue_log(f"예상치 못한 오류: {exc}")
                self.queue.put(("error", (action, str(exc), notify)))
            finally:
                self.queue.put(("busy", False))

        threading.Thread(target=worker, daemon=True).start()

    def _install(self, notify: bool = True) -> None:
        self._run_worker(
            "install",
            "한국어 패치 설치/업데이트",
            lambda: install_patch(self._path(), log=self._queue_log),
            notify,
        )

    def _restore(self, notify: bool = True) -> None:
        self._run_worker("restore", "원본 복구", lambda: restore_patch(self._path(), log=self._queue_log), notify)

    def _verify(self, notify: bool = True) -> None:
        self._run_worker("verify", "상태 새로고침", lambda: verify_patch(self._path(), log=self._queue_log), notify)

    def _check_update(self, notify: bool = True) -> None:
        self._run_worker("check_update", "최신 패처 확인", check_latest_release, notify)

    def _download_update(self, notify: bool = True) -> None:
        self._run_worker(
            "download_update",
            "최신 패처 다운로드",
            lambda: download_latest_release(default_download_dir(), log=self._queue_log, progress=self._download_progress),
            notify,
        )

    def _download_progress(self, downloaded: int, total: int) -> None:
        if total:
            percent = downloaded * 100 // total
            self.queue.put(("log", f"다운로드 진행: {percent}% ({downloaded:,}/{total:,} bytes)"))

    def _handle_result(self, action: str, result: dict[str, Any], notify: bool) -> None:
        if action == "verify":
            self._apply_verify_status(result)
            if notify:
                messagebox.showinfo("상태 확인", self.patch_status_var.get())
        elif action == "install":
            self.path_status_var.set("경로 확인됨")
            self.patch_status_var.set("한국어 패치 적용됨")
            self.progress_var.set("설치 완료. 게임을 다시 실행해 주세요.")
            if notify:
                messagebox.showinfo("설치 완료", "한국어 패치가 적용되었습니다. 게임을 다시 실행해 주세요.")
        elif action == "restore":
            self.path_status_var.set("경로 확인됨")
            self.patch_status_var.set("원본 복구됨")
            self.progress_var.set("복구 완료. 필요하면 Steam 파일 무결성 검사도 사용할 수 있습니다.")
            if notify:
                messagebox.showinfo("복구 완료", "설치 시 생성된 백업으로 복구했습니다.")
        elif action == "check_update":
            self.latest_release = result
            self._apply_update_status(result)
            if notify:
                messagebox.showinfo("최신 패처 확인", self.update_status_var.get())
        elif action == "download_update":
            self.latest_release = result
            self._apply_update_status(result)
            path = Path(str(result.get("path") or ""))
            if path.exists():
                self.progress_var.set(f"다운로드 완료: {path.name}")
                self._open_folder(path.parent)
            if notify:
                messagebox.showinfo("다운로드 완료", f"최신 패처 ZIP을 저장했습니다.\n{path}")
        self._sync_download_button()

    def _handle_error(self, action: str, message: str, notify: bool) -> None:
        if action == "verify":
            self.path_status_var.set("경로 확인 실패")
            self.patch_status_var.set("확인 불가")
            self.progress_var.set("게임 폴더를 다시 선택하거나 Steam 파일 상태를 확인해 주세요.")
        elif action == "check_update":
            self.update_status_var.set("릴리스 확인 실패")
            self.progress_var.set("네트워크 연결 또는 GitHub 접속 상태를 확인해 주세요.")
        elif action == "download_update":
            self.progress_var.set("최신 패처 다운로드에 실패했습니다.")
        else:
            self.progress_var.set("작업에 실패했습니다. 로그를 확인해 주세요.")
        if notify:
            messagebox.showerror("오류", message)

    def _apply_verify_status(self, result: dict[str, Any]) -> None:
        self.path_status_var.set("경로 확인됨")
        status = result.get("status")
        if status == "patched":
            self.patch_status_var.set("한국어 패치 적용됨")
            self.progress_var.set("현재 게임 파일은 패치된 상태입니다.")
        else:
            excel_ok = result.get("excel_ok")
            bag_ok = result.get("bag_ok")
            detail = f"텍스트 {'OK' if excel_ok else '미적용'}, 폰트 {'OK' if bag_ok else '미적용'}"
            self.patch_status_var.set(f"미적용 또는 일부 적용 ({detail})")
            self.progress_var.set("설치/업데이트를 실행하면 현재 지원 파일에 패치를 적용합니다.")

    def _apply_update_status(self, result: dict[str, Any]) -> None:
        latest = str(result.get("latest_tag") or "")
        status = result.get("status")
        if status == "update_available":
            self.update_status_var.set(f"새 패처 있음: {latest}")
            self.progress_var.set("최신 패처 ZIP을 다운로드할 수 있습니다.")
        elif status == "current":
            self.update_status_var.set(f"최신 버전: {PATCH_TAG}")
            self.progress_var.set("현재 패처가 최신 릴리스입니다.")
        elif status == "ahead":
            self.update_status_var.set(f"현재 빌드가 릴리스보다 최신: {latest}")
            self.progress_var.set("개발 빌드 상태입니다. 배포 후 다시 확인해 주세요.")
        else:
            self.update_status_var.set("릴리스 상태 확인됨")

    def _open_folder(self, folder: Path) -> None:
        try:
            os.startfile(folder)  # type: ignore[attr-defined]
        except Exception:
            self._log(f"다운로드 폴더: {folder}")

    def mainloop(self) -> None:
        self.root.mainloop()


def main() -> int:
    cli_flags = ("--install", "--restore", "--verify", "--check-update", "--download-update")
    if "--no-gui" in sys.argv or any(flag in sys.argv for flag in cli_flags):
        return cli_main()
    PatcherGui().mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
