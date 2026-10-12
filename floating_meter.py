"""Floating Overlay Widget for Internet Speed Meter."""
import ctypes
import tkinter as tk
from tkinter import Menu, messagebox
from typing import Callable, Optional

from config import ConfigManager, THEMES
from speed_tracker import SpeedTracker

# Windows API Constants for tool window styling
GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_APPWINDOW = 0x00040000


class FloatingMeter(tk.Tk):
    """Floating, draggable, always-on-top network speed overlay."""

    def __init__(self, config: ConfigManager, speed_tracker: SpeedTracker, on_quit_callback: Optional[Callable] = None):
        super().__init__()

        self.config = config
        self.speed_tracker = speed_tracker
        self.on_quit_callback = on_quit_callback

        self._drag_start_x = 0
        self._drag_start_y = 0
        self._is_dragging = False

        self._init_window()
        self._build_ui()
        self._apply_theme()
        self._setup_bindings()
        self._setup_context_menu()

        # Start speed update loop
        self.update_speed()

    def _init_window(self) -> None:
        """Configures frameless, always-on-top, toolwindow attributes."""
        self.title("Internet Speed Meter")

        # Frameless and Always-on-top
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        # Transparency
        opacity = float(self.config.get("opacity", 0.90))
        self.attributes("-alpha", opacity)

        # Restore saved position
        x = int(self.config.get("pos_x", 100))
        y = int(self.config.get("pos_y", 100))
        
        # Screen bounds validation
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        if x < 0 or x > screen_w - 50:
            x = max(20, screen_w - 200)
        if y < 0 or y > screen_h - 50:
            y = 50

        self.geometry(f"+{x}+{y}")

        # Set Windows ToolWindow style to remove from Taskbar and Alt-Tab
        self.after(10, self._apply_windows_styles)

    def _apply_windows_styles(self) -> None:
        """Applies Windows API styles to hide window from taskbar completely."""
        try:
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            if not hwnd:
                hwnd = self.winfo_id()
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style = (style | WS_EX_TOOLWINDOW) & ~WS_EX_APPWINDOW
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        except Exception as e:
            print(f"Failed to apply Windows style: {e}")

    def _build_ui(self) -> None:
        """Constructs the visual widgets inside the floating meter."""
        self.main_frame = tk.Frame(self, bd=1, relief="solid")
        self.main_frame.pack(fill="both", expand=True)

        self.inner_frame = tk.Frame(self.main_frame, padx=8, pady=4)
        self.inner_frame.pack(fill="both", expand=True)

        is_compact = self.config.get("compact_mode", False)

        if is_compact:
            self._build_compact_ui()
        else:
            self._build_detailed_ui()

    def _build_detailed_ui(self) -> None:
        """Constructs two-row detailed layout."""
        # Clear inner frame
        for child in self.inner_frame.winfo_children():
            child.destroy()

        # Row 0: Download Speed (⯆ DL)
        self.dl_icon_label = tk.Label(
            self.inner_frame,
            text="⯆",
            font=("Segoe UI", 10, "bold")
        )
        self.dl_icon_label.grid(row=0, column=0, sticky="w", padx=(0, 4), pady=(1, 1))

        self.dl_tag_label = tk.Label(
            self.inner_frame,
            text="DL",
            font=("Segoe UI", 8, "bold")
        )
        self.dl_tag_label.grid(row=0, column=1, sticky="w", padx=(0, 6), pady=(1, 1))

        self.dl_val_label = tk.Label(
            self.inner_frame,
            text="0.0",
            font=("Segoe UI Semibold", 10, "bold"),
            anchor="e",
            width=6
        )
        self.dl_val_label.grid(row=0, column=2, sticky="e", padx=(0, 2), pady=(1, 1))

        self.dl_unit_label = tk.Label(
            self.inner_frame,
            text="KB/s",
            font=("Segoe UI", 8),
            anchor="w",
            width=5
        )
        self.dl_unit_label.grid(row=0, column=3, sticky="w", padx=(0, 0), pady=(1, 1))

        # Row 1: Upload Speed (⯅ UL)
        self.ul_icon_label = tk.Label(
            self.inner_frame,
            text="⯅",
            font=("Segoe UI", 10, "bold")
        )
        self.ul_icon_label.grid(row=1, column=0, sticky="w", padx=(0, 4), pady=(1, 1))

        self.ul_tag_label = tk.Label(
            self.inner_frame,
            text="UL",
            font=("Segoe UI", 8, "bold")
        )
        self.ul_tag_label.grid(row=1, column=1, sticky="w", padx=(0, 6), pady=(1, 1))

        self.ul_val_label = tk.Label(
            self.inner_frame,
            text="0.0",
            font=("Segoe UI Semibold", 10, "bold"),
            anchor="e",
            width=6
        )
        self.ul_val_label.grid(row=1, column=2, sticky="e", padx=(0, 2), pady=(1, 1))

        self.ul_unit_label = tk.Label(
            self.inner_frame,
            text="KB/s",
            font=("Segoe UI", 8),
            anchor="w",
            width=5
        )
        self.ul_unit_label.grid(row=1, column=3, sticky="w", padx=(0, 0), pady=(1, 1))

        # Row 2 (Optional lock indicator badge)
        self.lock_indicator = tk.Label(
            self.inner_frame,
            text="🔒" if self.config.get("locked", False) else "",
            font=("Segoe UI", 6)
        )
        self.lock_indicator.grid(row=0, column=4, rowspan=2, sticky="ns", padx=(4, 0))

    def _build_compact_ui(self) -> None:
        """Constructs compact single-line layout."""
        for child in self.inner_frame.winfo_children():
            child.destroy()

        # Single Row: ⯆ 0.0 KB/s  ⯅ 0.0 KB/s
        self.dl_icon_label = tk.Label(self.inner_frame, text="⯆", font=("Segoe UI", 9, "bold"))
        self.dl_icon_label.grid(row=0, column=0, sticky="w", padx=(0, 2))

        self.dl_tag_label = tk.Label(self.inner_frame, text="", font=("Segoe UI", 1))
        
        self.dl_val_label = tk.Label(self.inner_frame, text="0.0", font=("Segoe UI Semibold", 9, "bold"), anchor="e")
        self.dl_val_label.grid(row=0, column=1, sticky="e", padx=(0, 1))

        self.dl_unit_label = tk.Label(self.inner_frame, text="KB/s", font=("Segoe UI", 8), anchor="w")
        self.dl_unit_label.grid(row=0, column=2, sticky="w", padx=(0, 6))

        self.ul_icon_label = tk.Label(self.inner_frame, text="⯅", font=("Segoe UI", 9, "bold"))
        self.ul_icon_label.grid(row=0, column=3, sticky="w", padx=(0, 2))

        self.ul_tag_label = tk.Label(self.inner_frame, text="", font=("Segoe UI", 1))

        self.ul_val_label = tk.Label(self.inner_frame, text="0.0", font=("Segoe UI Semibold", 9, "bold"), anchor="e")
        self.ul_val_label.grid(row=0, column=4, sticky="e", padx=(0, 1))

        self.ul_unit_label = tk.Label(self.inner_frame, text="KB/s", font=("Segoe UI", 8), anchor="w")
        self.ul_unit_label.grid(row=0, column=5, sticky="w", padx=(0, 0))

        self.lock_indicator = tk.Label(
            self.inner_frame,
            text="🔒" if self.config.get("locked", False) else "",
            font=("Segoe UI", 6)
        )
        self.lock_indicator.grid(row=0, column=6, sticky="ns", padx=(3, 0))

    def _apply_theme(self) -> None:
        """Applies colors based on currently active theme."""
        colors = self.config.get_theme_colors()

        bg = colors["bg"]
        border = colors["border"]
        dl_color = colors["dl_color"]
        ul_color = colors["ul_color"]
        text_color = colors["text_color"]
        muted_color = colors["muted_color"]

        self.configure(bg=border)
        self.main_frame.configure(bg=border, highlightbackground=border, highlightcolor=border)
        self.inner_frame.configure(bg=bg)

        # Labels styling
        self.dl_icon_label.configure(bg=bg, fg=dl_color)
        self.dl_tag_label.configure(bg=bg, fg=muted_color)
        self.dl_val_label.configure(bg=bg, fg=dl_color)
        self.dl_unit_label.configure(bg=bg, fg=text_color)

        self.ul_icon_label.configure(bg=bg, fg=ul_color)
        self.ul_tag_label.configure(bg=bg, fg=muted_color)
        self.ul_val_label.configure(bg=bg, fg=ul_color)
        self.ul_unit_label.configure(bg=bg, fg=text_color)

        self.lock_indicator.configure(bg=bg, fg=muted_color)

    def _setup_bindings(self) -> None:
        """Configures mouse drag, click, and double-click handlers."""
        widgets = [
            self,
            self.main_frame,
            self.inner_frame,
            self.dl_icon_label,
            self.dl_tag_label,
            self.dl_val_label,
            self.dl_unit_label,
            self.ul_icon_label,
            self.ul_tag_label,
            self.ul_val_label,
            self.ul_unit_label,
            self.lock_indicator
        ]

        for w in widgets:
            w.bind("<Button-1>", self._on_drag_start)
            w.bind("<B1-Motion>", self._on_drag_motion)
            w.bind("<ButtonRelease-1>", self._on_drag_end)
            w.bind("<Button-3>", self._show_context_menu)
            w.bind("<Double-Button-1>", self._toggle_compact_mode)

    def _on_drag_start(self, event: tk.Event) -> None:
        """Records initial coordinates when dragging starts."""
        if self.config.get("locked", False):
            return
        self._drag_start_x = event.x_root - self.winfo_x()
        self._drag_start_y = event.y_root - self.winfo_y()
        self._is_dragging = True

    def _on_drag_motion(self, event: tk.Event) -> None:
        """Moves window as cursor moves."""
        if self.config.get("locked", False) or not self._is_dragging:
            return

        new_x = event.x_root - self._drag_start_x
        new_y = event.y_root - self._drag_start_y

        # Snap to screen edges if enabled
        if self.config.get("snap_to_edges", True):
            snap_dist = 16
            screen_w = self.winfo_screenwidth()
            screen_h = self.winfo_screenheight()
            win_w = self.winfo_width()
            win_h = self.winfo_height()

            # Snap Left / Right
            if abs(new_x) < snap_dist:
                new_x = 4
            elif abs(new_x + win_w - screen_w) < snap_dist:
                new_x = screen_w - win_w - 4

            # Snap Top / Bottom
            if abs(new_y) < snap_dist:
                new_y = 4
            elif abs(new_y + win_h - screen_h) < snap_dist:
                new_y = screen_h - win_h - 4

        self.geometry(f"+{new_x}+{new_y}")

    def _on_drag_end(self, event: tk.Event) -> None:
        """Saves final position to config file."""
        if not self._is_dragging:
            return
        self._is_dragging = False
        self.config.set("pos_x", self.winfo_x(), save_immediately=False)
        self.config.set("pos_y", self.winfo_y(), save_immediately=True)

    def _toggle_compact_mode(self, event: Optional[tk.Event] = None) -> None:
        """Toggles between compact horizontal pill and detailed 2-line mode."""
        current = self.config.get("compact_mode", False)
        self.config.set("compact_mode", not current)
        if not current:
            self._build_compact_ui()
        else:
            self._build_detailed_ui()
        self._apply_theme()
        self._setup_bindings()

    def _setup_context_menu(self) -> None:
        """Constructs right-click context menu."""
        self.context_menu = Menu(self, tearoff=0)

        # Lock toggle
        self.context_menu.add_command(
            label="🔒 Unlock Position" if self.config.get("locked", False) else "🔓 Lock Position",
            command=self.toggle_lock
        )

        # Compact mode toggle
        self.context_menu.add_command(
            label="📐 Switch Layout Mode",
            command=self._toggle_compact_mode
        )

        self.context_menu.add_separator()

        # Theme Submenu
        theme_menu = Menu(self.context_menu, tearoff=0)
        for theme_key, theme_data in THEMES.items():
            theme_menu.add_command(
                label=theme_data["name"],
                command=lambda k=theme_key: self.set_theme(k)
            )
        self.context_menu.add_cascade(label="🎨 Themes", menu=theme_menu)

        # Opacity Submenu
        opacity_menu = Menu(self.context_menu, tearoff=0)
        for op in [1.0, 0.90, 0.75, 0.60, 0.40]:
            opacity_menu.add_command(
                label=f"{int(op * 100)}%",
                command=lambda o=op: self.set_opacity(o)
            )
        self.context_menu.add_cascade(label="🔍 Opacity", menu=opacity_menu)

        # Speed Units Submenu
        unit_menu = Menu(self.context_menu, tearoff=0)
        unit_menu.add_command(label="Bytes/s (KB/s, MB/s)", command=lambda: self.set_unit_mode("bytes"))
        unit_menu.add_command(label="Bits/s (Kbps, Mbps)", command=lambda: self.set_unit_mode("bits"))
        self.context_menu.add_cascade(label="📊 Speed Units", menu=unit_menu)

        # Refresh Rate Submenu
        refresh_menu = Menu(self.context_menu, tearoff=0)
        refresh_menu.add_command(label="0.5 Seconds (Fast)", command=lambda: self.set_refresh_rate(500))
        refresh_menu.add_command(label="1.0 Second (Default)", command=lambda: self.set_refresh_rate(1000))
        refresh_menu.add_command(label="2.0 Seconds (Eco)", command=lambda: self.set_refresh_rate(2000))
        self.context_menu.add_cascade(label="⚡ Refresh Rate", menu=refresh_menu)

        self.context_menu.add_separator()

        self.context_menu.add_command(label="📈 Data Usage Stats", command=self.show_stats)
        self.context_menu.add_command(label="📍 Reset Position", command=self.reset_position)
        self.context_menu.add_command(label="👁 Hide Meter (Tray Only)", command=self.hide_meter)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="❌ Exit", command=self.quit_app)

    def _show_context_menu(self, event: tk.Event) -> None:
        """Displays context menu on right click."""
        # Refresh the Lock/Unlock label
        is_locked = self.config.get("locked", False)
        self.context_menu.entryconfigure(0, label="🔓 Unlock Position" if is_locked else "🔒 Lock Position")
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def toggle_lock(self) -> None:
        """Toggles dragging lock state."""
        new_state = not self.config.get("locked", False)
        self.config.set("locked", new_state)
        self.lock_indicator.configure(text="🔒" if new_state else "")

    def set_theme(self, theme_key: str) -> None:
        """Updates active theme and repaints UI."""
        self.config.set("theme", theme_key)
        self._apply_theme()

    def set_opacity(self, opacity: float) -> None:
        """Updates window alpha transparency."""
        self.config.set("opacity", opacity)
        self.attributes("-alpha", opacity)

    def set_unit_mode(self, mode: str) -> None:
        """Switches between Bytes/s and Bits/s."""
        self.config.set("unit_mode", mode)

    def set_refresh_rate(self, ms: int) -> None:
        """Updates refresh rate interval."""
        self.config.set("refresh_interval_ms", ms)

    def reset_position(self) -> None:
        """Resets meter to top right of screen."""
        screen_w = self.winfo_screenwidth()
        new_x = screen_w - 220
        new_y = 50
        self.geometry(f"+{new_x}+{new_y}")
        self.config.set("pos_x", new_x, save_immediately=False)
        self.config.set("pos_y", new_y, save_immediately=True)

    def show_stats(self) -> None:
        """Displays session traffic statistics."""
        data = self.speed_tracker.get_formatted_speeds(self.config.get("unit_mode", "bytes"))
        msg = (
            f"📊 Session Network Statistics:\n\n"
            f"📥 Total Downloaded: {data['session_dl']}\n"
            f"📤 Total Uploaded: {data['session_ul']}\n"
            f"🌐 Total Traffic: {data['session_total']}\n"
        )
        messagebox.showinfo("Internet Speed Meter - Data Usage", msg)

    def hide_meter(self) -> None:
        """Hides the floating meter (accessible via system tray)."""
        self.withdraw()
        self.config.set("visible", False)

    def show_meter(self) -> None:
        """Restores and brings the floating meter to the foreground."""
        self.deiconify()
        self.attributes("-topmost", True)
        self.config.set("visible", True)

    def update_speed(self) -> None:
        """Periodic loop to update speed readings."""
        try:
            self.speed_tracker.update()
            unit_mode = self.config.get("unit_mode", "bytes")
            stats = self.speed_tracker.get_formatted_speeds(unit_mode)

            self.dl_val_label.configure(text=stats["dl_val"])
            self.dl_unit_label.configure(text=stats["dl_unit"])
            self.ul_val_label.configure(text=stats["ul_val"])
            self.ul_unit_label.configure(text=stats["ul_unit"])

            # Re-assert topmost to handle full-screen games/windows
            self.attributes("-topmost", True)
        except Exception as e:
            print(f"Error in speed update: {e}")

        interval = int(self.config.get("refresh_interval_ms", 1000))
        self.after(interval, self.update_speed)

    def quit_app(self) -> None:
        """Exits the application completely."""
        if self.on_quit_callback:
            self.on_quit_callback()
        self.destroy()
