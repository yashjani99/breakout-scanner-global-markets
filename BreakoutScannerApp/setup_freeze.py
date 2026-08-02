"""
Unified cx_Freeze build script for Breakout Scanner Global Markets.

Freezes the app (full Python runtime + every dependency) into a
self-contained bundle, then wraps it into the native installer format
for whichever OS you run this on. Nothing needs to be pre-installed on
the end user's machine in any case.

Run the matching command ON EACH TARGET OS (you cannot cross-build a
Windows MSI from Linux, a .deb from Windows, etc. - native packaging
tools only work for the OS they run on):

    Windows :  python setup_freeze.py bdist_msi
    Linux   :  python3 setup_freeze.py bdist_rpm      (needs rpmbuild)
               (for .deb, use build_deb.sh instead - see README)
    macOS   :  python3 setup_freeze.py bdist_dmg

Output lands in build/ and dist/.
"""

import sys
from cx_Freeze import setup, Executable

APP_NAME = "BreakoutScannerGlobalMarkets"
APP_TITLE = "Breakout Scanner Global Markets"
VERSION = "2.0.1"
AUTHOR = "Yash Jani"
DESCRIPTION = "Breakout Scanner Global Markets - multi-market NSE/TSX/NYSE/LSE/... breakout scanner"

# Fixed GUID so Windows upgrades happen in-place instead of installing side by side.
UPGRADE_CODE = "{7E5A9F3C-4B2D-4F1A-9C3E-1A2B3C4D5E6F}"

build_exe_options = {
    "packages": [
        "pandas", "numpy", "yfinance", "PyQt5", "reportlab", "openpyxl",
        "requests", "pytz",
    ],
    "excludes": ["tkinter", "test", "unittest"],
    "include_msvcr": True,
    # PyQt5's bundled Qt5 ships a PostgreSQL SQL-driver plugin linked against a
    # Homebrew libpq path from Riverbank's build machine that won't exist on
    # other systems. We never use QtSql, so just skip resolving/copying it.
    "bin_excludes": ["libpq.5.dylib"],
}

# --- Windows MSI -----------------------------------------------------------

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

# --- Linux RPM ---------------------------------------------------------

bdist_rpm_options = {
    "release": "1",
    "group": "Applications/Productivity",
    "vendor": AUTHOR,
    "packager": AUTHOR,
    # cx_Freeze bundles Python and dependencies. Only require minimal system libs for Qt5 GUI.
    "requires": [
        "libxcb >= 1.11",
        "libxkbcommon >= 0.5",
        "libxkbcommon-x11 >= 0.5",
        "dbus-libs >= 1.8",
        "mesa-libGL >= 18.0",
        "mesa-libEGL >= 18.0",
    ],
    "provides": ["breakout-scanner"],
    "conflicts": "BreakoutScannerIndianMarket",
}

# --- macOS .app / .dmg -----------------------------------------------------

bdist_mac_options = {
    "bundle_name": APP_TITLE,
}

bdist_dmg_options = {
    "applications_shortcut": True,
    "volume_label": APP_TITLE,
}

executables = [
    Executable(
        "breakout_scanner_app.py",
        base="Win32GUI" if sys.platform == "win32" else None,
        target_name=f"{APP_NAME}.exe" if sys.platform == "win32" else APP_NAME,
    )
]

setup(
    name=APP_NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    license="Proprietary",
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options,
        "bdist_rpm": bdist_rpm_options,
        "bdist_mac": bdist_mac_options,
        "bdist_dmg": bdist_dmg_options,
    },
    executables=executables,
)
