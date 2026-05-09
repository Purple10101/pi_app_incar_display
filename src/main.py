import sys
from PyQt5.QtWidgets import QApplication, QStackedWidget
from PyQt5.QtCore import Qt
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

    def show_wifi(self):
        self.setCurrentWidget(self.wifi)

    def show_files(self):
        self.setCurrentWidget(self.files)

    def show_home(self):
        self.setCurrentWidget(self.home)


def main():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    window = MainWindow()
    window.showFullScreen()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
