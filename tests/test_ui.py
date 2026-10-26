import os
import sys
import unittest

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt6.QtWidgets import QApplication

from autobackup.config import ConfigManager
from autobackup.logger import BackupLogger
from autobackup.scheduler import BackupScheduler
from ui.icons import create_app_icon, create_tray_icon
from ui.main_window import MainWindow
from ui.settings_dialog import SettingsDialog
from ui.styles import MODERN_DARK_STYLE
from ui.tray_icon import SystemTrayManager


class TestUIComponents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)
        cls.app.setStyleSheet(MODERN_DARK_STYLE)

    def test_icons(self):
        app_icon = create_app_icon(64)
        self.assertFalse(app_icon.isNull())
        for status in ["active", "working", "paused", "error"]:
            tray_icon = create_tray_icon(status, 32)
            self.assertFalse(tray_icon.isNull())

    def test_main_window_and_dialog_instantiation(self):
        config = ConfigManager()
        logger = BackupLogger()
        scheduler = BackupScheduler(config, logger)
        tray = SystemTrayManager(config)

        window = MainWindow(config, logger, scheduler, tray)
        self.assertIsNotNone(window)

        dialog = SettingsDialog(config, window)
        self.assertIsNotNone(dialog)


if __name__ == "__main__":
    unittest.main()
