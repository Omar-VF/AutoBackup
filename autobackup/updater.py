"""
Tethr GitHub Release Auto-Updater.
Automatically checks for new tagged releases on GitHub, downloads the updated
installer in the background, and seamlessly updates the Windows application.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
import urllib.error
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from autobackup import __version__

# Target GitHub Repository
GITHUB_REPO = "Omar-VF/Tethr"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


def parse_version(v_str: str) -> Tuple[int, ...]:
    """Extracts numeric tuple from version strings like 'v1.0.2', '1.2.0', 'v2.0'."""
    clean = re.sub(r"^[vV]", "", v_str.strip())
    # Extract numeric components
    nums = re.findall(r"\d+", clean)
    if not nums:
        return (0, 0, 0)
    return tuple(int(n) for n in nums[:3])


def is_newer_version(remote_v: str, current_v: str = __version__) -> bool:
    """Returns True if remote_v is strictly newer than current_v."""
    try:
        r_tuple = parse_version(remote_v)
        c_tuple = parse_version(current_v)
        return r_tuple > c_tuple
    except Exception:
        return False


@dataclass
class UpdateInfo:
    version: str
    release_name: str
    notes: str
    download_url: str
    asset_name: str
    size_bytes: int
    release_url: str


class UpdateCheckWorker(QThread):
    """Background worker that queries GitHub Releases API without blocking UI."""
    update_available = pyqtSignal(object)       # UpdateInfo
    no_update_available = pyqtSignal(str)       # current_version
    check_failed = pyqtSignal(str)              # error_message

    def __init__(self, repo: str = GITHUB_REPO, current_version: str = __version__, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.current_version = current_version

    def run(self):
        url = f"https://api.github.com/repos/{self.repo}/releases/latest"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": f"Tethr-App-Updater/{self.current_version}",
                "Accept": "application/vnd.github.v3+json",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status != 200:
                    self.check_failed.emit(f"GitHub returned HTTP status {resp.status}")
                    return
                data = json.loads(resp.read().decode("utf-8"))

            tag_name = data.get("tag_name", "")
            if not tag_name:
                self.check_failed.emit("No release tag found on GitHub.")
                return

            if is_newer_version(tag_name, self.current_version):
                # Search for installer asset (.exe)
                assets = data.get("assets", [])
                installer_asset = None
                for a in assets:
                    name = a.get("name", "").lower()
                    if name.endswith(".exe"):
                        # Prefer setup or tethr installer
                        if "setup" in name or "tethr" in name:
                            installer_asset = a
                            break
                        elif installer_asset is None:
                            installer_asset = a

                if installer_asset:
                    info = UpdateInfo(
                        version=tag_name,
                        release_name=data.get("name") or tag_name,
                        notes=data.get("body", "").strip(),
                        download_url=installer_asset.get("browser_download_url", ""),
                        asset_name=installer_asset.get("name", "Tethr-Setup.exe"),
                        size_bytes=int(installer_asset.get("size", 0)),
                        release_url=data.get("html_url", f"https://github.com/{self.repo}/releases"),
                    )
                    self.update_available.emit(info)
                else:
                    self.check_failed.emit(
                        f"Release {tag_name} exists, but installer executable is still building."
                    )
            else:
                self.no_update_available.emit(self.current_version)

        except urllib.error.HTTPError as e:
            if e.code == 404:
                # No releases published yet
                self.no_update_available.emit(self.current_version)
            elif e.code == 403:
                # GitHub REST API rate limit reached (60 req/hr on unauthenticated IP)
                # Seamless fallback to web URL which has no rate limit
                self._check_web_fallback()
            else:
                self.check_failed.emit(f"GitHub connection error: HTTP {e.code}")
        except Exception as e:
            self.check_failed.emit(str(e))

    def _check_web_fallback(self):
        """Fallback check via standard GitHub web release redirect, bypassing REST API rate limits."""
        web_url = f"https://github.com/{self.repo}/releases/latest"
        req = urllib.request.Request(
            web_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Accept": "text/html,application/xhtml+xml",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                final_url = resp.geturl()
                match = re.search(r"/releases/tag/([^/?#]+)", final_url)
                if match:
                    tag_name = match.group(1)
                    if is_newer_version(tag_name, self.current_version):
                        download_url = f"https://github.com/{self.repo}/releases/download/{tag_name}/Tethr-Setup.exe"
                        info = UpdateInfo(
                            version=tag_name,
                            release_name=f"Tethr {tag_name}",
                            notes="A new version of Tethr is available. Click Update to download and install.",
                            download_url=download_url,
                            asset_name="Tethr-Setup.exe",
                            size_bytes=0,
                            release_url=final_url,
                        )
                        self.update_available.emit(info)
                        return
                    else:
                        self.no_update_available.emit(self.current_version)
                        return

            self.no_update_available.emit(self.current_version)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                # No releases published yet on this repository -> current build is up to date
                self.no_update_available.emit(self.current_version)
            else:
                self.check_failed.emit(f"Could not reach GitHub (HTTP {e.code})")
        except Exception as e:
            self.check_failed.emit(str(e))



class UpdateDownloadWorker(QThread):
    """Background worker that streams the installer download with progress signals."""
    progress = pyqtSignal(int, int, int)    # downloaded_bytes, total_bytes, percent
    download_finished = pyqtSignal(str)     # local_file_path
    download_failed = pyqtSignal(str)       # error_message

    def __init__(self, download_url: str, filename: str = "Tethr-Setup.exe", parent=None):
        super().__init__(parent)
        self.download_url = download_url
        self.filename = filename
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            dest_dir = Path(tempfile.gettempdir()) / "Tethr_Update"
            dest_dir.mkdir(parents=True, exist_ok=True)
            local_path = dest_dir / self.filename

            req = urllib.request.Request(
                self.download_url,
                headers={"User-Agent": f"Tethr-App-Updater/{__version__}"},
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                total_size = int(response.headers.get("content-length", 0))
                downloaded = 0
                chunk_size = 64 * 1024  # 64 KB chunks

                with open(local_path, "wb") as f:
                    while True:
                        if self._cancelled:
                            local_path.unlink(missing_ok=True)
                            return
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        percent = int((downloaded / total_size) * 100) if total_size > 0 else 0
                        self.progress.emit(downloaded, total_size, percent)

            if local_path.exists() and local_path.stat().st_size > 1024 * 500:
                self.download_finished.emit(str(local_path))
            else:
                self.download_failed.emit("Downloaded update file was incomplete or corrupted.")

        except Exception as e:
            self.download_failed.emit(str(e))


def launch_installer_and_exit(installer_path: str, silent: bool = False):
    """
    Executes the Inno Setup installer and terminates the current Tethr process.
    Uses Inno Setup flags to cleanly close running process and restart upon completion.
    """
    if not os.path.exists(installer_path):
        raise FileNotFoundError(f"Installer not found at {installer_path}")

    args = [installer_path]
    if silent:
        # /SILENT: show progress, no wizard clicks needed
        # /CLOSEAPPLICATIONS: close running app via Windows Restart Manager
        # /RESTARTAPPLICATIONS: relaunch app when install finishes
        args.extend(["/SILENT", "/CLOSEAPPLICATIONS", "/RESTARTAPPLICATIONS"])
    else:
        args.extend(["/CLOSEAPPLICATIONS", "/RESTARTAPPLICATIONS"])

    # Launch detached process on Windows
    creationflags = 0
    if sys.platform == "win32":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS

    subprocess.Popen(args, creationflags=creationflags, close_fds=True)

    # Gracefully exit
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance()
    if app:
        app.quit()
    sys.exit(0)
