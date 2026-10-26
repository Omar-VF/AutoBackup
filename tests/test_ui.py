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
from ui.styles import TETHR_DESIGN_STYLE
from ui.tray_icon import SystemTrayManager


class TestUIComponents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)
        cls.app.setStyleSheet(TETHR_DESIGN_STYLE)

    def test_icons(self):
        app_icon = create_app_icon(64)
        self.assertFalse(app_icon.isNull())
        for status in ["active", "working", "paused", "error"]:
            tray_icon = create_tray_icon(status, 32)
            self.assertFalse(tray_icon.isNull())

    def test_main_window_and_modal(self):
        config = ConfigManager()
        logger = BackupLogger()
        scheduler = BackupScheduler(config, logger)
        tray = SystemTrayManager(config)

        window = MainWindow(config, logger, scheduler, tray)
        self.assertIsNotNone(window)
        window.show()
        self.assertFalse(window.overlay_widget.isVisible())

        # Test in-window modal open and close
        window._open_inwindow_settings()
        self.assertTrue(window.overlay_widget.isVisible())
        window._close_inwindow_settings()
        self.assertFalse(window.overlay_widget.isVisible())

    def test_hours_selection_and_presets(self):
        config = ConfigManager()
        logger = BackupLogger()
        scheduler = BackupScheduler(config, logger)
        tray = SystemTrayManager(config)

        window = MainWindow(config, logger, scheduler, tray)
        window._open_inwindow_settings()

        # Check combos are populated with 15-minute intervals
        self.assertGreaterEqual(window.combo_opens.count(), 96)
        self.assertGreaterEqual(window.combo_closes.count(), 97)

        # Apply preset "9 AM – 6 PM"
        window._apply_hour_preset("09:00", "18:00")
        self.assertEqual(window.combo_opens.currentData(), "09:00")
        self.assertEqual(window.combo_closes.currentData(), "18:00")
        self.assertTrue(window.hour_preset_buttons[1].isChecked())  # 9 AM – 6 PM is index 1

        # Check compat properties
        self.assertEqual(window.time_opens.time().hour(), 9)
        self.assertEqual(window.time_closes.time().hour(), 18)

        # Apply preset "24 Hours"
        window._apply_hour_preset("00:00", "23:59")
        self.assertEqual(window.combo_opens.currentData(), "00:00")
        self.assertEqual(window.combo_closes.currentData(), "23:59")
        self.assertTrue(window.hour_preset_buttons[3].isChecked())  # 24 Hours is index 3

        # Save settings and verify config updated
        window._save_inwindow_settings()
        self.assertEqual(config.get("start_time"), "00:00")
        self.assertEqual(config.get("end_time"), "23:59")


if __name__ == "__main__":
    unittest.main()
