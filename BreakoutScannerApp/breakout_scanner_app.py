#!/usr/bin/env python3
"""
Breakout Scanner Global Markets
Developed by Yash Jani

Two independent scan strategies, both ported from the notebooks in this
project (YouTuber_Stock_Scanner_Gujarati_FINAL.ipynb /
YouTuber_Stock_Scanner_TSX_FINAL.ipynb) and generalized to run against any
Yahoo-Finance-covered exchange via the MARKETS registry below:

- Breakout (DMA + CAR): price above the 30/50/200-day moving averages plus
  a strengthening Cumulative Average Return.
- RSI 5-Star: a multi-timeframe RSI pullback setup (Monthly/Weekly RSI > 60,
  a Daily RSI pullback near 40, entry above that signal candle's high).

GUI adds a splash screen, a strategy picker, a market picker, a live
results table, and Excel / PDF export.
"""

import sys
import warnings
import logging
from datetime import datetime

import pandas as pd
import yfinance as yf

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPainter, QPen
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QProgressBar,
    QFileDialog, QMessageBox, QHeaderView, QComboBox
)

warnings.filterwarnings("ignore")
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

APP_TITLE = "Breakout Scanner Global Markets"
APP_VERSION = "2.0.3"
AUTHOR_CREDIT = "Developed by Yash Jani"
SPLASH_DURATION_MS = 5000

BREAKOUT_DISPLAY_COLUMNS = [
    "Date", "Stock", "CMP", "30 DMA", "50 DMA", "200 DMA",
    "200 DMA Dist %", "SL", "T1", "T2", "T3", "CAR Status", "Action",
]

RSI_DISPLAY_COLUMNS = [
    "Date", "Stock", "CMP", "Monthly RSI", "Weekly RSI", "Signal Date",
    "Entry", "SL", "T1 (RSI 60 Est.)", "Action",
]

CONFLUENCE_DISPLAY_COLUMNS = [
    "Date", "Stock", "CMP", "30 DMA", "50 DMA", "200 DMA", "200 DMA Dist %",
    "Monthly RSI", "Weekly RSI", "Signal Date", "SL", "T1", "T2", "T3",
    "CAR Status", "Action",
]

# ---------------------------------------------------------------------------
# Market registry - one entry per exchange. "suffix" is the Yahoo Finance
# ticker suffix (or a tuple of suffixes, e.g. China's dual SS/SZ listings)
# used both to query yfinance and to strip back to a display-friendly symbol.
# Every market reuses the same scan_stocks() logic; only the ticker universe,
# suffix and display currency change.
# ---------------------------------------------------------------------------

NSE_STOCKS = [
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
    'WAAREEENER.NS', 'WIPRO.NS', 'YESBANK.NS', 'ZYDUSLIFE.NS',
]

TSX_STOCKS = [
    'RY.TO', 'TD.TO', 'BNS.TO', 'BMO.TO', 'CM.TO',
    'ENB.TO', 'TRP.TO', 'SU.TO', 'CNQ.TO', 'CVE.TO',
    'CNR.TO', 'CP.TO', 'BCE.TO', 'T.TO', 'RCI-B.TO',
    'SHOP.TO', 'CSU.TO', 'BN.TO', 'BAM.TO', 'MFC.TO',
    'SLF.TO', 'POW.TO', 'L.TO', 'ATD.TO', 'QSR.TO',
    'ABX.TO', 'AEM.TO', 'NTR.TO', 'FNV.TO', 'WCN.TO',
]

US_STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B', 'JPM', 'V',
    'MA', 'UNH', 'JNJ', 'WMT', 'PG', 'HD', 'DIS', 'BAC', 'KO', 'PEP',
    'COST', 'MCD', 'ADBE', 'CRM', 'NFLX', 'XOM', 'CVX', 'ORCL', 'CSCO', 'INTC',
]

UK_STOCKS = [
    'SHEL.L', 'AZN.L', 'HSBA.L', 'ULVR.L', 'BP.L', 'GSK.L', 'DGE.L', 'RIO.L',
    'BATS.L', 'GLEN.L', 'LLOY.L', 'BARC.L', 'VOD.L', 'NG.L', 'REL.L', 'PRU.L',
    'TSCO.L', 'NWG.L', 'STAN.L', 'AAL.L', 'CRH.L', 'EXPN.L', 'III.L', 'IMB.L', 'LSEG.L',
]

DE_STOCKS = [
    'SAP.DE', 'SIE.DE', 'ALV.DE', 'DTE.DE', 'BAS.DE', 'BAYN.DE', 'BMW.DE',
    'VOW3.DE', 'MBG.DE', 'ADS.DE', 'DBK.DE', 'MUV2.DE', 'RWE.DE', 'EOAN.DE',
    'IFX.DE', 'DB1.DE', 'HEN3.DE', 'FRE.DE', 'HEI.DE', 'CON.DE',
]

