import hashlib

from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QMenu, QMessageBox, QWidget

import database as db
from models import Activity

# ── Layout constants ──────────────────────────────────────────────────────────
HOUR_HEIGHT = 64       # px per hour
LABEL_WIDTH = 44       # px for hour labels on the left
START_HOUR = 6         # 06:00
END_HOUR = 26          # 26:00 = 02:00 next day
TOTAL_HOURS = END_HOUR - START_HOUR   # 20
SNAP_MIN = 10          # snap granularity in minutes
RESIZE_HANDLE = 7      # px from top/bottom edge that triggers resize

TAG_COLORS = [
    "#4A90D9", "#E74C3C", "#2ECC71", "#F39C12", "#9B59B6",
    "#1ABC9C", "#E67E22", "#3498DB", "#E91E63", "#00BCD4",
]


def tag_color(tag: str) -> str:
    idx = int(hashlib.md5(tag.encode()).hexdigest(), 16) % len(TAG_COLORS)
    return TAG_COLORS[idx]


# ── Time ↔ pixel helpers ──────────────────────────────────────────────────────

def time_to_min(t: str) -> int:
    """'HH:MM' → minutes from midnight (supports 24+ hours)."""
    h, m = map(int, t.split(":"))
    return h * 60 + m


def min_to_y(minutes: int) -> int:
    return int((minutes - START_HOUR * 60) * HOUR_HEIGHT / 60)


def y_to_min(y: int) -> int:
    return int(START_HOUR * 60 + y * 60 / HOUR_HEIGHT)


def snap(minutes: int) -> int:
    return round(minutes / SNAP_MIN) * SNAP_MIN


