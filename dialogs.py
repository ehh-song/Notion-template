import hashlib

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QWidget,
)

import database as db
from models import Activity, Reflection

TAG_COLORS = [
    "#4A90D9", "#E74C3C", "#2ECC71", "#F39C12", "#9B59B6",
    "#1ABC9C", "#E67E22", "#3498DB", "#E91E63", "#00BCD4",
]

DIALOG_STYLE = """
QDialog {
    background: #1E1E2E;
    color: #CCCCDD;
    border: 1px solid #3A3A5C;
    border-radius: 8px;
}
QLabel { color: #AAAACC; font-size: 11px; }
QLabel#title { color: #FFFFFF; font-size: 14px; font-weight: bold; }
QLabel#meta  { color: #666888; font-size: 10px; }
QLabel#tags  { color: #7090CC; font-size: 10px; }
QLabel#section { color: #AAAACC; font-size: 10px; font-weight: bold; }
QLineEdit {
    background: #2A2A3E;
    border: 1px solid #3A3A5C;
    border-radius: 4px;
    color: #CCCCDD;
    padding: 4px 6px;
    font-size: 11px;
}
QLineEdit:focus { border-color: #6478DC; }
QPushButton {
    background: #3A3A5C;
    border: none;
    border-radius: 5px;
    color: #CCCCDD;
    padding: 6px 14px;
    font-size: 11px;
}
QPushButton:hover { background: #4A4A6C; }
QPushButton#primary {
    background: #4A90D9;
    color: #FFFFFF;
    font-weight: bold;
}
QPushButton#primary:hover { background: #5AA0E9; }
"""


def _tag_color(tag: str) -> str:
    idx = int(hashlib.md5(tag.encode()).hexdigest(), 16) % len(TAG_COLORS)
    return TAG_COLORS[idx]


def _divider() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet("color: #2E2E4A; margin: 2px 0;")
    return line


# ── Add Activity Dialog ───────────────────────────────────────────────────────

class AddActivityDialog(QDialog):
    def __init__(self, date_str: str, start_time: str, end_time: str, parent=None):
        super().__init__(parent)
        self._date = date_str
        self._start = start_time
        self._end = end_time
        self._result: Activity | None = None

        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(DIALOG_STYLE)
        self.setFixedWidth(280)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # Header
        layout.addWidget(QLabel("활동 추가"))
        time_label = QLabel(f"⏱  {start_time} – {end_time}")
        time_label.setObjectName("meta")
        layout.addWidget(time_label)
        layout.addWidget(_divider())

        # Name
        layout.addWidget(QLabel("활동 이름"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("예: 알고리즘 공부")
        layout.addWidget(self.name_input)

        # Tags
        layout.addWidget(QLabel("태그  (쉼표로 구분)"))
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("예: 공부, 개발")
        layout.addWidget(self.tag_input)

        layout.addWidget(_divider())

        # Buttons
        btn = QHBoxLayout()
        cancel = QPushButton("취소")
        confirm = QPushButton("추가")
        confirm.setObjectName("primary")
        cancel.clicked.connect(self.reject)
        confirm.clicked.connect(self._confirm)
        btn.addWidget(cancel)
        btn.addWidget(confirm)
        layout.addLayout(btn)

        self.name_input.setFocus()

    def _confirm(self):
        name = self.name_input.text().strip()
        if not name:
            self.name_input.setPlaceholderText("이름을 입력하세요!")
            self.name_input.setFocus()
            return
        tags = [t.strip() for t in self.tag_input.text().split(",") if t.strip()]
        color = _tag_color(tags[0]) if tags else TAG_COLORS[0]
        self._result = Activity(
            date=self._date,
            start_time=self._start,
            end_time=self._end,
            name=name,
            tags=tags,
            color=color,
        )
        self.accept()

    def get_activity(self) -> Activity | None:
        return self._result


# ── Reflection Section ────────────────────────────────────────────────────────

class _ReflectionSection(QWidget):
    def __init__(self, emoji: str, title: str, values: list[str], parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        header = QLabel(f"{emoji}  {title}")
        header.setObjectName("section")
        layout.addWidget(header)

        self.inputs: list[QLineEdit] = []
        for i in range(3):
            inp = QLineEdit()
            inp.setText(values[i] if i < len(values) else "")
            inp.setPlaceholderText(f"{i + 1}번째 항목")
            layout.addWidget(inp)
            self.inputs.append(inp)

    def values(self) -> list[str]:
        return [inp.text().strip() for inp in self.inputs]


# ── Activity Detail / Reflection Dialog ───────────────────────────────────────

class ActivityDetailDialog(QDialog):
    def __init__(self, activity: Activity, parent=None):
        super().__init__(parent)
        self.activity = activity
        ref = db.get_reflection(activity.id) or Reflection(activity_id=activity.id)

        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(DIALOG_STYLE)
        self.setFixedWidth(300)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # Activity header
        title = QLabel(activity.name)
        title.setObjectName("title")
        title.setWordWrap(True)
        layout.addWidget(title)

        meta = QLabel(f"⏱  {activity.start_time} – {activity.end_time}")
        meta.setObjectName("meta")
        layout.addWidget(meta)

        if activity.tags:
            tags = QLabel("  ".join(f"#{t}" for t in activity.tags))
            tags.setObjectName("tags")
            layout.addWidget(tags)

        layout.addWidget(_divider())

        # Reflection sections
        self.good = _ReflectionSection("✅", "잘한 점", ref.good)
        self.bad = _ReflectionSection("😅", "아쉬운 점", ref.bad)
        self.nxt = _ReflectionSection("🚀", "나아갈 점", ref.next_steps)
        layout.addWidget(self.good)
        layout.addWidget(self.bad)
        layout.addWidget(self.nxt)

        layout.addWidget(_divider())

        # Buttons
        btn = QHBoxLayout()
        close_btn = QPushButton("닫기")
        save_btn = QPushButton("저장")
        save_btn.setObjectName("primary")
        close_btn.clicked.connect(self.reject)
        save_btn.clicked.connect(self._save)
        btn.addWidget(close_btn)
        btn.addWidget(save_btn)
        layout.addLayout(btn)

    def _save(self):
        db.save_reflection(Reflection(
            activity_id=self.activity.id,
            good=self.good.values(),
            bad=self.bad.values(),
            next_steps=self.nxt.values(),
        ))
        self.accept()
