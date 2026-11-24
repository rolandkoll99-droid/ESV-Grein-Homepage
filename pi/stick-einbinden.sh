#!/bin/bash
# Daten-Stick nach dem Wiedereinstecken einbinden und Webseite starten
# Aufruf: sudo bash /opt/esv-grein/pi/stick-einbinden.sh
STICK=/media/esv-stick
[ "$(id -u)" = "0" ] || { echo "Bitte mit sudo starten."; exit 1; }
sleep 2
mount "$STICK" 2>/dev/null || mount -a
if [ -f "$STICK/.esv-stick" ]; then
  systemctl restart esv-grein
  echo "Stick eingebunden – Webseite läuft wieder."
else
  echo "Daten-Stick „ESV-DATEN“ nicht gefunden. Ist er angesteckt?"
  exit 1
fi
