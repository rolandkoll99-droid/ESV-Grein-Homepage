#!/bin/bash
# Daten-Stick sicher entfernen (z. B. um Fotos am PC zu kopieren)
# Aufruf: sudo bash /opt/esv-grein/pi/stick-entfernen.sh
STICK=/media/esv-stick
[ "$(id -u)" = "0" ] || { echo "Bitte mit sudo starten."; exit 1; }
echo "Webseite wird angehalten …"
systemctl stop esv-grein
sync
if umount "$STICK"; then
  echo
  echo "Der Stick kann jetzt abgezogen werden."
  echo "Danach wieder anstecken und:  sudo bash /opt/esv-grein/pi/stick-einbinden.sh"
  echo "(oder den Pi einfach neu starten)"
else
  echo "Stick konnte nicht ausgehängt werden – bitte NICHT abziehen."
  systemctl start esv-grein
  exit 1
fi
