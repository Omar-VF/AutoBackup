# Shop AutoBackup Pro

A professional, modern desktop backup application built with **Python 3.13** and **PyQt6** designed specifically for retail shops, billing counters, and accounting PCs.

It runs quietly in the Windows System Tray, automatically archiving billing data into timestamped ZIP files on a secondary or external drive every hour during business working hours.

---

## Features

- **Professional PyQt6 Dashboard**:
  - High-DPI dark-themed UI with rounded cards and status badges.
  - Live metric cards: *Next Scheduled Backup countdown*, *Last Backup details*, *Backup Drive Health*, and *Success Rate*.
  - Live in-progress compression bar with file-by-file progress indicator.
  - Interactive backup history table with timestamps, archive names, file counts, sizes, and durations.
- **Windows System Tray Integration**:
  - Minimizes cleanly to the tray when you close (`X`) the window.
  - Dynamic status indicator icon (Active Green, Working Blue, Paused Amber, Error Red).
  - Quick action context menu: *Open Dashboard*, *Backup Now*, *Pause/Resume*, *Settings*, and *Exit*.
  - Windows native toast/balloon notifications.
- **Shop Operating Hours Gating**:
  - Configurable opening and closing times (e.g. `09:00 AM` to `09:00 PM`).
  - Active days of week selector (e.g. Monday to Saturday).
  - Configurable backup frequency (every 15 min, 30 min, 1 hour, 2 hours, 4 hours).
  - Intelligent standby outside business hours so it doesn't run backups when the shop is closed.
- **Safe Atomic Archiving & Verification**:
  - Compresses billing data into timestamped ZIP archives (`BillingBackup_YYYY-MM-DD_HH-MM-SS.zip`).
  - Writes to a `.tmp` file first, tests archive integrity with `testzip()`, and only then finalizes the backup.
  - Handles locked billing files gracefully without crashing or stopping.
- **Retention & Safeguards**:
  - Automatically purges backups older than *N* days (configurable, e.g. 30 days) to prevent filling up the backup drive.
  - Checks target drive free space and reports low-disk warnings.
  - Audible chime on success and warning alarm on failure or drive disconnection.
- **Windows Startup**:
  - Option to automatically start on Windows boot directly in the system tray.

---

## Quick Start

### 1. Launch the App
Double-click `run_autobackup.bat` or run:
```bash
python main.py
```

### 2. Configure Your Shop Settings
1. Click **Settings** (or the gear icon).
2. Browse and select your **Source Billing Folder** (e.g., `C:\BillingData` or `D:\Tally\Data`).
3. Browse and select your **Destination Drive / Folder** (e.g., `E:\ShopBackups` on an external USB drive or secondary hard drive).
4. Set your shop's **Opening Time** and **Closing Time** (e.g., 09:00 AM - 09:00 PM).
5. Choose your **Active Days** and **Retention Period** (e.g., 30 days).
6. Click **Save Settings**.

### 3. Let It Run!
- The app will immediately calculate the next scheduled hourly backup.
- You can trigger an instant backup anytime by clicking **⚡ Backup Now**.
- Closing the window minimizes the app into the Windows System Tray so it keeps protecting your shop's data in the background.

---

## Project Structure

```
d:\Projects\AutoBackup\
├── autobackup/
│   ├── __init__.py
│   ├── config.py             # Persistent configuration manager (JSON)
│   ├── backup_engine.py      # Atomic ZIP compression, testzip integrity, retention purge
│   ├── scheduler.py          # Background QThread timer & working-hours logic
│   ├── sound_alerts.py       # Audible Windows success chimes & failure alarms
│   ├── logger.py             # Rolling logs & JSON backup history
│   └── autostart.py          # Windows Registry boot autostart
├── ui/
│   ├── __init__.py
│   ├── icons.py              # Dynamic vector high-DPI icons
│   ├── styles.py             # Modern QSS stylesheet
│   ├── settings_dialog.py    # Setup modal with folder pickers & schedule
│   ├── tray_icon.py          # Windows System Tray icon & notifications
│   └── main_window.py        # Main dashboard with metrics & history table
├── tests/
│   ├── test_backup_engine.py # Core backup, schedule gate, and retention unit tests
│   └── test_ui.py            # Headless PyQt6 UI integration tests
├── main.py                   # Application entry point with single-instance lock
├── run_autobackup.bat        # Double-click launcher
└── requirements.txt          # Python dependencies (PyQt6, psutil)
```
