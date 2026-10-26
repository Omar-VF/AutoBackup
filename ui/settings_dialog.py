from typing import List

from PyQt6.QtCore import QTime
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
)

from autobackup import autostart
from autobackup.config import ConfigManager


class SettingsDialog(QDialog):
    """Refined modern configuration dialog for Shop AutoBackup Pro."""

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.setWindowTitle("Schedule & Options - AutoBackup")
        self.setFixedSize(460, 460)
        self.setModal(True)
        self._init_ui()
        self._load_values()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Header
        h_box = QVBoxLayout()
        h_box.setSpacing(2)
        title = QLabel("Backup Schedule & Rules")
        title.setProperty("role", "hero_title")
        sub = QLabel("Set your store opening hours, frequency, and retention policy.")
        sub.setProperty("role", "hero_subtitle")
        h_box.addWidget(title)
        h_box.addWidget(sub)
        layout.addLayout(h_box)

        # Settings Card
        card = QFrame()
        card.setProperty("card", "surface")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(12)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(10)

        # Backup Frequency
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

        # Store Opening & Closing Hours
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

        # Retention
        lbl_ret = QLabel("Retention:")
        lbl_ret.setProperty("role", "section_tag")
        self.spin_retention = QSpinBox()
        self.spin_retention.setRange(0, 365)
        self.spin_retention.setSuffix(" days")
        self.spin_retention.setSpecialValueText("Keep Forever")
        grid.addWidget(lbl_ret, 3, 0)
        grid.addWidget(self.spin_retention, 3, 1)

        card_layout.addLayout(grid)

        # Active Days
        lbl_days = QLabel("ACTIVE WORKING DAYS:")
        lbl_days.setProperty("role", "section_tag")
        card_layout.addWidget(lbl_days)

        days_layout = QHBoxLayout()
        days_layout.setSpacing(8)
        self.day_cbs: List[QCheckBox] = []
        for name in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
            cb = QCheckBox(name)
            self.day_cbs.append(cb)
            days_layout.addWidget(cb)
        card_layout.addLayout(days_layout)

        # Separator
        div = QFrame()
        div.setProperty("separator", "true")
        card_layout.addWidget(div)

        # Toggles
        self.cb_sound = QCheckBox("Audible chime on success / warning on failure")
        self.cb_notify = QCheckBox("Windows desktop notifications")
        self.cb_startup = QCheckBox("Run on startup (Windows boot)")

        card_layout.addWidget(self.cb_sound)
        card_layout.addWidget(self.cb_notify)
        card_layout.addWidget(self.cb_startup)

        layout.addWidget(card)

        layout.addStretch()

        # Action Buttons
        btns = QHBoxLayout()
        btns.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("Save Settings")
        btn_save.setProperty("role", "primary")
        btn_save.clicked.connect(self._save)

        btns.addWidget(btn_cancel)
        btns.addWidget(btn_save)
        layout.addLayout(btns)

    def _load_values(self):
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
        self.cb_startup.setChecked(self.config.get("run_on_startup", False))

    def _save(self):
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
        self.accept()
