#!/usr/bin/env python3
"""
Breakout Scanner Global Markets - core scanning logic

Pure data/logic module with no GUI dependency, so it can be imported both
by the PyQt5 desktop app (breakout_scanner_app.py) and by headless callers
(e.g. a scheduled CI job that generates the website's daily scan data).

Ported from the notebooks in this project
(YouTuber_Stock_Scanner_Gujarati_FINAL.ipynb / YouTuber_Stock_Scanner_TSX_FINAL.ipynb)
and generalized to run against any Yahoo-Finance-covered exchange via the
MARKETS registry below. Three independent strategies:

- Breakout (DMA + CAR): price above the 30/50/200-day moving averages plus
  a strengthening Cumulative Average Return.
- RSI 5-Star: a multi-timeframe RSI pullback setup (Monthly/Weekly RSI > 60,
  a Daily RSI pullback near 40, entry above that signal candle's high).
- Confluence (Both): stocks that pass both of the above at once.
"""

import warnings
import logging
from datetime import datetime

import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

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
            if pd.isna(cmp):
                # Yahoo Finance sometimes returns a NaN Close for the most
                # recent bar (session not fully settled yet) - skip rather
                # than let a NaN price leak into the results.
                continue

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

            if pd.isna(risk) or risk <= 0:
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
            if pd.isna(signal_high):
                continue

            cmp = float(close.iloc[-1])
            if pd.isna(cmp):
                # NaN Close (session not fully settled yet) - unlike the
                # Breakout strategy's strict `>` checks, `cmp <= signal_high`
                # below evaluates False for NaN and would silently let this
                # through, so it needs an explicit guard.
                continue
            if cmp <= signal_high:
                continue

            swing_window = low.loc[:signal_date].tail(RSI_SL_LOOKBACK_DAYS)
            sl = float(swing_window.min())
            entry = signal_high
            risk = entry - sl
            if pd.isna(risk) or risk <= 0:
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
            if pd.isna(cmp):
                # NaN Close (session not fully settled yet) - the RSI half's
                # `cmp <= signal_high` check evaluates False for NaN and
                # would silently let this through, so guard explicitly.
                continue

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
            if pd.isna(signal_high) or cmp <= signal_high:
                continue

            rsi_sl = float(low.loc[:signal_date].tail(RSI_SL_LOOKBACK_DAYS).min())

            # --- Both passed: combine into one set of trade levels ---
            sl = max(breakout_sl, rsi_sl)
            entry = cmp
            risk = entry - sl
            if pd.isna(risk) or risk <= 0:
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