def min_to_str(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def hour_label(hour: int) -> str:
    h = hour % 24
    return f"{h:02d}:00"


# ── Timeline widget ───────────────────────────────────────────────────────────

class TimelineWidget(QWidget):
    def __init__(self, date_str: str, parent=None):
        super().__init__(parent)
        self.date_str = date_str
        self.activities: list[Activity] = []

        # drag state
        self.drag_mode: str | None = None   # 'create' | 'move' | 'resize_top' | 'resize_bottom'
        self.drag_activity: Activity | None = None
        self.drag_start_y: int = 0
        self.drag_orig: tuple[int, int] = (0, 0)   # (start_min, end_min) before drag
        self.drag_create_start: int = 0
        self.drag_create_end: int = 0
        self.drag_moved: bool = False
        self.press_pos: QPoint | None = None

        self.setFixedSize(250, TOTAL_HOURS * HOUR_HEIGHT)
        self.setMouseTracking(True)
        self.load_activities()

    # ── Data ─────────────────────────────────────────────────────────────────

    def load_activities(self):
        self.activities = db.get_activities_by_date(self.date_str)

    # ── Geometry helpers ──────────────────────────────────────────────────────

    def activity_rect(self, a: Activity) -> QRect:
        y1 = min_to_y(time_to_min(a.start_time))
        y2 = min_to_y(time_to_min(a.end_time))
        return QRect(LABEL_WIDTH + 1, y1, self.width() - LABEL_WIDTH - 3, y2 - y1)

    def activity_at(self, pos: QPoint) -> Activity | None:
        for a in reversed(self.activities):
            if self.activity_rect(a).contains(pos):
                return a
        return None

    def drag_zone(self, a: Activity, pos: QPoint) -> str:
        r = self.activity_rect(a)
        if abs(pos.y() - r.top()) <= RESIZE_HANDLE:
            return "resize_top"
        if abs(pos.y() - r.bottom()) <= RESIZE_HANDLE:
            return "resize_bottom"
        return "move"

    # ── Mouse events ──────────────────────────────────────────────────────────

    def mousePressEvent(self, ev):
        pos = ev.pos()
        activity = self.activity_at(pos)

        if ev.button() == Qt.MouseButton.RightButton:
            if activity:
                self._show_context_menu(activity, ev.globalPosition().toPoint())
            return

        if ev.button() != Qt.MouseButton.LeftButton:
            return

        self.drag_moved = False
        self.press_pos = pos

        if activity:
            self.drag_mode = self.drag_zone(activity, pos)
            self.drag_activity = activity
            self.drag_start_y = pos.y()
            self.drag_orig = (time_to_min(activity.start_time), time_to_min(activity.end_time))
        elif pos.x() >= LABEL_WIDTH:
            self.drag_mode = "create"
            self.drag_start_y = pos.y()
            snapped = snap(y_to_min(pos.y()))
            self.drag_create_start = snapped
            self.drag_create_end = snapped + SNAP_MIN

    def mouseMoveEvent(self, ev):
        pos = ev.pos()

        if self.press_pos and not self.drag_moved:
            if abs(pos.y() - self.press_pos.y()) > 4 or abs(pos.x() - self.press_pos.x()) > 4:
                self.drag_moved = True

        if not self.drag_mode:
            self._update_cursor(pos)
            return

        if not self.drag_moved:
            return

        if self.drag_mode == "create":
            raw = snap(y_to_min(max(0, min(pos.y(), self.height() - 1))))
            base = snap(y_to_min(self.drag_start_y))
            if raw >= base:
                self.drag_create_start = base
                self.drag_create_end = max(raw, base + SNAP_MIN)
            else:
                self.drag_create_start = raw
                self.drag_create_end = base + SNAP_MIN
            self.update()
            return

        if not self.drag_activity:
            return

        delta_min = int((pos.y() - self.drag_start_y) * 60 / HOUR_HEIGHT)
        orig_s, orig_e = self.drag_orig
        duration = orig_e - orig_s

        if self.drag_mode == "move":
            new_s = snap(orig_s + delta_min)
            new_s = max(START_HOUR * 60, min(new_s, END_HOUR * 60 - duration))
            self.drag_activity.start_time = min_to_str(new_s)
            self.drag_activity.end_time = min_to_str(new_s + duration)

        elif self.drag_mode == "resize_top":
            new_s = snap(orig_s + delta_min)
            new_s = max(START_HOUR * 60, min(new_s, orig_e - SNAP_MIN))
            self.drag_activity.start_time = min_to_str(new_s)

        elif self.drag_mode == "resize_bottom":
            new_e = snap(orig_e + delta_min)
            new_e = max(orig_s + SNAP_MIN, min(new_e, END_HOUR * 60))
            self.drag_activity.end_time = min_to_str(new_e)

        self.update()

    def mouseReleaseEvent(self, ev):
        if ev.button() != Qt.MouseButton.LeftButton:
            return

        if not self.drag_moved:
            # Treat as a single click
            pos = ev.pos()
            clicked = self.activity_at(pos)
            if clicked and self.drag_mode != "create":
                self._show_detail(clicked)
        else:
            if self.drag_mode == "create":
                if self.drag_create_end > self.drag_create_start:
                    self._show_add_dialog(self.drag_create_start, self.drag_create_end)
            elif self.drag_mode in ("move", "resize_top", "resize_bottom") and self.drag_activity:
                db.save_activity(self.drag_activity)

        self._reset_drag()
        self.update()

    def _reset_drag(self):
        self.drag_mode = None
        self.drag_activity = None
        self.drag_orig = (0, 0)
        self.drag_create_start = 0
        self.drag_create_end = 0
        self.drag_moved = False
        self.press_pos = None

    def _update_cursor(self, pos: QPoint):
        a = self.activity_at(pos)
        if a:
            zone = self.drag_zone(a, pos)
            if zone in ("resize_top", "resize_bottom"):
                self.setCursor(Qt.CursorShape.SizeVerCursor)
            else:
                self.setCursor(Qt.CursorShape.SizeAllCursor)
        else:
            self.setCursor(Qt.CursorShape.CrossCursor if pos.x() >= LABEL_WIDTH else Qt.CursorShape.ArrowCursor)

    # ── Dialogs ───────────────────────────────────────────────────────────────

    def _show_add_dialog(self, start_min: int, end_min: int):
        from dialogs import AddActivityDialog
        dlg = AddActivityDialog(self.date_str, min_to_str(start_min), min_to_str(end_min), self)
        if dlg.exec():
            a = dlg.get_activity()
            db.save_activity(a)
            self.load_activities()
            self.update()

    def _show_detail(self, activity: Activity):
        from dialogs import ActivityDetailDialog
        dlg = ActivityDetailDialog(activity, self)
        dlg.exec()
        self.load_activities()
        self.update()

    def _show_context_menu(self, activity: Activity, global_pos: QPoint):
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu { background:#2A2A3E; color:#CCCCDD; border:1px solid #444466; }"
            "QMenu::item:selected { background:#4A4A6A; }"
        )
        delete_act = menu.addAction("🗑  삭제")
        chosen = menu.exec(global_pos)
        if chosen == delete_act:
            reply = QMessageBox.question(
                self, "삭제 확인", f"'{activity.name}' 활동을 삭제하시겠습니까?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                db.delete_activity(activity.id)
                self.load_activities()
                self.update()

    # ── Paint ─────────────────────────────────────────────────────────────────

    def paintEvent(self, _ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        p.fillRect(self.rect(), QColor("#13131F"))

        # Hour grid lines & labels
        for i in range(TOTAL_HOURS + 1):
            hour = START_HOUR + i
            y = i * HOUR_HEIGHT

            # Full-hour line
            p.setPen(QPen(QColor("#2E2E4A"), 1))
            p.drawLine(LABEL_WIDTH, y, self.width(), y)

            # Half-hour line
            if i < TOTAL_HOURS:
                p.setPen(QPen(QColor("#222234"), 1))
                p.drawLine(LABEL_WIDTH, y + HOUR_HEIGHT // 2, self.width(), y + HOUR_HEIGHT // 2)

            # Label
            p.setPen(QColor("#666888"))
            p.setFont(QFont("Arial", 8))
            p.drawText(2, y + 13, hour_label(hour))

        # Activity blocks
        for a in self.activities:
            self._draw_activity(p, a)

        # Drag-to-create preview
        if self.drag_mode == "create" and self.drag_moved:
            y1 = min_to_y(self.drag_create_start)
            y2 = min_to_y(self.drag_create_end)
            preview = QRect(LABEL_WIDTH + 1, y1, self.width() - LABEL_WIDTH - 3, y2 - y1)
            p.fillRect(preview, QColor(80, 110, 220, 100))
            p.setPen(QPen(QColor("#6478DC"), 2))
            p.drawRect(preview)
            # Time hint
            p.setPen(QColor("#AAAAEE"))
            p.setFont(QFont("Arial", 8))
            p.drawText(preview.adjusted(4, 2, -4, -2),
                       Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                       f"{min_to_str(self.drag_create_start)}–{min_to_str(self.drag_create_end)}")

    def _draw_activity(self, p: QPainter, a: Activity):
        rect = self.activity_rect(a)
        if rect.height() < 3:
            return

        base = QColor(a.color)
        p.fillRect(rect, base)

        # Border
        p.setPen(QPen(base.darker(130), 1))
        p.drawRect(rect)

        # Resize handle hints
        handle_color = base.lighter(150)
        handle_color.setAlpha(160)
        p.fillRect(QRect(rect.x(), rect.y(), rect.width(), 3), handle_color)
        p.fillRect(QRect(rect.x(), rect.bottom() - 2, rect.width(), 3), handle_color)

        # Name
        p.setPen(QColor("#FFFFFF"))
        f = QFont("Arial", 8)
        f.setBold(True)
        p.setFont(f)
        text_rect = rect.adjusted(4, 4, -4, -4)
        p.drawText(text_rect,
                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap,
                   a.name)

        # Tags (only if enough height)
        if a.tags and rect.height() >= 32:
            p.setPen(QColor("#DDDDEE"))
            p.setFont(QFont("Arial", 7))
            tag_text = "  ".join(f"#{t}" for t in a.tags)
            p.drawText(rect.adjusted(4, 0, -4, -4),
                       Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
                       tag_text)