FR_STOCKS = [
    'MC.PA', 'OR.PA', 'SAN.PA', 'AI.PA', 'BNP.PA', 'DG.PA', 'SU.PA', 'CS.PA',
    'EL.PA', 'RMS.PA', 'TTE.PA', 'KER.PA', 'DSY.PA', 'SGO.PA', 'ORA.PA',
    'ENGI.PA', 'VIE.PA', 'BN.PA', 'CAP.PA', 'ML.PA',
]

NL_STOCKS = [
    'ASML.AS', 'AD.AS', 'INGA.AS', 'PHIA.AS', 'HEIA.AS', 'RAND.AS',
    'WKL.AS', 'AKZA.AS', 'KPN.AS', 'ABN.AS', 'NN.AS', 'ASM.AS',
]

CH_STOCKS = [
    'NESN.SW', 'NOVN.SW', 'ROG.SW', 'UBSG.SW', 'ZURN.SW', 'ABBN.SW',
    'CFR.SW', 'SIKA.SW', 'LONN.SW', 'SREN.SW', 'GIVN.SW', 'HOLN.SW',
]

IT_STOCKS = [
    'ENI.MI', 'ISP.MI', 'UCG.MI', 'ENEL.MI', 'RACE.MI', 'G.MI',
    'STLAM.MI', 'TIT.MI', 'PST.MI', 'MB.MI',
]

JP_STOCKS = [
    '7203.T', '6758.T', '9984.T', '6861.T', '8306.T', '9432.T', '6098.T',
    '4063.T', '6501.T', '7267.T', '8035.T', '9433.T', '4519.T', '6902.T',
    '8058.T', '7974.T', '6367.T', '4502.T', '9983.T', '8316.T', '4661.T',
    '6178.T', '8801.T', '9020.T', '8001.T',
]

HK_STOCKS = [
    '0700.HK', '9988.HK', '0941.HK', '1299.HK', '0005.HK', '0388.HK',
    '3690.HK', '1810.HK', '2318.HK', '0027.HK', '0011.HK', '0016.HK',
    '0883.HK', '1928.HK', '2388.HK', '0762.HK', '1211.HK', '9633.HK',
    '0006.HK', '0002.HK',
]

CN_STOCKS = [
    '600519.SS', '601398.SS', '600036.SS', '000858.SZ', '300750.SZ',
    '601988.SS', '601288.SS', '600030.SS', '000333.SZ', '002594.SZ',
    '601318.SS', '600276.SS', '000651.SZ', '601857.SS', '600900.SS',
]

KR_STOCKS = [
    '005930.KS', '000660.KS', '005380.KS', '051910.KS', '035420.KS',
    '006400.KS', '105560.KS', '055550.KS', '015760.KS', '012330.KS',
    '032830.KS', '005490.KS', '066570.KS', '035720.KS', '034730.KS',
]

SG_STOCKS = [
    'D05.SI', 'O39.SI', 'U11.SI', 'C6L.SI', 'Z74.SI',
    'C38U.SI', 'A17U.SI', 'S68.SI', 'BN4.SI', 'U96.SI',
]

AU_STOCKS = [
    'BHP.AX', 'CBA.AX', 'CSL.AX', 'NAB.AX', 'WBC.AX', 'ANZ.AX', 'WES.AX',
    'WOW.AX', 'MQG.AX', 'TLS.AX', 'RIO.AX', 'FMG.AX', 'GMG.AX', 'TCL.AX',
    'WDS.AX', 'STO.AX', 'QBE.AX', 'COL.AX', 'ALL.AX', 'SUN.AX',
]

BR_STOCKS = [
    'PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'ABEV3.SA', 'BBAS3.SA',
    'WEGE3.SA', 'RENT3.SA', 'SUZB3.SA', 'ELET3.SA', 'B3SA3.SA', 'GGBR4.SA',
    'EQTL3.SA', 'RADL3.SA', 'JBSS3.SA',
]

