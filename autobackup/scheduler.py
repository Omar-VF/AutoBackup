import time
from datetime import datetime, timedelta
from typing import Optional

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from autobackup.backup_engine import BackupEngine, BackupResult
from autobackup.config import ConfigManager, format_time_12h
from autobackup.logger import BackupLogger
from autobackup.sound_alerts import SoundAlerts


class BackupWorkerThread(QThread):
    """Executes the backup compression task in a dedicated background thread."""

    progress_changed = pyqtSignal(str, int, int)  # file_name, current, total
    finished_result = pyqtSignal(object)  # BackupResult

    def __init__(self, engine: BackupEngine):
        super().__init__()
        self.engine = engine
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        result = self.engine.execute_backup(
            progress_callback=self._on_progress,
            cancel_requested=lambda: self._is_cancelled,
        )
        self.finished_result.emit(result)

    def _on_progress(self, file_name: str, current: int, total: int):
        self.progress_changed.emit(file_name, current, total)


class BackupScheduler(QObject):
    """
    Manages the hourly backup schedule, working-hours gating,
    and coordinates notifications and UI state.
    """

    status_changed = pyqtSignal(str)
    countdown_changed = pyqtSignal(int, str)  # seconds_remaining, human_readable
    backup_started = pyqtSignal()
    backup_progress = pyqtSignal(str, int, int)
    backup_finished = pyqtSignal(object)  # BackupResult
    state_changed = pyqtSignal()  # Emitted when paused/resumed/config refreshed

    def __init__(self, config: ConfigManager, logger: BackupLogger):
        super().__init__()
        self.config = config
        self.logger = logger
        self.engine = BackupEngine(config, logger)

        self._active_worker: Optional[BackupWorkerThread] = None
        self._next_backup_timestamp: Optional[float] = None
        self._last_backup_timestamp: float = 0.0

        # Read last backup time from config if available
        last_str = self.config.get("last_backup_time")
        if last_str:
            try:
                dt = datetime.strptime(last_str, "%Y-%m-%d %H:%M:%S")
                self._last_backup_timestamp = dt.timestamp()
            except Exception:
                pass

        self._calculate_next_backup_time()

    @property
    def seconds_until_next_backup(self) -> int:
        """Returns the number of seconds remaining until the next scheduled backup."""
        if self._next_backup_timestamp is None:
            self._calculate_next_backup_time()
        if self._next_backup_timestamp is None:
            return 0
        diff = int(self._next_backup_timestamp - time.time())
        return max(0, diff)

    def trigger_manual_backup(self) -> bool:
        """Alias for trigger_backup for manual user interactions."""
        return self.trigger_backup()

    def is_backing_up(self) -> bool:
        return self._active_worker is not None and self._active_worker.isRunning()

    def _calculate_next_backup_time(self, force_full_interval: bool = False):
        """Calculates the epoch timestamp of the next upcoming scheduled backup."""
        now = time.time()
        interval_secs = self.config.interval_minutes * 60

        if force_full_interval:
            self._next_backup_timestamp = now + interval_secs
        elif self._last_backup_timestamp == 0:
            # Never backed up before: due immediately once configured
            self._next_backup_timestamp = now
        else:
            elapsed = now - self._last_backup_timestamp
            if elapsed >= interval_secs:
                self._next_backup_timestamp = now  # Due immediately (catch-up)
            else:
                self._next_backup_timestamp = self._last_backup_timestamp + interval_secs

    def tick(self):
        """Called every second by the UI master timer."""
        if self.is_backing_up():
            self.status_changed.emit("Backing up data in progress...")
            return

        if self.config.is_paused:
            self.status_changed.emit("Backup scheduler is paused.")
            self.countdown_changed.emit(-1, "Paused")
            return

        if not self.config.is_configured():
            self.status_changed.emit("Configuration required: select Source & Destination.")
            self.countdown_changed.emit(-1, "Not Configured")
            return

        # Check working hours
        now_dt = datetime.now()
        is_working_hour = self.config.is_within_working_hours(now_dt)

        if not is_working_hour:
            reason = self._get_outside_hours_message(now_dt)
            self.status_changed.emit(f"Standby: {reason}")
            self.countdown_changed.emit(-1, "Outside Hours")
            return

        # We are inside working hours
        now_ts = time.time()
        if self._next_backup_timestamp is None:
            self._calculate_next_backup_time()

        seconds_left = int(self._next_backup_timestamp - now_ts)

        if seconds_left <= 0:
            # Trigger automatic scheduled backup!
            self.logger.info("Hourly backup triggered by schedule.")
            self.trigger_backup()
        else:
            mins, secs = divmod(seconds_left, 60)
            hours, mins = divmod(mins, 60)
            if hours > 0:
                time_str = f"{hours}h {mins:02d}m {secs:02d}s"
            else:
                time_str = f"{mins:02d}m {secs:02d}s"

            self.status_changed.emit(f"Active - Next scheduled backup in {time_str}")
            self.countdown_changed.emit(seconds_left, time_str)

    def _get_outside_hours_message(self, now_dt: datetime) -> str:
        """Helper to explain why backup is currently idle."""
        if now_dt.weekday() not in self.config.active_days:
            day_name = now_dt.strftime("%A")
            return f"{day_name} is marked as a non-working day."
        st = format_time_12h(self.config.get('start_time', '09:00'))
        et = format_time_12h(self.config.get('end_time', '21:00'))
        return f"Outside business hours ({st} to {et})"

    def trigger_backup(self) -> bool:
        """Initiates an immediate backup (either manually or by schedule)."""
        if self.is_backing_up():
            return False

        if not self.config.is_configured():
            self.status_changed.emit("Cannot backup: Please configure source and destination folders.")
            return False

        self.backup_started.emit()
        self.status_changed.emit("Starting backup...")

        self._active_worker = BackupWorkerThread(self.engine)
        self._active_worker.progress_changed.connect(self.backup_progress.emit)
        self._active_worker.finished_result.connect(self._on_backup_finished)
        self._active_worker.start()
        return True

    def _on_backup_finished(self, result: BackupResult):
        self._active_worker = None
        self._last_backup_timestamp = time.time()
        self._calculate_next_backup_time(force_full_interval=True)

        if result.success:
            now = datetime.now()
            h_12 = now.hour % 12 or 12
            time_str = f"{h_12}:{now.strftime('%M:%S %p')}"
            self.status_changed.emit(f"Last backup succeeded at {time_str}")
            if self.config.get("sound_alerts", True):
                SoundAlerts.play_success()
        else:
            self.status_changed.emit(f"Backup failed: {result.error_message}")
            if self.config.get("sound_alerts", True):
                SoundAlerts.play_failure()

        self.backup_finished.emit(result)

    def pause(self):
        self.config.is_paused = True
        self.state_changed.emit()

    def resume(self):
        self.config.is_paused = False
        self._calculate_next_backup_time()
        self.state_changed.emit()

    def reload_config(self):
        self.config.load()
        self._calculate_next_backup_time()
        self.state_changed.emit()
