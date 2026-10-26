import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class BackupLogger:
    """Manages application logging and persistent backup history records."""

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            self.data_dir = Path(__file__).resolve().parent.parent / "logs"
        else:
            self.data_dir = Path(data_dir)

        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.data_dir / "autobackup.log"
        self.history_file = self.data_dir / "history.json"

        # Setup standard logger
        self.logger = logging.getLogger("Tethr")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )
            # File handler
            file_h = logging.FileHandler(self.log_file, encoding="utf-8")
            file_h.setFormatter(formatter)
            self.logger.addHandler(file_h)

            # Console handler
            console_h = logging.StreamHandler()
            console_h.setFormatter(formatter)
            self.logger.addHandler(console_h)

    def info(self, msg: str) -> None:
        self.logger.info(msg)

    def warning(self, msg: str) -> None:
        self.logger.warning(msg)

    def error(self, msg: str) -> None:
        self.logger.error(msg)

    def add_history_entry(
        self,
        status: str,
        archive_name: str,
        source_path: str,
        dest_path: str,
        file_count: int,
        size_bytes: int,
        duration_seconds: float,
        error_message: Optional[str] = None,
        purged_count: int = 0,
    ) -> Dict[str, Any]:
        """Appends a new backup record into history.json."""
        history = self.get_history()

        entry = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": status,
            "archive_name": archive_name,
            "source_path": source_path,
            "dest_path": dest_path,
            "file_count": file_count,
            "size_bytes": size_bytes,
            "size_formatted": self.format_bytes(size_bytes),
            "duration_seconds": round(duration_seconds, 2),
            "error_message": error_message or "",
            "purged_count": purged_count,
        }

        history.insert(0, entry)
        # Keep maximum 500 records in history
        history = history[:500]

        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save history: {e}")

        return entry

    def get_history(self) -> List[Dict[str, Any]]:
        """Returns the list of past backups."""
        if not self.history_file.exists():
            return []
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []

    def get_stats(self) -> Dict[str, Any]:
        """Calculates summary metrics for display on the dashboard."""
        history = self.get_history()
        total = len(history)
        successful = sum(1 for h in history if h.get("status") == "SUCCESS")
        failed = sum(1 for h in history if h.get("status") == "FAILED")
        total_bytes = sum(h.get("size_bytes", 0) for h in history if h.get("status") == "SUCCESS")

        last_entry = history[0] if history else None

        return {
            "total_runs": total,
            "successful_runs": successful,
            "failed_runs": failed,
            "success_rate": f"{(successful / total * 100):.1f}%" if total > 0 else "100%",
            "total_bytes_formatted": self.format_bytes(total_bytes),
            "last_backup_time": last_entry["timestamp"] if last_entry else "Never",
            "last_backup_status": last_entry["status"] if last_entry else "N/A",
            "last_backup_size": last_entry["size_formatted"] if last_entry else "0 B",
            "last_archive_name": last_entry["archive_name"] if last_entry else "-",
        }

    @staticmethod
    def format_bytes(size: int) -> str:
        """Converts bytes to human readable string (KB, MB, GB)."""
        if size <= 0:
            return "0 B"
        units = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        s = float(size)
        while s >= 1024 and i < len(units) - 1:
            s /= 1024.0
            i += 1
        return f"{s:.2f} {units[i]}"
