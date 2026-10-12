# 🚀 Live Floating Internet Speed Meter for Windows

A lightweight, modern, always-on-top desktop application for Windows that displays real-time internet download and upload speeds.

---

## ✨ Features

- **⚡ Real-time Speed Monitoring**: Live Download (⯆ DL) and Upload (⯅ UL) speeds measured accurately every second.
- **🪟 Always-On-Top Floating Overlay**: Floats effortlessly above all open applications, full-screen games, videos, and browsers.
- **🖱️ Freely Draggable & Position Memory**: Click and drag the meter anywhere on your screen (with multi-monitor support and screen edge snapping). Remembers its last saved position on restart.
- **🚫 Zero Taskbar Clutter**: Completely hidden from the main Windows Taskbar (`WS_EX_TOOLWINDOW`).
- **🗔 System Tray ("Hidden Taskbar")**: Runs in the Windows Notification Overflow Tray with a full management menu.
- **🔒 Lock Position**: Prevents accidental dragging when gaming or working.
- **🎨 5 Aesthetic Themes**:
  - *Cyber Dark* (Dark slate with Neon Cyan & Amber)
  - *Midnight Blue* (Deep Sapphire with Sky Blue & Violet)
  - *Matrix Green* (Emerald & Lime)
  - *Minimal Slate* (Subtle grey & pastel blue)
  - *Light Glass* (Crisp frosted white)
- **🔍 Adjustable Opacity / Transparency**: 100%, 90%, 75%, 60%, 40% for subtle non-intrusive HUD monitoring.
- **📊 Units Switching**: Switch seamlessly between **Bytes/s** (`KB/s`, `MB/s`, `GB/s`) and **Bits/s** (`Kbps`, `Mbps`, `Gbps`).
- **📐 Dual Layout Modes**:
  - *Detailed 2-Line Card*
  - *Compact Single-Line Pill* (Double-click anywhere on the meter to toggle!)
- **🚀 Start with Windows**: One-click startup toggle in settings.
- **📈 Session Data Usage**: Track total download & upload volume used in the current session.
- **📦 Standalone Portable EXE**: Ready to run as a single `.exe` without needing Python installed.

---

## 🎯 Controls & Shortcuts

| Action | Control |
| :--- | :--- |
| **Move Meter** | Left-Click and drag anywhere on the meter |
| **Quick Settings** | Right-Click anywhere on the meter or the System Tray icon |
| **Toggle Layout (Compact/Detailed)** | Double-Click on the meter |
| **Show / Hide Meter** | Left-Click or Right-Click on the System Tray icon |
| **Lock / Unlock Dragging** | Right-Click > *Lock Position* |

---

## 🚀 How to Run

### Option 1: Standalone Portable Executable (Recommended)
Run the pre-compiled executable:
```bash
dist\InternetSpeedMeter.exe
```

### Option 2: Silent Launch with PythonW (No Terminal Window)
Double-click `main.pyw` or run:
```powershell
pythonw main.pyw
```

### Option 3: Standard Terminal Launch
```powershell
python main.py
```

---

## 🛠️ Building Standalone `.exe`
To rebuild the standalone executable using PyInstaller:
```powershell
python build_exe.py
```
The output file will be generated in the `dist/` directory.

---

## 📋 System Requirements
- Windows 10 / Windows 11
- Python 3.10+ (if running from source) with `psutil`, `pystray`, `Pillow`
