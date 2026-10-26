import os
import re
import shutil
import time
import zipfile
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from autobackup.config import ConfigManager
from autobackup.logger import BackupLogger


@dataclass
class BackupResult:
    success: bool
    archive_path: str = ""
    archive_name: str = ""
    file_count: int = 0
    size_bytes: int = 0
    duration_seconds: float = 0.0
    error_message: str = ""
    purged_count: int = 0
    skipped_files: List[str] = None

    def __post_init__(self):
        if self.skipped_files is None:
            self.skipped_files = []


class BackupEngine:
    """Core backup processing engine with atomic ZIP compression and retention management."""

    def __init__(self, config_manager: ConfigManager, logger: BackupLogger):
        self.config = config_manager
        self.logger = logger

    def check_destination_health(self, dest_path: str) -> Tuple[bool, str, int]:
        """
        Validates destination drive existence, write permissions, and disk space.
        Returns (is_healthy, error_reason, free_bytes).
        """
        dest = Path(dest_path)
        try:
            # Check if directory exists or can be created
            if not dest.exists():
                dest.mkdir(parents=True, exist_ok=True)

            # Check write permission with a test file
            test_file = dest / f".write_test_{int(time.time())}.tmp"
            test_file.touch()
            test_file.unlink()

            # Check free disk space
            total, used, free = shutil.disk_usage(dest)
            min_free_bytes = self.config.get("min_free_space_mb", 500) * 1024 * 1024

            if free < min_free_bytes:
                return (
                    False,
                    f"Insufficient disk space! Only {free // (1024 * 1024)} MB available, "
                    f"minimum {min_free_bytes // (1024 * 1024)} MB required.",
                    free,
                )

            return True, "", free

        except FileNotFoundError:
            return False, f"Destination drive or path is disconnected or does not exist: {dest_path}", 0
        except PermissionError:
            return False, f"Permission denied writing to destination: {dest_path}", 0
        except OSError as e:
            return False, f"Destination storage error: {str(e)}", 0

    def execute_backup(
        self,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
        cancel_requested: Optional[Callable[[], bool]] = None,
    ) -> BackupResult:
        """
        Performs a full safe backup of the configured source directory to destination.
        """
        start_time = time.time()
        source_dir = self.config.source_folder
        dest_dir = self.config.destination_folder
        prefix = self.config.get("backup_prefix", "BillingBackup")

        if not source_dir or not os.path.isdir(source_dir):
            err = f"Source billing directory is invalid or missing: '{source_dir}'"
            self.logger.error(err)
            self.logger.add_history_entry(
                status="FAILED",
                archive_name="",
                source_path=source_dir,
                dest_path=dest_dir,
                file_count=0,
                size_bytes=0,
                duration_seconds=0,
                error_message=err,
            )
            return BackupResult(success=False, error_message=err)

        # Health & Space check
        healthy, reason, _ = self.check_destination_health(dest_dir)
        if not healthy:
            self.logger.error(f"Backup aborted: {reason}")
            self.logger.add_history_entry(
                status="FAILED",
                archive_name="",
                source_path=source_dir,
                dest_path=dest_dir,
                file_count=0,
                size_bytes=0,
                duration_seconds=0,
                error_message=reason,
            )
            return BackupResult(success=False, error_message=reason)

        # Build archive filenames
        timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        archive_name = f"{prefix}_{timestamp_str}.zip"
        dest_path = Path(dest_dir)
        final_archive_path = dest_path / archive_name
        temp_archive_path = dest_path / f"{archive_name}.tmp"

        self.logger.info(f"Initiating backup: '{source_dir}' -> '{final_archive_path}'")

        file_list: List[Tuple[Path, str]] = []
        source_path_obj = Path(source_dir)

        # Collect files to compress
        for root, dirs, files in os.walk(source_path_obj):
            for file in files:
                # Skip temporary office lock files and hidden tmp files
                if file.startswith("~$") or file.endswith(".tmp"):
                    continue
                full_path = Path(root) / file
                rel_path = full_path.relative_to(source_path_obj).as_posix()
                file_list.append((full_path, rel_path))

        total_files = len(file_list)
        if total_files == 0:
            self.logger.warning("Source directory is empty, creating empty archive.")

        # Create ZIP atomically
        processed_files = 0
        skipped_files: List[str] = []

        try:
            with zipfile.ZipFile(
                temp_archive_path,
                mode="w",
                compression=zipfile.ZIP_DEFLATED,
                compresslevel=6,
                allowZip64=True,
            ) as zf:
                for full_path, arcname in file_list:
                    if cancel_requested and cancel_requested():
                        raise InterruptedError("Backup operation was cancelled by user.")

                    try:
                        zf.write(full_path, arcname)
                    except (PermissionError, OSError) as e:
                        # File might be locked by billing software, log and proceed
                        self.logger.warning(f"Could not read file (locked or access denied): {arcname} ({e})")
                        skipped_files.append(arcname)

                    processed_files += 1
                    if progress_callback:
                        progress_callback(arcname, processed_files, total_files)

            # Integrity Verification
            self.logger.info("Verifying ZIP integrity...")
            with zipfile.ZipFile(temp_archive_path, mode="r") as zf:
                bad_file = zf.testzip()
                if bad_file:
                    raise zipfile.BadZipFile(f"Integrity check failed: corrupted file '{bad_file}' inside archive")

            # Atomic Rename from .tmp to final .zip
            if final_archive_path.exists():
                final_archive_path.unlink()
            temp_archive_path.rename(final_archive_path)

            duration = time.time() - start_time
            size_bytes = final_archive_path.stat().st_size

            self.logger.info(
                f"Backup successful: {archive_name} ({BackupLogger.format_bytes(size_bytes)}, "
                f"{processed_files - len(skipped_files)} files, {duration:.2f}s)"
            )

            # Run retention cleanup
            purged = self.clean_old_backups(dest_dir, prefix)

            # Record in history
            self.logger.add_history_entry(
                status="SUCCESS",
                archive_name=archive_name,
                source_path=source_dir,
                dest_path=dest_dir,
                file_count=processed_files - len(skipped_files),
                size_bytes=size_bytes,
                duration_seconds=duration,
                error_message=f"Skipped {len(skipped_files)} locked files" if skipped_files else "",
                purged_count=purged,
            )

            # Update last backup in config
            self.config.set("last_backup_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            return BackupResult(
                success=True,
                archive_path=str(final_archive_path),
                archive_name=archive_name,
                file_count=processed_files - len(skipped_files),
                size_bytes=size_bytes,
                duration_seconds=duration,
                purged_count=purged,
                skipped_files=skipped_files,
            )

        except Exception as e:
            # Clean up temp file
            if temp_archive_path.exists():
                try:
                    temp_archive_path.unlink()
                except Exception:
                    pass

            duration = time.time() - start_time
            err_msg = str(e)
            self.logger.error(f"Backup failed: {err_msg}")
            self.logger.add_history_entry(
                status="FAILED",
                archive_name=archive_name,
                source_path=source_dir,
                dest_path=dest_dir,
                file_count=processed_files,
                size_bytes=0,
                duration_seconds=duration,
                error_message=err_msg,
            )
            return BackupResult(
                success=False,
                archive_name=archive_name,
                duration_seconds=duration,
                error_message=err_msg,
            )

    def clean_old_backups(self, dest_dir: str, prefix: str) -> int:
        """
        Removes backups older than the retention period specified in config.
        """
        retention_days = self.config.retention_days
        if retention_days <= 0:
            return 0  # 0 means keep indefinitely

        cutoff_date = datetime.now() - timedelta(days=retention_days)
        purged = 0
        dest_path = Path(dest_dir)

        pattern = re.compile(rf"^{re.escape(prefix)}_(\d{{4}}-\d{{2}}-\d{{2}}_\d{{2}}-\d{{2}}-\d{{2}})\.zip$")

        try:
            for item in dest_path.iterdir():
                if item.is_file():
                    match = pattern.match(item.name)
                    if match:
                        try:
                            file_time = datetime.strptime(match.group(1), "%Y-%m-%d_%H-%M-%S")
                            if file_time < cutoff_date:
                                item.unlink()
                                purged += 1
                                self.logger.info(f"Purged expired backup: {item.name}")
                        except Exception as parse_err:
                            # Fallback to file modification time if filename format differs
                            mtime = datetime.fromtimestamp(item.stat().st_mtime)
                            if mtime < cutoff_date:
                                item.unlink()
                                purged += 1
                                self.logger.info(f"Purged expired backup by mtime: {item.name}")
        except Exception as e:
            self.logger.warning(f"Error during retention cleanup: {e}")

        return purged
