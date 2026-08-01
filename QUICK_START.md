# ⚡ QUICK START GUIDE (5 Minutes)

## Windows Users - Fastest Way

### Step 1: Download Python
- Visit https://www.python.org/downloads/
- Download Python 3.11 (latest)
- **Check: "Add Python to PATH"** during installation
- Click Install

### Step 2: Install Dependencies (Copy & Paste)
Open Command Prompt and paste:
```bash
pip install PyQt5 yfinance pandas openpyxl pyinstaller
```
Press Enter. Wait for completion.

### Step 3: Run the App
Option A - As Python Script:
```bash
python breakout_scanner_gui.py
```

Option B - Build as EXE (Recommended):
```bash
build_exe.bat
```
Then find `BreakoutScanner.exe` in the `dist` folder and double-click it.

---

## Mac/Linux Users

### Step 1: Install Python
```bash
brew install python3  # macOS
# OR
sudo apt-get install python3  # Linux
```

### Step 2: Install Dependencies
```bash
pip3 install PyQt5 yfinance pandas openpyxl
```

### Step 3: Run
```bash
python3 breakout_scanner_gui.py
```

---

## Using the App

### 1️⃣ Click "🔍 START SCAN"
- App starts downloading data for 200+ stocks
- This takes **5-10 minutes** (first time)
- Watch the progress bar

### 2️⃣ Results Appear
- Table shows stocks sorted by Quality Score
- Green rows = Excellent signals
- Blue rows = Good signals

### 3️⃣ Understand the Results

**Quality Score**
- 80+ = Strong signal, take it
- 60-79 = Good signal, consider it
- <60 = Weak signal, skip it

**SL (Stop Loss)**
- Where to exit if wrong
- Never ignore this!

**T1, T2 (Targets)**
- T1 = First profit target
- T2 = Main profit target

### 4️⃣ Export to Excel
- Click "💾 EXPORT EXCEL"
- Save the file
- Analyze further with your broker

---

## First Run Checklist

✅ Python installed?
✅ Dependencies installed? (`pip install ...`)
✅ Internet connection on?
✅ Clicked "START SCAN"?
✅ Waited for progress bar to complete?
✅ Results showing in table?

---

## What to Do With Results

1. **Review Quality Score**
   - Only trade Quality > 70

2. **Check Risk:Reward Ratio**
   - Want 3:1 or better

3. **Verify in Your Broker**
   - Chart out the stock
   - Confirm the trend
   - Add to watchlist

4. **Plan Your Trade**
   - Entry: At CMP or breakout
   - SL: At given SL price
   - Target: T1 or T2

5. **Execute When Ready**
   - Follow risk management
   - Don't deviate from plan
   - Take profits at targets

---

## Common Issues

### "Python not found"
- Install Python from python.org
- Check "Add Python to PATH"
- Restart Command Prompt

### "ModuleNotFoundError"
```bash
pip install PyQt5 yfinance pandas openpyxl
```

### App is Slow / Freezing
- This is normal during first scan
- Downloading takes 5-10 minutes
- Don't close the app

### No Results Found
- Market conditions may not be favorable
- Check past week results (automatic fallback)
- Try adjusting RSI/ADX thresholds

---

## Next Steps

1. ✅ Get this working
2. 📊 Understand the indicators (read README.md)
3. 📈 Backtest on historical data
4. 💰 Start with small position sizes
5. 📝 Keep trading journal

---

## Need Help?

📖 Read: **README.md** (Full guide)
🔨 Build Help: **BUILD_EXE_INSTRUCTIONS.md**
⚙️ Issues: Check Python installation

---

**You're all set! Happy Trading! 📈**
