# =========================================================================
# INSTITUTIONAL GRADE BREAKOUT SCANNER + SL, T1, T2 TARGETS
# YouTuber's Original Filters + GPT Enhancements (SL, T1, T2, RSI, ADX, MACD)
# =========================================================================

import yfinance as yf
import pandas as pd
import warnings
import logging

logging.getLogger('yfinance').setLevel(logging.CRITICAL)
warnings.filterwarnings('ignore')

# =========================================================================
# HELPER FUNCTIONS FOR TECHNICAL INDICATORS
# =========================================================================

def calculate_rsi(data, period=14):
    """Calculate RSI (Relative Strength Index)"""
    close = data['Close'].squeeze()
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def calculate_adx(data, period=14):
    """Calculate ADX (Average Directional Index)"""
    high = data['High'].squeeze()
    low = data['Low'].squeeze()
    close = data['Close'].squeeze()

    plus_dm = high.diff()
    minus_dm = -low.diff()

    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0

    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(period).mean()
    plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(period).mean() / atr)

    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.rolling(period).mean()

    return adx.iloc[-1]

def calculate_macd(data):
    """Calculate MACD (Moving Average Convergence Divergence)"""
    close = data['Close'].squeeze()
    exp1 = close.ewm(span=12, adjust=False).mean()
    exp2 = close.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()

    # Check if MACD just crossed above signal (bullish)
    macd_bullish = (macd.iloc[-1] > signal.iloc[-1]) and (macd.iloc[-2] <= signal.iloc[-2])

    return macd_bullish

def calculate_atr(data, period=14):
    """Calculate ATR (Average True Range)"""
    high = data['High'].squeeze()
    low = data['Low'].squeeze()
    close = data['Close'].squeeze()

    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(period).mean()
    atr_percent = (atr / close) * 100

    return atr_percent.iloc[-1]

# =========================================================================
# HELPER FUNCTION: SCAN FOR A SPECIFIC DATE
# =========================================================================

