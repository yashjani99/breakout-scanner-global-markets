# Breakout Scanner Global Markets — App v2.0.4

GUI wrapper around the scanning logic from `YouTuber_Stock_Scanner_Gujarati_FINAL.ipynb` and
`YouTuber_Stock_Scanner_TSX_FINAL.ipynb`, generalized to run against any market with free Yahoo
Finance data.

## What it does

1. On launch, shows a splash screen for 5 seconds: title **"Breakout Scanner Global Markets"**,
   **"App v2.0.4"** version tag, a rotating circular loader, and **"Developed by Yash Jani"** at
   the bottom.
   The scan for the default strategy/market (Breakout / India NSE) starts in the background
   during this screen.
2. Opens the main window (standard OS title bar with minimize / maximize / close) with a
   **strategy picker**, a **market picker**, scan progress, and results in a sortable table.
3. **Generate Excel** and **Generate PDF** buttons export the current results via a save dialog.
4. **Scan** re-runs the scan for whichever strategy/market combination is selected.

### Strategies

| Strategy | Rule | Columns |
|---|---|---|
| Breakout (DMA + CAR) | Price above 30/50/200-day moving averages, with a strengthening Cumulative Average Return | Date, Stock, CMP, 30/50/200 DMA, 200 DMA Dist %, SL, T1, T2, T3, CAR Status, Action |
| RSI 5-Star | Monthly RSI > 60, Weekly RSI > 60, Daily RSI pullback near 40 (the "signal candle"), entry on breakout above that candle's high | Date, Stock, CMP, Monthly RSI, Weekly RSI, Signal Date, Entry, SL, T1 (RSI 60 Est.), Action |
| Confluence (Both) | A stock must pass the Breakout and RSI 5-Star filters at once (one data download per ticker, not two) | Date, Stock, CMP, 30/50/200 DMA, 200 DMA Dist %, Monthly RSI, Weekly RSI, Signal Date, SL, T1, T2, T3, CAR Status, Action |

For RSI 5-Star: Stop Loss is the lowest low of the 10 days up to the signal candle, and T1 is
solved from Wilder's RSI formula for the price that would put the next daily RSI reading at 60
(never below the current price - see `scan_rsi_five_star()` in `breakout_scanner_app.py` for the
exact fallback logic). A 3-5 bar trailing stop once in profit is a trade-management choice, not
something a one-shot scan computes, so it's surfaced as a status-bar tip rather than a column.

For Confluence: Stop Loss is whichever of the two strategies' stop levels is tighter (closer to
the current price), and T1/T2/T3 reuse the Breakout strategy's risk-multiple convention off that
combined stop, so the numbers stay simple to read even though two independent setups agree here.

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
| `scanner_core.py` | The scanning logic itself (markets, strategies, no GUI dependency) - imported by the app, and clonable standalone by headless callers like the website's daily scan job |
| `requirements.txt` | Runtime dependencies (GUI app) |
| `requirements-headless.txt` | Minimal deps for `scanner_core.py` alone (no PyQt5/reportlab/openpyxl) |
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

Produces `dist\BreakoutScannerGlobalMarkets.exe` (standalone) and `dist\*.msi`. This x64 build
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
uploads each installer as a workflow artifact, and a final `release` job auto-publishes all four
as a GitHub Release (replacing any existing release/tag with the same name).

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
