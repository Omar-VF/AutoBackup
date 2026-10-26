"""
Tethr Update Dialog.
Displays update notification, release notes, and progress bar for GitHub releases.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
import webbrowser

from autobackup import __version__
from autobackup.updater import UpdateInfo, UpdateDownloadWorker, launch_installer_and_exit
from ui.icons import create_app_icon, get_close_icon


class UpdateDialog(QDialog):
    """Luxury Editorial Update Dialog for Tethr."""

    def __init__(self, update_info: UpdateInfo, parent=None):
        super().__init__(parent)
        self.update_info = update_info
        self.download_worker: UpdateDownloadWorker = None

        self.setWindowTitle("Tethr Update")
        self.setWindowIcon(create_app_icon(32))
        self.setFixedSize(520, 460)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 24)
        layout.setSpacing(16)

        # Header: Icon + Title + Version Tag
        header = QHBoxLayout()
        header.setSpacing(14)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(create_app_icon(38).pixmap(38, 38))
        header.addWidget(icon_lbl)

        v_title = QVBoxLayout()
        v_title.setSpacing(2)

        title_lbl = QLabel("Update Available")
        title_lbl.setStyleSheet(
            'font-family: "Instrument Serif", Georgia, serif; font-size: 28px; color: #2E1A08;'
        )
        v_title.addWidget(title_lbl)

        sub_lbl = QLabel(f"Version {self.update_info.version} is now available (Current: v{__version__})")
        sub_lbl.setStyleSheet(
            'font-family: "Manrope", sans-serif; font-size: 13px; font-weight: 600; color: #8F4300;'
        )
        v_title.addWidget(sub_lbl)
        header.addLayout(v_title)

        header.addStretch()
        layout.addLayout(header)

        # Release Notes Label
        notes_hdr = QLabel("WHAT'S NEW")
        notes_hdr.setStyleSheet(
            'font-family: "Manrope", sans-serif; font-size: 11px; font-weight: 800; letter-spacing: 0.12em; color: #A04800;'
        )
        layout.addWidget(notes_hdr)

        # Release Notes Body
        self.notes_box = QTextEdit()
        self.notes_box.setReadOnly(True)
        display_notes = self.update_info.notes or "Includes improvements, performance updates, and bug fixes."
        self.notes_box.setPlainText(display_notes)
        self.notes_box.setStyleSheet(
            """
            QTextEdit {
                background-color: #EFE4B8;
                color: #2E1A08;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-family: "Manrope", sans-serif;
                font-size: 13px;
                line-height: 1.5;
            }
            """
        )
        layout.addWidget(self.notes_box, stretch=1)

        # Download Progress Area (initially hidden)
        self.progress_container = QWidget()
        v_prog = QVBoxLayout(self.progress_container)
        v_prog.setContentsMargins(0, 0, 0, 0)
        v_prog.setSpacing(6)

        self.lbl_progress_status = QLabel("Downloading update...")
        self.lbl_progress_status.setStyleSheet(
            'font-family: "Manrope", sans-serif; font-size: 12px; font-weight: 600; color: #6B4E31;'
        )
        v_prog.addWidget(self.lbl_progress_status)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                background-color: #E8DBA6;
                border: none;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #B85400;
                border-radius: 4px;
            }
            """
        )
        v_prog.addWidget(self.progress_bar)
        self.progress_container.hide()
        layout.addWidget(self.progress_container)

        # Action Buttons
        h_actions = QHBoxLayout()
        h_actions.setSpacing(16)

        self.btn_github = QPushButton("View on GitHub")
        self.btn_github.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_github.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                border: none;
                color: #8F4300;
                font-family: "Manrope", sans-serif;
                font-size: 13px;
                font-weight: 700;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #B85400;
            }
            """
        )
        self.btn_github.clicked.connect(self._open_github_release)
        h_actions.addWidget(self.btn_github)

        h_actions.addStretch()

        self.btn_later = QPushButton("Later")
        self.btn_later.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_later.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                border: none;
                color: #2E1A08;
                font-family: "Manrope", sans-serif;
                font-size: 13px;
                font-weight: 700;
                text-decoration: underline;
                padding: 10px 14px;
            }
            QPushButton:hover {
                color: #6B4E31;
            }
            """
        )
        self.btn_later.clicked.connect(self.reject)
        h_actions.addWidget(self.btn_later)

        self.btn_update = QPushButton("Update Now")
        self.btn_update.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_update.setStyleSheet(
            """
            QPushButton {
                background-color: #B85400;
                color: #FFF8E6;
                font-family: "Manrope", sans-serif;
                font-size: 14px;
                font-weight: 700;
                border: none;
                border-radius: 7px;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #A34A00;
            }
            QPushButton:disabled {
                background-color: #B85400;
                opacity: 0.5;
            }
            """
        )
        self.btn_update.clicked.connect(self._start_download)
        h_actions.addWidget(self.btn_update)

        layout.addLayout(h_actions)

    def _open_github_release(self):
        url = self.update_info.release_url or f"https://github.com/{self.update_info.version}"
        webbrowser.open(url)

    def _start_download(self):
        if not self.update_info.download_url:
            self.lbl_progress_status.setText("No download link available for this release.")
            return

        self.btn_update.setEnabled(False)
        self.btn_later.setEnabled(False)
        self.progress_container.show()
        self.lbl_progress_status.setText("Connecting to GitHub...")

        self.download_worker = UpdateDownloadWorker(
            self.update_info.download_url,
            self.update_info.asset_name or "Tethr-Setup.exe",
            self,
        )
        self.download_worker.progress.connect(self._on_progress)
        self.download_worker.download_finished.connect(self._on_download_finished)
        self.download_worker.download_failed.connect(self._on_download_failed)
        self.download_worker.start()

    def _on_progress(self, downloaded: int, total: int, percent: int):
        self.progress_bar.setValue(percent)
        mb_down = downloaded / (1024 * 1024)
        mb_total = total / (1024 * 1024) if total > 0 else 0
        if mb_total > 0:
            self.lbl_progress_status.setText(
                f"Downloading update... {percent}% ({mb_down:.1f} / {mb_total:.1f} MB)"
            )
        else:
            self.lbl_progress_status.setText(f"Downloading update... {mb_down:.1f} MB")

    def _on_download_finished(self, installer_path: str):
        self.lbl_progress_status.setText("Download complete! Launching installer...")
        self.progress_bar.setValue(100)
        # Launch installer and cleanly exit current process
        try:
            launch_installer_and_exit(installer_path, silent=True)
        except Exception as e:
            self.lbl_progress_status.setText(f"Could not launch installer: {e}")
            self.btn_update.setEnabled(True)
            self.btn_later.setEnabled(True)

    def _on_download_failed(self, error: str):
        self.lbl_progress_status.setText(f"Download failed: {error}")
        self.lbl_progress_status.setStyleSheet("color: #A04800; font-weight: 700;")
        self.btn_update.setEnabled(True)
        self.btn_later.setEnabled(True)

    def closeEvent(self, event):
        if self.download_worker and self.download_worker.isRunning():
            self.download_worker.cancel()
            self.download_worker.wait(1000)
        super().closeEvent(event)