def scan_for_date(ticker_list, days_back=0):
    """
    Scans stocks for a specific date (days_back = 0 for today)
    Returns (results, scan_date_str)
    """
    results = []

    for ticker in ticker_list:
        try:
            data = yf.download(ticker, period="2y", interval="1d", progress=False)

            if data.empty or len(data) < 200:
                continue

            # Get data up to 'days_back' days ago
            if days_back > 0:
                if len(data) <= days_back:
                    continue
                data = data.iloc[:-days_back]

            close_prices = data['Close'].squeeze()

            dma_30 = close_prices.rolling(window=30).mean().iloc[-1]
            dma_50 = close_prices.rolling(window=50).mean().iloc[-1]
            dma_200 = close_prices.rolling(window=200).mean().iloc[-1]

            cmp = close_prices.iloc[-1]
            dist_200_dma = ((cmp - dma_200) / dma_200) * 100

            last_1y_data = data.tail(252)
            high_date = last_1y_data['High'].squeeze().idxmax()

            car_data = close_prices.loc[high_date:]

            if len(car_data) < 10:
                continue

            car_values = car_data.expanding().mean()
            last_10_car = car_values.tail(10)

            if last_10_car.is_monotonic_increasing:
                car_status = 'Positive'
            else:
                car_status = 'Negative'

            # YouTuber's strict filter
            if not ((cmp > dma_30) and (cmp > dma_50) and (cmp > dma_200) and (car_status == 'Positive')):
                continue

            # GPT Enhancements
            swing_low = data['Low'].tail(10).min()
            sl = min(swing_low, dma_30)
            entry = cmp
            risk = entry - sl

            if risk <= 0:
                continue

            t1 = entry + (2 * risk)
            t2 = entry + (3 * risk)
            t3 = entry + (5 * risk)

            reward_percent = ((t2 - entry) / entry) * 100
            sl_percent = ((entry - sl) / entry) * 100

            high_52 = data['High'].tail(252).max()
            dist_52 = ((high_52 - entry) / high_52) * 100

            returns = ((entry - close_prices.iloc[-21]) / close_prices.iloc[-21]) * 100

            if dma_30 > dma_50 > dma_200:
                trend = "Strong Uptrend"
            else:
                trend = "Weak"

            rsi = calculate_rsi(data, period=14)
            rsi_signal = rsi > 55

            try:
                adx = calculate_adx(data, period=14)
                adx_signal = adx > 25
            except:
                adx = None
                adx_signal = False

            try:
                macd_bullish = calculate_macd(data)
            except:
                macd_bullish = False

            within_52w_high = dist_52 < 10
            atr_percent = calculate_atr(data, period=14)

            volume = data['Volume'].squeeze()
            avg_volume = volume.rolling(20).mean().iloc[-1]
            today_volume = volume.iloc[-1]
            volume_breakout = today_volume > (1.5 * avg_volume)

            quality_score = 50
            if rsi_signal:
                quality_score += 15
            if adx_signal:
                quality_score += 15
            if macd_bullish:
                quality_score += 10
            if within_52w_high:
                quality_score += 5
            if volume_breakout:
                quality_score += 5

            scan_date = data.index[-1].strftime("%d-%m-%Y")

            results.append({
                'Date': scan_date,
                'Stock': ticker.replace('.NS', ''),
                'CMP': round(entry, 2),
                '30 DMA': round(dma_30, 2),
                '50 DMA': round(dma_50, 2),
                '200 DMA': round(dma_200, 2),
                '200 DMA Dist %': round(dist_200_dma, 2),
                '52W High Dist %': round(dist_52, 2),
                'RSI(14)': round(rsi, 2),
                'RSI Signal': rsi_signal,
                'ADX(14)': round(adx, 2) if adx else 'N/A',
                'ADX Signal': adx_signal,
                'MACD Bullish': macd_bullish,
                'Volume Breakout': volume_breakout,
                'ATR %': round(atr_percent, 2),
                'Trend': trend,
                'SL': round(sl, 2),
                'SL %': round(sl_percent, 2),
                'T1': round(t1, 2),
                'T2': round(t2, 2),
                'T3': round(t3, 2),
                'Risk': round(risk, 2),
                'Reward %': round(reward_percent, 2),
                '1M Return %': round(returns, 2),
                'CAR Status': car_status,
                'Quality Score': quality_score,
                'Action': '🟢 Positive Breakout'
            })

        except Exception:
            pass

    if results:
        df = pd.DataFrame(results)
        df = df.sort_values(by='Quality Score', ascending=False)
        scan_date_str = df['Date'].iloc[0]
        return df, scan_date_str
    else:
        return pd.DataFrame(), None

# =========================================================================
# MAIN SCANNER FUNCTION
# =========================================================================

def advanced_stock_scanner(ticker_list):
    """
    Scans stocks using YouTuber's original filters + GPT enhancements
    First tries today, if no match, scans past 1 week
    """
    print(f"📊 Scanning {len(ticker_list)} stocks for TODAY... Please wait.\n")

    # Scan for today
    today_results, today_date = scan_for_date(ticker_list, days_back=0)

    if not today_results.empty:
        return today_results, None, "TODAY"

    # If no today results, scan past week
    print("⚠️ No matches found for TODAY. Scanning past 1 week...\n")

    past_week_results = []
    past_week_dates = []

    for days_back in range(1, 6):  # Scan past 5 trading days
        week_results, week_date = scan_for_date(ticker_list, days_back=days_back)
        if not week_results.empty:
            past_week_results.append(week_results)
            past_week_dates.append(week_date)

    if past_week_results:
        combined_week = pd.concat(past_week_results, ignore_index=True)
        combined_week = combined_week.sort_values(by=['Date', 'Quality Score'], ascending=[False, False])
        return combined_week, past_week_dates, "PAST_WEEK"
    else:
        return pd.DataFrame(), None, None


# =========================================================================
# EXECUTION
# =========================================================================

