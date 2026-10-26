import os
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMessageBox

from autobackup.config import ConfigManager
from autobackup.logger import BackupLogger
from autobackup.scheduler import BackupScheduler
from ui.main_window import MainWindow
from ui.styles import MODERN_DARK_STYLE
from ui.tray_icon import SystemTrayManager


MUTEX_HANDLE = None


def check_single_instance() -> bool:
    """Uses a Windows kernel mutex to guarantee single instance without memory orphan bugs."""
    global MUTEX_HANDLE
    if sys.platform != "win32":
        return True

    try:
        import ctypes
        ERROR_ALREADY_EXISTS = 183
        kernel32 = ctypes.windll.kernel32
        MUTEX_HANDLE = kernel32.CreateMutexW(None, False, "Tethr_Named_Mutex_v1")
        if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
            return False
        return True
    except Exception:
        return True


def main():
    # Group under app model ID on Windows
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Tethr")
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setApplicationName("Tethr")
    app.setOrganizationName("Tethr")
    app.setQuitOnLastWindowClosed(False)

    # Single-instance enforcement
    if not check_single_instance():
        print("Tethr is already running in your Windows System Tray.")
        QMessageBox.information(
            None,
            "Already Running",
            "Tethr is already running. Check your Windows System Tray (near the clock).",
        )
        sys.exit(0)

    # Load custom fonts
    from PyQt6.QtGui import QFontDatabase, QFont
    if getattr(sys, "frozen", False):
        base_dir = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    else:
        base_dir = Path(__file__).resolve().parent
    fonts_dir = base_dir / "assets" / "fonts"
    if fonts_dir.exists():
        QFontDatabase.addApplicationFont(str(fonts_dir / "InstrumentSerif-Regular.ttf"))
        QFontDatabase.addApplicationFont(str(fonts_dir / "Manrope-Variable.ttf"))
    app.setFont(QFont("Manrope", 13))

    # Apply modern custom stylesheet
    app.setStyleSheet(MODERN_DARK_STYLE)

    # Core subsystems
    config = ConfigManager()
    logger = BackupLogger()
    scheduler = BackupScheduler(config, logger)
    tray = SystemTrayManager(config)

    window = MainWindow(config, logger, scheduler, tray)

    # Check start arguments (e.g. Windows autostart flag)
    is_minimized = "--minimized" in sys.argv or "--tray" in sys.argv
    if not is_minimized:
        window.show()
        window.raise_()
        window.activateWindow()
    else:
        tray.notify("Tethr Active", "Running quietly in the system tray.")

    exit_code = app.exec()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
