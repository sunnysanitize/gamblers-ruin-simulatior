from __future__ import annotations

import platform
import subprocess
import threading
from pathlib import Path

try:
    from flask import Flask, send_file
except ImportError as exc:
    raise SystemExit("Missing dependency: flask. Install it with: pip install flask") from exc


def _open_target(target: str) -> bool:
    system = platform.system()
    if system == "Darwin":
        commands = [["open", target]]
    elif system == "Windows":
        commands = [
            ["powershell", "-NoProfile", "-Command", f"Start-Process '{target}'"],
            ["cmd", "/c", "start", "", target],
        ]
    else:
        commands = [["xdg-open", target], ["gio", "open", target]]

    for command in commands:
        try:
            completed = subprocess.run(
                command,
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if completed.returncode == 0:
                return True
        except Exception:
            continue

    return False


def _open_target_with_notice(target: str) -> None:
    if _open_target(target):
        print(f"Opened browser at: {target}")
    else:
        print(f"Auto-open failed. Open this URL manually: {target}")


def serve_dashboard(html_file: Path, host: str, port: int, open_browser: bool) -> None:
    resolved = html_file.resolve()
    app = Flask(__name__)

    @app.get("/")
    def index():
        return send_file(resolved)

    dashboard_url = f"http://{host}:{port}"
    if open_browser:
        threading.Timer(0.8, _open_target_with_notice, args=[dashboard_url]).start()

    print(f"Serving dashboard at: {dashboard_url}")
    print("Press Ctrl+C to stop the server.")
    app.run(host=host, port=port, debug=False, use_reloader=False)
