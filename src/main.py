import glob
import os
import random
import subprocess
import sys
if sys.platform != "win32":
    os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

from PyQt5.QtWidgets import QApplication, QStackedWidget, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtCore import QProcess, Qt
from home_screen import HomeScreen
from wifi_screen import WifiScreen
from files_screen import FilesScreen


class BackOverlay(QWidget):
    def __init__(self, on_close):
        super().__init__(None, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        btn = QPushButton("←")
        btn.setFixedSize(80, 80)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(28, 28, 30, 210);
                color: white;
                font-size: 32px;
                border-radius: 40px;
                border: 2px solid rgba(255, 255, 255, 60);
            }
            QPushButton:pressed {
                background-color: rgba(60, 60, 65, 230);
            }
        """)
        btn.clicked.connect(on_close)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(btn)
        self.setFixedSize(80, 80)

    def show_at_corner(self):
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - self.width() - 24, screen.height() - self.height() - 24)
        self.show()


class MainWindow(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Miata UI")
        self.setStyleSheet("background-color: black;")

        self.home = HomeScreen(self)
        self.wifi = WifiScreen(self)
        self.files = FilesScreen(self)

        self.addWidget(self.home)
        self.addWidget(self.wifi)
        self.addWidget(self.files)

        self.setCurrentWidget(self.home)

        self._overlay = BackOverlay(self._close_external)

        self._aa_process = QProcess(self)
        self._aa_process.finished.connect(self._on_external_closed)
        self._aa_process.errorOccurred.connect(lambda _: self._on_external_closed())

        self._spotify_process = QProcess(self)
        self._spotify_process.finished.connect(self._on_external_closed)
        self._spotify_process.errorOccurred.connect(lambda _: self._on_external_closed())

    def show_wifi(self):
        self.setCurrentWidget(self.wifi)

    def show_files(self):
        self.setCurrentWidget(self.files)

    def show_home(self):
        self.setCurrentWidget(self.home)

    def launch_android_auto(self):
        if self._aa_process.state() != QProcess.NotRunning:
            return
        self.showNormal()
        self.hide()
        self._aa_process.start(os.path.expanduser("~/.hudiy/share/hudiy_launcher.sh"), [])
        self._overlay.show_at_corner()

    def launch_spotify(self):
        if self._spotify_process.state() != QProcess.NotRunning:
            return
        self.showNormal()
        self.hide()
        self._spotify_process.start("chromium", [
            "--kiosk",
            "--app=https://open.spotify.com",
        ])
        self._overlay.show_at_corner()

    def _close_external(self):
        self._overlay.hide()
        if self._aa_process.state() != QProcess.NotRunning:
            self._aa_process.terminate()
        if self._spotify_process.state() != QProcess.NotRunning:
            self._spotify_process.terminate()

    def _on_external_closed(self):
        self._overlay.hide()
        self.setCurrentWidget(self.home)
        self.showFullScreen()


def _play_startup_media():
    if sys.platform == "win32":
        return
    media_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "sounds")
    audio = (glob.glob(os.path.join(media_dir, "*.wav")) +
             glob.glob(os.path.join(media_dir, "*.ogg")) +
             glob.glob(os.path.join(media_dir, "*.mp3")))
    video = (glob.glob(os.path.join(media_dir, "*.mp4")) +
             glob.glob(os.path.join(media_dir, "*.mkv")) +
             glob.glob(os.path.join(media_dir, "*.webm")))
    all_media = audio + video
    if not all_media:
        return
    pick = random.choice(all_media)
    if pick in video:
        subprocess.run(["mpv", "--fullscreen", "--really-quiet", "--no-osc", pick])
    elif pick.endswith(".mp3"):
        subprocess.Popen(["mpg123", "-q", pick])
    else:
        subprocess.Popen(["paplay", pick])


def main():
    app = QApplication(sys.argv)
    _play_startup_media()

    window = MainWindow()
    window.showFullScreen()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
