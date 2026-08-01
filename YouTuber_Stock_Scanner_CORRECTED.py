#!/usr/bin/env python3
"""
YouTuber's Stock Scanner with SL, T1, T2 - CORRECTED VERSION
=============================================================
Fixed Pandas Series handling issue
"""

import yfinance as yf
import pandas as pd
import warnings
import logging
from datetime import datetime

logging.getLogger('yfinance').setLevel(logging.CRITICAL)
warnings.filterwarnings('ignore')

def advanced_stock_scanner(ticker_list):
    """
    Scans stocks for breakout signals with SL, T1, T2 calculations.
    FIXED: Proper Pandas Series to scalar conversion.
    """
    results = []
    today_date = datetime.now().strftime("%d-%m-%Y")

    print(f"🔍 Scanning {len(ticker_list)} stocks... Please wait.\n")

    for ticker in ticker_list:
        try:
            # Download 2 years of daily data
            data = yf.download(ticker, period="2y", interval="1d", progress=False)

            if data.empty or len(data) < 200:
                continue

            close_prices = data['Close'].squeeze()

            # Calculate Moving Averages
            dma_30 = float(close_prices.rolling(window=30).mean().iloc[-1])
            dma_50 = float(close_prices.rolling(window=50).mean().iloc[-1])
            dma_200 = float(close_prices.rolling(window=200).mean().iloc[-1])
            cmp = float(close_prices.iloc[-1])

            dist_200_dma = ((cmp - dma_200) / dma_200) * 100

            # Find highest high in last year
            last_1y_data = data.tail(252)
            high_date = last_1y_data['High'].squeeze().idxmax()
            car_data = close_prices.loc[high_date:]

            if len(car_data) < 10:
                continue

            # Calculate CAR (Cumulative Average Return)
            car_values = car_data.expanding().mean()
            last_10_car = car_values.tail(10)

            if last_10_car.is_monotonic_increasing:
                car_status = 'Positive'
            else:
                car_status = 'Negative'

            # ============================================================
            # YOUTUBER'S ORIGINAL FILTERS (UNCHANGED)
            # ============================================================
            if not ((cmp > dma_30) and (cmp > dma_50) and (cmp > dma_200) and (car_status == 'Positive')):
                continue

            # ============================================================
            # STOP LOSS, T1, T2 CALCULATION - CORRECTED VERSION
            # ============================================================

            # FIX: Convert Series to scalar using float()
            swing_low = float(data['Low'].tail(10).min())

            # Use swing_low as SL (don't min with DMA - simpler and safer)
            sl = swing_low

            entry = cmp  # Entry is current market price
            risk = entry - sl  # Risk in rupees

            # Skip if risk is invalid (shouldn't happen now)
            if risk <= 0:
                continue

            # Calculate target prices
            t1 = entry + (2 * risk)
            t2 = entry + (3 * risk)
            t3 = entry + (5 * risk)

            # Calculate percentages
            reward_percent = ((t2 - entry) / entry) * 100
            sl_percent = ((entry - sl) / entry) * 100
            rr_ratio = reward_percent / sl_percent if sl_percent > 0 else 0

            # Additional metrics
            high_52 = float(data['High'].tail(252).max())
            dist_52 = ((high_52 - entry) / high_52) * 100

            returns = 0
            if len(close_prices) > 21:
                close_21_days_ago = float(close_prices.iloc[-21])
                returns = ((entry - close_21_days_ago) / close_21_days_ago) * 100

            # Trend strength
            if dma_30 > dma_50 > dma_200:
                trend = "Strong Uptrend"
            else:
                trend = "Weak"

            # Add to results
            results.append({
                'Date': today_date,
                'Stock': ticker.replace('.NS', ''),
                'CMP': round(entry, 2),
                '30 DMA': round(dma_30, 2),
                '50 DMA': round(dma_50, 2),
                '200 DMA': round(dma_200, 2),
                '200 DMA Dist %': round(dist_200_dma, 2),
                '52W High Dist %': round(dist_52, 2),
                'SL': round(sl, 2),
                'SL %': round(sl_percent, 2),
                'T1': round(t1, 2),
                'T2': round(t2, 2),
                'T3': round(t3, 2),
                'Risk': round(risk, 2),
                'Reward %': round(reward_percent, 2),
                'R:R Ratio': round(rr_ratio, 2),
                '1M Return %': round(returns, 2),
                'Trend': trend,
                'CAR Status': car_status,
                'Action': '🟢 Positive Breakout'
            })

        except Exception as e:
            pass

    # Return results
    if results:
        df = pd.DataFrame(results)
        df = df.sort_values(by='200 DMA Dist %', ascending=True)
        return df
    else:
        return pd.DataFrame()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":

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

    print("=" * 120)
    print("🟢 YouTuber Stock Scanner with SL, T1, T2 - CORRECTED VERSION")
    print("=" * 120 + "\n")

    result = advanced_stock_scanner(my_stocks)

    if result.empty:
        print("❌ No stocks found today.\n")
    else:
        # Show key columns
        display_cols = ['Stock', 'CMP', '30 DMA', '50 DMA', '200 DMA', 'SL', 'SL %', 'T1', 'T2', 'Reward %', 'R:R Ratio', 'Trend']
        print(result[display_cols].to_string(index=False))

        print("\n" + "=" * 120)
        print(f"✅ Total Stocks Found: {len(result)}")
        print(f"📊 Avg SL %: {result['SL %'].mean():.2f}%")
        print(f"📊 Avg Reward %: {result['Reward %'].mean():.2f}%")
        print(f"📊 Avg R:R Ratio: {result['R:R Ratio'].mean():.2f}:1")
        print("=" * 120)

        # Save to Excel
        result.to_excel("YouTuber_Scanner_CORRECTED.xlsx", index=False)
        print("✅ Saved to 'YouTuber_Scanner_CORRECTED.xlsx'\n")
