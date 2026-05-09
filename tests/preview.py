"""
Windows preview script — runs the full app with mocked nmcli responses.
Usage: python tests/preview.py  (from the project root)
"""
import sys
import os
import subprocess
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# --- Mock state -----------------------------------------------------------
_connected_ssid = "HomeNetwork"

MOCK_NETWORKS = [
    {"in_use": True,  "ssid": "HomeNetwork",     "signal": 90, "security": "WPA2"},
    {"in_use": False, "ssid": "Neighbor_WiFi",   "signal": 72, "security": "WPA2"},
    {"in_use": False, "ssid": "CoffeeShop_Free", "signal": 58, "security": "--"},
    {"in_use": False, "ssid": "5G_Network_Ext",  "signal": 45, "security": "WPA3"},
    {"in_use": False, "ssid": "TinySignal",      "signal": 18, "security": "WPA2"},
]


def _build_list_output():
    lines = []
    for n in MOCK_NETWORKS:
        star = "*" if n["in_use"] else ""
        lines.append(f"{star}:{n['ssid']}:{n['signal']}:{n['security']}")
    return "\n".join(lines)


def _mock_run(cmd, **kwargs):
    global _connected_ssid

    result = SimpleNamespace(returncode=0, stdout="", stderr="")

    if not isinstance(cmd, (list, tuple)):
        return result

    if "rescan" in cmd:
        pass  # no-op, instant

    elif "list" in cmd:
        result.stdout = _build_list_output()

    elif "connect" in cmd:
        try:
            ssid_index = cmd.index("connect") + 1
            new_ssid = cmd[ssid_index]
        except (ValueError, IndexError):
            result.returncode = 1
            return result

        # Update which network is marked in-use
        for n in MOCK_NETWORKS:
            n["in_use"] = n["ssid"] == new_ssid
        _connected_ssid = new_ssid
        result.stdout = f"Device 'wlan0' successfully activated with '{new_ssid}'"

    return result


# Patch subprocess.run before the app modules import it
subprocess.run = _mock_run

# --- Launch app -----------------------------------------------------------
from main import main  # noqa: E402 — must come after patch

if __name__ == "__main__":
    main()
