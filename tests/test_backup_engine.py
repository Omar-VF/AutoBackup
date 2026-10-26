import os
import shutil
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
import unittest

from autobackup.config import ConfigManager
from autobackup.logger import BackupLogger
from autobackup.backup_engine import BackupEngine


class TestAutoBackupCore(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="autobackup_test_")
        self.src_dir = os.path.join(self.test_dir, "billing_source")
        self.dst_dir = os.path.join(self.test_dir, "backup_destination")
        os.makedirs(self.src_dir, exist_ok=True)
        os.makedirs(self.dst_dir, exist_ok=True)

        # Create dummy billing data files
        for i in range(5):
            with open(os.path.join(self.src_dir, f"invoice_2026_{i}.dat"), "w") as f:
                f.write(f"Sample billing transaction line data {i} * " * 50)

        # Create subfolder
        sub = os.path.join(self.src_dir, "db")
        os.makedirs(sub, exist_ok=True)
        with open(os.path.join(sub, "billing.sqlite"), "w") as f:
            f.write("SQLite format 3 header placeholder content for test")

        self.config_path = os.path.join(self.test_dir, "test_config.json")
        self.config = ConfigManager(self.config_path)
        self.config.update({
            "source_folder": self.src_dir,
            "destination_folder": self.dst_dir,
            "interval_minutes": 60,
            "start_time": "08:00",
            "end_time": "22:00",
            "active_days": [0, 1, 2, 3, 4, 5, 6],
            "retention_days": 7,
            "backup_prefix": "",
            "min_free_space_mb": 1,
        })

        self.logger = BackupLogger(data_dir=Path(self.test_dir) / "logs")
        self.engine = BackupEngine(self.config, self.logger)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_backup_execution_and_integrity(self):
        result = self.engine.execute_backup()
        self.assertTrue(result.success, f"Backup failed: {result.error_message}")
        self.assertTrue(os.path.isfile(result.archive_path))
        self.assertRegex(result.archive_name, r"^\d{2}-\d{2}-\d{4}_\d{2}-\d{2}\.zip$")
        self.assertGreater(result.size_bytes, 0)
        self.assertEqual(result.file_count, 6)

        # Check that history logged
        history = self.logger.get_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["status"], "SUCCESS")
        self.assertEqual(history[0]["file_count"], 6)

    def test_working_hours_check(self):
        # Test within hours
        dt_within = datetime.now().replace(hour=12, minute=0)
        self.assertTrue(self.config.is_within_working_hours(dt_within))

        # Test outside hours
        dt_night = datetime.now().replace(hour=23, minute=30)
        self.assertFalse(self.config.is_within_working_hours(dt_night))

    def test_retention_purge(self):
        # Create an artificial old backup file (10 days old in DD-MM-YYYY_HR-MIN format)
        old_time = datetime.now() - timedelta(days=10)
        old_filename = f"{old_time.strftime('%d-%m-%Y_%H-%M')}.zip"
        old_path = os.path.join(self.dst_dir, old_filename)
        with open(old_path, "w") as f:
            f.write("mock old archive content")

        # Run backup which triggers retention cleaner
        result = self.engine.execute_backup()
        self.assertTrue(result.success)
        self.assertEqual(result.purged_count, 1)
        self.assertFalse(os.path.exists(old_path), "Old backup was not purged according to retention policy")


if __name__ == "__main__":
    unittest.main()
