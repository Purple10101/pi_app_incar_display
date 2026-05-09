import os
import sys
os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

from PyQt5.QtWidgets import QApplication, QStackedWidget
from PyQt5.QtCore import QProcess
from home_screen import HomeScreen
from wifi_screen import WifiScreen
from files_screen import FilesScreen


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

        self._aa_process = QProcess(self)
        self._aa_process.finished.connect(self._on_android_auto_closed)

    def show_wifi(self):
        self.setCurrentWidget(self.wifi)

    def show_files(self):
        self.setCurrentWidget(self.files)

    def show_home(self):
        self.setCurrentWidget(self.home)

    def launch_android_auto(self):
        if self._aa_process.state() != QProcess.NotRunning:
            return
        self.hide()
        self._aa_process.start("openauto", [])

    def _on_android_auto_closed(self):
        self.setCurrentWidget(self.home)
        self.showFullScreen()


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.showFullScreen()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
