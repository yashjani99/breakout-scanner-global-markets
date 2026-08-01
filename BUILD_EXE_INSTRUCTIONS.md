# 📦 Build Breakout Scanner as EXE File

## Prerequisites

### 1. Install Python Dependencies

```bash
pip install PyQt5 yfinance pandas openpyxl
```

### 2. Install PyInstaller

```bash
pip install pyinstaller
```

---

## Build Options

### **Option A: Simple One-File Executable (Recommended)**

```bash
pyinstaller --onefile --windowed --icon=icon.ico breakout_scanner_gui.py
```

This creates a single `.exe` file that can be shared and run on any Windows PC.

**Location:** `dist/breakout_scanner_gui.exe`

---

### **Option B: Folder-Based Executable (Smaller Download)**

```bash
pyinstaller --windowed breakout_scanner_gui.py
```

This creates a folder with the executable and dependencies.

**Location:** `dist/breakout_scanner_gui/breakout_scanner_gui.exe`

---

### **Option C: With Console (For Debugging)**

```bash
pyinstaller --onefile breakout_scanner_gui.py
```

Shows console window for error messages.

---

## Usage

1. **Run from Terminal:**
   ```bash
   python breakout_scanner_gui.py
   ```

2. **Run the EXE (After building):**
   - Double-click `breakout_scanner_gui.exe` in the `dist` folder

---

## App Features

✅ **Scan 200+ NSE Stocks** for breakout signals  
✅ **Customizable Filters**: RSI & ADX thresholds  
✅ **Real-Time Progress**: See scanning progress  
✅ **Professional Table**: All results displayed beautifully  
✅ **Quality Scoring**: Stocks ranked 0-100  
✅ **Export to Excel**: Save results for further analysis  

---

## GUI Components

- **RSI Threshold Slider**: Adjust momentum filter (default: 55)
- **ADX Threshold Slider**: Adjust trend strength (default: 20)
- **START SCAN Button**: Begin stock screening
- **EXPORT EXCEL Button**: Save results
- **Progress Bar**: Real-time scanning progress
- **Results Table**: Sorted by quality score
- **Status Bar**: Summary statistics

---

## Output Columns Explained

| Column | Meaning |
|--------|---------|
| Stock | Stock ticker name |
| CMP | Current Market Price |
| 30/50/200 DMA | Moving averages |
| Dist % | Distance from 200 DMA |
| SL | Stop Loss level |
| T1, T2 | Target prices |
| RSI, ADX | Technical indicators |
| ATR % | Volatility |
| Reward % | Potential profit target |
| Quality | Score 0-100 |

---

## Troubleshooting

### "ModuleNotFoundError" when running EXE
- Make sure all dependencies are installed before building
- Rebuild using Option A with `--onefile`

### Scan takes too long
- Normal! Downloading 2 years of data for 200+ stocks takes 5-10 minutes
- Check Progress Bar for status

### Internet connection required
- Yes, the app downloads live data from Yahoo Finance

---

## System Requirements

- **Windows 7 or higher**
- **Internet Connection**
- **2GB RAM minimum**

---

## Advanced: Create a Desktop Shortcut

After building:
1. Navigate to `dist/breakout_scanner_gui.exe`
2. Right-click → Send to → Desktop (Create Shortcut)
3. Right-click shortcut → Properties
4. Change start directory to avoid file path issues

---

## Contact & Support

For issues or feature requests, contact your father or developer.

Happy Trading! 📈
