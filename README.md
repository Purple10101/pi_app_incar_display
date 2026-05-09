# Raspberry Pi Application

A Python application designed to run on Raspberry Pi.

## Setup

Create a virtual environment:

```bash
py -m venv .venv

## TODO: Android Auto (Hudiy)

The Android Auto button is wired but requires **Hudiy** to be installed on the Pi.

- License: $10 one-time from [hudiy.eu](https://hudiy.eu)
- Supports Pi 5 + Pi OS Bookworm (explicitly confirmed)
- Also provides CarPlay, OBD-II, Bluetooth calling
- Once installed, the button will launch it automatically — no code changes needed
- Integration pattern is the same as Spotify (hide app → launch Hudiy → return on close)
- Update `launch_android_auto()` in `src/main.py` to use the correct Hudiy binary name