my_stocks = [
    '360ONE.NS', 'ABB.NS', 'APLAPOLLO.NS', 'AUBANK.NS', 'ADANIENSOL.NS',
    'ADANIENT.NS', 'ADANIGREEN.NS', 'ADANIPORTS.NS', 'ADANIPOWER.NS', 'ABCAPITAL.NS',
    'ALKEM.NS', 'AMBER.NS', 'AMBUJACEM.NS', 'ANGELONE.NS', 'APOLLOHOSP.NS',
    'ASHOKLEY.NS', 'ASIANPAINT.NS', 'ASTRAL.NS', 'AUROPHARMA.NS', 'DMART.NS',
    'AXISBANK.NS', 'BSE.NS', 'BAJAJ-AUTO.NS', 'BAJFINANCE.NS', 'BAJAJFINSV.NS',
    'BAJAJHLDNG.NS', 'BANDHANBNK.NS', 'BANKBARODA.NS', 'BANKINDIA.NS', 'BDL.NS',
    'BEL.NS', 'BHARATFORG.NS', 'BHEL.NS', 'BPCL.NS', 'BHARTIARTL.NS',
    'BIOCON.NS', 'BLUESTARCO.NS', 'BOSCHLTD.NS', 'BRITANNIA.NS', 'CGPOWER.NS',
    'CANBK.NS', 'CDSL.NS', 'CHOLAFIN.NS', 'CIPLA.NS', 'COALINDIA.NS',
    'COCHINSHIP.NS', 'COFORGE.NS', 'COLPAL.NS', 'CAMS.NS', 'CONCOR.NS',
    'CROMPTON.NS', 'CUMMINSIND.NS', 'DLF.NS', 'DABUR.NS', 'DALBHARAT.NS',
    'DELHIVERY.NS', 'DIVISLAB.NS', 'DIXON.NS', 'DRREDDY.NS', 'ETERNAL.NS',
    'EICHERMOT.NS', 'EXIDEIND.NS', 'FORCEMOT.NS', 'NYKAA.NS', 'FORTIS.NS',
    'GAIL.NS', 'GVTD.NS', 'GMRAIRPORT.NS', 'GLENMARK.NS', 'GODFRYPHLP.NS',
    'GODREJCP.NS', 'GODREJPROP.NS', 'GRASIM.NS', 'HCLTECH.NS', 'HDFCAMC.NS',
    'HDFCBANK.NS', 'HDFCLIFE.NS', 'HAVELLS.NS', 'HEROMOTOCO.NS', 'HINDALCO.NS',
    'HAL.NS', 'HINDPETRO.NS', 'HINDUNILVR.NS', 'HINDZINC.NS', 'POWERINDIA.NS',
    'HYUNDAI.NS', 'ICICIBANK.NS', 'ICICIGI.NS', 'ICICIPRULI.NS', 'IDFCFIRSTB.NS',
    'ITC.NS', 'INDIANB.NS', 'IEX.NS', 'IOC.NS', 'IRFC.NS', 'IREDA.NS',
    'INDUSTOWER.NS', 'INDUSINDBK.NS', 'NAUKRI.NS', 'INFY.NS', 'INOXWIND.NS',
    'INDIGO.NS', 'JINDALSTEL.NS', 'JSWENERGY.NS', 'JSWSTEEL.NS', 'JIOFIN.NS',
    'JUBLFOOD.NS', 'KEI.NS', 'KPITTECH.NS', 'KALYANIJIL.NS', 'KAYNES.NS',
    'KFINTECH.NS', 'KOTAKBANK.NS', 'LTF.NS', 'LICHSGFIN.NS', 'LTM.NS',
    'LT.NS', 'LAURUSLABS.NS', 'LICI.NS', 'LODHA.NS', 'LUPIN.NS',
    'MM.NS', 'MANAPPURAM.NS', 'MANKIND.NS', 'MARICO.NS', 'MARUTI.NS',
    'MFSL.NS', 'MAXHEALTH.NS', 'MAZDOCK.NS', 'MOTILALOFS.NS', 'MPHASIS.NS',
    'MCX.NS', 'MUTHOOTFIN.NS', 'NBCC.NS', 'NHPC.NS', 'NMDC.NS',
    'NTPC.NS', 'NATIONALUM.NS', 'NESTLEIND.NS', 'NAMINDIA.NS', 'NUVAMA.NS',
    'OBEROIRLTY.NS', 'ONGC.NS', 'OIL.NS', 'PAYTM.NS', 'OFSS.NS',
    'POLICYBZR.NS', 'PGEL.NS', 'PIIND.NS', 'PNBHOUSING.NS', 'PAGEIND.NS',
    'PATANJALI.NS', 'PERSISTENT.NS', 'PETRONET.NS', 'PIDILITIND.NS', 'POLYCAB.NS',
    'PFC.NS', 'POWERGRID.NS', 'PREMIERENE.NS', 'PRESTIGE.NS', 'PNB.NS',
    'RBLBANK.NS', 'RECLTD.NS', 'RADICO.NS', 'RVNL.NS', 'RELIANCE.NS',
    'SBICARD.NS', 'SBILIFE.NS', 'SHREECEM.NS', 'SRF.NS', 'MOTHERSON.NS',
    'SHRIRAMFIN.NS', 'SIEMENS.NS', 'SOLARINDS.NS', 'SONACOMS.NS', 'SBIN.NS',
    'SAIL.NS', 'SUNPHARMA.NS', 'SUPREMEIND.NS', 'SUZLON.NS', 'SWIGGY.NS',
    'TATACONSUM.NS', 'TVSMOTOR.NS', 'TCS.NS', 'TATAELXSI.NS', 'TMPV.NS',
    'TATAPOWER.NS', 'TATASTEEL.NS', 'TECHM.NS', 'FEDERALBNK.NS', 'INDHOTEL.NS',
    'PHOENIXLTD.NS', 'TITAN.NS', 'TORNTPHARM.NS', 'TRENT.NS', 'TIINDIA.NS',
    'UNOMINDA.NS', 'UPL.NS', 'ULTRACEMCO.NS', 'UNIONBANK.NS', 'UNITDSPR.NS',
    'VBL.NS', 'VEDL.NS', 'VMM.NS', 'IDEA.NS', 'VOLTAS.NS',
    'WAAREEENER.NS', 'WIPRO.NS', 'YESBANK.NS', 'ZYDUSLIFE.NS'
]