MARKETS = {
    "India (NSE)": {"suffix": ".NS", "currency": "INR", "tickers": NSE_STOCKS},
    "United States (NYSE/NASDAQ)": {"suffix": "", "currency": "USD", "tickers": US_STOCKS},
    "Canada (TSX)": {"suffix": ".TO", "currency": "CAD", "tickers": TSX_STOCKS},
    "United Kingdom (LSE)": {"suffix": ".L", "currency": "GBP", "tickers": UK_STOCKS},
    "Germany (XETRA)": {"suffix": ".DE", "currency": "EUR", "tickers": DE_STOCKS},
    "France (Euronext Paris)": {"suffix": ".PA", "currency": "EUR", "tickers": FR_STOCKS},
    "Netherlands (Euronext Amsterdam)": {"suffix": ".AS", "currency": "EUR", "tickers": NL_STOCKS},
    "Switzerland (SIX)": {"suffix": ".SW", "currency": "CHF", "tickers": CH_STOCKS},
    "Italy (Borsa Italiana)": {"suffix": ".MI", "currency": "EUR", "tickers": IT_STOCKS},
    "Japan (Tokyo)": {"suffix": ".T", "currency": "JPY", "tickers": JP_STOCKS},
    "Hong Kong (HKEX)": {"suffix": ".HK", "currency": "HKD", "tickers": HK_STOCKS},
    "China A-Shares (Shanghai/Shenzhen)": {"suffix": (".SS", ".SZ"), "currency": "CNY", "tickers": CN_STOCKS},
    "South Korea (KOSPI)": {"suffix": ".KS", "currency": "KRW", "tickers": KR_STOCKS},
    "Singapore (SGX)": {"suffix": ".SI", "currency": "SGD", "tickers": SG_STOCKS},
    "Australia (ASX)": {"suffix": ".AX", "currency": "AUD", "tickers": AU_STOCKS},
    "Brazil (B3)": {"suffix": ".SA", "currency": "BRL", "tickers": BR_STOCKS},
}

DEFAULT_MARKET = "India (NSE)"


def strip_ticker_suffix(ticker, suffix):
    """Removes the exchange suffix so the table shows a clean symbol."""
    suffixes = suffix if isinstance(suffix, (list, tuple)) else (suffix,)
    for s in suffixes:
        if s and ticker.endswith(s):
            return ticker[: -len(s)]
    return ticker


# ---------------------------------------------------------------------------
# Scanning logic (unchanged from the Gujarati notebook, generalized to any
# exchange suffix)
# ---------------------------------------------------------------------------

def scan_stocks(ticker_list, suffix="", progress_cb=None):
    """Runs the notebook's advanced_stock_scanner logic and returns a DataFrame."""
    results = []
    today_date = datetime.now().strftime("%d-%m-%Y")
    total = len(ticker_list)

    for idx, ticker in enumerate(ticker_list):
        try:
            data = yf.download(ticker, period="2y", interval="1d", progress=False)

            if data.empty or len(data) < 200:
                continue

            close_prices = data["Close"].squeeze()

            dma_30 = float(close_prices.rolling(window=30).mean().iloc[-1])
            dma_50 = float(close_prices.rolling(window=50).mean().iloc[-1])
            dma_200 = float(close_prices.rolling(window=200).mean().iloc[-1])
            cmp = float(close_prices.iloc[-1])

            dist_200_dma = ((cmp - dma_200) / dma_200) * 100

            last_1y_data = data.tail(252)
            high_date = last_1y_data["High"].squeeze().idxmax()
            car_data = close_prices.loc[high_date:]

            if len(car_data) < 10:
                continue

            car_values = car_data.expanding().mean()
            last_10_car = car_values.tail(10)
            car_status = "Positive" if last_10_car.is_monotonic_increasing else "Negative"

            if not ((cmp > dma_30) and (cmp > dma_50) and (cmp > dma_200) and (car_status == "Positive")):
                continue

            swing_low = float(data["Low"].tail(10).min().item())
            sl = swing_low
            entry = cmp
            risk = entry - sl

            if risk <= 0:
                continue

            t1 = entry + (2 * risk)
            t2 = entry + (3 * risk)
            t3 = entry + (5 * risk)

            results.append({
                "Date": today_date,
                "Stock": strip_ticker_suffix(ticker, suffix),
                "CMP": round(entry, 2),
                "30 DMA": round(dma_30, 2),
                "50 DMA": round(dma_50, 2),
                "200 DMA": round(dma_200, 2),
                "200 DMA Dist %": round(dist_200_dma, 2),
                "SL": round(sl, 2),
                "T1": round(t1, 2),
                "T2": round(t2, 2),
                "T3": round(t3, 2),
                "CAR Status": car_status,
                "Action": "Positive Breakout",
            })

        except Exception:
            pass

        if progress_cb:
            progress_cb(idx + 1, total)

    if results:
        df = pd.DataFrame(results)
        df = df.sort_values(by="200 DMA Dist %", ascending=True).reset_index(drop=True)
        return df
    return pd.DataFrame(columns=BREAKOUT_DISPLAY_COLUMNS)


