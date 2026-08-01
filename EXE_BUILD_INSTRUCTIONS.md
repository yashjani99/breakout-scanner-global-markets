# 📈 Stock Scanner Pro - EXE Build Instructions

## Quick Summary
I've created a **professional GUI application** that scans 210 NSE stocks for breakout signals with automatic SL, T1, T2 calculations.

To create the standalone **EXE file** for Windows, follow these steps:

---

## ⚙️ OPTION 1: Automatic Build (Easiest)

### Step 1: On Your Windows PC
1. Download these files to a folder:
   - `stock_scanner_exe.py`
   - `build_exe.py`

2. Open **Command Prompt** in that folder:
   - Shift + Right-Click → "Open PowerShell window here"
   - Or: `Win + R` → Type `cmd` → Navigate to folder

3. Run this command:
   ```
   python build_exe.py
   ```

4. Wait 1-2 minutes for the build to complete

5. Your EXE will be at: `dist\Stock_Scanner_Pro.exe`

---

## ⚙️ OPTION 2: Manual Build (Step by Step)

### Step 1: Install Python
- Download from: https://www.python.org/downloads/
- During installation, **CHECK: "Add Python to PATH"**
- Verify: Open Command Prompt and type `python --version`

### Step 2: Install Build Tools
Open Command Prompt and run:
```
python -m pip install pyinstaller yfinance pandas PyQt5 openpyxl
```

### Step 3: Create the EXE
In the folder with `stock_scanner_exe.py`, run:
```
python -m pyinstaller --onefile --windowed --name Stock_Scanner_Pro stock_scanner_exe.py
```

### Step 4: Find Your EXE
Look in: `dist\Stock_Scanner_Pro.exe`

---

## ⚙️ OPTION 3: Using Batch File (Windows Native)

1. Download: `BUILD_EXE_ON_WINDOWS.bat`
2. Place it in the same folder as `stock_scanner_exe.py`
3. Double-click the `.bat` file
4. Wait for completion

---

## ✅ After Building

### Share with Your Father:
1. Copy `dist\Stock_Scanner_Pro.exe` to a USB drive or email it
2. He just needs to double-click it on ANY Windows PC
3. **NO installation needed!** ✨

### Cleanup (Optional):
You can delete these folders to save space:
- `build/`
- `__pycache__/`
- `*.spec` files

---

## 🎯 How to Use the Application

### When Your Father Opens It:

1. **Main Window Opens** - Shows professional dark-themed GUI
2. **Click "▶️ Start Scanning"** - Begins scanning 210 NSE stocks
3. **Progress Bar** - Shows scanning progress (0-100%)
4. **Results Display** - Shows all matched stocks in a table with:
   - Stock name
   - Current price
   - Stop Loss (SL) level
   - SL risk percentage
   - Target 1, 2, 3 (T1, T2, T3)
   - Risk in rupees
   - Target profit percentage
   - Risk:Reward ratio
   - Trend status (Strong Uptrend/Weak)
   - CAR status

5. **Click "💾 Export to Excel"** - Saves results to Excel file

---

## 📊 Features

✅ **Professional GUI**
- Dark theme with teal/green buttons
- Responsive table with sortable columns
- Real-time progress tracking

✅ **Complete Analysis**
- 30, 50, 200-day moving average alignment
- CAR (Cumulative Average Return) confirmation
- Automatic SL calculation (10-day swing low)
- T1, T2, T3 target calculation
- Risk:Reward ratio
- Trend detection

✅ **Easy Export**
- One-click Excel export
- Timestamped filenames
- All data included

✅ **No Dependencies**
- Single EXE file
- No Python installation needed
- Works on any Windows 7+
- File size: ~150-200 MB

---

## 🔧 Troubleshooting

### Problem: "Python is not installed"
**Solution:** Download from python.org and install with "Add to PATH" checked

### Problem: "Module not found" during build
**Solution:** Run this first:
```
python -m pip install --upgrade pip
python -m pip install pyinstaller yfinance pandas PyQt5 openpyxl
```

### Problem: Build takes very long
**Solution:** This is normal (1-2 minutes). Don't close the command prompt.

### Problem: EXE doesn't run
**Solution:** 
1. Make sure .NET Framework is installed on Windows
2. Try running from Command Prompt to see error messages
3. Rebuild with Option 1 or 2

---

## 📦 What's Included in EXE

The standalone EXE includes:
- Python 3.9+ runtime
- All stock scanning logic
- PyQt5 GUI framework
- yfinance for data download
- pandas for data processing
- Excel export capability

**Total size:** ~150-200 MB (one-time download)
**After first run:** All data cached, runs much faster

---

## 🎓 Technical Details

**Built with:**
- Python 3.9+
- PyQt5 (Professional GUI)
- yfinance (Stock data)
- pandas (Data processing)
- PyInstaller (EXE creation)

**Scans:**
- 210 major NSE stocks
- 2 years of daily data
- Updates in real-time

**Calculations:**
- Moving averages (30, 50, 200 DMA)
- Swing low (10-day minimum)
- Risk management ratios
- Trend confirmation (CAR)

---

## ❓ Questions?

If the build fails:
1. Make sure Python 3.8+ is installed
2. Check internet connection (needs to download packages)
3. Try Option 2 (manual step by step)
4. Check Command Prompt for error messages

---

## 📝 File Checklist

Before building, make sure you have:
- ✅ `stock_scanner_exe.py` - Main application
- ✅ `build_exe.py` - Build script (Option 1)
- ✅ `BUILD_EXE_ON_WINDOWS.bat` - Batch builder (Option 3)
- ✅ This README file

---

**Ready to build? Choose one option above and get started!** 🚀
