import os
import sys
from pathlib import Path


REG_APP_NAME = "ShopAutoBackupPro"
REG_SUBKEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def get_startup_command() -> str:
    """Returns the exact launch command to place into the Windows startup registry."""
    main_py = Path(__file__).resolve().parent.parent / "main.py"
    # Use pythonw if available for windowless startup
    python_exe = sys.executable
    if "python.exe" in python_exe.lower():
        pythonw_candidate = python_exe.lower().replace("python.exe", "pythonw.exe")
        if os.path.exists(pythonw_candidate):
            python_exe = pythonw_candidate

    return f'"{python_exe}" "{main_py}" --minimized'


def is_autostart_enabled() -> bool:
    """Checks whether the application is registered to start on Windows boot."""
    if sys.platform != "win32":
        return False

    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_SUBKEY, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, REG_APP_NAME)
            return bool(value)
    except (FileNotFoundError, OSError):
        return False


def set_autostart(enable: bool) -> bool:
    """Adds or removes the application from the Windows startup registry."""
    if sys.platform != "win32":
        return False

    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_SUBKEY, 0, winreg.KEY_SET_VALUE) as key:
            if enable:
                cmd = get_startup_command()
                winreg.SetValueEx(key, REG_APP_NAME, 0, winreg.REG_SZ, cmd)
            else:
                try:
                    winreg.DeleteValue(key, REG_APP_NAME)
                except FileNotFoundError:
                    pass
        return True
    except Exception as e:
        print(f"Failed to set Windows autostart: {e}")
        return False