# ---------------------------------------------------------------------------
# RSI 5-Star strategy - a multi-timeframe RSI pullback setup:
#   - Monthly RSI > 60, Weekly RSI > 60 (strong higher-timeframe momentum)
#   - Daily RSI near 40 on a recent "signal candle" (a pullback)
#   - Entry once price closes above that signal candle's high
#   - Stop Loss = lowest low of the swing (10 days up to the signal candle)
#   - Target 1 = the price where daily RSI would reach back up to 60
#
# "Near 40" and the signal-candle lookback aren't single exact numbers in the
# original rules, so they're pinned down explicitly below: RSI(14) between
# 35-45, most recent such day within the last 15 trading days. A 3-5 bar
# trailing stop (per the strategy notes) is a trade-management choice made
# after entry, not something a one-shot scan can compute, so it isn't
# included as a column.
# ---------------------------------------------------------------------------

RSI_PERIOD = 14
RSI_SIGNAL_LOW, RSI_SIGNAL_HIGH = 35, 45
RSI_SIGNAL_LOOKBACK_DAYS = 15
RSI_SL_LOOKBACK_DAYS = 10
RSI_TARGET_LEVEL = 60


def compute_rsi(price_series, period=RSI_PERIOD):
    """Wilder's RSI. Also returns the avg gain/loss series, needed to solve
    for the price that would put a future RSI reading at a target level."""
    delta = price_series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi_series = 100 - (100 / (1 + rs))
    return rsi_series, avg_gain, avg_loss


def scan_rsi_five_star(ticker_list, suffix="", progress_cb=None):
    """RSI 5-Star multi-timeframe pullback scan. Same signature/shape as
    scan_stocks() so the GUI can drive either strategy interchangeably."""
    results = []
    today_date = datetime.now().strftime("%d-%m-%Y")
    total = len(ticker_list)

    for idx, ticker in enumerate(ticker_list):
        try:
            data = yf.download(ticker, period="2y", interval="1d", progress=False)

            if data.empty or len(data) < 220:
                continue

            close = data["Close"].squeeze()
            high = data["High"].squeeze()
            low = data["Low"].squeeze()

            monthly_close = close.resample("ME").last().dropna()
            weekly_close = close.resample("W").last().dropna()
            if len(monthly_close) < RSI_PERIOD + 1 or len(weekly_close) < RSI_PERIOD + 1:
                continue

            monthly_rsi, _, _ = compute_rsi(monthly_close)
            weekly_rsi, _, _ = compute_rsi(weekly_close)
            daily_rsi, daily_avg_gain, daily_avg_loss = compute_rsi(close)

            last_monthly_rsi = float(monthly_rsi.iloc[-1])
            last_weekly_rsi = float(weekly_rsi.iloc[-1])

            if not (last_monthly_rsi > 60 and last_weekly_rsi > 60):
                continue

            recent_rsi = daily_rsi.tail(RSI_SIGNAL_LOOKBACK_DAYS)
            signal_mask = (recent_rsi >= RSI_SIGNAL_LOW) & (recent_rsi <= RSI_SIGNAL_HIGH)
            if not signal_mask.any():
                continue
            signal_date = signal_mask[signal_mask].index[-1]
            signal_high = float(high.loc[signal_date])

            cmp = float(close.iloc[-1])
            if cmp <= signal_high:
                continue

            swing_window = low.loc[:signal_date].tail(RSI_SL_LOOKBACK_DAYS)
            sl = float(swing_window.min())
            entry = signal_high
            risk = entry - sl
            if risk <= 0:
                continue

            last_avg_gain = float(daily_avg_gain.iloc[-1])
            last_avg_loss = float(daily_avg_loss.iloc[-1])
            target_rs = RSI_TARGET_LEVEL / (100 - RSI_TARGET_LEVEL)
            price_change_needed = (RSI_PERIOD - 1) * (target_rs * last_avg_loss - last_avg_gain)
            rsi_implied_t1 = cmp + price_change_needed
            # The RSI-implied target can already be behind the current price
            # (e.g. price ran up fast after the signal candle, well past
            # where RSI would next read 60) - always take the highest of the
            # RSI-implied level, a 2x-risk level from entry, and one more
            # risk unit above the current price, so T1 is a genuine forward
            # target rather than a level already passed.
            t1 = max(rsi_implied_t1, entry + (2 * risk), cmp + risk)

            results.append({
                "Date": today_date,
                "Stock": strip_ticker_suffix(ticker, suffix),
                "CMP": round(cmp, 2),
                "Monthly RSI": round(last_monthly_rsi, 1),
                "Weekly RSI": round(last_weekly_rsi, 1),
                "Signal Date": signal_date.strftime("%d-%m-%Y"),
                "Entry": round(entry, 2),
                "SL": round(sl, 2),
                "T1 (RSI 60 Est.)": round(t1, 2),
                "Action": "RSI 5-Star Setup",
            })

        except Exception:
            pass

        if progress_cb:
            progress_cb(idx + 1, total)

    if results:
        df = pd.DataFrame(results)
        df = df.sort_values(by="Weekly RSI", ascending=False).reset_index(drop=True)
        return df
    return pd.DataFrame(columns=RSI_DISPLAY_COLUMNS)


