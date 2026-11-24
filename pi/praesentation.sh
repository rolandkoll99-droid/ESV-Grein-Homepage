#!/bin/bash
# =====================================================================
#  ESV Grein – Webseite als Vollbild-Präsentation auf dem Pi-Bildschirm
#  (Raspberry Pi OS mit Desktop, Monitor/Beamer am Pi)
#
#  sudo bash /opt/esv-grein/pi/praesentation.sh ein   -> startet ab jetzt nach jedem Einschalten im Vollbild
#  sudo bash /opt/esv-grein/pi/praesentation.sh aus   -> normaler Desktop
#  Im Vollbild: Alt+F4 beendet den Browser, F5 lädt neu.
# =====================================================================
MODUS="$1"
[ "$(id -u)" = "0" ] || { echo "Bitte mit sudo starten."; exit 1; }
BENUTZER=${SUDO_USER:-pi}
HEIM=$(getent passwd "$BENUTZER" | cut -d: -f6)
AUTOSTART="$HEIM/.config/autostart"
DATEI="$AUTOSTART/esv-grein-praesentation.desktop"

case "$MODUS" in
  ein)
    BROWSER=$(command -v chromium-browser || command -v chromium || true)
    if [ -z "$BROWSER" ]; then
      echo "Chromium wird installiert …"
      apt-get update -qq && (apt-get install -y -qq chromium-browser || apt-get install -y -qq chromium)
      BROWSER=$(command -v chromium-browser || command -v chromium || true)
    fi
    [ -n "$BROWSER" ] || { echo "Chromium konnte nicht installiert werden."; exit 1; }
    SITZUNGEN=$(ls /usr/share/xsessions /usr/share/wayland-sessions 2>/dev/null | grep -c "\.desktop$" || true)
    if [ "${SITZUNGEN:-0}" = "0" ] && ! systemctl get-default 2>/dev/null | grep -q graphical; then
      echo "Hinweis: Auf diesem Pi ist kein Desktop installiert (Raspberry Pi OS Lite)."
      echo "Für die Vollbild-Präsentation wird „Raspberry Pi OS mit Desktop“ benötigt."
      echo "Die Webseite selbst läuft trotzdem und ist über das Netzwerk erreichbar."
      exit 2
    fi
    # andere Vollbild-Anwendungen (z. B. Anzeigetafel) im Autostart?
    ANDERE=$(grep -l -- "--kiosk" "$AUTOSTART"/*.desktop 2>/dev/null | grep -v esv-grein-praesentation || true)
    if [ -n "$ANDERE" ]; then
      echo "Achtung: Im Autostart ist bereits eine andere Vollbild-Anwendung eingetragen:"
      echo "$ANDERE"
      echo "Beide gleichzeitig funktionieren nicht. Bitte zuerst dort deaktivieren (Datei umbenennen)."
      exit 3
    fi
    sudo -u "$BENUTZER" mkdir -p "$AUTOSTART"
    cat > "$DATEI" <<DESKTOP
[Desktop Entry]
Type=Application
Name=ESV Grein Präsentation
Comment=Vereinswebseite im Vollbild
Exec=sh -c 'sleep 10; $BROWSER --kiosk --noerrdialogs --disable-infobars --disable-session-crashed-bubble --incognito --check-for-update-interval=31536000 http://localhost/'
X-GNOME-Autostart-enabled=true
DESKTOP
    chown "$BENUTZER":"$BENUTZER" "$DATEI"
    command -v raspi-config >/dev/null && raspi-config nonint do_blanking 1 >/dev/null 2>&1 || true   # Bildschirm nicht abschalten
    echo "Vollbild-Präsentation eingeschaltet. Sie startet beim nächsten Einschalten automatisch."
    echo "Jetzt sofort starten:  sudo reboot"
    ;;
  aus)
    rm -f "$DATEI"
    echo "Vollbild-Präsentation ausgeschaltet (wirkt nach dem nächsten Neustart)."
    ;;
  *)
    echo "Aufruf: sudo bash $0 ein|aus"
    exit 1
    ;;
esac
