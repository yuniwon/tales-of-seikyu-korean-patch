from __future__ import annotations

import queue
import sys
import threading
from pathlib import Path
from tkinter import BOTH, END, LEFT, RIGHT, X, Button, Entry, Frame, Label, StringVar, Text, Tk, filedialog, messagebox

from tos_ko_patcher.core import PatchError, cli_main, default_game_data, install_patch, restore_patch, verify_patch


class PatcherGui:
    def __init__(self) -> None:
        self.root = Tk()
        self.root.title("Tales of Seikyu 비공식 한글패치")
        self.root.geometry("780x520")
        self.path_var = StringVar(value=str(default_game_data()))
        self.queue: queue.Queue[str] = queue.Queue()
        self._build()
        self._pump()

    def _build(self) -> None:
        outer = Frame(self.root, padx=14, pady=14)
        outer.pack(fill=BOTH, expand=True)

        Label(outer, text="게임 폴더 또는 Tales Of Seikyu_Data 경로").pack(anchor="w")
        path_row = Frame(outer)
        path_row.pack(fill=X, pady=(4, 10))
        Entry(path_row, textvariable=self.path_var).pack(side=LEFT, fill=X, expand=True)
        Button(path_row, text="찾아보기", command=self._browse).pack(side=RIGHT, padx=(8, 0))

        button_row = Frame(outer)
        button_row.pack(fill=X, pady=(0, 10))
        Button(button_row, text="한국어 패치 설치/업데이트", command=lambda: self._run("install")).pack(side=LEFT, padx=(0, 8))
        Button(button_row, text="적용 상태 확인", command=lambda: self._run("verify")).pack(side=LEFT, padx=(0, 8))
        Button(button_row, text="원본 복구", command=lambda: self._run("restore")).pack(side=LEFT)

        self.log = Text(outer, wrap="word", height=22)
        self.log.pack(fill=BOTH, expand=True)
        self._log("게임을 완전히 종료한 뒤 설치/복구를 진행해 주세요.")

    def _browse(self) -> None:
        selected = filedialog.askdirectory(title="Tales of Seikyu 설치 폴더 선택")
        if selected:
            self.path_var.set(selected)

    def _log(self, message: str) -> None:
        self.log.insert(END, message + "\n")
        self.log.see(END)

    def _queue_log(self, message: str) -> None:
        self.queue.put(message)

    def _pump(self) -> None:
        try:
            while True:
                self._log(self.queue.get_nowait())
        except queue.Empty:
            pass
        self.root.after(100, self._pump)

    def _run(self, action: str) -> None:
        path = Path(self.path_var.get())
        thread = threading.Thread(target=self._worker, args=(action, path), daemon=True)
        thread.start()

    def _worker(self, action: str, path: Path) -> None:
        self._queue_log("")
        self._queue_log(f"[{action}] 시작")
        try:
            if action == "install":
                result = install_patch(path, log=self._queue_log)
                title = "설치 완료"
            elif action == "restore":
                result = restore_patch(path, log=self._queue_log)
                title = "복구 완료"
            else:
                result = verify_patch(path, log=self._queue_log)
                title = "검증 완료"
            self._queue_log(str(result))
            messagebox.showinfo(title, result.get("status", title))
        except PatchError as exc:
            self._queue_log(f"오류: {exc}")
            messagebox.showerror("오류", str(exc))
        except Exception as exc:  # noqa: BLE001 - GUI should not crash silently.
            self._queue_log(f"예상치 못한 오류: {exc}")
            messagebox.showerror("예상치 못한 오류", str(exc))

    def mainloop(self) -> None:
        self.root.mainloop()


def main() -> int:
    if "--no-gui" in sys.argv or any(flag in sys.argv for flag in ("--install", "--restore", "--verify")):
        return cli_main()
    PatcherGui().mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
