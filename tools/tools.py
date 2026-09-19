"""
tools.py — OS-independent tool implementations.

Supports:
  - Windows  → pyautogui for all GUI actions
  - Linux X11 → pyautogui
  - Linux Wayland → ydotool (with GNOME xdotool fallback) → pyautogui
  - macOS → pyautogui
"""

import os
import platform
import shutil
import subprocess
import time

import pyautogui

pyautogui.FAILSAFE = False

# ── Detect current OS once at import time ─────────────────────────────────────
PLATFORM = platform.system()   # 'Windows' | 'Linux' | 'Darwin'

# On Linux, grant the current user access to the X display (no-op on Wayland/Windows)
if PLATFORM == "Linux":
    import getpass
    _username = getpass.getuser()
    subprocess.run(
        ["xhost", f"+SI:localuser:{_username}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


# ══════════════════════════════════════════════════════════════════════════════
# Terminal tool
# ══════════════════════════════════════════════════════════════════════════════

def use_terminal(text: str) -> subprocess.CompletedProcess:
    """Executes a terminal command after asking for user confirmation.

    Works on Windows (cmd/PowerShell), Linux, and macOS.
    """
    des = input(
        f"Do you want to execute this command?\n"
        f"{text}\n"
        f"Enter 1 for Yes, 0 for No: "
    )

    try:
        des = int(des)
    except ValueError:
        print("Invalid input. Please enter 1 or 0.")
        return subprocess.CompletedProcess(
            args=text, returncode=1, stdout="", stderr="Invalid user input"
        )

    if des == 1:
        print("Running Process....")
        res = subprocess.run(
            text,
            shell=True,
            capture_output=True,
            text=True,
        )
        print("Command Executed Output is: ", res.stdout, "Exiting...")
        return res
    else:
        print("Command Execution cancelled")
        return subprocess.CompletedProcess(
            args=text, returncode=1, stdout="", stderr="Command execution cancelled by user"
        )


# ══════════════════════════════════════════════════════════════════════════════
# Linux Wayland helpers  (all guarded — never called on Windows/macOS)
# ══════════════════════════════════════════════════════════════════════════════

def _is_wayland() -> bool:
    """True only on Linux Wayland sessions."""
    if PLATFORM != "Linux":
        return False
    return (
        os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland"
        or bool(os.environ.get("WAYLAND_DISPLAY"))
    )


def _is_gnome() -> bool:
    """True only on GNOME desktops (Linux)."""
    if PLATFORM != "Linux":
        return False
    return "gnome" in os.environ.get("XDG_CURRENT_DESKTOP", "").lower()


def _run_ydotool(cmd_args: list[str]) -> subprocess.CompletedProcess:
    """Run an ydotool command, injecting the socket path if needed."""
    env = os.environ.copy()
    if (
        "/tmp/.ydotool_socket" not in env.get("YDOTOOL_SOCKET", "")
        and os.path.exists("/tmp/.ydotool_socket")
    ):
        env["YDOTOOL_SOCKET"] = "/tmp/.ydotool_socket"
    return subprocess.run(["ydotool"] + cmd_args, capture_output=True, text=True, env=env)


def _ydotool_working() -> bool:
    """True if the ydotool daemon is running and uinput is accessible."""
    res = _run_ydotool(["key", "--delay", "0", "a:1", "a:0"])
    return res.returncode == 0


def _run_gnome_hotkey(keys: list[str]) -> bool:
    """Send a hotkey via xdotool to the XWayland display.

    Works on GNOME Wayland — the compositor intercepts system shortcuts
    sent to the XWayland display.  Returns True on success.
    """
    if shutil.which("xdotool") is None:
        return False

    _xdotool_key_map = {
        "ctrl": "ctrl", "alt": "alt", "shift": "shift",
        "super": "super", "win": "super",
        "tab": "Tab", "return": "Return", "enter": "Return",
        "escape": "Escape", "esc": "Escape", "space": "space",
        "left": "Left", "right": "Right", "up": "Up", "down": "Down",
    }
    combo = "+".join(_xdotool_key_map.get(k.lower(), k) for k in keys)

    env = os.environ.copy()
    if not env.get("DISPLAY"):
        env["DISPLAY"] = ":0"

    res = subprocess.run(
        ["xdotool", "key", "--clearmodifiers", combo],
        capture_output=True, text=True, env=env, timeout=5,
    )
    return res.returncode == 0


# ══════════════════════════════════════════════════════════════════════════════
# GUI control — unified cross-platform entry point
# ══════════════════════════════════════════════════════════════════════════════

def gui_control(
    action: str,
    x: int = None,
    y: int = None,
    duration: float = 0.0,
    clicks: int = 1,
    interval: float = 0.0,
    button: str = "left",
    text: str = None,
    keys: list = None,
    scroll: int = None,
) -> str:
    """Perform GUI actions using the best available backend for the current OS.

    Backend selection:
      • Windows / macOS    → pyautogui (always)
      • Linux X11          → pyautogui
      • Linux Wayland      → ydotool → GNOME xdotool → pyautogui (fallback chain)

    Parameters
    ----------
    action : str
        One of 'move', 'click', 'double_click', 'right_click',
        'typewrite', 'press', 'hotkey', 'scroll'.
    x, y : int, optional
        Screen coordinates for mouse actions.
    duration : float
        Seconds taken to move the mouse (pyautogui).
    clicks : int
        Number of clicks (default 1).
    interval : float
        Seconds between clicks.
    button : str
        Mouse button — 'left', 'right', or 'middle'.
    text : str, optional
        Text to type ('typewrite') or key to press ('press').
    keys : list[str], optional
        Key combination for 'hotkey' (e.g. ['ctrl', 'c']).
    scroll : int, optional
        Scroll amount — positive = up, negative = down.

    Returns
    -------
    str
        'Success' or an error description.
    """
    # Wayland + ydotool are only relevant on Linux
    is_wayland = _is_wayland()
    has_ydotool = (PLATFORM == "Linux") and (shutil.which("ydotool") is not None)

    try:
        # ── move ──────────────────────────────────────────────────────
        if action == "move":
            if x is None or y is None:
                return "Error: x and y must be provided for move action"
            if is_wayland and has_ydotool:
                res = _run_ydotool(["mousemove", "-a", str(x), str(y)])
                if res.returncode != 0:
                    pyautogui.moveTo(x, y, duration=duration)
            else:
                pyautogui.moveTo(x, y, duration=duration)

        # ── click ─────────────────────────────────────────────────────
        elif action == "click":
            if is_wayland and has_ydotool:
                if x is not None and y is not None:
                    _run_ydotool(["mousemove", "-a", str(x), str(y)])
                btn_code = "0xC0" if button == "left" else "0xC1" if button == "right" else "0xC2"
                _run_ydotool(["click", btn_code])
            else:
                if x is not None and y is not None:
                    pyautogui.click(x, y, clicks=clicks, interval=interval, button=button)
                else:
                    pyautogui.click(clicks=clicks, interval=interval, button=button)

        # ── double_click ──────────────────────────────────────────────
        elif action == "double_click":
            if is_wayland and has_ydotool:
                if x is not None and y is not None:
                    _run_ydotool(["mousemove", "-a", str(x), str(y)])
                _run_ydotool(["click", "0xC0"])
                time.sleep(0.1)
                _run_ydotool(["click", "0xC0"])
            else:
                if x is not None and y is not None:
                    pyautogui.doubleClick(x, y, interval=interval, button=button)
                else:
                    pyautogui.doubleClick(interval=interval, button=button)

        # ── right_click ───────────────────────────────────────────────
        elif action == "right_click":
            if is_wayland and has_ydotool:
                if x is not None and y is not None:
                    _run_ydotool(["mousemove", "-a", str(x), str(y)])
                _run_ydotool(["click", "0xC1"])
            else:
                if x is not None and y is not None:
                    pyautogui.rightClick(x, y, clicks=clicks, interval=interval)
                else:
                    pyautogui.rightClick(clicks=clicks, interval=interval)

        # ── typewrite ─────────────────────────────────────────────────
        elif action == "typewrite":
            if text is None:
                return "Error: text must be provided for typewrite action"
            if is_wayland and has_ydotool:
                _run_ydotool(["type", "--", text])
            else:
                pyautogui.typewrite(text, interval=interval)

        # ── press ─────────────────────────────────────────────────────
        elif action == "press":
            if text is None:
                return "Error: key must be provided in text parameter for press action"
            if is_wayland and has_ydotool:
                _run_ydotool(["key", f"{text}:1", f"{text}:0"])
            else:
                pyautogui.press(text)

        # ── hotkey ────────────────────────────────────────────────────
        elif action == "hotkey":
            if not keys:
                return "Error: keys list must be provided for hotkey action"
            if is_wayland:
                # Fallback chain: GNOME xdotool → ydotool daemon → pyautogui
                if _is_gnome() and _run_gnome_hotkey(keys):
                    pass  # handled
                elif has_ydotool and _ydotool_working():
                    key_args = [f"{k}:1" for k in keys] + [f"{k}:0" for k in reversed(keys)]
                    _run_ydotool(["key"] + key_args)
                else:
                    pyautogui.hotkey(*keys)
            else:
                pyautogui.hotkey(*keys)

        # ── scroll ────────────────────────────────────────────────────
        elif action == "scroll":
            if scroll is None:
                return "Error: scroll amount must be provided for scroll action"
            pyautogui.scroll(scroll, x=x, y=y)

        else:
            return f"Error: Unknown action '{action}'"

        return "Success"

    except Exception as e:
        return f"Error: {e}"
