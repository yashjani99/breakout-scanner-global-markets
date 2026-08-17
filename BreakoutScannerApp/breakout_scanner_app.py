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

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPainter, QPen
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QProgressBar,
    QFileDialog, QMessageBox, QHeaderView, QComboBox
)

from scanner_core import (
    MARKETS, DEFAULT_MARKET, STRATEGIES, DEFAULT_STRATEGY, BREAKOUT_DISPLAY_COLUMNS,
)

warnings.filterwarnings("ignore")
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

APP_TITLE = "Breakout Scanner Global Markets"
APP_VERSION = "2.0.4"
AUTHOR_CREDIT = "Developed by Yash Jani"
SPLASH_DURATION_MS = 5000


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
