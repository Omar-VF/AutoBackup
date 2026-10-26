import sys
import threading
import time


class SoundAlerts:
    """Provides audible cues for backup completions and critical alerts."""

    @staticmethod
    def _play_success_tones() -> None:
        if sys.platform != "win32":
            return
        try:
            import winsound
            # Melodic confirmation beep
            winsound.Beep(800, 100)
            time.sleep(0.05)
            winsound.Beep(1200, 150)
        except Exception:
            try:
                import winsound
                winsound.MessageBeep(winsound.MB_OK)
            except Exception:
                pass

    @staticmethod
    def _play_failure_tones() -> None:
        if sys.platform != "win32":
            return
        try:
            import winsound
            # Urgent alarm warning sound (two low pulses)
            winsound.Beep(450, 250)
            time.sleep(0.08)
            winsound.Beep(350, 350)
            time.sleep(0.1)
            winsound.Beep(350, 400)
        except Exception:
            try:
                import winsound
                winsound.MessageBeep(winsound.MB_ICONHAND)
            except Exception:
                pass

    @classmethod
    def play_success(cls) -> None:
        """Plays the success notification sound asynchronously."""
        threading.Thread(target=cls._play_success_tones, daemon=True).start()

    @classmethod
    def play_failure(cls) -> None:
        """Plays the failure alert alarm asynchronously."""
        threading.Thread(target=cls._play_failure_tones, daemon=True).start()
