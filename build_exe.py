#!/usr/bin/env python3
"""
Build Script for Stock Scanner Pro EXE
Run this on Windows to create the standalone EXE
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and report status"""
    print(f"\n[{'*' * 60}]")
    print(f"  {description}")
    print(f"[{'*' * 60}]")
    try:
        subprocess.check_call(cmd, shell=True)
        print(f"✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        return False

def main():
    print("\n" + "=" * 80)
    print("          📈 STOCK SCANNER PRO - EXE BUILDER")
    print("=" * 80)

    if sys.platform != "win32":
        print("\n⚠️  WARNING: This script should be run on Windows!")
        print("   You are on:", sys.platform)
        response = input("\nContinue anyway? (y/n): ").lower()
        if response != 'y':
            sys.exit(1)

    steps = [
        (
            f"{sys.executable} -m pip install pyinstaller -q",
            "Installing PyInstaller"
        ),
        (
            f"{sys.executable} -m pip install yfinance pandas PyQt5 openpyxl -q",
            "Installing Required Dependencies"
        ),
        (
            f"{sys.executable} -m pyinstaller --onefile --windowed "
            f"--name Stock_Scanner_Pro --hidden-import=yfinance "
            f"--hidden-import=pandas --hidden-import=pytz "
            f"--hidden-import=requests stock_scanner_exe.py",
            "Building Standalone EXE"
        ),
    ]

    for cmd, description in steps:
        if not run_command(cmd, description):
            print(f"\n❌ Build failed at: {description}")
            sys.exit(1)

    exe_path = Path("dist/Stock_Scanner_Pro.exe")
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print("\n" + "=" * 80)
        print("                    ✅ BUILD SUCCESSFUL!")
        print("=" * 80)
        print(f"\n📁 EXE Location: {exe_path.absolute()}")
        print(f"📦 File Size: {size_mb:.1f} MB")
        print("\n📋 NEXT STEPS:")
        print("   1. Copy 'dist/Stock_Scanner_Pro.exe' to send to your father")
        print("   2. No dependencies needed - it runs standalone on any Windows PC")
        print("   3. Just double-click to run!")
        print("\n💡 Optional: Delete 'build' and '__pycache__' folders to save space")
        print("=" * 80 + "\n")
    else:
        print("\n❌ EXE file not found after build!")
        sys.exit(1)

if __name__ == "__main__":
    main()
