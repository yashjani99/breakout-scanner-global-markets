# 📈 INSTITUTIONAL BREAKOUT SCANNER

**Professional Stock Screening Tool for Identifying High-Probability Trading Setups**

---

## 🎯 What This Does

This scanner helps identify stocks that are breaking out upward with:
- ✅ **Strong Uptrend Confirmation** (DMAs aligned: 30 > 50 > 200)
- ✅ **Positive Momentum** (CAR - Cumulative Average Return increasing)
- ✅ **Automatic Risk Management** (SL, T1, T2 targets pre-calculated)
- ✅ **Quality Scoring** (Ranked by technical strength)
- ✅ **Professional GUI** (Beautiful interface with live scanning)

---

## 📊 Strategy Explained

### Core Filtering Logic

The scanner uses **3-layer filtering**:

#### Layer 1: Price Action (YouTuber's Original Logic)
```
Current Price > 30-DMA ✓
Current Price > 50-DMA ✓
Current Price > 200-DMA ✓
```

#### Layer 2: Trend Confirmation (CAR Status)
```
Cumulative Average Return = POSITIVE
(Trend continuously upward for past 10 days)
```

#### Layer 3: Technical Confirmation (GPT Enhancements)
```
RSI(14) > 55 (Momentum)
ADX(14) > 20 (Trend Strength)
MACD Bullish Crossover (Trend Direction)
Volume Breakout (1.5× average volume)
```

---

## 💰 Entry/Exit Strategy

For **every stock found**, the scanner calculates:

```
Entry Price = Current Market Price (CMP)

Stop Loss (SL) = min(10-day swing low, 30-DMA)
                 (Protective level if trade goes wrong)

T1 (Target 1) = Entry + (2 × Risk)
                 (First profit-taking level)

T2 (Target 2) = Entry + (3 × Risk)
                 (Main profit target)

T3 (Target 3) = Entry + (5 × Risk)
                 (Extended upside target)

Risk = Entry - SL
Reward = T2 - Entry
Risk:Reward Ratio = Calculated automatically
```

### Example
```
Stock: INFY
Current Price (Entry): ₹2,500
10-Day Low: ₹2,450
Stop Loss: ₹2,445
Risk: ₹55

T1 = 2,500 + (2 × 55) = ₹2,610
T2 = 2,500 + (3 × 55) = ₹2,665
T3 = 2,500 + (5 × 55) = ₹2,775

Reward %: 6.6%
SL %: 2.2%
Ratio: 3:1 (Excellent!)
```

---

## 🚀 How to Use

### Option 1: GUI Application (Recommended)

1. **Install Dependencies:**
   ```bash
   pip install PyQt5 yfinance pandas openpyxl
   ```

2. **Run the App:**
   ```bash
   python breakout_scanner_gui.py
   ```

3. **Scan Stocks:**
   - Click "🔍 START SCAN"
   - Wait 5-10 minutes (downloads 2 years of data)
   - See results in beautiful table

4. **Export Results:**
   - Click "💾 EXPORT EXCEL"
   - Save and analyze further

---

### Option 2: Build as EXE (Windows)

**One-time Setup:**
```bash
pip install PyQt5 yfinance pandas openpyxl pyinstaller
```

**Build EXE:**
```bash
pyinstaller --onefile --windowed --name="BreakoutScanner" breakout_scanner_gui.py
```

**Run:**
- Navigate to `dist/` folder
- Double-click `BreakoutScanner.exe`
- Share with others (standalone app)

---

### Option 3: Google Colab (No Installation)

1. Upload `Combined_Scanner_SL_T1_T2.py` to Google Colab
2. Run the code
3. Download Excel results automatically
4. Takes ~5-10 minutes per run

---

## 📊 Output Explained

### Table Columns

| Column | What It Means |
|--------|---------------|
| **Stock** | Company ticker |
| **CMP** | Current Market Price (entry point) |
| **30/50/200 DMA** | Moving averages (confirm trend) |
| **Dist %** | How far from 200-DMA (lower = closer to trend) |
| **SL** | Stop Loss price |
| **SL %** | Risk as % of entry |
| **T1, T2** | Profit targets |
| **RSI** | Momentum indicator (0-100, >55 is strong) |
| **ADX** | Trend strength (0-100, >20 is trending) |
| **ATR %** | Volatility (daily price swing %) |
| **Trend** | Strong Uptrend or Weak |
| **Reward %** | Potential profit from T2 |
| **1M Ret %** | Last 30-day return |
| **Quality** | Overall score 0-100 (higher = better) |
| **Vol Break** | Volume spike (✓ = yes, ✗ = no) |
| **MACD** | Bullish crossover (✓ = yes, ✗ = no) |

