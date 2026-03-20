from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Callable

from fullscreen_module.fullscreen_server import FullscreenLocalServer


def run_app(
    *,
    command_provider: Callable[[], list[str]] | None = None,
    stop_event=None,
    on_health: Callable[..., None] | None = None,
    start_hidden: bool = False,
    config_dir: Path | None = None,
    data_dir: Path | None = None,
    log_dir: Path | None = None,
) -> None:
    fullscreen_server = FullscreenLocalServer()
    fullscreen_server.start()

    root = tk.Tk()
    root.title("Fullscreen Companion Module")
    root.geometry("760x420")
    root.minsize(680, 360)

    status_var = tk.StringVar(value="Idle")
    server_var = tk.StringVar(value=f"Local helper: {fullscreen_server.base_url}")
    action_var = tk.StringVar(value="Last action: idle")

    shell = ttk.Frame(root, padding=16)
    shell.pack(fill="both", expand=True)

    ttk.Label(shell, text="Fullscreen Companion Module", font=("Segoe UI Semibold", 18)).pack(anchor="w")
    ttk.Label(
        shell,
        text="Ovaj modul pokreće localhost fullscreen helper za Full screen btn CWC i može poslati F11 lokalnom browseru.",
        wraplength=700,
    ).pack(anchor="w", pady=(8, 12))

    ttk.Label(shell, textvariable=status_var).pack(anchor="w")
    ttk.Label(shell, textvariable=server_var).pack(anchor="w", pady=(4, 4))
    ttk.Label(shell, textvariable=action_var).pack(anchor="w", pady=(0, 12))

    button_row = ttk.Frame(shell)
    button_row.pack(fill="x", pady=(0, 12))

    def _toggle() -> None:
        fullscreen_server._perform("toggle")
        action_var.set(f"Last action: {fullscreen_server.last_action}")
        status_var.set("F11 sent")

    ttk.Button(button_row, text="Send F11", command=_toggle).pack(side="left")

    info = tk.Text(shell, height=14, wrap="word")
    info.pack(fill="both", expand=True)
    info.insert(
        "1.0",
        "\n".join(
            [
                "Hosted dirs and runtime info:",
                f"config_dir = {config_dir}",
                f"data_dir   = {data_dir}",
                f"log_dir    = {log_dir}",
                f"local_helper = {fullscreen_server.base_url}",
                "",
                "Endpoints:",
                "- /health",
                "- /fullscreen/enter",
                "- /fullscreen/exit",
                "- /fullscreen/toggle",
                "",
                "Use this module when the CWC fullscreen button should use a local helper instead of only browser APIs.",
            ]
        ),
    )
    info.configure(state="disabled")

    closed = {"done": False}

    def _show() -> None:
        root.deiconify()
        root.lift()
        try:
            root.focus_force()
        except Exception:
            pass

    def _close() -> None:
        if closed["done"]:
            return
        closed["done"] = True
        fullscreen_server.stop()
        try:
            root.destroy()
        except Exception:
            pass

    def _tick() -> None:
        if closed["done"]:
            return
        if command_provider is not None:
            for cmd in command_provider():
                if cmd == "show":
                    _show()
                elif cmd == "toggle":
                    _toggle()
                elif cmd == "close":
                    _close()
                    return
        if stop_event is not None and stop_event.is_set():
            _close()
            return
        action_var.set(f"Last action: {fullscreen_server.last_action}")
        if on_health is not None:
            try:
                on_health(
                    status="running",
                    ui_ready=True,
                    pipe_connected=False,
                    last_error="",
                    helper_url=fullscreen_server.base_url,
                    last_action=fullscreen_server.last_action,
                )
            except Exception:
                pass
        root.after(250, _tick)

    root.protocol("WM_DELETE_WINDOW", _close)
    if start_hidden:
        root.withdraw()
        status_var.set("Hosted / hidden")
    else:
        status_var.set("Standalone")
    _tick()
    root.mainloop()
