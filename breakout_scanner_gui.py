#!/usr/bin/env python3
"""
INSTITUTIONAL GRADE BREAKOUT SCANNER WITH GUI
Stock Screening Tool for Trading Setups (SL, T1, T2)
"""

import sys
import json
from datetime import datetime
from threading import Thread
import yfinance as yf
import pandas as pd
import warnings
import logging

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel,
                             QPushButton, QProgressBar, QComboBox, QSpinBox,
                             QCheckBox, QMessageBox, QFileDialog, QTabWidget)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QColor, QFont, QIcon

logging.getLogger('yfinance').setLevel(logging.CRITICAL)
warnings.filterwarnings('ignore')

# =========================================================================
# TECHNICAL INDICATOR FUNCTIONS
# =========================================================================

def calculate_rsi(data, period=14):
    close = data['Close'].squeeze()
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1] if len(rsi) > 0 else 0

def calculate_adx(data, period=14):
    try:
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
        return adx.iloc[-1] if len(adx) > 0 else 0
    except:
        return 0

def calculate_macd(data):
    try:
        close = data['Close'].squeeze()
        exp1 = close.ewm(span=12, adjust=False).mean()
        exp2 = close.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        macd_bullish = (macd.iloc[-1] > signal.iloc[-1]) and (macd.iloc[-2] <= signal.iloc[-2])
        return macd_bullish
    except:
        return False

def calculate_atr(data, period=14):
    try:
        high = data['High'].squeeze()
        low = data['Low'].squeeze()
        close = data['Close'].squeeze()
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()
        atr_percent = (atr / close) * 100
        return atr_percent.iloc[-1] if len(atr_percent) > 0 else 0
    except:
        return 0

# =========================================================================
# SCANNER THREAD (For non-blocking UI)
# =========================================================================

class ScannerThread(QThread):
    progress = pyqtSignal(int)
    result = pyqtSignal(pd.DataFrame)
    error = pyqtSignal(str)

    def __init__(self, ticker_list, filters):
        super().__init__()
        self.ticker_list = ticker_list
        self.filters = filters

    def run(self):
        try:
            results = []
            total = len(self.ticker_list)

            for idx, ticker in enumerate(self.ticker_list):
                self.progress.emit(int((idx / total) * 100))

                try:
                    data = yf.download(ticker, period="2y", interval="1d", progress=False)

                    if data.empty or len(data) < 200:
                        continue

                    close_prices = data['Close'].squeeze()

                    # Calculate DMAs
                    dma_30 = close_prices.rolling(window=30).mean().iloc[-1]
                    dma_50 = close_prices.rolling(window=50).mean().iloc[-1]
                    dma_200 = close_prices.rolling(window=200).mean().iloc[-1]
                    cmp = close_prices.iloc[-1]

                    # Core filter: Price above DMAs
                    if not (cmp > dma_30 and cmp > dma_50 and cmp > dma_200):
                        continue

                    # CAR check (with relaxed condition)
                    dist_200_dma = ((cmp - dma_200) / dma_200) * 100

                    last_1y_data = data.tail(252)
                    high_date = last_1y_data['High'].squeeze().idxmax()
                    car_data = close_prices.loc[high_date:]

                    if len(car_data) < 10:
                        continue

                    car_values = car_data.expanding().mean()
                    last_10_car = car_values.tail(10)

                    # Relaxed CAR: At least 70% of days should be positive
                    car_increases = sum(1 for i in range(1, len(last_10_car)) if last_10_car.iloc[i] > last_10_car.iloc[i-1])
                    car_status = 'Positive' if car_increases >= 7 else 'Negative'

                    if car_status != 'Positive':
                        continue

                    # SL, T1, T2 Calculation
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

                    # Technical indicators
                    high_52 = data['High'].tail(252).max()
                    dist_52 = ((high_52 - entry) / high_52) * 100

                    returns = ((entry - close_prices.iloc[-21]) / close_prices.iloc[-21]) * 100 if len(close_prices) > 21 else 0

                    if dma_30 > dma_50 > dma_200:
                        trend = "Strong Uptrend"
                    else:
                        trend = "Weak"

                    rsi = calculate_rsi(data)
                    rsi_signal = rsi > self.filters['rsi_threshold']

                    adx = calculate_adx(data)
                    adx_signal = adx > self.filters['adx_threshold']

                    macd_bullish = calculate_macd(data)

                    within_52w_high = dist_52 < 10

                    volume = data['Volume'].squeeze()
                    avg_volume = volume.rolling(20).mean().iloc[-1]
                    today_volume = volume.iloc[-1]
                    volume_breakout = today_volume > (1.5 * avg_volume)

                    atr_percent = calculate_atr(data)

                    # Quality Score
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
                        'Dist %': round(dist_200_dma, 2),
                        'SL': round(sl, 2),
                        'SL %': round(sl_percent, 2),
                        'T1': round(t1, 2),
                        'T2': round(t2, 2),
                        'RSI': round(rsi, 2),
                        'ADX': round(adx, 2),
                        'ATR %': round(atr_percent, 2),
                        'Trend': trend,
                        'Reward %': round(reward_percent, 2),
                        '1M Ret %': round(returns, 2),
                        'Quality': quality_score,
                        'Vol Break': '✓' if volume_breakout else '✗',
                        'MACD': '✓' if macd_bullish else '✗'
                    })

                except Exception:
                    pass

            self.progress.emit(100)

            if results:
                df = pd.DataFrame(results)
                df = df.sort_values(by='Quality', ascending=False)
                self.result.emit(df)
            else:
                self.error.emit("No stocks found matching criteria")

        except Exception as e:
            self.error.emit(f"Error: {str(e)}")