# Run scanner
positive_breakout_data, past_week_dates, scan_type = advanced_stock_scanner(my_stocks)

# Display results
print("\n" + "="*150)

if scan_type == "TODAY":
    print("🟢 FINAL LIST: POSITIVE BREAKOUT STOCKS (TODAY)")
elif scan_type == "PAST_WEEK":
    print("⚠️ WARNING: NO STOCKS MATCHED TODAY")
    print("🟡 SHOWING RESULTS FROM PAST 1 WEEK")
else:
    print("❌ NO MATCHES FOUND - TODAY OR PAST WEEK")

print("="*150 + "\n")

if positive_breakout_data.empty:
    print("❌ No stocks matched the YouTuber's strict criteria in the past week either.\n")
else:
    print(positive_breakout_data.to_string(index=False))
    print("\n" + "="*150 + "\n")

    if scan_type == "PAST_WEEK":
        print("📅 DATES COVERED IN SCAN:")
        for date in set(positive_breakout_data['Date'].unique()):
            print(f"   • {date}")
        print()

    # Save to Excel
    positive_breakout_data.to_excel("Final_Breakout_List_with_SL_T1_T2.xlsx", index=False)
    print("✅ Results saved to 'Final_Breakout_List_with_SL_T1_T2.xlsx'\n")

    # Summary stats
    print("="*150)
    print("📈 SUMMARY STATISTICS")
    print("="*150)
    print(f"Total Breakout Stocks Found: {len(positive_breakout_data)}")
    print(f"Average Reward %: {positive_breakout_data['Reward %'].mean():.2f}%")
    print(f"Average SL %: {positive_breakout_data['SL %'].mean():.2f}%")
    print(f"Average Risk:Reward Ratio: {(positive_breakout_data['Reward %'] / positive_breakout_data['SL %']).mean():.2f}:1")
    print(f"Average Quality Score: {positive_breakout_data['Quality Score'].mean():.2f}/100")
    print("="*150 + "\n")

# Google Colab download
try:
    from google.colab import files
    if not positive_breakout_data.empty:
        files.download("Final_Breakout_List_with_SL_T1_T2.xlsx")
except ImportError:
    pass
