"""PyInstaller build script to compile Internet Speed Meter into a standalone Windows EXE."""
import os
import subprocess
import sys


def build():
    print("=== Building Standalone Internet Speed Meter EXE ===")
    project_dir = os.path.dirname(os.path.abspath(__file__))
    main_file = os.path.join(project_dir, "main.pyw")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name=InternetSpeedMeter",
        "--clean",
        main_file
    ]

    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=project_dir)

    if result.returncode == 0:
        exe_path = os.path.join(project_dir, "dist", "InternetSpeedMeter.exe")
        print("\n" + "=" * 50)
        print("Build Succeeded!")
        print(f"Standalone executable created at: {exe_path}")
        print("=" * 50)
    else:
        print("\nBuild Failed with return code:", result.returncode)


if __name__ == "__main__":
    build()
