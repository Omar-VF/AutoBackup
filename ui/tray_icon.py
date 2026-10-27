from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMenu, QSystemTrayIcon

from autobackup.config import ConfigManager
from ui.icons import create_tray_icon


class SystemTrayManager(QObject):
    """Manages the Windows system tray icon, context menu, and desktop notifications."""

    open_requested = pyqtSignal()
    backup_now_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    check_updates_requested = pyqtSignal()
    exit_requested = pyqtSignal()
    pause_toggled = pyqtSignal()

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.tray_icon = QSystemTrayIcon(parent)
        self.tray_icon.setIcon(create_tray_icon("active"))
        self.tray_icon.setToolTip("Tethr - Automated Billing Backup")

        self._create_menu()
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _create_menu(self):
        self.menu = QMenu()

        self.status_action = self.menu.addAction("Status: Initializing...")
        self.status_action.setEnabled(False)
        self.menu.addSeparator()

        self.open_action = self.menu.addAction("Open Dashboard")
        self.open_action.triggered.connect(self.open_requested.emit)

        self.backup_now_action = self.menu.addAction("Backup Now")
        self.backup_now_action.triggered.connect(self.backup_now_requested.emit)

        self.pause_resume_action = self.menu.addAction("Pause Tethr")
        self.pause_resume_action.triggered.connect(self._toggle_pause)

        self.settings_action = self.menu.addAction("Settings...")
        self.settings_action.triggered.connect(self.settings_requested.emit)

        self.menu.addSeparator()
        self.check_updates_action = self.menu.addAction("Check for Updates...")
        self.check_updates_action.triggered.connect(self.check_updates_requested.emit)

        self.menu.addSeparator()
        self.exit_action = self.menu.addAction("Exit Tethr")
        self.exit_action.triggered.connect(self.exit_requested.emit)

        self.tray_icon.setContextMenu(self.menu)

    def _on_tray_activated(self, reason):
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            self.open_requested.emit()

    def _toggle_pause(self):
        is_paused = self.config.is_paused
        self.config.is_paused = not is_paused
        self.update_state()
        self.pause_toggled.emit()

    def set_status(self, current_status: str = "active", tooltip_text: str = ""):
        self.update_state(current_status, tooltip_text)

    def update_state(self, current_status: str = "active", tooltip_text: str = ""):
        """Updates the icon appearance, context menu text, and tooltip."""
        if self.config.is_paused:
            self.tray_icon.setIcon(create_tray_icon("paused"))
            self.pause_resume_action.setText("Resume Tethr")
            self.status_action.setText("Status: Paused")
            self.tray_icon.setToolTip("Tethr - PAUSED")
        else:
            self.tray_icon.setIcon(create_tray_icon(current_status))
            self.pause_resume_action.setText("Pause Tethr")
            if tooltip_text:
                self.status_action.setText(f"Status: {tooltip_text[:30]}")
                self.tray_icon.setToolTip(f"Tethr - {tooltip_text}")

    def notify(self, title: str, message: str, is_error: bool = False):
        """Displays a native Windows toast notification via the system tray."""
        if not self.config.get("desktop_notifications", True):
            return

        icon = (
            QSystemTrayIcon.MessageIcon.Critical
            if is_error
            else QSystemTrayIcon.MessageIcon.Information
        )
        self.tray_icon.showMessage(title, message, icon, 5000)

    def hide(self):
        """Explicitly hides the tray icon so Windows immediately removes it from the taskbar."""
        if self.tray_icon:
            self.tray_icon.hide()

