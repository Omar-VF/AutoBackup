import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from PyQt6.QtCore import Qt, QTime, QTimer, pyqtSignal
from PyQt6.QtGui import QCloseEvent, QMouseEvent
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
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
    DashedArrowWidget,
    create_app_icon,
    get_close_icon,
    get_drive_icon,
    get_folder_icon,
    get_gear_icon,
    get_pause_icon,
    get_play_icon,
    get_sync_icon,
)
from ui.toggle_switch import ToggleSwitch
from ui.tray_icon import SystemTrayManager


class ClickableFrame(QFrame):
    """QFrame that emits a clicked signal on mouse release."""
    clicked = pyqtSignal()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)


class MainWindow(QMainWindow):
    """
    Tethr desktop interface.
    Faithfully replicates design/Tethr Redesign.html & design/Tethr Redesign.pdf.
    """

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

        self.setWindowTitle("Tethr")
        self.setWindowIcon(create_app_icon(38))
        self.setMinimumSize(1040, 680)
        self.resize(1140, 720)
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

        self.root_stack = QStackedLayout(root_container)
        self.root_stack.setStackingMode(QStackedLayout.StackingMode.StackAll)

        # ================= LAYER 0: MAIN DASHBOARD =================
        self.dashboard_widget = QWidget()
        dash_layout = QVBoxLayout(self.dashboard_widget)
        dash_layout.setContentsMargins(32, 28, 32, 28)
        dash_layout.setSpacing(20)

        # --- 1. HEADER (44px) ---
        header = QHBoxLayout()
        header.setSpacing(10)

        app_icon_lbl = QLabel()
        app_icon_lbl.setPixmap(create_app_icon(38).pixmap(38, 38))
        header.addWidget(app_icon_lbl)

        title_lbl = QLabel("Tethr")
        title_lbl.setProperty("role", "app_title")
        header.addWidget(title_lbl)

        header.addStretch()

        self.btn_pause = QPushButton()
        self.btn_pause.setProperty("role", "header_btn")
        self.btn_pause.setIcon(get_pause_icon(16))
        self.btn_pause.setToolTip("Pause / Resume scheduled backups")
        self.btn_pause.clicked.connect(self._toggle_pause)
        header.addWidget(self.btn_pause)

        self.btn_settings = QPushButton()
        self.btn_settings.setProperty("role", "header_btn")
        self.btn_settings.setIcon(get_gear_icon(18))
        self.btn_settings.setToolTip("Edit backup schedule and preferences")
        self.btn_settings.clicked.connect(self._open_inwindow_settings)
        header.addWidget(self.btn_settings)

        dash_layout.addLayout(header)

        # --- 2. HERO CARD (#2E1A08) ---
        self.hero_card = QFrame()
        self.hero_card.setProperty("card", "hero")
        hero_layout = QHBoxLayout(self.hero_card)
        hero_layout.setContentsMargins(36, 32, 36, 32)
        hero_layout.setSpacing(32)

        # Left Column: Tag, Title, Subtitle
        v_hero_left = QVBoxLayout()
        v_hero_left.setSpacing(12)

        self.lbl_hero_tag = QLabel("SETUP NEEDED")
        self.lbl_hero_tag.setProperty("role", "hero_tag")
        v_hero_left.addWidget(self.lbl_hero_tag)

        self.lbl_hero_title = QLabel("Choose what to back up")
        self.lbl_hero_title.setProperty("role", "hero_title")
        self.lbl_hero_title.setWordWrap(True)
        v_hero_left.addWidget(self.lbl_hero_title)

        self.lbl_hero_sub = QLabel(
            "Choose the folder to protect and where Tethr should keep the copies. "
            "Backups then run on their own during your active hours."
        )
        self.lbl_hero_sub.setProperty("role", "hero_subtitle")
        self.lbl_hero_sub.setWordWrap(True)
        self.lbl_hero_sub.setMaximumWidth(600)
        v_hero_left.addWidget(self.lbl_hero_sub)

        hero_layout.addLayout(v_hero_left, stretch=1)

        # Right Column: Back up now Button & note
        v_hero_right = QVBoxLayout()
        v_hero_right.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        v_hero_right.setSpacing(10)

        self.btn_backup_now = QPushButton("  Back up now")
        self.btn_backup_now.setProperty("role", "hero_btn")
        self.btn_backup_now.setIcon(get_sync_icon(18, "#FFF8E6"))
        self.btn_backup_now.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_backup_now.clicked.connect(self._manual_backup)
        v_hero_right.addWidget(self.btn_backup_now, alignment=Qt.AlignmentFlag.AlignRight)

        self.lbl_hero_note = QLabel("Finish 2 steps to enable")
        self.lbl_hero_note.setProperty("role", "hero_note")
        v_hero_right.addWidget(self.lbl_hero_note, alignment=Qt.AlignmentFlag.AlignRight)

        hero_layout.addLayout(v_hero_right)
        dash_layout.addWidget(self.hero_card)

        # --- 3. SOURCE -> DESTINATION ROW ---
        source_dest_layout = QHBoxLayout()
        source_dest_layout.setSpacing(0)

        # Source Card
        self.source_card = QFrame()
        self.source_card.setProperty("card", "surface")
        v_src = QVBoxLayout(self.source_card)
        v_src.setContentsMargins(26, 26, 26, 26)
        v_src.setSpacing(16)

        src_top = QHBoxLayout()
        src_top.setSpacing(14)
        src_badge = QLabel()
        src_badge.setFixedSize(44, 44)
        src_badge.setStyleSheet("background-color: #E8DBA6; border-radius: 7px;")
        src_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        src_badge.setPixmap(get_folder_icon(22, "#8F4300").pixmap(22, 22))
        src_top.addWidget(src_badge)

        v_src_titles = QVBoxLayout()
        v_src_titles.setSpacing(3)
        lbl_src_tag = QLabel("1 · SOURCE")
        lbl_src_tag.setProperty("role", "card_tag")
        v_src_titles.addWidget(lbl_src_tag)
        lbl_src_title = QLabel("Folder to back up")
        lbl_src_title.setProperty("role", "card_title")
        v_src_titles.addWidget(lbl_src_title)
        src_top.addLayout(v_src_titles)
        src_top.addStretch()
        v_src.addLayout(src_top)

        self.lbl_source_path = QLabel("No folder selected yet")
        self.lbl_source_path.setProperty("role", "card_status")
        self.lbl_source_path.setWordWrap(True)
        v_src.addWidget(self.lbl_source_path, stretch=1)

        self.btn_choose_source = QPushButton("Choose folder")
        self.btn_choose_source.setProperty("role", "dark_btn")
        self.btn_choose_source.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_choose_source.clicked.connect(self._select_source_folder)
        v_src.addWidget(self.btn_choose_source, alignment=Qt.AlignmentFlag.AlignLeft)

        source_dest_layout.addWidget(self.source_card, stretch=1)

        # Dashed Arrow in Center Column
        arrow_container = QWidget()
        arrow_container.setFixedWidth(72)
        v_arrow = QVBoxLayout(arrow_container)
        v_arrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v_arrow.setContentsMargins(0, 0, 0, 0)
        v_arrow.addWidget(DashedArrowWidget())
        source_dest_layout.addWidget(arrow_container)

        # Destination Card
        self.dest_card = QFrame()
        self.dest_card.setProperty("card", "surface")
        v_dest = QVBoxLayout(self.dest_card)
        v_dest.setContentsMargins(26, 26, 26, 26)
        v_dest.setSpacing(16)

        dest_top = QHBoxLayout()
        dest_top.setSpacing(14)
        dest_badge = QLabel()
        dest_badge.setFixedSize(44, 44)
        dest_badge.setStyleSheet("background-color: #E8DBA6; border-radius: 7px;")
        dest_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dest_badge.setPixmap(get_drive_icon(22, "#8F4300").pixmap(22, 22))
        dest_top.addWidget(dest_badge)

        v_dest_titles = QVBoxLayout()
        v_dest_titles.setSpacing(3)
        lbl_dest_tag = QLabel("2 · DESTINATION")
        lbl_dest_tag.setProperty("role", "card_tag")
        v_dest_titles.addWidget(lbl_dest_tag)
        lbl_dest_title = QLabel("Backup drive")
        lbl_dest_title.setProperty("role", "card_title")
        v_dest_titles.addWidget(lbl_dest_title)
        dest_top.addLayout(v_dest_titles)
        dest_top.addStretch()
        v_dest.addLayout(dest_top)

        self.lbl_dest_path = QLabel("No drive selected yet")
        self.lbl_dest_path.setProperty("role", "card_status")
        self.lbl_dest_path.setWordWrap(True)
        v_dest.addWidget(self.lbl_dest_path, stretch=1)

        self.btn_choose_dest = QPushButton("Choose drive")
        self.btn_choose_dest.setProperty("role", "dark_btn")
        self.btn_choose_dest.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_choose_dest.clicked.connect(self._select_dest_folder)
        v_dest.addWidget(self.btn_choose_dest, alignment=Qt.AlignmentFlag.AlignLeft)

        source_dest_layout.addWidget(self.dest_card, stretch=1)
        dash_layout.addLayout(source_dest_layout)

        # --- 4. SCHEDULE SUMMARY ROW CARD ---
        self.summary_card = ClickableFrame()
        self.summary_card.setProperty("card", "surface")
        self.summary_card.setCursor(Qt.CursorShape.PointingHandCursor)
        self.summary_card.setToolTip("Click to customize schedule, hours, and retention")
        self.summary_card.clicked.connect(self._open_inwindow_settings)

        summary_layout = QHBoxLayout(self.summary_card)
        summary_layout.setContentsMargins(26, 24, 26, 24)
        summary_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        summary_layout.setSpacing(56)

        # Col 1: Hours
        col_hours = QVBoxLayout()
        col_hours.setSpacing(6)
        lbl_h_tag = QLabel("HOURS")
        lbl_h_tag.setProperty("role", "summary_tag")
        col_hours.addWidget(lbl_h_tag)
        self.lbl_sum_hours = QLabel("09:00 – 21:00")
        self.lbl_sum_hours.setProperty("role", "summary_val")
        col_hours.addWidget(self.lbl_sum_hours)
        summary_layout.addLayout(col_hours)

        # Col 2: Days
        col_days = QVBoxLayout()
        col_days.setSpacing(8)
        lbl_d_tag = QLabel("DAYS")
        lbl_d_tag.setProperty("role", "summary_tag")
        col_days.addWidget(lbl_d_tag)

        days_row = QHBoxLayout()
        days_row.setSpacing(4)
        day_letters = ["M", "T", "W", "T", "F", "S", "S"]
        self.day_pills: List[QLabel] = []
        for ch in day_letters:
            lbl_day = QLabel(ch)
            lbl_day.setProperty("role", "summary_day_on")
            days_row.addWidget(lbl_day)
            self.day_pills.append(lbl_day)
        col_days.addLayout(days_row)
        summary_layout.addLayout(col_days)

        # Col 3: Every
        col_every = QVBoxLayout()
        col_every.setSpacing(6)
        lbl_e_tag = QLabel("EVERY")
        lbl_e_tag.setProperty("role", "summary_tag")
        col_every.addWidget(lbl_e_tag)
        self.lbl_sum_every = QLabel("1 hour")
        self.lbl_sum_every.setProperty("role", "summary_val")
        col_every.addWidget(self.lbl_sum_every)
        summary_layout.addLayout(col_every)

        # Col 4: Keep
        col_keep = QVBoxLayout()
        col_keep.setSpacing(6)
        lbl_k_tag = QLabel("KEEP")
        lbl_k_tag.setProperty("role", "summary_tag")
        col_keep.addWidget(lbl_k_tag)
        self.lbl_sum_keep = QLabel("30 days")
        self.lbl_sum_keep.setProperty("role", "summary_val")
        col_keep.addWidget(self.lbl_sum_keep)
        summary_layout.addLayout(col_keep)

        dash_layout.addWidget(self.summary_card)

        # Push footer to bottom
        dash_layout.addStretch(1)

        # --- 5. FOOTER ---
        footer = QHBoxLayout()
        self.lbl_footer_status = QLabel("No backups recorded yet")
        self.lbl_footer_status.setProperty("role", "footer_text")
        footer.addWidget(self.lbl_footer_status)

        footer.addStretch()

        self.btn_open_folder = QPushButton("Open backup folder")
        self.btn_open_folder.setProperty("role", "link_btn")
        self.btn_open_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open_folder.clicked.connect(self._open_backup_directory)
        footer.addWidget(self.btn_open_folder)

        dash_layout.addLayout(footer)

        self.root_stack.addWidget(self.dashboard_widget)

        # ================= LAYER 1: IN-WINDOW MODAL SETTINGS =================
        self.overlay_widget = QWidget()
        self.overlay_widget.setProperty("role", "scrim")
        overlay_layout = QVBoxLayout(self.overlay_widget)
        overlay_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_layout.setContentsMargins(40, 24, 40, 24)

        # Modal Card Frame
        self.modal_card = QFrame()
        self.modal_card.setProperty("card", "modal")
        self.modal_card.setFixedWidth(570)
        self.modal_card.setMaximumHeight(680)

        modal_card_layout = QVBoxLayout(self.modal_card)
        modal_card_layout.setContentsMargins(32, 28, 32, 24)
        modal_card_layout.setSpacing(14)

        # Modal Header: Title, Subtitle, Close X
        modal_header = QHBoxLayout()
        v_mod_title = QVBoxLayout()
        v_mod_title.setSpacing(4)

        m_title = QLabel("Backup schedule")
        m_title.setProperty("role", "modal_title")
        v_mod_title.addWidget(m_title)

        m_sub = QLabel("Active hours, frequency and retention.")
        m_sub.setProperty("role", "modal_subtitle")
        v_mod_title.addWidget(m_sub)
        modal_header.addLayout(v_mod_title)
        modal_header.addStretch()

        btn_modal_x = QPushButton()
        btn_modal_x.setProperty("role", "close_btn")
        btn_modal_x.setIcon(get_close_icon(16))
        btn_modal_x.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_modal_x.clicked.connect(self._close_inwindow_settings)
        modal_header.addWidget(btn_modal_x, alignment=Qt.AlignmentFlag.AlignTop)

        modal_card_layout.addLayout(modal_header)

        # Scroll Area for Modal Content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_content = QWidget()
        form_layout = QVBoxLayout(scroll_content)
        form_layout.setContentsMargins(0, 2, 6, 2)
        form_layout.setSpacing(14)

        # 1. FREQUENCY SECTION
        row_freq = QHBoxLayout()
        row_freq.setSpacing(20)
        lbl_freq_sec = QLabel("FREQUENCY")
        lbl_freq_sec.setProperty("role", "section_label")
        lbl_freq_sec.setFixedWidth(96)
        row_freq.addWidget(lbl_freq_sec, alignment=Qt.AlignmentFlag.AlignTop)

        v_freq_content = QVBoxLayout()
        v_freq_content.setSpacing(6)

        grid_freq = QGridLayout()
        grid_freq.setSpacing(4)
        self.freq_options = [
            (5, "5 min"), (15, "15 min"), (30, "30 min"), (60, "1 hour"),
            (120, "2 hours"), (240, "4 hours"), (360, "6 hours"), (-1, "Custom")
        ]
        self.freq_buttons: List[QPushButton] = []
        for idx, (val, text) in enumerate(self.freq_options):
            b = QPushButton(text)
            b.setCheckable(True)
            b.setProperty("role", "chip")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda _, v=val: self._select_freq(v))
            grid_freq.addWidget(b, idx // 4, idx % 4)
            self.freq_buttons.append(b)
        v_freq_content.addLayout(grid_freq)

        # Custom Frequency Row
        self.custom_freq_container = QWidget()
        h_custom = QHBoxLayout(self.custom_freq_container)
        h_custom.setContentsMargins(0, 2, 0, 0)
        h_custom.setSpacing(8)
        lbl_every = QLabel("Every")
        lbl_every.setProperty("role", "input_label")
        h_custom.addWidget(lbl_every)

        self.spin_custom_val = QSpinBox()
        self.spin_custom_val.setRange(1, 1440)
        self.spin_custom_val.setValue(45)
        h_custom.addWidget(self.spin_custom_val, stretch=1)

        self.combo_custom_unit = QComboBox()
        self.combo_custom_unit.addItems(["minutes", "hours"])
        h_custom.addWidget(self.combo_custom_unit, stretch=1)
        v_freq_content.addWidget(self.custom_freq_container)

        lbl_freq_note = QLabel("1 hour is a good default for most folders.")
        lbl_freq_note.setProperty("role", "field_note")
        v_freq_content.addWidget(lbl_freq_note)
        row_freq.addLayout(v_freq_content)
        form_layout.addLayout(row_freq)

        # 2. HOURS SECTION
        row_hours = QHBoxLayout()
        row_hours.setSpacing(20)
        lbl_hours_sec = QLabel("HOURS")
        lbl_hours_sec.setProperty("role", "section_label")
        lbl_hours_sec.setFixedWidth(96)
        row_hours.addWidget(lbl_hours_sec, alignment=Qt.AlignmentFlag.AlignTop)

        v_hours_content = QHBoxLayout()
        v_hours_content.setSpacing(8)

        v_opens = QVBoxLayout()
        v_opens.setSpacing(4)
        lbl_opens = QLabel("Opens")
        lbl_opens.setProperty("role", "input_label")
        v_opens.addWidget(lbl_opens)
        self.time_opens = QTimeEdit()
        self.time_opens.setDisplayFormat("hh:mm AP")
        self.time_opens.setTime(QTime(9, 0))
        v_opens.addWidget(self.time_opens)
        v_hours_content.addLayout(v_opens)

        v_closes = QVBoxLayout()
        v_closes.setSpacing(4)
        lbl_closes = QLabel("Closes")
        lbl_closes.setProperty("role", "input_label")
        v_closes.addWidget(lbl_closes)
        self.time_closes = QTimeEdit()
        self.time_closes.setDisplayFormat("hh:mm AP")
        self.time_closes.setTime(QTime(21, 0))
        v_closes.addWidget(self.time_closes)
        v_hours_content.addLayout(v_closes)

        row_hours.addLayout(v_hours_content)
        form_layout.addLayout(row_hours)

        # 3. DAYS SECTION
        row_days = QHBoxLayout()
        row_days.setSpacing(20)
        lbl_days_sec = QLabel("DAYS")
        lbl_days_sec.setProperty("role", "section_label")
        lbl_days_sec.setFixedWidth(96)
        row_days.addWidget(lbl_days_sec)

        grid_days = QHBoxLayout()
        grid_days.setSpacing(4)
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        self.day_buttons: List[QPushButton] = []
        for i, name in enumerate(day_names):
            b = QPushButton(name)
            b.setCheckable(True)
            b.setProperty("role", "day_chip")
            b.setChecked(i < 6)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda _, d_idx=i: self._toggle_day_button(d_idx))
            grid_days.addWidget(b)
            self.day_buttons.append(b)
        row_days.addLayout(grid_days)
        form_layout.addLayout(row_days)

        # 4. DELETE AFTER SECTION
        row_retention = QHBoxLayout()
        row_retention.setSpacing(20)
        lbl_ret_sec = QLabel("DELETE AFTER")
        lbl_ret_sec.setProperty("role", "section_label")
        lbl_ret_sec.setFixedWidth(96)
        row_retention.addWidget(lbl_ret_sec, alignment=Qt.AlignmentFlag.AlignTop)

        v_ret_content = QVBoxLayout()
        v_ret_content.setSpacing(6)

        grid_ret = QGridLayout()
        grid_ret.setSpacing(4)
        self.ret_options = [
            (7, "7 days"), (14, "14 days"), (30, "30 days"), (60, "60 days"),
            (90, "90 days"), (180, "6 months"), (365, "1 year"), (0, "Never")
        ]
        self.ret_buttons: List[QPushButton] = []
        for idx, (val, text) in enumerate(self.ret_options):
            b = QPushButton(text)
            b.setCheckable(True)
            b.setProperty("role", "chip")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda _, v=val: self._select_retention(v))
            grid_ret.addWidget(b, idx // 4, idx % 4)
            self.ret_buttons.append(b)
        v_ret_content.addLayout(grid_ret)

        self.lbl_ret_note = QLabel("Older copies are deleted automatically.")
        self.lbl_ret_note.setProperty("role", "field_note")
        v_ret_content.addWidget(self.lbl_ret_note)
        row_retention.addLayout(v_ret_content)
        form_layout.addLayout(row_retention)

        # 5. ALERTS SECTION
        row_alerts = QHBoxLayout()
        row_alerts.setSpacing(20)
        lbl_alerts_sec = QLabel("ALERTS")
        lbl_alerts_sec.setProperty("role", "section_label")
        lbl_alerts_sec.setFixedWidth(96)
        row_alerts.addWidget(lbl_alerts_sec, alignment=Qt.AlignmentFlag.AlignTop)

        v_alerts_content = QVBoxLayout()
        v_alerts_content.setSpacing(12)

        # Sound switch
        row_sw1 = QHBoxLayout()
        lbl_sw1 = QLabel("Chime on success or failure")
        lbl_sw1.setProperty("role", "switch_label")
        row_sw1.addWidget(lbl_sw1)
        row_sw1.addStretch()
        self.switch_chime = ToggleSwitch(checked=self.config.get("sound_alerts", True))
        row_sw1.addWidget(self.switch_chime)
        v_alerts_content.addLayout(row_sw1)

        # Windows notifications switch
        row_sw2 = QHBoxLayout()
        lbl_sw2 = QLabel("Windows notifications")
        lbl_sw2.setProperty("role", "switch_label")
        row_sw2.addWidget(lbl_sw2)
        row_sw2.addStretch()
        self.switch_notif = ToggleSwitch(checked=self.config.get("desktop_notifications", True))
        row_sw2.addWidget(self.switch_notif)
        v_alerts_content.addLayout(row_sw2)

        row_alerts.addLayout(v_alerts_content)
        form_layout.addLayout(row_alerts)

        scroll.setWidget(scroll_content)
        modal_card_layout.addWidget(scroll, stretch=1)

        # 6. MODAL ACTIONS (Cancel & Save settings)
        modal_actions = QHBoxLayout()
        modal_actions.setSpacing(24)
        modal_actions.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setProperty("role", "cancel_btn")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.clicked.connect(self._close_inwindow_settings)
        modal_actions.addWidget(btn_cancel)

        btn_save = QPushButton("Save settings")
        btn_save.setProperty("role", "save_btn")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.clicked.connect(self._save_inwindow_settings)
        modal_actions.addWidget(btn_save)

        modal_card_layout.addLayout(modal_actions)
        overlay_layout.addWidget(self.modal_card)

        self.root_stack.addWidget(self.overlay_widget)
        self.overlay_widget.hide()

    def _connect_signals(self):
        self.scheduler.backup_started.connect(self._on_backup_started)
        self.scheduler.backup_finished.connect(self._on_backup_finished)
        self.scheduler.state_changed.connect(self._refresh_state)

        # System tray interactions
        self.tray.open_requested.connect(self._show_and_raise)
        self.tray.backup_now_requested.connect(self._manual_backup)
        self.tray.settings_requested.connect(self._open_inwindow_settings)

    # ================= MODAL STATE MANAGEMENT =================
    def _select_freq(self, minutes: int):
        self._modal_selected_freq = minutes
        for btn, (val, _) in zip(self.freq_buttons, self.freq_options):
            btn.setChecked(val == minutes)
        self.custom_freq_container.setVisible(minutes == -1)

    def _select_retention(self, days: int):
        self._modal_selected_retention = days
        for btn, (val, _) in zip(self.ret_buttons, self.ret_options):
            btn.setChecked(val == days)
        if days == 0:
            self.lbl_ret_note.setText("Nothing is deleted. Watch your drive space.")
        else:
            self.lbl_ret_note.setText("Older copies are deleted automatically.")

    def _toggle_day_button(self, day_idx: int):
        # Already toggled by checkable button click
        pass

    def _open_inwindow_settings(self):
        """Populates and opens the in-window modal overlay."""
        # Active days
        active_days = set(self.config.get("active_days", [0, 1, 2, 3, 4, 5]))
        for i, btn in enumerate(self.day_buttons):
            btn.setChecked(i in active_days)

        # Hours
        st = self.config.get("start_time", "09:00")
        et = self.config.get("end_time", "21:00")
        try:
            sh, sm = map(int, st.split(":"))
            self.time_opens.setTime(QTime(sh, sm))
        except Exception:
            self.time_opens.setTime(QTime(9, 0))

        try:
            eh, em = map(int, et.split(":"))
            self.time_closes.setTime(QTime(eh, em))
        except Exception:
            self.time_closes.setTime(QTime(21, 0))

        # Frequency
        interval = self.config.get("interval_minutes", 60)
        matched = False
        for val, _ in self.freq_options:
            if val == interval:
                self._select_freq(val)
                matched = True
                break
        if not matched:
            self._select_freq(-1)
            if interval % 60 == 0:
                self.spin_custom_val.setValue(interval // 60)
                self.combo_custom_unit.setCurrentText("hours")
            else:
                self.spin_custom_val.setValue(interval)
                self.combo_custom_unit.setCurrentText("minutes")

        # Retention
        ret_days = self.config.get("retention_days", 30)
        matched_ret = False
        for val, _ in self.ret_options:
            if val == ret_days:
                self._select_retention(val)
                matched_ret = True
                break
        if not matched_ret:
            self._select_retention(30)

        # Switches
        self.switch_chime.setChecked(self.config.get("sound_alerts", True))
        self.switch_notif.setChecked(self.config.get("desktop_notifications", True))

        self.overlay_widget.show()
        self.overlay_widget.raise_()

    def _close_inwindow_settings(self):
        self.overlay_widget.hide()

    def _save_inwindow_settings(self):
        """Saves settings from modal overlay and updates scheduler."""
        # Frequency
        if self._modal_selected_freq == -1:
            val = self.spin_custom_val.value()
            unit = self.combo_custom_unit.currentText()
            interval = val * 60 if unit == "hours" else val
        else:
            interval = self._modal_selected_freq

        # Active days
        new_active_days = [i for i, b in enumerate(self.day_buttons) if b.isChecked()]
        if not new_active_days:
            new_active_days = [0]  # Minimum Monday

        # Hours
        st = self.time_opens.time().toString("HH:mm")
        et = self.time_closes.time().toString("HH:mm")

        # Retention
        ret_days = self._modal_selected_retention

        # Switches
        chime = self.switch_chime.isChecked()
        notif = self.switch_notif.isChecked()

        # Commit to config
        self.config.set("interval_minutes", interval, auto_save=False)
        self.config.set("active_days", new_active_days, auto_save=False)
        self.config.set("start_time", st, auto_save=False)
        self.config.set("end_time", et, auto_save=False)
        self.config.set("retention_days", ret_days, auto_save=False)
        self.config.set("sound_alerts", chime, auto_save=False)
        self.config.set("desktop_notifications", notif, auto_save=True)

        # Clean up autostart registry if previously configured
        if autostart.is_autostart_enabled():
            autostart.set_autostart(False)

        self._close_inwindow_settings()
        self._refresh_state()

    # ================= APPLICATION STATE REFRESH =================
    def _refresh_state(self):
        src = self.config.get("source_folder", "")
        dst = self.config.get("destination_folder", "")
        is_paused = self.config.get("is_paused", False)

        has_src = bool(src and Path(src).exists())
        has_dst = bool(dst and Path(dst).exists())
        is_configured = has_src and has_dst

        # 1. Update Source Card
        if has_src:
            self.lbl_source_path.setText(src)
            self.lbl_source_path.setStyleSheet("color: #2E1A08; font-weight: 600;")
            self.btn_choose_source.setText("Change folder")
        else:
            self.lbl_source_path.setText("No folder selected yet")
            self.lbl_source_path.setStyleSheet("color: #6B4E31; font-weight: 500;")
            self.btn_choose_source.setText("Choose folder")

        # 2. Update Destination Card
        if has_dst:
            free_gb = self._get_free_space_gb(dst)
            free_str = f" ({free_gb:.1f} GB free)" if free_gb is not None else ""
            self.lbl_dest_path.setText(f"{dst}{free_str}")
            self.lbl_dest_path.setStyleSheet("color: #2E1A08; font-weight: 600;")
            self.btn_choose_dest.setText("Change drive")
        else:
            self.lbl_dest_path.setText("No drive selected yet")
            self.lbl_dest_path.setStyleSheet("color: #6B4E31; font-weight: 500;")
            self.btn_choose_dest.setText("Choose drive")

        # 3. Update Hero Card
        if not is_configured:
            self.lbl_hero_tag.setText("SETUP NEEDED")
            self.lbl_hero_tag.setStyleSheet("color: #F7BE72;")
            self.lbl_hero_title.setText("Choose what to back up")
            self.lbl_hero_sub.setText(
                "Choose the folder to protect and where Tethr should keep the copies. "
                "Backups then run on their own during your active hours."
            )
            self.btn_backup_now.setEnabled(False)
            self.lbl_hero_note.setText("Finish 2 steps to enable")
            self.tray.set_status("paused")
        elif is_paused:
            self.lbl_hero_tag.setText("PAUSED")
            self.lbl_hero_tag.setStyleSheet("color: #E8DBA6;")
            self.lbl_hero_title.setText("Backups paused")
            self.lbl_hero_sub.setText("Scheduled automatic backups are temporarily halted.")
            self.btn_backup_now.setEnabled(False)
            self.lbl_hero_note.setText("Resume schedule to backup")
            self.tray.set_status("paused")
        else:
            self.lbl_hero_tag.setText("PROTECTED")
            self.lbl_hero_tag.setStyleSheet("color: #F7BE72;")
            self._update_countdown_label()
            self.lbl_hero_sub.setText("Automated hourly backup protecting billing data.")
            self.btn_backup_now.setEnabled(True)
            self.lbl_hero_note.setText("Trigger instant backup")
            self.tray.set_status("active")

        # 4. Header buttons
        self.btn_pause.setIcon(get_play_icon(16) if is_paused else get_pause_icon(16))
        self.btn_pause.setToolTip("Resume backups" if is_paused else "Pause backups")

        # 5. Summary Card
        st = self.config.get("start_time", "09:00")
        et = self.config.get("end_time", "21:00")
        self.lbl_sum_hours.setText(f"{st} – {et}")

        active_days = set(self.config.get("active_days", [0, 1, 2, 3, 4, 5]))
        for i, pill in enumerate(self.day_pills):
            is_active = i in active_days
            pill.setProperty("role", "summary_day_on" if is_active else "summary_day_off")
            pill.style().unpolish(pill)
            pill.style().polish(pill)

        interval = self.config.get("interval_minutes", 60)
        if interval < 60:
            self.lbl_sum_every.setText(f"{interval} min")
        elif interval % 60 == 0:
            hrs = interval // 60
            self.lbl_sum_every.setText(f"{hrs} hour" if hrs == 1 else f"{hrs} hours")
        else:
            self.lbl_sum_every.setText(f"{interval} min")

        ret = self.config.get("retention_days", 30)
        if ret == 0:
            self.lbl_sum_keep.setText("Never")
        elif ret == 180:
            self.lbl_sum_keep.setText("6 months")
        elif ret == 365:
            self.lbl_sum_keep.setText("1 year")
        elif ret == 1:
            self.lbl_sum_keep.setText("1 day")
        else:
            self.lbl_sum_keep.setText(f"{ret} days")

        # 6. Footer Last Backup Info
        last_dt = self.config.get("last_backup_time")
        if last_dt:
            try:
                dt = datetime.fromisoformat(last_dt)
                self.lbl_footer_status.setText(f"Last backup: {dt.strftime('%b %d at %H:%M')}")
            except Exception:
                self.lbl_footer_status.setText("Last backup recorded")
        else:
            self.lbl_footer_status.setText("No backups recorded yet")

    def _update_countdown_label(self):
        if not self.config.is_configured() or self.config.get("is_paused", False):
            return

        in_hours = self.config.is_within_working_hours()
        if not in_hours:
            self.lbl_hero_title.setText("Outside active hours")
            return

        secs = self.scheduler.seconds_until_next_backup
        if secs <= 0:
            self.lbl_hero_title.setText("Next backup due now")
        elif secs < 60:
            self.lbl_hero_title.setText(f"Next backup in {secs}s")
        else:
            mins = secs // 60
            self.lbl_hero_title.setText(f"Next backup in {mins}m")

    def _on_tick(self):
        if self.config.is_configured() and not self.config.get("is_paused", False):
            self._update_countdown_label()

    def _on_backup_started(self):
        self.lbl_hero_title.setText("Backing up data...")
        self.btn_backup_now.setEnabled(False)
        self.tray.set_status("working")

    def _on_backup_finished(self, result: BackupResult):
        self.btn_backup_now.setEnabled(True)
        if result.success:
            self.tray.set_status("active")
            if self.config.get("desktop_notifications", True):
                self.tray.notify(
                    "Tethr Backup Successful",
                    f"Saved {result.file_count} files ({result.size_bytes / 1024 / 1024:.2f} MB)",
                )
        else:
            self.tray.set_status("error")
            if self.config.get("desktop_notifications", True):
                self.tray.notify("Tethr Backup Failed", result.error_message or "Unknown error")
        self._refresh_state()

    def _manual_backup(self):
        if self.config.is_configured():
            self.scheduler.trigger_manual_backup()

    def _toggle_pause(self):
        new_val = not self.config.get("is_paused", False)
        self.config.set("is_paused", new_val)
        self.scheduler.state_changed.emit()
        self._refresh_state()

    def _select_source_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Billing Source Folder", self.config.get("source_folder", "")
        )
        if folder:
            self.config.set("source_folder", folder)
            self._refresh_state()

    def _select_dest_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Backup Target Drive / Folder", self.config.get("destination_folder", "")
        )
        if folder:
            self.config.set("destination_folder", folder)
            self._refresh_state()

    def _open_backup_directory(self):
        dst = self.config.get("destination_folder", "")
        if dst and os.path.exists(dst):
            os.startfile(dst)
        elif self.config.get("source_folder", "") and os.path.exists(self.config.get("source_folder", "")):
            os.startfile(self.config.get("source_folder", ""))

    def _get_free_space_gb(self, folder_path: str) -> Optional[float]:
        try:
            stat = shutil.disk_usage(folder_path)
            return stat.free / (1024**3)
        except Exception:
            return None

    def _show_and_raise(self):
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event: QCloseEvent):
        """Minimize to Windows system tray instead of closing."""
        if not self._first_minimize_notified:
            self.tray.notify(
                "Tethr Active",
                "Tethr is running in the background to ensure continuous backup protection.",
            )
            self._first_minimize_notified = True
        event.ignore()
        self.hide()
