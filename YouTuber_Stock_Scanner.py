#!/usr/bin/env python3
"""
YouTuber's Stock Breakout Scanner - Clean Python Version
========================================================

Strategy: Multi-layer Moving Average Breakout + CAR Confirmation

What it does:
- Downloads 2 years of stock data
- Calculates 30, 50, 200-day moving averages
- Identifies stocks where price > all three DMAs
- Confirms trend with CAR (gets stronger each day)
- Exports results to Excel
"""

import yfinance as yf
import pandas as pd
import warnings
import logging
from datetime import datetime

# Suppress warnings and unnecessary logs
logging.getLogger('yfinance').setLevel(logging.CRITICAL)
warnings.filterwarnings('ignore')


def advanced_stock_scanner(ticker_list):
    """
    Scans a list of stocks for breakout signals.

    Filters:
    1. Price must be above 30-day moving average
    2. Price must be above 50-day moving average
    3. Price must be above 200-day moving average
    4. CAR (Cumulative Average Return) must be positive for 10+ days

    Parameters:
    -----------
    ticker_list : list
        List of NSE stock tickers (with .NS suffix)

    Returns:
    --------
    pd.DataFrame : Stocks that passed all filters, sorted by distance from 200 DMA
    """

    results = []
    today_date = datetime.now().strftime("%d-%m-%Y")

    print(f"🔍 Scanning {len(ticker_list)} stocks... Please wait.\n")

    for ticker in ticker_list:
        try:
            # Download 2 years of daily historical data
            data = yf.download(ticker, period="2y", interval="1d", progress=False)

            # Skip if insufficient data
            if data.empty or len(data) < 200:
                continue

            close_prices = data['Close'].squeeze()

            # Calculate 30, 50, 200-day moving averages
            dma_30 = close_prices.rolling(window=30).mean().iloc[-1]
            dma_50 = close_prices.rolling(window=50).mean().iloc[-1]
            dma_200 = close_prices.rolling(window=200).mean().iloc[-1]

            # Current market price (today's close)
            cmp = close_prices.iloc[-1]

            # Calculate distance from 200-day average (in percentage)
            dist_200_dma = ((cmp - dma_200) / dma_200) * 100

            # Find the date of highest high in last year (252 trading days)
            last_1y_data = data.tail(252)
            high_date = last_1y_data['High'].squeeze().idxmax()

            # Get close prices from highest high date onwards
            car_data = close_prices.loc[high_date:]

            # Skip if insufficient CAR data
            if len(car_data) < 10:
                continue

            # Calculate Cumulative Average Return (expanding average from high date)
            car_values = car_data.expanding().mean()

            # Get last 10 days of CAR values
            last_10_car = car_values.tail(10)

            # Check if CAR is consistently increasing (monotonic increase)
            # This ensures the uptrend is strengthening
            if last_10_car.is_monotonic_increasing:
                car_status = 'Positive'
            else:
                car_status = 'Negative'

            # Apply Core Filters
            # All four conditions MUST be true
            condition_1 = cmp > dma_30          # Price above 30 DMA
            condition_2 = cmp > dma_50          # Price above 50 DMA
            condition_3 = cmp > dma_200         # Price above 200 DMA
            condition_4 = car_status == 'Positive'  # CAR is increasing

            if not (condition_1 and condition_2 and condition_3 and condition_4):
                continue

            # Stock passed all filters - record it
            action = '🟢 Positive Breakout'

            results.append({
                'Date': today_date,
                'Stock': ticker.replace('.NS', ''),
                'CMP': round(cmp, 2),
                '30 DMA': round(dma_30, 2),
                '50 DMA': round(dma_50, 2),
                '200 DMA': round(dma_200, 2),
                '200 DMA Dist %': round(dist_200_dma, 2),
                'CAR Status': car_status,
                'Action': action
            })

        except Exception as e:
            # Skip stocks that fail to download or process
            pass

    # Convert results to DataFrame and sort
    if results:
        df_positive = pd.DataFrame(results)
        # Sort by distance from 200 DMA (ascending = closest first)
        df_positive = df_positive.sort_values(by='200 DMA Dist %', ascending=True)
        return df_positive
    else:
        return pd.DataFrame()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":

    # List of 210 major NSE stocks to scan
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

    # Run the scanner
    positive_breakout_data = advanced_stock_scanner(my_stocks)

    # Display results
    print("\n" + "="*100)
    print("🟢 FINAL LIST: POSITIVE BREAKOUT STOCKS")
    print("="*100 + "\n")

    if positive_breakout_data.empty:
        print("❌ No stocks matched the criteria.\n")
    else:
        print(positive_breakout_data.to_string(index=False))
        print("\n" + "="*100)
        print(f"Total stocks found: {len(positive_breakout_data)}")
        print("="*100)

        # Save to Excel
        filename = "YouTuber_Breakout_Scanner_Results.xlsx"
        positive_breakout_data.to_excel(filename, index=False)
        print(f"✅ Results saved to '{filename}'")
