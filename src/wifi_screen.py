import subprocess
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QListWidgetItem, QDialog, QLineEdit,
    QDialogButtonBox,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont


class NetworkScanner(QThread):
    networks_found = pyqtSignal(list)

    def run(self):
        try:
            subprocess.run(
                ["nmcli", "device", "wifi", "rescan"],
                capture_output=True, timeout=10,
            )
            result = subprocess.run(
                ["nmcli", "-t", "-f", "IN-USE,SSID,SIGNAL,SECURITY", "device", "wifi", "list"],
                capture_output=True, text=True, timeout=10,
            )
            networks = []
            seen = set()
            for line in result.stdout.strip().splitlines():
                parts = line.split(":")
                if len(parts) < 4:
                    continue
                in_use = parts[0].strip() == "*"
                ssid = parts[1].strip()
                if not ssid or ssid in seen:
                    continue
                seen.add(ssid)
                try:
                    signal = int(parts[2])
                except ValueError:
                    signal = 0
                security = parts[3].strip()
                networks.append({
                    "ssid": ssid,
                    "signal": signal,
                    "secured": bool(security and security != "--"),
                    "in_use": in_use,
                })
            networks.sort(key=lambda n: (n["in_use"], n["signal"]), reverse=True)
            self.networks_found.emit(networks)
        except Exception:
            self.networks_found.emit([])


class PasswordDialog(QDialog):
    def __init__(self, parent, ssid):
        super().__init__(parent)
        self.setWindowTitle(f"Connect to {ssid}")
        self.setModal(True)
        self.setMinimumWidth(420)
        self.setStyleSheet("background-color: #1c1c1e; color: white;")

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        label = QLabel(f'Password for "{ssid}"')
        label.setFont(QFont("Arial", 16))
        layout.addWidget(label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(QFont("Arial", 16))
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #2c2c2e;
                color: white;
                border: 1px solid #3a3a3c;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.password_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.setStyleSheet("""
            QPushButton {
                color: #0a84ff;
                background: none;
                border: none;
                font-size: 16px;
                padding: 6px 12px;
            }
        """)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def get_password(parent, ssid):
        dialog = PasswordDialog(parent, ssid)
        accepted = dialog.exec_() == QDialog.Accepted
        return dialog.password_input.text(), accepted


class WifiScreen(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("background-color: black;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 32, 48, 48)
        layout.setSpacing(20)

        # Header row
        header = QHBoxLayout()

        back_btn = QPushButton("‹  Back")
        back_btn.setFont(QFont("Arial", 18))
        back_btn.setStyleSheet("""
            QPushButton { background: none; color: #0a84ff; border: none; }
            QPushButton:pressed { color: #0060c0; }
        """)
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.clicked.connect(self._go_back)

        title = QLabel("WiFi")
        title.setFont(QFont("Arial", 26, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: white;")

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFont(QFont("Arial", 18))
        refresh_btn.setStyleSheet("""
            QPushButton { background: none; color: #0a84ff; border: none; }
            QPushButton:pressed { color: #0060c0; }
        """)
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.clicked.connect(self._scan)

        header.addWidget(back_btn)
        header.addWidget(title, 1)
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        # Status line
        self.status_label = QLabel("Scanning…")
        self.status_label.setFont(QFont("Arial", 14))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #8e8e93;")
        layout.addWidget(self.status_label)

        # Network list
        self.network_list = QListWidget()
        self.network_list.setFont(QFont("Arial", 17))
        self.network_list.setStyleSheet("""
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
        self.network_list.itemClicked.connect(self._on_network_clicked)
        layout.addWidget(self.network_list)

    def showEvent(self, event):
        super().showEvent(event)
        self._scan()

    def _scan(self):
        self.status_label.setText("Scanning…")
        self.network_list.clear()
        self.network_list.setEnabled(False)
        self._scanner = NetworkScanner()
        self._scanner.networks_found.connect(self._on_networks_found)
        self._scanner.start()

    def _on_networks_found(self, networks):
        self.network_list.setEnabled(True)
        self.network_list.clear()

        if not networks:
            self.status_label.setText("No networks found")
            return

        self.status_label.setText(f"{len(networks)} network{'s' if len(networks) != 1 else ''} found")

        for net in networks:
            text = self._format_network(net)
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, net)
            if net["in_use"]:
                item.setForeground(Qt.green)
            self.network_list.addItem(item)

    def _format_network(self, net):
        connected = "✓  " if net["in_use"] else "    "
        lock = "  🔒" if net["secured"] else ""
        bars = self._signal_bars(net["signal"])
        return f"{connected}{net['ssid']}{lock}   {bars}"

    def _signal_bars(self, signal):
        if signal >= 75:
            return "▂▄▆█"
        if signal >= 50:
            return "▂▄▆░"
        if signal >= 25:
            return "▂▄░░"
        return "▂░░░"

    def _on_network_clicked(self, item):
        net = item.data(Qt.UserRole)
        if net["in_use"]:
            return

        if net["secured"]:
            password, ok = PasswordDialog.get_password(self, net["ssid"])
            if not ok:
                return
        else:
            password = None

        self._connect(net["ssid"], password)

    def _connect(self, ssid, password):
        self.status_label.setText(f"Connecting to {ssid}…")
        self.network_list.setEnabled(False)
        try:
            cmd = ["nmcli", "device", "wifi", "connect", ssid]
            if password:
                cmd += ["password", password]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                self.status_label.setText(f"Connected to {ssid}")
            else:
                self.status_label.setText("Connection failed — check password")
        except subprocess.TimeoutExpired:
            self.status_label.setText("Connection timed out")
        except Exception:
            self.status_label.setText("Connection error")
        finally:
            self._scan()

    def _go_back(self):
        if self.main_window:
            self.main_window.show_home()
