"""Configuration manager for Floating Internet Speed Meter."""
import json
import os
from typing import Any, Dict

DEFAULT_CONFIG: Dict[str, Any] = {
    "pos_x": 100,
    "pos_y": 100,
    "locked": False,
    "opacity": 0.90,
    "unit_mode": "bytes",  # 'bytes' (KB/s, MB/s) or 'bits' (Kbps, Mbps)
    "theme": "cyber_dark",  # cyber_dark, midnight_blue, matrix_green, minimal_slate, light_glass
    "refresh_interval_ms": 1000,  # 500, 1000, 2000
    "show_session_totals": True,
    "snap_to_edges": True,
    "start_with_windows": False,
    "visible": True,
    "compact_mode": False
}

THEMES = {
    "cyber_dark": {
        "name": "Cyber Dark",
        "bg": "#12131C",
        "border": "#282A3A",
        "dl_color": "#00F0FF",      # Neon Cyan
        "ul_color": "#FF8800",      # Neon Amber / Orange
        "text_color": "#ECEFF4",
        "muted_color": "#6E768E",
        "badge_bg": "#1B1D2C"
    },
    "midnight_blue": {
        "name": "Midnight Blue",
        "bg": "#0D1117",
        "border": "#1E293B",
        "dl_color": "#38BDF8",      # Sky Blue
        "ul_color": "#A78BFA",      # Violet
        "text_color": "#F8FAFC",
        "muted_color": "#64748B",
        "badge_bg": "#1E293B"
    },
    "matrix_green": {
        "name": "Matrix Green",
        "bg": "#0A0F0D",
        "border": "#1B3B2B",
        "dl_color": "#10B981",      # Emerald Green
        "ul_color": "#FBBF24",      # Warm Amber
        "text_color": "#E6FFED",
        "muted_color": "#4B7C5E",
        "badge_bg": "#13231B"
    },
    "minimal_slate": {
        "name": "Minimal Slate",
        "bg": "#1E222A",
        "border": "#323842",
        "dl_color": "#61AFEF",      # Calm Blue
        "ul_color": "#E5C07B",      # Soft Yellow
        "text_color": "#ABB2BF",
        "muted_color": "#5C6370",
        "badge_bg": "#282C34"
    },
    "light_glass": {
        "name": "Light Glass",
        "bg": "#F1F5F9",
        "border": "#CBD5E1",
        "dl_color": "#0284C7",      # Deep Sky Blue
        "ul_color": "#D97706",      # Amber
        "text_color": "#0F172A",
        "muted_color": "#64748B",
        "badge_bg": "#E2E8F0"
    }
}


class ConfigManager:
    """Handles loading, saving, and querying configuration options."""

    def __init__(self, config_filename: str = "config.json"):
        self.config_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.config_dir, config_filename)
        self.data: Dict[str, Any] = self.load()

    def load(self) -> Dict[str, Any]:
        """Loads configuration from JSON file or initializes defaults."""
        config = DEFAULT_CONFIG.copy()
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    if isinstance(saved, dict):
                        config.update(saved)
            except Exception as e:
                print(f"Warning: Failed to load config ({e}), using defaults.")
        return config

    def save(self) -> None:
        """Saves current configuration to JSON file."""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Gets a configuration parameter."""
        return self.data.get(key, default if default is not None else DEFAULT_CONFIG.get(key))

    def set(self, key: str, value: Any, save_immediately: bool = True) -> None:
        """Sets a configuration parameter and optionally saves to disk."""
        self.data[key] = value
        if save_immediately:
            self.save()

    def get_theme_colors(self) -> Dict[str, str]:
        """Returns the color palette for current theme."""
        theme_key = self.get("theme", "cyber_dark")
        return THEMES.get(theme_key, THEMES["cyber_dark"])
