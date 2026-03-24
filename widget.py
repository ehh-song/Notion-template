from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QVBoxLayout, QWidget,
)

from timeline import HOUR_HEIGHT, START_HOUR, TimelineWidget

_DAYS = ["월", "화", "수", "목", "금", "토", "일"]

WIDGET_STYLE = """
QWidget#shell {
    background: #1A1A2A;
    border-radius: 10px;
    border: 1px solid #2A2A42;
}
"""

HEADER_STYLE = """
QWidget#header {
    background: #232336;
    border-radius: 10px 10px 0 0;
}
QPushButton {
    background: #2E2E4A;
    border: none;
    border-radius: 5px;
    color: #AAAACC;
    font-size: 12px;
    padding: 0;
}
QPushButton:hover { background: #3E3E5A; }
"""

SCROLL_STYLE = """
QScrollArea { border: none; background: #13131F; }
QScrollBar:vertical {
    background: #1E1E30;
    width: 6px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #3A3A5C;
    border-radius: 3px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.current_date = QDate.currentDate()
        self._drag_pos = None
        self._search_win = None

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(262)

        self._build_ui()
        self._position()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self.shell = QWidget()
        self.shell.setObjectName("shell")
        self.shell.setStyleSheet(WIDGET_STYLE)

        inner = QVBoxLayout(self.shell)
        inner.setContentsMargins(0, 0, 0, 0)
        inner.setSpacing(0)

        inner.addWidget(self._build_header())
        inner.addWidget(self._build_scroll())

        outer.addWidget(self.shell)

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("header")
        header.setFixedHeight(52)
        header.setStyleSheet(HEADER_STYLE)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        btn_prev = QPushButton("◀")
        btn_prev.setFixedSize(28, 28)
        btn_prev.clicked.connect(self._prev_day)

        self.date_label = QLabel(self._format_date())
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.date_label.setStyleSheet("color: #FFFFFF;")

        btn_next = QPushButton("▶")
        btn_next.setFixedSize(28, 28)
        btn_next.clicked.connect(self._next_day)

        btn_search = QPushButton("🔍")
        btn_search.setFixedSize(28, 28)
        btn_search.clicked.connect(self._open_search)

        layout.addWidget(btn_prev)
        layout.addWidget(self.date_label, 1)
        layout.addWidget(btn_next)
        layout.addWidget(btn_search)

        # Enable dragging the widget by its header
        header.mousePressEvent = self._on_header_press
        header.mouseMoveEvent = self._on_header_move

        return header

    def _build_scroll(self) -> QScrollArea:
        self.scroll = QScrollArea()
        self.scroll.setStyleSheet(SCROLL_STYLE)
        self.scroll.setWidgetResizable(False)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setFixedHeight(640)

        self.timeline = TimelineWidget(self._date_str())
        self.scroll.setWidget(self.timeline)

        # Scroll to 08:00 by default
        self.scroll.verticalScrollBar().setValue(2 * HOUR_HEIGHT)
        return self.scroll

    # ── Header drag (move window) ─────────────────────────────────────────────

    def _on_header_press(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = ev.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def _on_header_move(self, ev):
        if self._drag_pos and ev.buttons() == Qt.MouseButton.LeftButton:
            self.move(ev.globalPosition().toPoint() - self._drag_pos)

    # ── Navigation ────────────────────────────────────────────────────────────

    def _prev_day(self):
        self.current_date = self.current_date.addDays(-1)
        self._refresh()

    def _next_day(self):
        self.current_date = self.current_date.addDays(1)
        self._refresh()

    def _refresh(self):
        self.date_label.setText(self._format_date())
        self.timeline.date_str = self._date_str()
        self.timeline.load_activities()
        self.timeline.update()

    # ── Search ────────────────────────────────────────────────────────────────

    def _open_search(self):
        from search import SearchWindow
        if self._search_win is None or not self._search_win.isVisible():
            self._search_win = SearchWindow()
            self._search_win.show()
        else:
            self._search_win.raise_()
            self._search_win.activateWindow()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _date_str(self) -> str:
        return self.current_date.toString("yyyy-MM-dd")

    def _format_date(self) -> str:
        dow = _DAYS[self.current_date.dayOfWeek() - 1]
        return self.current_date.toString(f"M월 d일 {dow}요일")

    def _position(self):
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - self.width() - 20, 80)
