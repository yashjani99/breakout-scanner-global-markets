#!/usr/bin/env python3
"""
Professional Stock Scanner GUI - Standalone Windows EXE
Built for: Trading India Stock Breakout Scanner
Version: 2.0
"""

import sys
import os
import threading
from datetime import datetime
from pathlib import Path

import yfinance as yf
import pandas as pd
import warnings
import logging

warnings.filterwarnings('ignore')
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QTableWidget, QTableWidgetItem, QProgressBar,
        QSpinBox, QComboBox, QFileDialog, QMessageBox, QStatusBar
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
    from PyQt5.QtGui import QFont, QColor, QIcon
except ImportError:
    print("ERROR: PyQt5 not installed!")
    sys.exit(1)


class ScannerThread(QThread):
    """Runs stock scanning in background thread"""
    progress = pyqtSignal(int)
    result_ready = pyqtSignal(pd.DataFrame)
    error_signal = pyqtSignal(str)

    def __init__(self, stocks, rsi_threshold, adx_threshold):
        super().__init__()
        self.stocks = stocks
        self.rsi_threshold = rsi_threshold
        self.adx_threshold = adx_threshold

    def run(self):
        try:
            results = []
            today_date = datetime.now().strftime("%d-%m-%Y")

            for idx, ticker in enumerate(self.stocks):
                try:
                    data = yf.download(ticker, period="2y", interval="1d", progress=False)

                    if data.empty or len(data) < 200:
                        continue

                    close_prices = data['Close'].squeeze()

                    dma_30 = float(close_prices.rolling(window=30).mean().iloc[-1])
                    dma_50 = float(close_prices.rolling(window=50).mean().iloc[-1])
                    dma_200 = float(close_prices.rolling(window=200).mean().iloc[-1])
                    cmp = float(close_prices.iloc[-1])

                    dist_200_dma = ((cmp - dma_200) / dma_200) * 100

                    last_1y_data = data.tail(252)
                    high_date = last_1y_data['High'].squeeze().idxmax()
                    car_data = close_prices.loc[high_date:]

                    if len(car_data) < 10:
                        continue

                    car_values = car_data.expanding().mean()
                    last_10_car = car_values.tail(10)
                    car_status = 'Positive' if last_10_car.is_monotonic_increasing else 'Negative'

                    if not ((cmp > dma_30) and (cmp > dma_50) and (cmp > dma_200) and (car_status == 'Positive')):
                        continue

                    swing_low = float(data['Low'].tail(10).min().item())
                    sl = swing_low
                    entry = cmp
                    risk = entry - sl

                    if risk <= 0:
                        continue

                    t1 = entry + (2 * risk)
                    t2 = entry + (3 * risk)
                    t3 = entry + (5 * risk)

                    reward_percent = ((t2 - entry) / entry) * 100
                    sl_percent = ((entry - sl) / entry) * 100
                    rr_ratio = reward_percent / sl_percent if sl_percent > 0 else 0

                    high_52 = float(data['High'].tail(252).max().item())
                    dist_52 = ((high_52 - entry) / high_52) * 100

                    if dma_30 > dma_50 > dma_200:
                        trend = "Strong Uptrend"
                    else:
                        trend = "Weak"

                    results.append({
                        'Date': today_date,
                        'Stock': ticker.replace('.NS', ''),
                        'Price': round(entry, 2),
                        'SL': round(sl, 2),
                        'SL %': round(sl_percent, 2),
                        'T1': round(t1, 2),
                        'T2': round(t2, 2),
                        'T3': round(t3, 2),
                        'Risk': round(risk, 2),
                        'Target %': round(reward_percent, 2),
                        'R:R': round(rr_ratio, 2),
                        'Trend': trend,
                        'CAR': car_status,
                    })

                except:
                    pass

                progress_value = int((idx + 1) / len(self.stocks) * 100)
                self.progress.emit(progress_value)

            if results:
                df = pd.DataFrame(results)
                df = df.sort_values(by='Target %', ascending=False)
                self.result_ready.emit(df)
            else:
                self.result_ready.emit(pd.DataFrame())

        except Exception as e:
            self.error_signal.emit(f"Error: {str(e)}")


class StockScannerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.results_df = None
        self.init_ui()
        self.setWindowTitle("📈 Stock Breakout Scanner Pro")
        self.setGeometry(100, 100, 1400, 800)

    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(15)

        title_label = QLabel("📊 NSE Stock Breakout Scanner")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        top_layout.addWidget(title_label)

        self.scan_button = QPushButton("▶️ Start Scanning")
        self.scan_button.setStyleSheet("""
            QPushButton {
                background-color: #0d7377;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #14919b;
            }
            QPushButton:pressed {
                background-color: #0a5a61;
            }
        """)
        self.scan_button.clicked.connect(self.start_scan)
        top_layout.addWidget(self.scan_button)

        self.export_button = QPushButton("💾 Export to Excel")
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #2d6a4f;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #40916c;
            }
            QPushButton:pressed {
                background-color: #1b4332;
            }
        """)
        self.export_button.clicked.connect(self.export_to_excel)
        self.export_button.setEnabled(False)
        top_layout.addWidget(self.export_button)

        top_layout.addStretch()
        main_layout.addLayout(top_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #0d7377;
                border-radius: 5px;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #0d7377;
            }
        """)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        self.table = QTableWidget()
        self.table.setColumnCount(13)
        self.table.setHorizontalHeaderLabels([
            'Stock', 'Price', 'SL', 'SL %', 'T1', 'T2', 'T3',
            'Risk', 'Target %', 'R:R', 'Trend', 'CAR', 'Date'
        ])
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f9f9f9;
                gridline-color: #d0d0d0;
                border: 1px solid #d0d0d0;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #0d7377;
                color: white;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #0d7377;
                color: white;
            }
        """)
        self.table.setAlternatingRowColors(True)
        main_layout.addWidget(self.table)

        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready to scan...")
        self.status_label.setStyleSheet("color: #0d7377; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        self.count_label = QLabel("")
        self.count_label.setStyleSheet("color: #2d6a4f; font-weight: bold;")
        status_layout.addWidget(self.count_label)

        main_layout.addLayout(status_layout)
        central_widget.setLayout(main_layout)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #fafafa;
            }
        """)

    def start_scan(self):
        """Start the stock scanning process"""
        self.scan_button.setEnabled(False)
        self.export_button.setEnabled(False)
        self.table.setRowCount(0)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("🔍 Scanning stocks... Please wait.")

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

        self.scanner_thread = ScannerThread(stocks, 0, 0)
        self.scanner_thread.progress.connect(self.update_progress)
        self.scanner_thread.result_ready.connect(self.display_results)
        self.scanner_thread.error_signal.connect(self.show_error)
        self.scanner_thread.start()

    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)

    def display_results(self, df):
        """Display results in table"""
        self.progress_bar.setVisible(False)
        self.scan_button.setEnabled(True)

        if df.empty:
            self.status_label.setText("❌ No stocks matched criteria today.")
            self.count_label.setText("")
        else:
            self.results_df = df
            self.table.setRowCount(len(df))

            for row, (idx, data) in enumerate(df.iterrows()):
                for col, key in enumerate(df.columns):
                    item = QTableWidgetItem(str(data[key]))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, col, item)

            self.table.resizeColumnsToContents()
            self.export_button.setEnabled(True)

            self.status_label.setText("✅ Scan complete!")
            self.count_label.setText(f"📊 Found {len(df)} stocks | Avg R:R: {df['R:R'].mean():.2f}:1")

    def export_to_excel(self):
        """Export results to Excel"""
        if self.results_df is None or self.results_df.empty:
            QMessageBox.warning(self, "No Data", "No results to export.")
            return

        filename = f"Stock_Scanner_Results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        self.results_df.to_excel(filename, index=False)
        QMessageBox.information(self, "Success", f"Results saved to:\n{filename}")

    def show_error(self, error_msg):
        """Show error message"""
        self.scan_button.setEnabled(True)
        QMessageBox.critical(self, "Error", error_msg)


def main():
    app = QApplication(sys.argv)
    window = StockScannerGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
