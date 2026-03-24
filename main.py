import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

import database as db


def _make_tray_icon() -> QIcon:
    px = QPixmap(16, 16)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor("#4A90D9"))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(1, 1, 14, 14)
    p.end()
    return QIcon(px)


def main():
    db.init_db()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    from widget import MainWidget
    win = MainWidget()
    win.show()

    # System tray
    tray = QSystemTrayIcon(_make_tray_icon(), app)

    menu = QMenu()
    menu.setStyleSheet(
        "QMenu { background:#2A2A3E; color:#CCCCDD; border:1px solid #3A3A5C; }"
        "QMenu::item:selected { background:#3E3E5A; }"
    )
    act_show   = menu.addAction("위젯 보기")
    act_search = menu.addAction("검색 열기")
    menu.addSeparator()
    act_quit   = menu.addAction("종료")

    act_show.triggered.connect(lambda: (win.show(), win.raise_(), win.activateWindow()))
    act_search.triggered.connect(win._open_search)
    act_quit.triggered.connect(app.quit)

    tray.setContextMenu(menu)
    tray.activated.connect(
        lambda reason: (win.show(), win.raise_()) if reason == QSystemTrayIcon.ActivationReason.Trigger else None
    )
    tray.setToolTip("타임로그")
    tray.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
