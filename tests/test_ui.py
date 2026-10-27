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

    def test_show_and_raise(self):
        config = ConfigManager()
        logger = BackupLogger()
        scheduler = BackupScheduler(config, logger)
        tray = SystemTrayManager(config)

        window = MainWindow(config, logger, scheduler, tray)
        window.hide()
        self.assertFalse(window.isVisible())
        window._show_and_raise()
        self.assertTrue(window.isVisible())

    def test_12hr_time_formatting(self):
        from datetime import datetime
        from autobackup.config import format_time_12h, format_datetime_12h

        self.assertEqual(format_time_12h("09:00"), "9:00 AM")
        self.assertEqual(format_time_12h("21:00"), "9:00 PM")
        self.assertEqual(format_time_12h("00:00"), "12:00 AM")
        self.assertEqual(format_time_12h("12:00"), "12:00 PM")
        self.assertEqual(format_time_12h("12:30"), "12:30 PM")
        self.assertEqual(format_time_12h("18:15"), "6:15 PM")
        self.assertEqual(format_time_12h("23:59"), "11:59 PM")

        dt = datetime(2026, 10, 27, 21, 5)
        self.assertEqual(format_datetime_12h(dt), "Oct 27 at 9:05 PM")
        dt_am = datetime(2026, 5, 4, 9, 0)
        self.assertEqual(format_datetime_12h(dt_am), "May 04 at 9:00 AM")

        config = ConfigManager()
        logger = BackupLogger()
        scheduler = BackupScheduler(config, logger)
        tray = SystemTrayManager(config)
        window = MainWindow(config, logger, scheduler, tray)
        self.assertIn("AM", window.lbl_sum_hours.text())
        self.assertIn("PM", window.lbl_sum_hours.text())


if __name__ == "__main__":
    unittest.main()

