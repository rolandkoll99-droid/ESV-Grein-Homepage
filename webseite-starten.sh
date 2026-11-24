#!/bin/sh
# ESV Grein Webseite (macOS / Linux / Raspberry Pi)
cd "$(dirname "$0")"
exec python3 server.py "$@"
