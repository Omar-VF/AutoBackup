import unittest
from autobackup.updater import parse_version, is_newer_version, UpdateInfo
from ui.update_dialog import UpdateDialog


class TestUpdater(unittest.TestCase):
    def test_version_parsing(self):
        self.assertEqual(parse_version("v1.0.0"), (1, 0, 0))
        self.assertEqual(parse_version("1.2.3"), (1, 2, 3))
        self.assertEqual(parse_version("v2.10.4-rc1"), (2, 10, 4))
        self.assertEqual(parse_version(""), (0, 0, 0))

    def test_version_comparison(self):
        self.assertTrue(is_newer_version("v1.0.1", "1.0.0"))
        self.assertTrue(is_newer_version("v1.1.0", "1.0.9"))
        self.assertTrue(is_newer_version("v2.0.0", "1.99.99"))
        self.assertFalse(is_newer_version("v1.0.0", "1.0.0"))
        self.assertFalse(is_newer_version("v0.9.9", "1.0.0"))
        self.assertFalse(is_newer_version("v1.0.0", "1.0.1"))

    def test_update_dialog_init(self):
        info = UpdateInfo(
            version="v1.1.0",
            release_name="Tethr v1.1.0 Feature Release",
            notes="* Added GitHub release auto-updater\n* Polished time pickers",
            download_url="https://github.com/Omar-VF/Tethr/releases/download/v1.1.0/Tethr-Setup.exe",
            asset_name="Tethr-Setup.exe",
            size_bytes=27000000,
            release_url="https://github.com/Omar-VF/Tethr/releases/tag/v1.1.0",
        )
        dialog = UpdateDialog(info)
        self.assertIsNotNone(dialog)
        self.assertEqual(dialog.update_info.version, "v1.1.0")
        self.assertIn("auto-updater", dialog.notes_box.toPlainText())
        self.assertTrue(dialog.btn_update.isEnabled())
        self.assertTrue(dialog.btn_later.isEnabled())

    def test_settings_persistence_across_updates(self):
        import tempfile
        import os
        from autobackup.config import ConfigManager

        with tempfile.TemporaryDirectory() as tmp_dir:
            config_file = os.path.join(tmp_dir, "config.json")
            mgr = ConfigManager(config_file)
            mgr.update({
                "source_folder": r"C:\Billing\Data",
                "destination_folder": r"E:\Backups\2026",
                "interval_minutes": 15,
                "start_time": "08:30",
                "end_time": "20:00",
                "retention_days": 60,
            })

            # Simulate app restart after update
            mgr_after_update = ConfigManager(config_file)
            self.assertEqual(mgr_after_update.get("source_folder"), r"C:\Billing\Data")
            self.assertEqual(mgr_after_update.get("destination_folder"), r"E:\Backups\2026")
            self.assertEqual(mgr_after_update.get("interval_minutes"), 15)
            self.assertEqual(mgr_after_update.get("start_time"), "08:30")
            self.assertEqual(mgr_after_update.get("end_time"), "20:00")
            self.assertEqual(mgr_after_update.get("retention_days"), 60)


if __name__ == "__main__":
    unittest.main()
