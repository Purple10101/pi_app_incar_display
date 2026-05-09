import os
import subprocess
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QListWidgetItem,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

MEDIA_EXTENSIONS = {
    ".mp3", ".wav", ".flac", ".ogg", ".aac", ".m4a", ".opus",
    ".mp4", ".mkv", ".avi", ".mov", ".webm", ".m4v",
}

START_DIR = os.path.expanduser("~")


def _open_file(path):
    try:
        if sys.platform == "win32":
            os.startfile(path)
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception:
        pass


class FilesScreen(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self._current_path = START_DIR
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("background-color: black;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 32, 48, 48)
        layout.setSpacing(20)

        # Header
        header = QHBoxLayout()

        back_btn = QPushButton("‹  Back")
        back_btn.setFont(QFont("Arial", 18))
        back_btn.setStyleSheet("""
            QPushButton { background: none; color: #0a84ff; border: none; }
            QPushButton:pressed { color: #0060c0; }
        """)
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.clicked.connect(self._go_home)

        title = QLabel("Files")
        title.setFont(QFont("Arial", 26, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: white;")

        up_btn = QPushButton("↑  Up")
        up_btn.setFont(QFont("Arial", 18))
        up_btn.setStyleSheet("""
            QPushButton { background: none; color: #0a84ff; border: none; }
            QPushButton:pressed { color: #0060c0; }
        """)
        up_btn.setCursor(Qt.PointingHandCursor)
        up_btn.clicked.connect(self._go_up)

        header.addWidget(back_btn)
        header.addWidget(title, 1)
        header.addWidget(up_btn)
        layout.addLayout(header)

        # Current path breadcrumb
        self.path_label = QLabel()
        self.path_label.setFont(QFont("Arial", 13))
        self.path_label.setStyleSheet("color: #8e8e93;")
        self.path_label.setAlignment(Qt.AlignCenter)
        self.path_label.setWordWrap(True)
        layout.addWidget(self.path_label)

        # File/folder list
        self.file_list = QListWidget()
        self.file_list.setFont(QFont("Arial", 17))
        self.file_list.setStyleSheet("""
            QListWidget {
                background-color: #1c1c1e;
                border-radius: 14px;
                border: none;
                color: white;
            }
            QListWidget::item {
                padding: 18px 20px;
                border-bottom: 1px solid #2c2c2e;
            }
            QListWidget::item:last-child {
                border-bottom: none;
            }
            QListWidget::item:selected {
                background-color: #2c2c2e;
            }
        """)
        self.file_list.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.file_list)

    def showEvent(self, event):
        super().showEvent(event)
        self._load_directory(self._current_path)

    def _load_directory(self, path):
        self._current_path = path
        self.path_label.setText(path)
        self.file_list.clear()

        try:
            dirs, files = [], []
            for entry in os.scandir(path):
                if entry.name.startswith("."):
                    continue
                if entry.is_dir(follow_symlinks=False):
                    dirs.append(entry.name)
                elif entry.is_file():
                    ext = os.path.splitext(entry.name)[1].lower()
                    if ext in MEDIA_EXTENSIONS:
                        files.append(entry.name)

            dirs.sort(key=str.lower)
            files.sort(key=str.lower)

            for name in dirs:
                item = QListWidgetItem(f"📁   {name}")
                item.setData(Qt.UserRole, ("dir", os.path.join(path, name)))
                self.file_list.addItem(item)

            for name in files:
                item = QListWidgetItem(f"♪   {name}")
                item.setData(Qt.UserRole, ("file", os.path.join(path, name)))
                item.setForeground(Qt.cyan)
                self.file_list.addItem(item)

            if self.file_list.count() == 0:
                placeholder = QListWidgetItem("No media files here")
                placeholder.setForeground(Qt.gray)
                placeholder.setFlags(placeholder.flags() & ~Qt.ItemIsEnabled)
                self.file_list.addItem(placeholder)

        except PermissionError:
            err = QListWidgetItem("Permission denied")
            err.setForeground(Qt.red)
            err.setFlags(err.flags() & ~Qt.ItemIsEnabled)
            self.file_list.addItem(err)

    def _on_item_clicked(self, item):
        data = item.data(Qt.UserRole)
        if data is None:
            return
        kind, path = data
        if kind == "dir":
            self._load_directory(path)
        elif kind == "file":
            _open_file(path)

    def _go_up(self):
        parent = os.path.dirname(self._current_path)
        if parent != self._current_path:
            self._load_directory(parent)

    def _go_home(self):
        self._current_path = START_DIR
        if self.main_window:
            self.main_window.show_home()
