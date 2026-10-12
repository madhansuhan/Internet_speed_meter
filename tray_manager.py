"""System Tray Manager for Internet Speed Meter (Hidden Taskbar)."""
import threading
from typing import Callable, Optional
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item, Menu

from autostart import is_autostart_enabled, set_autostart
from config import ConfigManager, THEMES


def create_tray_icon_image() -> Image.Image:
    """Generates an attractive speedometer icon for the system tray."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Outer circle border / gauge arc
    draw.arc([4, 4, size - 4, size - 4], start=135, end=405, fill=(0, 240, 255, 255), width=5)

    # Inner circular background
    draw.ellipse([14, 14, size - 14, size - 14], fill=(18, 19, 28, 255))

    # Download arrow (cyan)
    draw.polygon([(26, 26), (38, 26), (32, 34)], fill=(0, 240, 255, 255))

    # Upload arrow (amber)
    draw.polygon([(26, 44), (38, 44), (32, 36)], fill=(255, 136, 0, 255))

    return img


class TrayManager:
    """Controls the Windows notification tray icon and menu."""

    def __init__(self, config: ConfigManager, meter_app, on_exit: Optional[Callable] = None):
        self.config = config
        self.meter = meter_app
        self.on_exit = on_exit
        self.icon: Optional[pystray.Icon] = None
        self._thread: Optional[threading.Thread] = None

    def _build_menu(self) -> Menu:
        """Constructs the system tray context menu."""
        return Menu(
            item("👁 Show / Hide Meter", self._toggle_visibility, default=True),
            item(
                "🔒 Lock Position",
                self._toggle_lock,
                checked=lambda item: self.config.get("locked", False)
            ),
            item(
                "📐 Compact Mode",
                self._toggle_compact,
                checked=lambda item: self.config.get("compact_mode", False)
            ),
            Menu.SEPARATOR,
            item("🎨 Themes", Menu(
                *[
                    item(
                        theme_data["name"],
                        self._create_theme_setter(k),
                        checked=self._create_theme_checker(k),
                        radio=True
                    )
                    for k, theme_data in THEMES.items()
                ]
            )),
            item("🔍 Opacity", Menu(
                item("100%", lambda: self._set_opacity(1.0)),
                item("90%", lambda: self._set_opacity(0.90)),
                item("75%", lambda: self._set_opacity(0.75)),
                item("60%", lambda: self._set_opacity(0.60)),
                item("40%", lambda: self._set_opacity(0.40)),
            )),
            item("📊 Speed Units", Menu(
                item("Bytes/s (KB/s, MB/s)", lambda: self._set_units("bytes")),
                item("Bits/s (Kbps, Mbps)", lambda: self._set_units("bits")),
            )),
            item("⚡ Refresh Rate", Menu(
                item("0.5 Seconds", lambda: self._set_refresh(500)),
                item("1.0 Second", lambda: self._set_refresh(1000)),
                item("2.0 Seconds", lambda: self._set_refresh(2000)),
            )),
            Menu.SEPARATOR,
            item(
                "🚀 Start with Windows",
                self._toggle_autostart,
                checked=lambda item: is_autostart_enabled()
            ),
            item("📈 Data Usage", self._show_stats),
            item("📍 Reset Position", self._reset_position),
            Menu.SEPARATOR,
            item("❌ Exit", self._exit_app)
        )

    def _create_theme_setter(self, theme_key: str):
        return lambda: self.meter.after(0, lambda: self.meter.set_theme(theme_key))

    def _create_theme_checker(self, theme_key: str):
        return lambda item: self.config.get("theme", "cyber_dark") == theme_key

    def _toggle_visibility(self) -> None:
        if self.config.get("visible", True):
            self.meter.after(0, self.meter.hide_meter)
        else:
            self.meter.after(0, self.meter.show_meter)

    def _toggle_lock(self) -> None:
        self.meter.after(0, self.meter.toggle_lock)

    def _toggle_compact(self) -> None:
        self.meter.after(0, self.meter._toggle_compact_mode)

    def _set_opacity(self, op: float) -> None:
        self.meter.after(0, lambda: self.meter.set_opacity(op))

    def _set_units(self, unit: str) -> None:
        self.meter.after(0, lambda: self.meter.set_unit_mode(unit))

    def _set_refresh(self, ms: int) -> None:
        self.meter.after(0, lambda: self.meter.set_refresh_rate(ms))

    def _toggle_autostart(self) -> None:
        current = is_autostart_enabled()
        new_state = not current
        set_autostart(new_state)
        self.config.set("start_with_windows", new_state)

    def _show_stats(self) -> None:
        self.meter.after(0, self.meter.show_stats)

    def _reset_position(self) -> None:
        self.meter.after(0, self.meter.reset_position)

    def _exit_app(self) -> None:
        if self.icon:
            self.icon.stop()
        if self.on_exit:
            self.on_exit()
        self.meter.after(0, self.meter.quit_app)

    def start(self) -> None:
        """Starts the tray icon in a dedicated background thread."""
        img = create_tray_icon_image()
        menu = self._build_menu()

        self.icon = pystray.Icon(
            name="InternetSpeedMeter",
            icon=img,
            title="Internet Speed Meter",
            menu=menu
        )

        self._thread = threading.Thread(target=self.icon.run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stops the tray icon."""
        if self.icon:
            try:
                self.icon.stop()
            except Exception:
                pass
