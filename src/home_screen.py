import os
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPainter, QPixmap, QIcon

_ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
_BG_PATH = os.path.join(_ASSETS_DIR, "background.jpg")
_ICONS_DIR = os.path.join(_ASSETS_DIR, "icons")

ICON_SIZE = 200  # pixels

# (icon_filename, action) icon_filename is relative to assets/icons/
BUTTONS = [
    ("wifi.png",    "wifi"),
    ("filesys.png", "files"),
    ("AA.png",      "android_auto"),
    ("spotify.png", "spotify"),
    ("claude.png",  "claude"),
    (None, None),
]


class HomeScreen(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self._bg = QPixmap(_BG_PATH) if os.path.exists(_BG_PATH) else None
        self._setup_ui()

    def paintEvent(self, _):
        painter = QPainter(self)
        if self._bg:
            scaled = self._bg.scaled(
                self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        else:
            painter.fillRect(self.rect(), Qt.black)

    def _setup_ui(self):
        self.setStyleSheet("background: transparent;")

        layout = QGridLayout(self)
        layout.setSpacing(64)
        layout.setContentsMargins(48, 48, 48, 48)

        for i, (icon_file, action) in enumerate(BUTTONS):
            row, col = divmod(i, 3)
            btn = self._make_button(icon_file, action)
            layout.addWidget(btn, row, col)

    def _make_button(self, icon_file, action):
        btn = QPushButton()
        btn.setMinimumSize(140, 200)
        btn.setCursor(Qt.PointingHandCursor if action else Qt.ArrowCursor)

        if icon_file:
            icon_path = os.path.join(_ICONS_DIR, icon_file)
            if os.path.exists(icon_path):
                btn.setIcon(QIcon(icon_path))
                btn.setIconSize(QSize(ICON_SIZE, ICON_SIZE))

        if action:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(28, 28, 30, 180);
                    border-radius: 20px;
                    border: 2px solid rgba(255, 255, 255, 60);
                }
                QPushButton:pressed {
                    background-color: rgba(60, 60, 65, 200);
                }
            """)
            btn.clicked.connect(lambda _, a=action: self._on_action(a))
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(20, 20, 22, 100);
                    border-radius: 20px;
                    border: 2px solid rgba(255, 255, 255, 20);
                }
            """)
            btn.setEnabled(False)

        return btn

    def _on_action(self, action):
        if not self.main_window:
            return
        if action == "wifi":
            self.main_window.show_wifi()
        elif action == "files":
            self.main_window.show_files()
        elif action == "android_auto":
            self.main_window.launch_android_auto()
        elif action == "spotify":
            self.main_window.launch_spotify()
