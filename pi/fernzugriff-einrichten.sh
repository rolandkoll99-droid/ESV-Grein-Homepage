#!/bin/bash
# =====================================================================
#  ESV Grein – Fernzugriff über esv-grein.com einrichten (Cloudflare-Tunnel)
#  Aufruf:  sudo bash /opt/esv-grein/pi/fernzugriff-einrichten.sh <TUNNEL-TOKEN>
#  Den Token gibt es im Cloudflare-Dashboard beim Anlegen des Tunnels
#  (siehe ANLEITUNG-PI.md, Schritt 4).
# =====================================================================
set -e
TOKEN="$1"
[ "$(id -u)" = "0" ] || { echo "Bitte mit sudo starten."; exit 1; }
if [ -z "$TOKEN" ]; then
  echo "Aufruf: sudo bash $0 <TUNNEL-TOKEN>"
  echo "Den Token findest du im Cloudflare-Dashboard beim Tunnel (Teil des angezeigten Befehls nach „service install“)."
  exit 1
fi

ARCH=$(dpkg --print-architecture)   # arm64 (64-Bit-System) oder armhf (32-Bit)
case "$ARCH" in
  arm64|armhf|amd64) ;;
  *) echo "Unbekannte Architektur: $ARCH"; exit 1 ;;
esac

if ! command -v cloudflared >/dev/null; then
  echo "cloudflared wird installiert ($ARCH) …"
  TMP=$(mktemp -d)
  curl -fsSL -o "$TMP/cloudflared.deb" "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-$ARCH.deb"
  dpkg -i "$TMP/cloudflared.deb"
  rm -rf "$TMP"
fi

# vorhandenen Tunnel-Dienst ersetzen
if systemctl list-unit-files | grep -q '^cloudflared.service'; then
  cloudflared service uninstall || true
fi
cloudflared service install "$TOKEN"
systemctl enable --now cloudflared
sleep 3
if systemctl is-active --quiet cloudflared; then
  echo
  echo "Fernzugriff eingerichtet. Der Tunnel startet ab jetzt automatisch."
  echo "Im Cloudflare-Dashboard sollte der Tunnel als „Healthy“ angezeigt werden."
  echo "Test von außen (z. B. Handy ohne WLAN):  https://esv-grein.com"
else
  echo "Der Tunnel läuft nicht. Protokoll:"
  journalctl -u cloudflared -n 30 --no-pager
fi
