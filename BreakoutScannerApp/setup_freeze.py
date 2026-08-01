"""
cx_Freeze build script for Breakout Scanner Global Markets (Windows MSI).

Freezes the app (full Python runtime + every dependency) into a
self-contained bundle, then wraps it into an MSI installer. Nothing
needs to be pre-installed on the end user's machine.

Usage (on Windows, with requirements installed):
    pip install cx_Freeze
    python setup_freeze.py bdist_msi

Output lands in build/ and dist/.
"""

from cx_Freeze import setup, Executable

APP_NAME = "BreakoutScannerIndianMarket"
APP_TITLE = "Breakout Scanner Global Markets"
VERSION = "2.0.1"
AUTHOR = "Yash Jani"
DESCRIPTION = "Breakout Scanner Global Markets - multi-market NSE/TSX/NYSE/LSE/... breakout scanner"

# Fixed GUID so future versions upgrade in-place instead of installing side by side.
UPGRADE_CODE = "{7E5A9F3C-4B2D-4F1A-9C3E-1A2B3C4D5E6F}"

build_exe_options = {
    "packages": [
        "pandas", "numpy", "yfinance", "PyQt5", "reportlab", "openpyxl",
        "requests", "pytz",
    ],
    "excludes": ["tkinter", "test", "unittest"],
    "include_msvcr": True,
}

# Desktop + Start Menu shortcuts pointing at the installed exe.
shortcut_table = [
    (
        "DesktopShortcut", "DesktopFolder", APP_TITLE, "TARGETDIR",
        f"[TARGETDIR]{APP_NAME}.exe", None, None, None, None, None, None, "TARGETDIR",
    ),
    (
        "StartMenuShortcut", "ProgramMenuFolder", APP_TITLE, "TARGETDIR",
        f"[TARGETDIR]{APP_NAME}.exe", None, None, None, None, None, None, "TARGETDIR",
    ),
]

bdist_msi_options = {
    "data": {"Shortcut": shortcut_table},
    "upgrade_code": UPGRADE_CODE,
    "add_to_path": False,
    "initial_target_dir": rf"[ProgramFilesFolder]\{APP_TITLE}",
    "summary_data": {
        "author": AUTHOR,
        "comments": "Installs Breakout Scanner Global Markets and all required dependencies.",
    },
}

executables = [
    Executable(
        "breakout_scanner_app.py",
        base="Win32GUI",
        target_name=f"{APP_NAME}.exe",
    )
]

setup(
    name=APP_NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options,
    },
    executables=executables,
)