def scan_confluence(ticker_list, suffix="", progress_cb=None):
    """Stocks that pass BOTH the Breakout (DMA + CAR) and RSI 5-Star filters
    at once, checked from a single data download per ticker (not two).

    Stop loss uses whichever of the two strategies' stop levels is tighter
    (closer to the current price), and T1/T2/T3 are risk multiples off that
    combined stop - the same convention as the plain Breakout strategy, so
    the numbers stay simple to read even though two setups agree here."""
    results = []
    today_date = datetime.now().strftime("%d-%m-%Y")
    total = len(ticker_list)

    for idx, ticker in enumerate(ticker_list):
        try:
            data = yf.download(ticker, period="2y", interval="1d", progress=False)

            if data.empty or len(data) < 220:
                continue

            close = data["Close"].squeeze()
            high = data["High"].squeeze()
            low = data["Low"].squeeze()
            cmp = float(close.iloc[-1])

            # --- Breakout (DMA + CAR) conditions ---
            dma_30 = float(close.rolling(window=30).mean().iloc[-1])
            dma_50 = float(close.rolling(window=50).mean().iloc[-1])
            dma_200 = float(close.rolling(window=200).mean().iloc[-1])
            dist_200_dma = ((cmp - dma_200) / dma_200) * 100

            last_1y_data = data.tail(252)
            high_date = last_1y_data["High"].squeeze().idxmax()
            car_data = close.loc[high_date:]
            if len(car_data) < 10:
                continue
            car_status = (
                "Positive" if car_data.expanding().mean().tail(10).is_monotonic_increasing else "Negative"
            )

            if not ((cmp > dma_30) and (cmp > dma_50) and (cmp > dma_200) and (car_status == "Positive")):
                continue

            breakout_sl = float(data["Low"].tail(10).min().item())

            # --- RSI 5-Star conditions (reusing the same downloaded data) ---
            monthly_close = close.resample("ME").last().dropna()
            weekly_close = close.resample("W").last().dropna()
            if len(monthly_close) < RSI_PERIOD + 1 or len(weekly_close) < RSI_PERIOD + 1:
                continue

            monthly_rsi, _, _ = compute_rsi(monthly_close)
            weekly_rsi, _, _ = compute_rsi(weekly_close)
            daily_rsi, _, _ = compute_rsi(close)

            last_monthly_rsi = float(monthly_rsi.iloc[-1])
            last_weekly_rsi = float(weekly_rsi.iloc[-1])
            if not (last_monthly_rsi > 60 and last_weekly_rsi > 60):
                continue

            recent_rsi = daily_rsi.tail(RSI_SIGNAL_LOOKBACK_DAYS)
            signal_mask = (recent_rsi >= RSI_SIGNAL_LOW) & (recent_rsi <= RSI_SIGNAL_HIGH)
            if not signal_mask.any():
                continue
            signal_date = signal_mask[signal_mask].index[-1]
            signal_high = float(high.loc[signal_date])
            if cmp <= signal_high:
                continue

            rsi_sl = float(low.loc[:signal_date].tail(RSI_SL_LOOKBACK_DAYS).min())

            # --- Both passed: combine into one set of trade levels ---
            sl = max(breakout_sl, rsi_sl)
            entry = cmp
            risk = entry - sl
            if risk <= 0:
                continue

            t1 = entry + (2 * risk)
            t2 = entry + (3 * risk)
            t3 = entry + (5 * risk)

            results.append({
                "Date": today_date,
                "Stock": strip_ticker_suffix(ticker, suffix),
                "CMP": round(cmp, 2),
                "30 DMA": round(dma_30, 2),
                "50 DMA": round(dma_50, 2),
                "200 DMA": round(dma_200, 2),
                "200 DMA Dist %": round(dist_200_dma, 2),
                "Monthly RSI": round(last_monthly_rsi, 1),
                "Weekly RSI": round(last_weekly_rsi, 1),
                "Signal Date": signal_date.strftime("%d-%m-%Y"),
                "SL": round(sl, 2),
                "T1": round(t1, 2),
                "T2": round(t2, 2),
                "T3": round(t3, 2),
                "CAR Status": car_status,
                "Action": "Breakout + RSI 5-Star",
            })

        except Exception:
            pass

        if progress_cb:
            progress_cb(idx + 1, total)

    if results:
        df = pd.DataFrame(results)
        df = df.sort_values(by="Weekly RSI", ascending=False).reset_index(drop=True)
        return df
    return pd.DataFrame(columns=CONFLUENCE_DISPLAY_COLUMNS)


