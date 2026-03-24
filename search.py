from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

import database as db

STYLE = """
QWidget#root {
    background: #1A1A2A;
    border-radius: 8px;
}
QWidget { background: #1A1A2A; color: #CCCCDD; }
QLineEdit {
    background: #2A2A3E;
    border: 1px solid #3A3A5C;
    border-radius: 5px;
    color: #CCCCDD;
    padding: 6px 10px;
    font-size: 12px;
}
QLineEdit:focus { border-color: #6478DC; }
QPushButton {
    background: #4A90D9;
    border: none;
    border-radius: 5px;
    color: #FFFFFF;
    padding: 7px 16px;
    font-size: 12px;
    font-weight: bold;
}
QPushButton:hover { background: #5AA0E9; }
QScrollArea { border: none; }
QScrollBar:vertical { background: #2A2A3E; width: 6px; border-radius: 3px; }
QScrollBar::handle:vertical { background: #4A4A6A; border-radius: 3px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""


def _divider() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet("QFrame { background: #2E2E48; max-height: 1px; }")
    return line


class _ResultCard(QFrame):
    def __init__(self, result: dict, parent=None):
        super().__init__(parent)
        a = result["activity"]
        r = result["reflection"]

        self.setStyleSheet("""
            QFrame {
                background: #23233A;
                border: 1px solid #2E2E4A;
                border-radius: 6px;
            }
            QLabel { background: transparent; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(3)

        # Name
        name = QLabel(a.name)
        name.setStyleSheet("color: #FFFFFF; font-size: 13px; font-weight: bold;")
        name.setWordWrap(True)
        layout.addWidget(name)

        # Date + time
        meta = QLabel(f"📅  {a.date}    ⏱  {a.start_time} – {a.end_time}")
        meta.setStyleSheet("color: #666888; font-size: 10px;")
        layout.addWidget(meta)

        # Tags
        if a.tags:
            tags = QLabel("  ".join(f"#{t}" for t in a.tags))
            tags.setStyleSheet("color: #7090CC; font-size: 10px;")
            layout.addWidget(tags)

        # Reflections
        if r:
            def _section(emoji, title, items):
                filled = [i for i in items if i.strip()]
                if not filled:
                    return
                layout.addWidget(_divider())
                hdr = QLabel(f"{emoji}  {title}")
                hdr.setStyleSheet("color: #AAAACC; font-size: 10px; font-weight: bold;")
                layout.addWidget(hdr)
                for item in filled:
                    lbl = QLabel(f"  • {item}")
                    lbl.setStyleSheet("color: #BBBBCC; font-size: 10px;")
                    lbl.setWordWrap(True)
                    layout.addWidget(lbl)

            _section("✅", "잘한 점", r.good)
            _section("😅", "아쉬운 점", r.bad)
            _section("🚀", "나아갈 점", r.next_steps)


class SearchWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("활동 검색")
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)
        self.setMinimumSize(340, 520)
        self.resize(360, 620)
        self.setStyleSheet(STYLE)
        self.setObjectName("root")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # Title
        title = QLabel("활동 검색")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(title)

        sub = QLabel("태그로 전체 기간의 활동과 회고를 검색합니다.")
        sub.setStyleSheet("color: #666888; font-size: 10px;")
        layout.addWidget(sub)

        # Search bar
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("태그 입력  (예: 공부)")
        self.search_input.returnPressed.connect(self._search)
        search_row.addWidget(self.search_input)

        btn = QPushButton("검색")
        btn.setFixedWidth(60)
        btn.clicked.connect(self._search)
        search_row.addWidget(btn)
        layout.addLayout(search_row)

        # Result count
        self.count_label = QLabel("")
        self.count_label.setStyleSheet("color: #666888; font-size: 10px;")
        layout.addWidget(self.count_label)

        # Scrollable results
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self._container = QWidget()
        self._results_layout = QVBoxLayout(self._container)
        self._results_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._results_layout.setSpacing(8)
        self._results_layout.setContentsMargins(0, 0, 4, 0)

        self.scroll.setWidget(self._container)
        layout.addWidget(self.scroll)

        self.search_input.setFocus()

    def _clear_results(self):
        while self._results_layout.count():
            item = self._results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _search(self):
        tag = self.search_input.text().strip()
        if not tag:
            return

        self._clear_results()
        results = db.search_by_tag(tag)
        self.count_label.setText(f"'{tag}' 검색 결과: {len(results)}개")

        if results:
            for r in results:
                self._results_layout.addWidget(_ResultCard(r))
        else:
            empty = QLabel("검색 결과가 없습니다.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color: #444466; font-size: 13px; padding: 40px 0;")
            self._results_layout.addWidget(empty)