# =========================================================================
# MAIN GUI APPLICATION
# =========================================================================

class BreakoutScannerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📈 Institutional Breakout Scanner")
        self.setGeometry(100, 100, 1600, 900)
        self.setStyleSheet(self.get_stylesheet())

        self.results_df = None
        self.scanner_thread = None

        self.init_ui()

    def get_stylesheet(self):
        return """
        QMainWindow {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        QLabel {
            color: #ffffff;
            font-size: 11px;
        }
        QPushButton {
            background-color: #0d7377;
            color: #ffffff;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #14919b;
        }
        QPushButton:pressed {
            background-color: #0a5a5f;
        }
        QTableWidget {
            background-color: #2d2d2d;
            gridline-color: #3d3d3d;
            color: #ffffff;
        }
        QTableWidget::item {
            padding: 4px;
        }
        QHeaderView::section {
            background-color: #0d7377;
            color: #ffffff;
            padding: 5px;
            border: none;
        }
        QProgressBar {
            border: none;
            border-radius: 4px;
            background-color: #3d3d3d;
            color: #ffffff;
        }
        QProgressBar::chunk {
            background-color: #0d7377;
        }
        QSpinBox, QComboBox {
            background-color: #2d2d2d;
            color: #ffffff;
            border: 1px solid #0d7377;
            padding: 4px;
        }
        QCheckBox {
            color: #ffffff;
        }
        """

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()

        # ===== TOP CONTROL PANEL =====
        control_layout = QHBoxLayout()

        control_layout.addWidget(QLabel("RSI Threshold:"))
        self.rsi_spin = QSpinBox()
        self.rsi_spin.setValue(55)
        self.rsi_spin.setMaximum(100)
        control_layout.addWidget(self.rsi_spin)

        control_layout.addWidget(QLabel("ADX Threshold:"))
        self.adx_spin = QSpinBox()
        self.adx_spin.setValue(20)
        self.adx_spin.setMaximum(100)
        control_layout.addWidget(self.adx_spin)

        self.scan_btn = QPushButton("🔍 START SCAN")
        self.scan_btn.setMinimumHeight(35)
        self.scan_btn.clicked.connect(self.start_scan)
        control_layout.addWidget(self.scan_btn)

        self.export_btn = QPushButton("💾 EXPORT EXCEL")
        self.export_btn.setMinimumHeight(35)
        self.export_btn.clicked.connect(self.export_excel)
        self.export_btn.setEnabled(False)
        control_layout.addWidget(self.export_btn)

        control_layout.addStretch()

        layout.addLayout(control_layout)

        # ===== PROGRESS BAR =====
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setStyleSheet("QProgressBar::chunk {background-color: #14c784;}")
        layout.addWidget(self.progress_bar)

        # ===== RESULTS TABLE =====
        self.table = QTableWidget()
        self.table.setColumnCount(0)
        self.table.setRowCount(0)
        layout.addWidget(self.table)

        # ===== STATUS BAR =====
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready to scan")
        self.stats_label = QLabel("")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.stats_label)
        layout.addLayout(status_layout)

        main_widget.setLayout(layout)

    def start_scan(self):
        self.scan_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("⏳ Scanning... (This may take 5-10 minutes)")

        # NSE Stock list
        stocks = [
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
            'KFINTECH.NS', 'KOTAKBANK.NS', 'LT.NS', 'LAURUSLABS.NS', 'LICI.NS',
            'LODHA.NS', 'LUPIN.NS', 'MM.NS', 'MANAPPURAM.NS', 'MANKIND.NS',
            'MARICO.NS', 'MARUTI.NS', 'MFSL.NS', 'MAXHEALTH.NS', 'MOTILALOFS.NS',
            'MPHASIS.NS', 'MCX.NS', 'MUTHOOTFIN.NS', 'NBCC.NS', 'NHPC.NS',
            'NMDC.NS', 'NTPC.NS', 'NATIONALUM.NS', 'NESTLEIND.NS', 'NAMINDIA.NS',
            'OBEROIRLTY.NS', 'ONGC.NS', 'OIL.NS', 'PAYTM.NS', 'OFSS.NS',
            'POLICYBZR.NS', 'PGEL.NS', 'PIIND.NS', 'PNBHOUSING.NS', 'PAGEIND.NS',
            'PATANJALI.NS', 'PERSISTENT.NS', 'PETRONET.NS', 'PIDILITIND.NS', 'POLYCAB.NS',
            'PFC.NS', 'POWERGRID.NS', 'PREMIERENE.NS', 'PRESTIGE.NS', 'PNB.NS',
            'RBLBANK.NS', 'RECLTD.NS', 'RADICO.NS', 'RVNL.NS', 'RELIANCE.NS',
            'SBICARD.NS', 'SBILIFE.NS', 'SHREECEM.NS', 'SRF.NS', 'MOTHERSON.NS',
            'SHRIRAMFIN.NS', 'SIEMENS.NS', 'SOLARINDS.NS', 'SONACOMS.NS', 'SBIN.NS',
            'SAIL.NS', 'SUNPHARMA.NS', 'SUPREMEIND.NS', 'SUZLON.NS', 'SWIGGY.NS',
            'TATACONSUM.NS', 'TVSMOTOR.NS', 'TCS.NS', 'TATAELXSI.NS', 'TATAPOWER.NS',
            'TATASTEEL.NS', 'TECHM.NS', 'FEDERALBNK.NS', 'INDHOTEL.NS', 'PHOENIXLTD.NS',
            'TITAN.NS', 'TORNTPHARM.NS', 'TRENT.NS', 'TIINDIA.NS', 'UNOMINDA.NS',
            'UPL.NS', 'ULTRACEMCO.NS', 'UNIONBANK.NS', 'UNITDSPR.NS', 'VBL.NS',
            'VEDL.NS', 'IDEA.NS', 'VOLTAS.NS', 'WAAREEENER.NS', 'WIPRO.NS',
            'YESBANK.NS', 'ZYDUSLIFE.NS'
        ]

        filters = {
            'rsi_threshold': self.rsi_spin.value(),
            'adx_threshold': self.adx_spin.value()
        }

        self.scanner_thread = ScannerThread(stocks, filters)
        self.scanner_thread.progress.connect(self.update_progress)
        self.scanner_thread.result.connect(self.display_results)
        self.scanner_thread.error.connect(self.handle_error)
        self.scanner_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def display_results(self, df):
        self.results_df = df
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels(df.columns)

        for row_idx, row in df.iterrows():
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setFont(QFont("Courier", 10))

                # Color coding
                if col_idx == df.columns.get_loc('Quality'):
                    if value >= 70:
                        item.setBackground(QColor('#1a5f3a'))
                    elif value >= 60:
                        item.setBackground(QColor('#3d6b3f'))

                self.table.setItem(row_idx, col_idx, item)

        self.table.resizeColumnsToContents()

        self.status_label.setText(f"✅ Scan Complete! Found {len(df)} stocks")
        self.stats_label.setText(
            f"Avg Quality: {df['Quality'].mean():.0f} | "
            f"Avg Reward: {df['Reward %'].mean():.2f}% | "
            f"Avg SL: {df['SL %'].mean():.2f}%"
        )

        self.scan_btn.setEnabled(True)
        self.export_btn.setEnabled(True)

    def handle_error(self, error_msg):
        self.status_label.setText(f"⚠️ {error_msg}")
        self.scan_btn.setEnabled(True)
        QMessageBox.warning(self, "Scan Error", error_msg)

    def export_excel(self):
        if self.results_df is None or self.results_df.empty:
            QMessageBox.warning(self, "Export Error", "No results to export")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "breakout_stocks.xlsx", "Excel Files (*.xlsx)"
        )

        if file_path:
            self.results_df.to_excel(file_path, index=False)
            QMessageBox.information(self, "Success", f"Results saved to {file_path}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BreakoutScannerApp()
    window.show()
    sys.exit(app.exec_())
