# Tethr

An automated billing data vault for Windows desktop designed for retail shops, billing counters, and accounting PCs.

**Tethr** permanently connects your critical billing directory to a secondary storage drive or external disk, automatically producing timestamped, verified archives during active store business hours.

---

## ✨ Features

- **Lavish & Minimalist Desktop Canvas**:
  - Warm linen cream (`#FCF7DE`) and deep espresso (`#2E1A08`) editorial aesthetic with vibrant terracotta (`#B85400`) accents.
  - Custom typography loaded natively via **Instrument Serif** and **Manrope**.
  - Generous 1140 × 720 px workspace with clean visual hierarchy.
  - Live in-window schedule popover modal (570 px) — zero second-window clutter on Windows.
  - Custom vector iconography for folders, drives, gears, sync operations, and dashed connectors.
- **Intelligent Working Hours Gate**:
  - Automatically runs hourly (or 5m, 15m, 30m, 2h, 4h, 6h, or custom intervals) only when the shop is open (e.g. 09:00 AM – 09:00 PM).
  - Configurable active working days (e.g. Monday to Saturday).
  - Smart catch-up scheduler: if the system boots mid-day after store hours start, Tethr immediately catches up with a backup.
- **Atomic ZIP Compression & Verification**:
  - Creates safe `DD-MM-YYYY_HR-MIN.zip` archives (e.g. `26-10-2026_21-30.zip`).
  - Writes to `.tmp` first, verifies archive health with `testzip()`, and only then atomically finalizes to `.zip`.
  - Automatic retention cleaner: auto-purges archives older than *N* days (default 30 days) and cleans orphaned temporary files.
  - Target drive health check and low-space warnings.
- **Quiet System Tray Integration**:
  - Closing (`✕`) docks Tethr quietly to the Windows System Tray near the clock.
  - Windows desktop notifications and optional success/warning chimes.
  - Windows boot autostart option.
- **GitHub Release Auto-Updater**:
  - Queries `Omar-VF/Tethr` releases via background thread on startup and periodically every 4 hours.
  - When you tag a new release (e.g. `git tag v1.0.3 && git push origin v1.0.3`), GitHub Actions automatically builds `Tethr-Setup.exe` and publishes the release.
  - Tethr detects the new release, shows the changelog in an editorial update modal, downloads the installer, and seamlessly upgrades and restarts the app.

---

## 📦 Download & Installation

The standalone Windows installer is available on the GitHub Releases page:
👉 **[Download Tethr for Windows (Latest Release)](https://github.com/Omar-VF/Tethr/releases/latest)**

- Standalone executable (requires no Python or external dependencies on the target PC).
- Installs to Program Files / User AppData with multi-resolution desktop and Start Menu shortcuts.
- Includes Windows Add/Remove Programs clean uninstaller.

To build the installer from source locally:
```powershell
.\build_installer.bat
```
*(The compiled installer will be generated in `dist\installer\Tethr-Setup.exe`)*

---

## 🚀 Quick Launch (Source)

```powershell
python .\main.py
```
*(or double-click `run_autobackup.bat` for windowless background startup).*
