import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List

from PyQt6.QtCore import Qt, QTime, QTimer
from PyQt6.QtGui import QCloseEvent, QMouseEvent
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QStackedLayout,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from autobackup import autostart
from autobackup.backup_engine import BackupResult
from autobackup.config import ConfigManager
from autobackup.logger import BackupLogger
from autobackup.scheduler import BackupScheduler
from ui.icons import (
    create_app_icon,
    get_drive_icon,
    get_folder_icon,
    get_gear_icon,
    get_pause_icon,
    get_play_icon,
    get_sync_icon,
)
from ui.tray_icon import SystemTrayManager


class MainWindow(QMainWindow):
    """Spacious, lavish desktop interface with in-window popup settings for Shop AutoBackup Pro."""

    def __init__(
        self,
        config_manager: ConfigManager,
        logger: BackupLogger,
        scheduler: BackupScheduler,
        tray_manager: SystemTrayManager,
    ):
        super().__init__()
        self.config = config_manager
        self.logger = logger
        self.scheduler = scheduler
        self.tray = tray_manager

        self.setWindowTitle("Shop AutoBackup Pro")
        self.setWindowIcon(create_app_icon(32))
        self.setMinimumSize(860, 580)
        self.resize(920, 620)
        self._center_on_screen()

        self._first_minimize_notified = False

        self._init_ui()
        self._connect_signals()
        self._refresh_state()

        # Master 1-second timer
        self.master_timer = QTimer(self)
        self.master_timer.timeout.connect(self._on_tick)
        self.master_timer.start(1000)

    def _center_on_screen(self):
        screen = self.screen() or QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.move((geo.width() - self.width()) // 2, (geo.height() - self.height()) // 2)

    def _init_ui(self):
        root_container = QWidget(self)
        self.setCentralWidget(root_container)

        # Use stacked layout so the settings popup overlays seamlessly inside the same window
        self.root_stack = QStackedLayout(root_container)
        self.root_stack.setStackingMode(QStackedLayout.StackingMode.StackAll)

        # ================= LAYER 0: MAIN DASHBOARD =================
        self.dashboard_widget = QWidget()
        dash_layout = QVBoxLayout(self.dashboard_widget)
        dash_layout.setContentsMargins(36, 28, 36, 28)
        dash_layout.setSpacing(22)

        # --- 1. HEADER ---
        header = QHBoxLayout()
        header.setSpacing(12)

        app_icon_lbl = QLabel()
        app_icon_lbl.setPixmap(create_app_icon(32).pixmap(32, 32))
        header.addWidget(app_icon_lbl)

        title_lbl = QLabel("Shop AutoBackup Pro")
        title_lbl.setProperty("role", "app_title")
        header.addWidget(title_lbl)

        header.addStretch()

        self.status_pill = QLabel("● INITIALIZING")
        self.status_pill.setProperty("pill", "neutral")
        self.status_pill.setMinimumWidth(120)
        header.addWidget(self.status_pill)

        self.btn_pause = QPushButton()
        self.btn_pause.setProperty("role", "icon")
        self.btn_pause.setIcon(get_pause_icon(16))
        self.btn_pause.setToolTip("Pause / Resume scheduled backups")
        self.btn_pause.clicked.connect(self._toggle_pause)
        header.addWidget(self.btn_pause)

        self.btn_settings = QPushButton()
        self.btn_settings.setProperty("role", "icon")
        self.btn_settings.setIcon(get_gear_icon(16))
        self.btn_settings.setToolTip("Open in-window schedule & retention settings")
        self.btn_settings.clicked.connect(self._open_inwindow_settings)
        header.addWidget(self.btn_settings)

        dash_layout.addLayout(header)

        # --- 2. HERO STATUS CARD ---
        self.hero_card = QFrame()
        self.hero_card.setProperty("card", "hero")
        hero_layout = QVBoxLayout(self.hero_card)
        hero_layout.setContentsMargins(26, 22, 26, 22)
        hero_layout.setSpacing(12)

        hero_top = QHBoxLayout()
        v_hero_text = QVBoxLayout()
        v_hero_text.setSpacing(4)

        self.lbl_hero_title = QLabel("Checking schedule...")
        self.lbl_hero_title.setProperty("role", "hero_title")
        self.lbl_hero_title.setWordWrap(True)

        self.lbl_hero_sub = QLabel("Automated hourly backup protecting billing data")
        self.lbl_hero_sub.setProperty("role", "hero_subtitle")
        self.lbl_hero_sub.setWordWrap(True)

        v_hero_text.addWidget(self.lbl_hero_title)
        v_hero_text.addWidget(self.lbl_hero_sub)
        hero_top.addLayout(v_hero_text)
        hero_top.addStretch()

        self.btn_backup = QPushButton("  Backup Now")
        self.btn_backup.setProperty("role", "primary")
        self.btn_backup.setIcon(get_sync_icon(16))
        self.btn_backup.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_backup.clicked.connect(self._trigger_backup)
        hero_top.addWidget(self.btn_backup)

        hero_layout.addLayout(hero_top)

        # In-Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        hero_layout.addWidget(self.progress_bar)

        self.lbl_progress_file = QLabel("")
        self.lbl_progress_file.setProperty("role", "hero_subtitle")
        self.lbl_progress_file.setStyleSheet("font-size: 12px;")
        self.lbl_progress_file.setVisible(False)
        hero_layout.addWidget(self.lbl_progress_file)

        dash_layout.addWidget(self.hero_card)

        # --- 3. FOLDERS CARD ---
        folders_card = QFrame()
        folders_card.setProperty("card", "surface")
        f_layout = QVBoxLayout(folders_card)
        f_layout.setContentsMargins(26, 22, 26, 22)
        f_layout.setSpacing(18)

        # Row 1: Source
        row_src = QHBoxLayout()
        row_src.setSpacing(16)

        icon_src = QLabel()
        icon_src.setPixmap(get_folder_icon(30).pixmap(30, 30))
        row_src.addWidget(icon_src)

        v_src = QVBoxLayout()
        v_src.setSpacing(4)
        lbl_src_title = QLabel("SOURCE BILLING FOLDER")
        lbl_src_title.setProperty("role", "section_tag")
        self.lbl_src_path = QLabel("Select your billing data folder...")
        self.lbl_src_path.setProperty("role", "path_value")
        v_src.addWidget(lbl_src_title)
        v_src.addWidget(self.lbl_src_path)
        row_src.addLayout(v_src)
        row_src.addStretch()

        self.btn_src_browse = QPushButton("Select Folder...")
        self.btn_src_browse.clicked.connect(self._browse_source)
        row_src.addWidget(self.btn_src_browse)
        f_layout.addLayout(row_src)

        div = QFrame()
        div.setProperty("separator", "true")
        f_layout.addWidget(div)

        # Row 2: Destination
        row_dst = QHBoxLayout()
        row_dst.setSpacing(16)

        icon_dst = QLabel()
        icon_dst.setPixmap(get_drive_icon(30).pixmap(30, 30))
        row_dst.addWidget(icon_dst)

        v_dst = QVBoxLayout()
        v_dst.setSpacing(4)
        lbl_dst_title = QLabel("BACKUP TARGET DRIVE / FOLDER")
        lbl_dst_title.setProperty("role", "section_tag")

        h_dst_path = QHBoxLayout()
        h_dst_path.setSpacing(10)
        self.lbl_dst_path = QLabel("Select external or secondary drive...")
        self.lbl_dst_path.setProperty("role", "path_value")
        self.lbl_disk_free = QLabel("")
        self.lbl_disk_free.setProperty("pill", "neutral")
        self.lbl_disk_free.setVisible(False)
        h_dst_path.addWidget(self.lbl_dst_path)
        h_dst_path.addWidget(self.lbl_disk_free)
        h_dst_path.addStretch()

        v_dst.addWidget(lbl_dst_title)
        v_dst.addLayout(h_dst_path)
        row_dst.addLayout(v_dst)
        row_dst.addStretch()

        self.btn_dst_browse = QPushButton("Select Drive...")
        self.btn_dst_browse.clicked.connect(self._browse_destination)
        row_dst.addWidget(self.btn_dst_browse)
        f_layout.addLayout(row_dst)

        dash_layout.addWidget(folders_card)

        # --- 4. SCHEDULE PILLS BAR ---
        sched_bar = QHBoxLayout()
        sched_bar.setSpacing(10)

        self.pill_hours = QLabel("🕒 Hours: 09:00 AM – 09:00 PM")
        self.pill_hours.setProperty("pill", "neutral")

        self.pill_days = QLabel("📅 Days: Mon – Sat")
        self.pill_days.setProperty("pill", "neutral")

        self.pill_retention = QLabel("🗄️ Retain 30 Days")
        self.pill_retention.setProperty("pill", "neutral")

        btn_edit_sched = QPushButton("⚙ Customize Schedule...")
        btn_edit_sched.setProperty("role", "ghost")
        btn_edit_sched.clicked.connect(self._open_inwindow_settings)

        sched_bar.addWidget(self.pill_hours)
        sched_bar.addWidget(self.pill_days)
        sched_bar.addWidget(self.pill_retention)
        sched_bar.addStretch()
        sched_bar.addWidget(btn_edit_sched)

        dash_layout.addLayout(sched_bar)

        dash_layout.addStretch()

        # --- 5. FOOTER ---
        footer = QHBoxLayout()
        footer.setSpacing(10)

        self.lbl_footer_status = QLabel("No backups recorded yet")
        self.lbl_footer_status.setProperty("role", "muted")
        footer.addWidget(self.lbl_footer_status)

        footer.addStretch()

        self.btn_open_folder = QPushButton("📂 Open Backup Folder")
        self.btn_open_folder.setProperty("role", "ghost")
        self.btn_open_folder.clicked.connect(self._open_backup_directory)
        footer.addWidget(self.btn_open_folder)

        dash_layout.addLayout(footer)

        self.root_stack.addWidget(self.dashboard_widget)

        # ================= LAYER 1: IN-WINDOW SETTINGS POPUP =================
        self._init_inwindow_settings_overlay()

    def _init_inwindow_settings_overlay(self):
        """Builds the in-window modal popup overlay."""
        self.overlay_widget = QWidget()
        self.overlay_widget.setProperty("role", "scrim")
        overlay_layout = QVBoxLayout(self.overlay_widget)
        overlay_layout.setContentsMargins(0, 0, 0, 0)
        overlay_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Centered Modal Card
        self.modal_card = QFrame()
        self.modal_card.setProperty("card", "modal")
        self.modal_card.setFixedSize(560, 520)
        m_layout = QVBoxLayout(self.modal_card)
        m_layout.setContentsMargins(32, 26, 32, 26)
        m_layout.setSpacing(16)

        # Modal Header
        m_header = QHBoxLayout()
        v_m_title = QVBoxLayout()
        v_m_title.setSpacing(2)

        m_title = QLabel("Backup Schedule & Rules")
        m_title.setProperty("role", "hero_title")
        m_sub = QLabel("Configure shop operating hours, frequency, and retention.")
        m_sub.setProperty("role", "hero_subtitle")
        v_m_title.addWidget(m_title)
        v_m_title.addWidget(m_sub)
        m_header.addLayout(v_m_title)
        m_header.addStretch()

        btn_close_modal = QPushButton("✕")
        btn_close_modal.setProperty("role", "ghost")
        btn_close_modal.setStyleSheet("font-size: 16px; font-weight: 700; color: #713600; padding: 2px;")
        btn_close_modal.setFixedSize(32, 32)
        btn_close_modal.clicked.connect(self._close_inwindow_settings)
        m_header.addWidget(btn_close_modal)
        m_layout.addLayout(m_header)

        # Form Grid
        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(12)

        lbl_freq = QLabel("Frequency:")
        lbl_freq.setProperty("role", "section_tag")
        self.combo_interval = QComboBox()
        self.combo_interval.addItem("Every 15 Minutes", 15)
        self.combo_interval.addItem("Every 30 Minutes", 30)
        self.combo_interval.addItem("Every 1 Hour (Recommended)", 60)
        self.combo_interval.addItem("Every 2 Hours", 120)
        self.combo_interval.addItem("Every 4 Hours", 240)
        grid.addWidget(lbl_freq, 0, 0)
        grid.addWidget(self.combo_interval, 0, 1)

        lbl_open = QLabel("Shop Opens:")
        lbl_open.setProperty("role", "section_tag")
        self.time_start = QTimeEdit()
        self.time_start.setDisplayFormat("hh:mm AP")
        grid.addWidget(lbl_open, 1, 0)
        grid.addWidget(self.time_start, 1, 1)

        lbl_close = QLabel("Shop Closes:")
        lbl_close.setProperty("role", "section_tag")
        self.time_end = QTimeEdit()
        self.time_end.setDisplayFormat("hh:mm AP")
        grid.addWidget(lbl_close, 2, 0)
        grid.addWidget(self.time_end, 2, 1)

        lbl_ret = QLabel("Retention:")
        lbl_ret.setProperty("role", "section_tag")
        self.spin_retention = QSpinBox()
        self.spin_retention.setRange(0, 365)
        self.spin_retention.setSuffix(" days")
        self.spin_retention.setSpecialValueText("Keep Forever")
        grid.addWidget(lbl_ret, 3, 0)
        grid.addWidget(self.spin_retention, 3, 1)

        m_layout.addLayout(grid)

        # Active Days
        lbl_days = QLabel("ACTIVE WORKING DAYS:")
        lbl_days.setProperty("role", "section_tag")
        m_layout.addWidget(lbl_days)

        days_layout = QHBoxLayout()
        days_layout.setSpacing(8)
        self.day_cbs: List[QCheckBox] = []
        for name in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
            cb = QCheckBox(name)
            self.day_cbs.append(cb)
            days_layout.addWidget(cb)
        m_layout.addLayout(days_layout)

        div_m = QFrame()
        div_m.setProperty("separator", "true")
        m_layout.addWidget(div_m)

        # Toggles
        self.cb_sound = QCheckBox("Audible chime on success / warning on failure")
        self.cb_notify = QCheckBox("Windows desktop notifications")
        self.cb_startup = QCheckBox("Start automatically on Windows boot (System Tray)")

        m_layout.addWidget(self.cb_sound)
        m_layout.addWidget(self.cb_notify)
        m_layout.addWidget(self.cb_startup)

        m_layout.addStretch()

        # Modal Bottom Buttons
        m_btns = QHBoxLayout()
        m_btns.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self._close_inwindow_settings)

        btn_save = QPushButton("Save Settings")
        btn_save.setProperty("role", "primary")
        btn_save.clicked.connect(self._save_inwindow_settings)

        m_btns.addWidget(btn_cancel)
        m_btns.addWidget(btn_save)
        m_layout.addLayout(m_btns)

        overlay_layout.addWidget(self.modal_card)
        self.root_stack.addWidget(self.overlay_widget)

        # Initially hidden
        self.overlay_widget.setVisible(False)

    def _open_inwindow_settings(self):
        """Opens the settings modal popup inside the same window."""
        self._load_settings_values()
        self.overlay_widget.setVisible(True)
        self.overlay_widget.raise_()

    def _close_inwindow_settings(self):
        """Closes the in-window settings popup."""
        self.overlay_widget.setVisible(False)

    def _load_settings_values(self):
        interval = self.config.interval_minutes
        idx = self.combo_interval.findData(interval)
        if idx >= 0:
            self.combo_interval.setCurrentIndex(idx)

        st = self.config.get("start_time", "09:00").split(":")
        self.time_start.setTime(QTime(int(st[0]), int(st[1])))

        et = self.config.get("end_time", "21:00").split(":")
        self.time_end.setTime(QTime(int(et[0]), int(et[1])))

        active_days = self.config.active_days
        for i, cb in enumerate(self.day_cbs):
            cb.setChecked(i in active_days)

        self.spin_retention.setValue(self.config.retention_days)
        self.cb_sound.setChecked(self.config.get("sound_alerts", True))
        self.cb_notify.setChecked(self.config.get("desktop_notifications", True))
        self.cb_startup.setChecked(autostart.is_autostart_enabled())

    def _save_inwindow_settings(self):
        selected_days = [i for i, cb in enumerate(self.day_cbs) if cb.isChecked()]
        if not selected_days:
            selected_days = [0, 1, 2, 3, 4, 5]

        self.config.update(
            {
                "interval_minutes": self.combo_interval.currentData(),
                "start_time": self.time_start.time().toString("HH:mm"),
                "end_time": self.time_end.time().toString("HH:mm"),
                "active_days": selected_days,
                "retention_days": self.spin_retention.value(),
                "sound_alerts": self.cb_sound.isChecked(),
                "desktop_notifications": self.cb_notify.isChecked(),
                "run_on_startup": self.cb_startup.isChecked(),
            }
        )
        autostart.set_autostart(self.cb_startup.isChecked())
        self.scheduler.reload_config()
        self._refresh_state()
        self._close_inwindow_settings()

    def _connect_signals(self):
        self.scheduler.countdown_changed.connect(self._on_countdown_changed)
        self.scheduler.backup_started.connect(self._on_backup_started)
        self.scheduler.backup_progress.connect(self._on_backup_progress)
        self.scheduler.backup_finished.connect(self._on_backup_finished)
        self.scheduler.state_changed.connect(self._refresh_state)

        self.tray.open_requested.connect(self._show_window)
        self.tray.backup_now_requested.connect(self._trigger_backup)
        self.tray.settings_requested.connect(self._open_inwindow_settings)
        self.tray.exit_requested.connect(self._clean_exit)

    def _on_tick(self):
        self.scheduler.tick()

    def _on_countdown_changed(self, seconds_left: int, readable: str):
        if self.scheduler.is_backing_up():
            self._set_status_pill("active", "● BACKING UP")
            self.lbl_hero_title.setText("Backing up billing files...")
            return

        if self.config.is_paused:
            self._set_status_pill("paused", "● PAUSED")
            self.lbl_hero_title.setText("AutoBackup is Paused")
            self.lbl_hero_sub.setText("Scheduled runs are temporarily suspended")
            return

        if not self.config.is_configured():
            self._set_status_pill("error", "● SETUP NEEDED")
            self.lbl_hero_title.setText("Setup Needed")
            self.lbl_hero_sub.setText("Please select your billing folder and backup destination drive below.")
            return

        now_dt = datetime.now()
        if not self.config.is_within_working_hours(now_dt):
            self._set_status_pill("neutral", "● STANDBY")
            self.lbl_hero_title.setText("Standby (Outside Shop Hours)")
            st = self.config.get("start_time", "09:00")
            et = self.config.get("end_time", "21:00")
            self.lbl_hero_sub.setText(f"Scheduled to resume during working hours ({st} – {et})")
            return

        self._set_status_pill("active", "● ACTIVE")
        self.lbl_hero_title.setText(f"Next Backup in {readable}")
        freq = self.config.interval_minutes
        self.lbl_hero_sub.setText(f"Archiving automatically every {freq} minutes during working hours")

    def _set_status_pill(self, pill_type: str, text: str):
        self.status_pill.setProperty("pill", pill_type)
        self.status_pill.setText(text)
        self.status_pill.style().unpolish(self.status_pill)
        self.status_pill.style().polish(self.status_pill)
        self.status_pill.adjustSize()

    def _on_backup_started(self):
        self.btn_backup.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.lbl_progress_file.setVisible(True)
        self.lbl_progress_file.setText("Preparing and indexing files...")
        self.tray.update_state("working", "Backing up billing files...")

    def _on_backup_progress(self, file_name: str, current: int, total: int):
        if total > 0:
            pct = int((current / total) * 100)
            self.progress_bar.setValue(pct)
            self.lbl_progress_file.setText(f"Archiving: {Path(file_name).name} ({current}/{total} files)")

    def _on_backup_finished(self, result: BackupResult):
        self.btn_backup.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.lbl_progress_file.setVisible(False)

        if result.success:
            self.tray.update_state("active", "Backup completed successfully")
            self.tray.notify(
                "Billing Backup Succeeded",
                f"{result.file_count} files archived ({BackupLogger.format_bytes(result.size_bytes)})",
            )
        else:
            self.tray.update_state("error", result.error_message)
            self.tray.notify("Backup FAILED!", result.error_message, is_error=True)

        self._refresh_state()

    def _refresh_state(self):
        src = self.config.source_folder
        dst = self.config.destination_folder

        if src:
            self.lbl_src_path.setText(src)
            self.lbl_src_path.setStyleSheet("color: #38240D;")
        else:
            self.lbl_src_path.setText("Select your billing data folder...")
            self.lbl_src_path.setStyleSheet("color: rgba(56, 36, 13, 0.5);")

        if dst:
            self.lbl_dst_path.setText(dst)
            self.lbl_dst_path.setStyleSheet("color: #38240D;")
            if os.path.exists(dst):
                try:
                    total, used, free = shutil.disk_usage(dst)
                    drive_letter = Path(dst).drive or dst
                    self.lbl_disk_free.setText(f"{drive_letter} • {BackupLogger.format_bytes(free)} free")
                    self.lbl_disk_free.setVisible(True)
                except Exception:
                    self.lbl_disk_free.setVisible(False)
            else:
                self.lbl_disk_free.setText("Drive Disconnected")
                self.lbl_disk_free.setVisible(True)
        else:
            self.lbl_dst_path.setText("Select external or secondary drive...")
            self.lbl_dst_path.setStyleSheet("color: rgba(56, 36, 13, 0.5);")
            self.lbl_disk_free.setVisible(False)

        if self.config.is_paused:
            self.btn_pause.setIcon(get_play_icon(16))
            self.btn_pause.setToolTip("Resume automated backups")
        else:
            self.btn_pause.setIcon(get_pause_icon(16))
            self.btn_pause.setToolTip("Pause automated backups")

        st = self.config.get("start_time", "09:00")
        et = self.config.get("end_time", "21:00")
        self.pill_hours.setText(f"🕒 Hours: {st} – {et}")

        day_map = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}
        active_days = self.config.active_days
        if len(active_days) == 7:
            days_str = "Every Day"
        elif active_days == [0, 1, 2, 3, 4, 5]:
            days_str = "Mon – Sat"
        else:
            days_str = ", ".join([day_map.get(d, "") for d in sorted(active_days)])
        self.pill_days.setText(f"📅 Days: {days_str}")

        ret_days = self.config.retention_days
        self.pill_retention.setText(f"🗄️ Retain {ret_days} Days" if ret_days > 0 else "🗄️ Keep Forever")

        stats = self.logger.get_stats()
        last_time = stats["last_backup_time"]
        if last_time != "Never":
            status_text = "✓ Success" if stats["last_backup_status"] == "SUCCESS" else "✕ Failed"
            self.lbl_footer_status.setText(
                f"Last Backup: {last_time} ({stats['last_backup_size']}) • {status_text}"
            )
        else:
            self.lbl_footer_status.setText("No backups recorded yet")

    def _browse_source(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Billing Folder", self.config.source_folder)
        if folder:
            path = os.path.normpath(folder)
            self.config.set("source_folder", path)
            self.scheduler.reload_config()
            self._refresh_state()

    def _browse_destination(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Backup Target Drive / Folder", self.config.destination_folder)
        if folder:
            path = os.path.normpath(folder)
            self.config.set("destination_folder", path)
            self.scheduler.reload_config()
            self._refresh_state()

    def _trigger_backup(self):
        if not self.config.is_configured():
            self._open_inwindow_settings()
            return
        self.scheduler.trigger_backup()

    def _toggle_pause(self):
        if self.config.is_paused:
            self.scheduler.resume()
        else:
            self.scheduler.pause()
        self._refresh_state()

    def _open_backup_directory(self):
        dst = self.config.destination_folder
        if dst and os.path.isdir(dst):
            os.startfile(dst)

    def _show_window(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def _clean_exit(self):
        self.master_timer.stop()
        self.tray.tray_icon.hide()
        self.close()

    def closeEvent(self, event: QCloseEvent):
        event.ignore()
        self.hide()
        if not self._first_minimize_notified:
            self.tray.notify(
                "Running in Background",
                "Shop AutoBackup Pro is protecting your data in the Windows System Tray.",
            )
            self._first_minimize_notified = True
