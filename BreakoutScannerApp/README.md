# Breakout Scanner Global Markets — App v2.0.1

GUI wrapper around the scanning logic from `YouTuber_Stock_Scanner_Gujarati_FINAL.ipynb`,
generalized to run against any market with free Yahoo Finance data.

## What it does

1. On launch, shows a splash screen for 5 seconds: title **"Breakout Scanner Global Markets"**,
   **"App v2.0.1"** version tag, a rotating circular loader, and **"Developed by Yash Jani"** at
   the bottom.
   The scan for the default market (India/NSE) starts in the background during this screen.
2. Opens the main window (standard OS title bar with minimize / maximize / close) with a
   **market picker** dropdown, scan progress, and results in a sortable table (Date, Stock,
   CMP, 30/50/200 DMA, 200 DMA Dist %, SL, T1, T2, T3, CAR Status, Action).
3. **Generate Excel** and **Generate PDF** buttons export the current results via a save dialog.
4. **Scan** re-runs the scan for whichever market is selected.

### Markets included (16, all free via Yahoo Finance)

| Market | Suffix | Currency | Stocks |
|---|---|---|---|
| India (NSE) | `.NS` | INR | 210 |
| United States (NYSE/NASDAQ) | *(none)* | USD | 30 |
| Canada (TSX) | `.TO` | CAD | 30 |
| United Kingdom (LSE) | `.L` | GBP | 25 |
| Germany (XETRA) | `.DE` | EUR | 20 |
| France (Euronext Paris) | `.PA` | EUR | 20 |
| Netherlands (Euronext Amsterdam) | `.AS` | EUR | 12 |
| Switzerland (SIX) | `.SW` | CHF | 12 |
| Italy (Borsa Italiana) | `.MI` | EUR | 10 |
| Japan (Tokyo) | `.T` | JPY | 25 |
| Hong Kong (HKEX) | `.HK` | HKD | 20 |
| China A-Shares (Shanghai/Shenzhen) | `.SS`/`.SZ` | CNY | 15 |
| South Korea (KOSPI) | `.KS` | KRW | 15 |
| Singapore (SGX) | `.SI` | SGD | 10 |
| Australia (ASX) | `.AX` | AUD | 20 |
| Brazil (B3) | `.SA` | BRL | 15 |

Each list is a curated set of large, liquid blue-chip stocks for that exchange (not the full
index) — good enough to demo the scanner and easy to extend. To add more tickers or a new
market entirely, edit the `MARKETS` dict at the top of `breakout_scanner_app.py`; the scan
logic, table, and exports all work off that registry automatically.

## Files

| File | Purpose |
|---|---|
| `breakout_scanner_app.py` | The application (PyQt5) |
| `requirements.txt` | Runtime dependencies |
| `setup_freeze.py` | Unified `cx_Freeze` script — MSI (Windows), RPM (Linux), DMG (macOS) |
| `build_installer.bat` | Windows: installs deps, builds standalone EXE + MSI |
| `build_rpm.sh` | Linux (Fedora/RHEL/openSUSE, needs `rpmbuild`): builds `.rpm` |
| `build_deb.sh` | Linux (Debian/Ubuntu, needs `dpkg-deb`): builds `.deb` |
| `build_mac.sh` | macOS: builds `.app` + `.dmg` |

## Building

Every platform's installer is fully self-contained: `cx_Freeze`/`PyInstaller` bundle the Python
runtime and every dependency (PyQt5, pandas, yfinance, reportlab, openpyxl) into the app, so end
users install nothing extra.

### Windows

Requires Python 3.10–3.12 (64-bit) from python.org (not the Microsoft Store version). Then:

```
build_installer.bat
```

Produces `dist\BreakoutScannerIndianMarket.exe` (standalone) and `dist\*.msi`. This x64 build
also runs on ARM64 Windows 11 machines via Microsoft's built-in x64 emulation — PyQt5 has no
ARM64 Windows wheels, so a native ARM64 build isn't currently possible, but emulation covers it.

### Linux / macOS

Native installers can only be built on the OS they target. Run the matching script on that OS:

```
./build_rpm.sh   # Fedora/RHEL/openSUSE -> dist/*.rpm
./build_deb.sh   # Debian/Ubuntu        -> dist/*.deb
./build_mac.sh   # macOS                -> dist/*.dmg
```

### CI (all four at once)

`.github/workflows/build-installers.yml` runs all of the above on real Windows, Linux and macOS
GitHub-hosted runners on every push to `main` that touches this folder (or via manual dispatch),
and uploads each installer as a workflow artifact.

## Running from source (no build)

```
pip install -r requirements.txt
python breakout_scanner_app.py
```

## Notes

- Scanning a market's full ticker list via Yahoo Finance can take a few minutes depending on
  network speed and Yahoo's rate limiting; the progress bar tracks this.
- To change the upgrade behavior of future MSI releases, keep `UPGRADE_CODE` in
  `setup_freeze.py` fixed across versions and just bump `VERSION`.
