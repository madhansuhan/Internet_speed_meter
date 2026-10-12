"""Network speed tracker measuring real-time upload and download speeds."""
import time
from typing import Tuple, Dict, Any

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


def format_bytes_speed(bytes_per_sec: float) -> Tuple[str, str]:
    """Formats bytes per second into (value_str, unit_str)."""
    if bytes_per_sec < 1024:
        return f"{bytes_per_sec:.0f}", "B/s"
    elif bytes_per_sec < 1024 * 1024:
        kb = bytes_per_sec / 1024
        return (f"{kb:.1f}" if kb < 100 else f"{kb:.0f}"), "KB/s"
    elif bytes_per_sec < 1024 * 1024 * 1024:
        mb = bytes_per_sec / (1024 * 1024)
        return f"{mb:.1f}", "MB/s"
    else:
        gb = bytes_per_sec / (1024 * 1024 * 1024)
        return f"{gb:.2f}", "GB/s"


def format_bits_speed(bytes_per_sec: float) -> Tuple[str, str]:
    """Formats bytes per second into bits per second (value_str, unit_str)."""
    bits_per_sec = bytes_per_sec * 8
    if bits_per_sec < 1000:
        return f"{bits_per_sec:.0f}", "bps"
    elif bits_per_sec < 1000 * 1000:
        kbps = bits_per_sec / 1000
        return (f"{kbps:.1f}" if kbps < 100 else f"{kbps:.0f}"), "Kbps"
    elif bits_per_sec < 1000 * 1000 * 1000:
        mbps = bits_per_sec / (1000 * 1000)
        return f"{mbps:.1f}", "Mbps"
    else:
        gbps = bits_per_sec / (1000 * 1000 * 1000)
        return f"{gbps:.2f}", "Gbps"


def format_data_volume(total_bytes: int) -> str:
    """Formats total volume in bytes to human-readable string (MB, GB, TB)."""
    if total_bytes < 1024 * 1024:
        return f"{total_bytes / 1024:.1f} KB"
    elif total_bytes < 1024 * 1024 * 1024:
        return f"{total_bytes / (1024 * 1024):.1f} MB"
    elif total_bytes < 1024 * 1024 * 1024 * 1024:
        return f"{total_bytes / (1024 * 1024 * 1024):.2f} GB"
    else:
        return f"{total_bytes / (1024 * 1024 * 1024 * 1024):.2f} TB"


class SpeedTracker:
    """Calculates download and upload network throughput in real-time."""

    def __init__(self):
        self.last_recv = 0
        self.last_sent = 0
        self.last_time = time.time()

        self.initial_recv = 0
        self.initial_sent = 0

        self.session_recv = 0
        self.session_sent = 0

        self.current_dl_bytes = 0.0
        self.current_ul_bytes = 0.0

        self._initialize_counters()

    def _get_raw_counters(self) -> Tuple[int, int]:
        """Fetches total system bytes received and sent."""
        if PSUTIL_AVAILABLE:
            try:
                counters = psutil.net_io_counters()
                if counters:
                    return counters.bytes_recv, counters.bytes_sent
            except Exception:
                pass
        return 0, 0

    def _initialize_counters(self) -> None:
        """Initial baseline readings."""
        r, s = self._get_raw_counters()
        self.last_recv = r
        self.last_sent = s
        self.initial_recv = r
        self.initial_sent = s
        self.last_time = time.time()

    def update(self) -> Dict[str, Any]:
        """Calculates delta speeds and updates session usage."""
        now = time.time()
        elapsed = now - self.last_time

        if elapsed <= 0:
            elapsed = 0.001

        current_recv, current_sent = self._get_raw_counters()

        # Check for system restarts or counter resets
        delta_recv = max(0, current_recv - self.last_recv) if current_recv >= self.last_recv else 0
        delta_sent = max(0, current_sent - self.last_sent) if current_sent >= self.last_sent else 0

        self.current_dl_bytes = delta_recv / elapsed
        self.current_ul_bytes = delta_sent / elapsed

        self.session_recv += delta_recv
        self.session_sent += delta_sent

        self.last_recv = current_recv
        self.last_sent = current_sent
        self.last_time = now

        return {
            "dl_bps": self.current_dl_bytes,
            "ul_bps": self.current_ul_bytes,
            "session_recv": self.session_recv,
            "session_sent": self.session_sent
        }

    def get_formatted_speeds(self, unit_mode: str = "bytes") -> Dict[str, str]:
        """Returns formatted string representations for UI display."""
        if unit_mode == "bits":
            dl_val, dl_unit = format_bits_speed(self.current_dl_bytes)
            ul_val, ul_unit = format_bits_speed(self.current_ul_bytes)
        else:
            dl_val, dl_unit = format_bytes_speed(self.current_dl_bytes)
            ul_val, ul_unit = format_bytes_speed(self.current_ul_bytes)

        return {
            "dl_val": dl_val,
            "dl_unit": dl_unit,
            "ul_val": ul_val,
            "ul_unit": ul_unit,
            "session_dl": format_data_volume(self.session_recv),
            "session_ul": format_data_volume(self.session_sent),
            "session_total": format_data_volume(self.session_recv + self.session_sent)
        }