STRATEGIES = {
    "Breakout (DMA + CAR)": {"scan_fn": scan_stocks, "columns": BREAKOUT_DISPLAY_COLUMNS},
    "RSI 5-Star": {"scan_fn": scan_rsi_five_star, "columns": RSI_DISPLAY_COLUMNS},
    "Confluence (Both)": {"scan_fn": scan_confluence, "columns": CONFLUENCE_DISPLAY_COLUMNS},
}

DEFAULT_STRATEGY = "Breakout (DMA + CAR)"


def export_dataframe_to_pdf(df, filepath, title):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(
        filepath, pagesize=landscape(A4),
        leftMargin=12 * mm, rightMargin=12 * mm,
        topMargin=12 * mm, bottomMargin=12 * mm,
    )

    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], textColor=colors.HexColor("#0d7377"))
    elements = [
        Paragraph(title, title_style),
        Paragraph(f"Generated: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", styles["Normal"]),
        Paragraph(AUTHOR_CREDIT, styles["Normal"]),
        Spacer(1, 10),
    ]

    data = [list(df.columns)] + df.astype(str).values.tolist()
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d7377")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d0d0d0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f7f7")]),
    ]))
    elements.append(table)
    doc.build(elements)


def slugify_market(name):
    return "".join(ch if ch.isalnum() else "_" for ch in name).strip("_")


# ---------------------------------------------------------------------------
# Background scan thread
# ---------------------------------------------------------------------------

class ScannerThread(QThread):
    progress = pyqtSignal(int, int)
    finished_ok = pyqtSignal(pd.DataFrame)
    failed = pyqtSignal(str)

    def __init__(self, scan_fn, tickers, suffix):
        super().__init__()
        self.scan_fn = scan_fn
        self.tickers = tickers
        self.suffix = suffix

    def run(self):
        try:
            df = self.scan_fn(
                self.tickers, self.suffix,
                progress_cb=lambda done, total: self.progress.emit(done, total),
            )
            self.finished_ok.emit(df)
        except Exception as exc:
            self.failed.emit(str(exc))


# ---------------------------------------------------------------------------
# Splash screen
# ---------------------------------------------------------------------------

class SpinnerWidget(QWidget):
    def __init__(self, diameter=70, line_width=6, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.line_width = line_width
        self.setFixedSize(diameter, diameter)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._rotate)
        self.timer.start(16)

    def _rotate(self):
        self.angle = (self.angle + 8) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(
            self.line_width, self.line_width, -self.line_width, -self.line_width
        )

        track_pen = QPen(QColor("#1b3a44"))
        track_pen.setWidth(self.line_width)
        track_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(track_pen)
        painter.drawArc(rect, 0, 360 * 16)

        arc_pen = QPen(QColor("#14ffe0"))
        arc_pen.setWidth(self.line_width)
        arc_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(arc_pen)
        start_angle = int(-self.angle * 16)
        span_angle = 100 * 16
        painter.drawArc(rect, start_angle, span_angle)