---

## 🎛️ Customization

### GUI Settings

**RSI Threshold** (Default: 55)
- Lower (45): More signals, lower quality
- Higher (70): Fewer signals, higher quality

**ADX Threshold** (Default: 20)
- Lower (15): More trending stocks
- Higher (30): Only very strong trends

---

## 📈 Results Interpretation

### Quality Score Breakdown

| Quality | What It Means |
|---------|---------------|
| **80-100** | 🟢 EXCELLENT - Strongest signals |
| **70-79** | 🟡 GOOD - Quality breakouts |
| **60-69** | 🟠 FAIR - Multiple filters passed |
| **Below 60** | 🔴 WEAK - Few filters matched |

### Risk:Reward Ratio Interpretation

```
3:1 = ₹1 risk to make ₹3 profit (EXCELLENT)
2:1 = ₹1 risk to make ₹2 profit (GOOD)
1:1 = ₹1 risk to make ₹1 profit (FAIR)
< 1:1 = Risk > Reward (POOR - AVOID)
```

---

## ⚡ Key Features

✅ **Institutional-Grade Logic**
- Based on professional trading strategies
- Used by fund managers and traders

✅ **Automatic Risk Management**
- SL, T1, T2 pre-calculated
- No guesswork on exit levels

✅ **Quality Scoring**
- Stocks ranked by signal strength
- Focus on highest probability setups

✅ **Past Week Fallback**
- No results today? Shows past week's setups
- Never misses a trading opportunity

✅ **Multiple Indicators**
- DMAs, RSI, ADX, MACD, Volume, ATR
- Comprehensive confirmation

✅ **Professional Output**
- Beautiful GUI interface
- Excel export for analysis
- Ready for trading platform

---

## 📝 Files Included

| File | Purpose |
|------|---------|
| `breakout_scanner_gui.py` | Main GUI application |
| `Combined_Scanner_SL_T1_T2.py` | Google Colab version |
| `build_exe.bat` | Automated EXE builder (Windows) |
| `BUILD_EXE_INSTRUCTIONS.md` | Detailed build guide |
| `README.md` | This file |

---

## 🔧 Requirements

### For GUI/EXE
- Python 3.8+
- Windows 7 or later
- 2GB RAM minimum
- Internet connection (for data download)

### Dependencies
```
PyQt5 (GUI framework)
yfinance (Yahoo Finance data)
pandas (Data manipulation)
openpyxl (Excel export)
```

---

## ⚠️ Important Notes

1. **Internet Required**: App downloads 2 years of data for 200+ stocks
2. **First Scan Slow**: Takes 5-10 minutes (depends on internet speed)
3. **Subsequent Scans Faster**: Caching helps after first run
4. **Data Source**: Yahoo Finance (free, reliable)
5. **Not Financial Advice**: Use with your own analysis and risk management

---

## 🐛 Troubleshooting

### "No Internet" Error
- Check your WiFi connection
- Restart the app
- Try again

### "ModuleNotFoundError"
```bash
pip install PyQt5 yfinance pandas openpyxl
```

### Slow Scanning
- This is normal - downloading 2 years of data takes time
- Check progress bar
- Don't close the app during scan

### EXE Won't Run
- Make sure Python dependencies are installed
- Try building again with `build_exe.bat`
- Run in administrator mode

---

## 💡 Trading Tips

### Do's ✓
- Always follow your risk management rules
- Don't ignore the Stop Loss
- Use the Quality score to prioritize
- Backtest before trading with real money
- Follow proper position sizing

### Don'ts ✗
- Don't override the system
- Don't put stop loss too tight
- Don't trade all signals (filter by quality)
- Don't use money you can't afford to lose
- Don't blame the tool - trade with discipline

---

## 📞 Support

For issues or feature requests:
1. Check this README
2. Review BUILD_EXE_INSTRUCTIONS.md
3. Contact developer with error messages

---

## 📜 License

Educational use. Commercial use requires permission.

---

**Happy Trading! 📈**

*Remember: Past performance ≠ Future results. Always do your own research.*
