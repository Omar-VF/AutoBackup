import json
import os
import shutil
import sys
from datetime import datetime, time
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_CONFIG: Dict[str, Any] = {
    "source_folder": "",
    "destination_folder": "",
    "interval_minutes": 60,
    "start_time": "09:00",
    "end_time": "21:00",
    "active_days": [0, 1, 2, 3, 4, 5],  # 0=Monday, 6=Sunday. Default: Mon-Sat
    "retention_days": 30,
    "backup_prefix": "",
    "sound_alerts": True,
    "desktop_notifications": True,
    "run_on_startup": False,
    "min_free_space_mb": 500,
    "last_backup_time": None,
    "is_paused": False,
}


class ConfigManager:
    """Manages application settings with persistent JSON storage."""

    def __init__(self, config_path: Optional[str] = None):
        if config_path:
            self.config_path = Path(config_path)
        elif getattr(sys, "frozen", False):
            # When running as packaged application, user configuration and storage
            # paths MUST always live in %APPDATA%/Tethr so updates never overwrite them.
            app_data = Path(os.getenv("APPDATA", ".")) / "Tethr"
            app_data.mkdir(parents=True, exist_ok=True)
            self.config_path = app_data / "config.json"

            # Migration: if a legacy config exists in exe directory or parent, migrate it
            if not self.config_path.exists() or self.config_path.stat().st_size == 0:
                try:
                    exe_dir = Path(sys.executable).parent
                    candidates = [
                        exe_dir / "config.json",
                        exe_dir / "_internal" / "config.json",
                        Path(__file__).resolve().parent.parent / "config.json",
                    ]
                    for cand in candidates:
                        if cand.exists() and cand.is_file() and cand.stat().st_size > 0:
                            shutil.copy2(cand, self.config_path)
                            break
                except Exception:
                    pass
        else:
            # Development mode: local repository directory if writable, else AppData
            local_path = Path(__file__).resolve().parent.parent / "config.json"
            try:
                if not local_path.exists() or local_path.stat().st_size == 0:
                    with open(local_path, "w", encoding="utf-8") as f:
                        json.dump(DEFAULT_CONFIG, f, indent=4)
                self.config_path = local_path
            except (PermissionError, OSError):
                app_data = Path(os.getenv("APPDATA", ".")) / "Tethr"
                app_data.mkdir(parents=True, exist_ok=True)
                self.config_path = app_data / "config.json"

        self.data: Dict[str, Any] = self.load()

    def load(self) -> Dict[str, Any]:
        """Loads configuration from file or returns defaults."""
        data = dict(DEFAULT_CONFIG)
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        saved = json.loads(content)
                        if isinstance(saved, dict):
                            data.update(saved)
            except Exception as e:
                print(f"Error loading config from {self.config_path}: {e}")
        return data

    def save(self) -> bool:
        """Saves current configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config to {self.config_path}: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any, auto_save: bool = True) -> None:
        self.data[key] = value
        if auto_save:
            self.save()

    def update(self, new_data: Dict[str, Any], auto_save: bool = True) -> None:
        self.data.update(new_data)
        if auto_save:
            self.save()

    @property
    def source_folder(self) -> str:
        return self.data.get("source_folder", "")

    @property
    def destination_folder(self) -> str:
        return self.data.get("destination_folder", "")

    @property
    def interval_minutes(self) -> int:
        return max(1, int(self.data.get("interval_minutes", 60)))

    @property
    def retention_days(self) -> int:
        return max(0, int(self.data.get("retention_days", 30)))

    @property
    def active_days(self) -> List[int]:
        return self.data.get("active_days", [0, 1, 2, 3, 4, 5])

    @property
    def is_paused(self) -> bool:
        return bool(self.data.get("is_paused", False))

    @is_paused.setter
    def is_paused(self, val: bool) -> None:
        self.set("is_paused", bool(val))

    def parse_time(self, time_str: str) -> time:
        """Parses HH:MM string to datetime.time."""
        try:
            parts = [int(p) for p in time_str.split(":")]
            return time(hour=parts[0], minute=parts[1])
        except Exception:
            return time(9, 0)

    def is_within_working_hours(self, dt: Optional[datetime] = None) -> bool:
        """Determines if the specified datetime (or now) falls in the shop's active hours and days."""
        if dt is None:
            dt = datetime.now()

        # Day of week check (Monday is 0, Sunday is 6)
        if dt.weekday() not in self.active_days:
            return False

        start = self.parse_time(self.data.get("start_time", "09:00"))
        end = self.parse_time(self.data.get("end_time", "21:00"))
        current_time = dt.time()

        if start <= end:
            return start <= current_time <= end
        else:
            # Over-midnight shifts (e.g., 22:00 to 04:00)
            return current_time >= start or current_time <= end

    def is_configured(self) -> bool:
        """Checks whether source and destination paths are validly set."""
        src = self.source_folder
        dst = self.destination_folder
        return bool(src and dst and os.path.isdir(src))