class SplashScreen(QWidget):
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(520, 340)
        self._center_on_screen()
        self._build_ui()
        QTimer.singleShot(SPLASH_DURATION_MS, self._finish)

    def _center_on_screen(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.center().x() - self.width() // 2,
                  screen.center().y() - self.height() // 2)

    def _build_ui(self):
        self.setObjectName("splashRoot")
        self.setStyleSheet("""
            #splashRoot {
                background-color: #0b1f28;
                border: 1px solid #14ffe0;
                border-radius: 10px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 40, 30, 25)
        layout.setSpacing(14)

        title = QLabel(APP_TITLE)
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #f2f2f2;")
        layout.addWidget(title)

        version_label = QLabel(f"App v{APP_VERSION}")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #14ffe0; font-size: 9pt; letter-spacing: 1px;")
        layout.addWidget(version_label)

        layout.addStretch(1)

        spinner_row = QHBoxLayout()
        spinner_row.addStretch(1)
        spinner_row.addWidget(SpinnerWidget())
        spinner_row.addStretch(1)
        layout.addLayout(spinner_row)

        status = QLabel("Loading...")
        status.setAlignment(Qt.AlignCenter)
        status.setStyleSheet("color: #9fd6cf; font-size: 11pt;")
        layout.addWidget(status)

        layout.addStretch(1)

        credit = QLabel(AUTHOR_CREDIT)
        credit.setAlignment(Qt.AlignCenter)
        credit.setStyleSheet("color: #6d8b92; font-size: 10pt;")
        layout.addWidget(credit)

    def _finish(self):
        self.finished.emit()
        self.close()


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------

BUTTON_STYLE = """
    QPushButton {{
        background-color: {bg};
        color: white;
        border: none;
        padding: 8px 12px;
        font-size: 10pt;
        font-weight: bold;
        border-radius: 5px;
    }}
    QPushButton:hover {{ background-color: {hover}; }}
    QPushButton:pressed {{ background-color: {pressed}; }}
    QPushButton:disabled {{ background-color: #4a4a4a; color: #9a9a9a; }}
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.results_df = pd.DataFrame(columns=BREAKOUT_DISPLAY_COLUMNS)
        self.scanner_thread = None
        self.current_market = DEFAULT_MARKET
        self.current_strategy = DEFAULT_STRATEGY

        self.setWindowTitle(f"{APP_TITLE} v{APP_VERSION}")
        self.resize(1280, 780)
        self.setStyleSheet("QMainWindow { background-color: #f7f9f9; }")
        self._build_ui()

        QTimer.singleShot(300, self.start_scan)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        title_row = QHBoxLayout()
        title_row.setSpacing(12)

        title_label = QLabel(APP_TITLE)
        title_label.setFont(QFont("Segoe UI", 17, QFont.Bold))
        title_label.setStyleSheet("color: #0d3b3e;")
        title_row.addWidget(title_label)

        version_tag = QLabel(f"App v{APP_VERSION}")
        version_tag.setStyleSheet("color: #0d7377; font-weight: bold;")
        title_row.addWidget(version_tag)

        title_row.addStretch(1)
        layout.addLayout(title_row)

        controls_row = QHBoxLayout()
        controls_row.setSpacing(8)

        combo_style = """
            QComboBox {
                padding: 6px 8px;
                border: 1px solid #0d7377;
                border-radius: 5px;
                background-color: white;
                font-size: 10pt;
            }
        """

        strategy_label = QLabel("Strategy:")
        strategy_label.setStyleSheet("color: #0d3b3e; font-weight: bold;")
        controls_row.addWidget(strategy_label)

        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems(list(STRATEGIES.keys()))
        self.strategy_combo.setCurrentText(DEFAULT_STRATEGY)
        self.strategy_combo.setFixedWidth(180)
        self.strategy_combo.setStyleSheet(combo_style)
        self.strategy_combo.setToolTip(
            "Breakout (DMA + CAR): price above 30/50/200-day averages with a strengthening trend.\n"
            "RSI 5-Star: Monthly/Weekly RSI > 60, a Daily RSI pullback near 40, entry on breakout\n"
            "above that signal candle's high.\n"
            "Confluence (Both): only stocks that pass both strategies at once."
        )
        controls_row.addWidget(self.strategy_combo)

        market_label = QLabel("Market:")
        market_label.setStyleSheet("color: #0d3b3e; font-weight: bold;")
        controls_row.addWidget(market_label)

        self.market_combo = QComboBox()
        self.market_combo.addItems(list(MARKETS.keys()))
        self.market_combo.setCurrentText(DEFAULT_MARKET)
        self.market_combo.setFixedWidth(220)
        self.market_combo.setStyleSheet(combo_style)
        controls_row.addWidget(self.market_combo)

        controls_row.addStretch(1)

        self.scan_button = QPushButton("Scan")
        self.scan_button.setStyleSheet(BUTTON_STYLE.format(bg="#3b3b3b", hover="#525252", pressed="#242424"))
        self.scan_button.clicked.connect(self.start_scan)
        controls_row.addWidget(self.scan_button)

        self.excel_button = QPushButton("Generate Excel")
        self.excel_button.setStyleSheet(BUTTON_STYLE.format(bg="#2d6a4f", hover="#40916c", pressed="#1b4332"))
        self.excel_button.setEnabled(False)
        self.excel_button.clicked.connect(self.export_excel)
        controls_row.addWidget(self.excel_button)

        self.pdf_button = QPushButton("Generate PDF")
        self.pdf_button.setStyleSheet(BUTTON_STYLE.format(bg="#0d7377", hover="#14919b", pressed="#0a5a61"))
        self.pdf_button.setEnabled(False)
        self.pdf_button.clicked.connect(self.export_pdf)
        controls_row.addWidget(self.pdf_button)

        layout.addLayout(controls_row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #0d7377;
                border-radius: 5px;
                background-color: #eef2f2;
                text-align: center;
                height: 18px;
            }
            QProgressBar::chunk { background-color: #0d7377; }
        """)
        layout.addWidget(self.progress_bar)

        self.table = QTableWidget()
        self.table.setColumnCount(len(BREAKOUT_DISPLAY_COLUMNS))
        self.table.setHorizontalHeaderLabels(BREAKOUT_DISPLAY_COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f2f7f7;
                gridline-color: #d8e2e2;
                border: 1px solid #d8e2e2;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #0d7377;
                color: white;
                padding: 6px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item { padding: 6px; }
            QTableWidget::item:selected { background-color: #0d7377; color: white; }
        """)
        layout.addWidget(self.table)

        footer = QHBoxLayout()
        self.status_label = QLabel("Starting scan...")
        self.status_label.setStyleSheet("color: #0d7377; font-weight: bold;")
        footer.addWidget(self.status_label)
        footer.addStretch(1)
        self.count_label = QLabel("")
        self.count_label.setStyleSheet("color: #2d6a4f; font-weight: bold;")
        footer.addWidget(self.count_label)
        layout.addLayout(footer)

    # -- scanning -----------------------------------------------------

    def start_scan(self):
        if self.scanner_thread is not None and self.scanner_thread.isRunning():
            return

        self.current_market = self.market_combo.currentText()
        self.current_strategy = self.strategy_combo.currentText()
        market = MARKETS[self.current_market]
        strategy = STRATEGIES[self.current_strategy]

        self.market_combo.setEnabled(False)
        self.strategy_combo.setEnabled(False)
        self.scan_button.setEnabled(False)
        self.excel_button.setEnabled(False)
        self.pdf_button.setEnabled(False)
        self.table.setRowCount(0)
        self.table.setColumnCount(len(strategy["columns"]))
        self.table.setHorizontalHeaderLabels(strategy["columns"])
        self.progress_bar.setValue(0)
        self.status_label.setText(
            f"Scanning {self.current_market} ({market['currency']}) - {self.current_strategy}... "
            "this can take a few minutes."
        )
        self.count_label.setText("")

        self.scanner_thread = ScannerThread(strategy["scan_fn"], market["tickers"], market["suffix"])
        self.scanner_thread.progress.connect(self.on_progress)
        self.scanner_thread.finished_ok.connect(self.on_results)
        self.scanner_thread.failed.connect(self.on_error)
        self.scanner_thread.start()

    def on_progress(self, done, total):
        self.progress_bar.setValue(int(done / total * 100))
        self.status_label.setText(f"Scanning {self.current_market}... {done}/{total} stocks checked")

    def on_results(self, df):
        self.market_combo.setEnabled(True)
        self.strategy_combo.setEnabled(True)
        self.scan_button.setEnabled(True)
        self.results_df = df

        if df.empty:
            self.status_label.setText(
                f"No {self.current_market} stocks matched the {self.current_strategy} setup today."
            )
            self.count_label.setText("")
            return

        columns = list(df.columns)
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setRowCount(len(df))
        for row, (_, record) in enumerate(df.iterrows()):
            for col, key in enumerate(columns):
                item = QTableWidgetItem(str(record[key]))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

        currency = MARKETS[self.current_market]["currency"]
        status_text = f"Scan complete - {self.current_market} ({currency}) - {self.current_strategy}"
        if self.current_strategy == "RSI 5-Star":
            status_text += "  |  Tip: consider a 3-5 bar trailing stop once the trade is in profit"
        self.status_label.setText(status_text)
        self.count_label.setText(f"{len(df)} stocks matched")
        self.excel_button.setEnabled(True)
        self.pdf_button.setEnabled(True)

    def on_error(self, message):
        self.market_combo.setEnabled(True)
        self.strategy_combo.setEnabled(True)
        self.scan_button.setEnabled(True)
        QMessageBox.critical(self, "Scan Error", message)

    # -- exports --------------------------------------------------------

    def export_excel(self):
        if self.results_df.empty:
            QMessageBox.warning(self, "No Data", "Run a scan before exporting.")
            return

        default_name = (
            f"{slugify_market(self.current_strategy)}_{slugify_market(self.current_market)}_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        path, _ = QFileDialog.getSaveFileName(self, "Save Excel", default_name, "Excel Files (*.xlsx)")
        if not path:
            return
        try:
            self.results_df.to_excel(path, index=False)
            QMessageBox.information(self, "Saved", f"Excel file saved:\n{path}")
        except Exception as exc:
            QMessageBox.critical(self, "Export Failed", str(exc))

    def export_pdf(self):
        if self.results_df.empty:
            QMessageBox.warning(self, "No Data", "Run a scan before exporting.")
            return

        default_name = (
            f"{slugify_market(self.current_strategy)}_{slugify_market(self.current_market)}_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", default_name, "PDF Files (*.pdf)")
        if not path:
            return
        try:
            pdf_title = f"{APP_TITLE} - {self.current_strategy} - {self.current_market}"
            export_dataframe_to_pdf(self.results_df, path, pdf_title)
            QMessageBox.information(self, "Saved", f"PDF file saved:\n{path}")
        except Exception as exc:
            QMessageBox.critical(self, "Export Failed", str(exc))


def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    splash = SplashScreen()
    splash.finished.connect(window.show)
    splash.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
