"""Windows Registry Autostart helper for Internet Speed Meter."""
import os
import sys
import winreg

APP_NAME = "InternetSpeedMeter"
RUN_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"


def get_launch_command() -> str:
    """Constructs the command to launch the app silently on startup."""
    # If compiled with pyinstaller
    if getattr(sys, 'frozen', False):
        return f'"{sys.executable}"'

    # If running from python script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    main_pyw = os.path.join(base_dir, "main.pyw")
    if not os.path.exists(main_pyw):
        main_pyw = os.path.join(base_dir, "main.py")

    # Use pythonw if available to avoid opening a terminal window
    python_exe = sys.executable
    pythonw_exe = os.path.join(os.path.dirname(python_exe), "pythonw.exe")
    if os.path.exists(pythonw_exe):
        exe = pythonw_exe
    else:
        exe = python_exe

    return f'"{exe}" "{main_pyw}"'


def is_autostart_enabled() -> bool:
    """Checks if autostart registry entry exists and is set."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, APP_NAME)
            return bool(value)
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"Error checking autostart: {e}")
        return False


def set_autostart(enable: bool) -> bool:
    """Enables or disables automatic startup with Windows."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_WRITE) as key:
            if enable:
                cmd = get_launch_command()
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                except FileNotFoundError:
                    pass
        return True
    except Exception as e:
        print(f"Error updating autostart registry: {e}")
        return False
