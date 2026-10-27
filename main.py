import os
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtNetwork import QLocalServer, QLocalSocket

from autobackup.config import ConfigManager
from autobackup.logger import BackupLogger
from autobackup.scheduler import BackupScheduler
from ui.main_window import MainWindow
from ui.styles import MODERN_DARK_STYLE
from ui.tray_icon import SystemTrayManager

IPC_SERVER_NAME = "Tethr_App_SingleInstance_v1"


def main() -> int:
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

    # 1. Single-instance check via QLocalSocket
    client_socket = QLocalSocket()
    client_socket.connectToServer(IPC_SERVER_NAME)
    if client_socket.waitForConnected(500):
        # Existing instance is already running: bring it to the foreground
        client_socket.write(b"SHOW\n")
        client_socket.waitForBytesWritten(500)
        client_socket.disconnectFromServer()
        return 0

    # 2. First instance: start IPC local server to listen for secondary launches
    QLocalServer.removeServer(IPC_SERVER_NAME)
    ipc_server = QLocalServer(app)
    if not ipc_server.listen(IPC_SERVER_NAME):
        QLocalServer.removeServer(IPC_SERVER_NAME)
        ipc_server.listen(IPC_SERVER_NAME)

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

    # Wire IPC listener to bring window to foreground when desktop shortcut is clicked
    def _on_ipc_incoming():
        conn = ipc_server.nextPendingConnection()
        if conn:
            window._show_and_raise()
            conn.disconnectFromServer()

    ipc_server.newConnection.connect(_on_ipc_incoming)

    # Check start arguments (e.g. Windows autostart flag)
    is_minimized = "--minimized" in sys.argv or "--tray" in sys.argv
    if not is_minimized:
        window._show_and_raise()
    else:
        tray.notify("Tethr Active", "Running quietly in the system tray.")

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
