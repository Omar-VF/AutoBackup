# Tethr

An automated billing data vault for Windows desktop designed for retail shops, billing counters, and accounting PCs.

**Tethr** permanently connects your billing directory to an external/secondary drive, automatically producing timestamped, verified archives every hour during business working hours.

---

## ✨ Features

- **Lavish & Minimalist Desktop Canvas**:
  - Warm cream (`#FDFBD4`) and espresso (`#38240D`) editorial paper aesthetic with terracotta (`#C05800`) accents.
  - Generous 920 × 620 px workspace with clean visual hierarchy.
  - Live in-window settings popover modal — zero second-window clutter on Windows.
  - Vector iconography for folders, drives, gears, and sync operations.
- **Intelligent Working Hours Gate**:
  - Automatically runs hourly (or 15m, 30m, 2h, 4h) only when the shop is open (e.g. 09:00 AM – 09:00 PM).
  - Configurable active working days (e.g. Monday to Saturday).
- **Atomic ZIP Compression & Verification**:
  - Creates safe `TethrBackup_YYYY-MM-DD_HH-MM-SS.zip` archives.
  - Writes to `.tmp` first, verifies archive health with `testzip()`, and only then finalizes to `.zip`.
  - Automatic retention cleaner: auto-purges archives older than *N* days (default 30 days).
  - Target drive health check and low-space warnings.
- **Quiet System Tray Integration**:
  - Closing (`✕`) docks Tethr quietly to the Windows System Tray near the clock.
  - Windows desktop notifications and optional success/warning chimes.
  - Windows boot autostart option.

---

## 🚀 Quick Launch

```powershell
python .\main.py
```
*(or double-click `run_autobackup.bat`).*
