"""Main Entry Point for Internet Speed Meter."""
import ctypes
import os
import sys
from typing import Optional

from config import ConfigManager
from speed_tracker import SpeedTracker
from floating_meter import FloatingMeter
from tray_manager import TrayManager

MUTEX_NAME = "Global\\InternetSpeedMeterFloatingOverlay_Mutex"
ERROR_ALREADY_EXISTS = 183


def acquire_single_instance_mutex():
    """Prevents multiple instances of the speed meter from running simultaneously."""
    try:
        mutex = ctypes.windll.kernel32.CreateMutexW(None, False, MUTEX_NAME)
        last_error = ctypes.windll.kernel32.GetLastError()
        if last_error == ERROR_ALREADY_EXISTS:
            return None
        return mutex
    except Exception:
        return True


def main() -> None:
    # Enforce single instance
    mutex = acquire_single_instance_mutex()
    if mutex is None:
        print("Internet Speed Meter is already running in the background.")
        sys.exit(0)

    # Initialize configuration and speed tracking
    config = ConfigManager()
    speed_tracker = SpeedTracker()

    tray_ref: list = [None]

    def on_quit():
        if tray_ref[0]:
            tray_ref[0].stop()

    # Create Floating HUD Window
    app = FloatingMeter(config=config, speed_tracker=speed_tracker, on_quit_callback=on_quit)

    # If visibility was set to False, hide window on launch
    if not config.get("visible", True):
        app.withdraw()

    # Initialize and start System Tray
    tray = TrayManager(config=config, meter_app=app, on_exit=on_quit)
    tray_ref[0] = tray
    tray.start()

    # Run Tkinter GUI event loop
    try:
        app.mainloop()
    except KeyboardInterrupt:
        on_quit()


if __name__ == "__main__":
    main()
