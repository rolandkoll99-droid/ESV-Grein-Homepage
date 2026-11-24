#!/bin/bash
# =====================================================================
#  ESV Grein – Webseite auf dem Raspberry Pi installieren / aktualisieren
#  Aufruf (im entpackten Ordner):   sudo bash pi/installieren.sh
#  Mehrfach ausführbar: aktualisiert das Programm, Daten bleiben erhalten.
# =====================================================================
set -e

ZIEL=/opt/esv-grein                 # Programm (SD-Karte)
STICK=/media/esv-stick              # Daten-Stick (USB)
STICK_NAME=ESV-DATEN                # Bezeichnung (Label) des USB-Sticks
RECHNERNAME=esv-grein               # -> http://esv-grein.local im Hallen-Netz
BENUTZER=${SUDO_USER:-pi}
QUELLE="$(cd "$(dirname "$0")/.." && pwd)"

rot()  { echo -e "\e[31m$*\e[0m"; }
gruen(){ echo -e "\e[32m$*\e[0m"; }
info() { echo -e "\e[1m$*\e[0m"; }

if [ "$(id -u)" != "0" ]; then rot "Bitte mit sudo starten:  sudo bash pi/installieren.sh"; exit 1; fi

# Das Paket kann direkt vom Daten-Stick gestartet werden. Weil der Stick unten neu
# eingebunden wird, arbeitet das Skript mit einer Kopie im Zwischenspeicher weiter.
if [ "${ESV_KOPIE:-}" != "1" ]; then
  TMPD=$(mktemp -d /tmp/esv-installation.XXXXXX)
  cp -r "$QUELLE" "$TMPD/paket"
  ESV_KOPIE=1 exec bash "$TMPD/paket/pi/installieren.sh" "$@"
fi

# Port 80 schon von einem anderen Programm belegt (z. B. Anzeige, nginx)?
if ! systemctl is-active --quiet esv-grein 2>/dev/null && ss -ltnH 2>/dev/null | awk '{print $4}' | grep -qE '(^|:)80$'; then
  rot "Port 80 ist auf diesem Pi bereits von einem anderen Programm belegt:"
  ss -ltnp 2>/dev/null | grep -E ':80[[:space:]]' || true
  echo "  → Am besten einen eigenen Pi für die Webseite verwenden"
  echo "    oder das andere Programm zuerst beenden."
  exit 3
fi

info "1/6  Pakete installieren …"
apt-get update -qq
apt-get install -y -qq python3 avahi-daemon exfatprogs dosfstools rsync curl unzip >/dev/null

info "2/6  Programm nach $ZIEL kopieren …"
mkdir -p "$ZIEL"
rsync -a --delete \
  --exclude data --exclude export --exclude fotos --exclude sicherung-sd \
  --exclude "*.bat" --exclude "__pycache__" --exclude ".git" \
  "$QUELLE"/ "$ZIEL"/
mkdir -p "$ZIEL/sicherung-sd"
chown -R "$BENUTZER":"$BENUTZER" "$ZIEL"

info "3/6  USB-Stick „$STICK_NAME“ suchen …"
GERAET=$(blkid -L "$STICK_NAME" || true)
if [ -z "$GERAET" ]; then
  rot "Kein USB-Stick mit der Bezeichnung „$STICK_NAME“ gefunden."
  echo "  → Stick am PC formatieren: Dateisystem exFAT, Volumebezeichnung: $STICK_NAME"
  echo "  → Stick am Pi anstecken und dieses Skript erneut starten."
  exit 2
fi
UUID=$(blkid -s UUID -o value "$GERAET")
TYP=$(blkid -s TYPE -o value "$GERAET")
NUTZER_ID=$(id -u "$BENUTZER"); GRUPPE_ID=$(id -g "$BENUTZER")
case "$TYP" in
  exfat|vfat) OPTIONEN="defaults,nofail,noatime,uid=$NUTZER_ID,gid=$GRUPPE_ID,umask=0022,x-systemd.device-timeout=15" ;;
  *)          OPTIONEN="defaults,nofail,noatime,x-systemd.device-timeout=15" ;;
esac
mkdir -p "$STICK"
sed -i "\#[[:space:]]$STICK[[:space:]]#d" /etc/fstab
echo "UUID=$UUID $STICK $TYP $OPTIONEN 0 0" >> /etc/fstab
systemctl daemon-reload
umount "$GERAET" 2>/dev/null || true
mount "$STICK"
[ "$TYP" = "exfat" ] || [ "$TYP" = "vfat" ] || chown "$BENUTZER":"$BENUTZER" "$STICK"
gruen "  Stick ($TYP) eingebunden unter $STICK"

info "4/6  Datenordner auf dem Stick vorbereiten …"
sudo -u "$BENUTZER" mkdir -p "$STICK/data" "$STICK/fotos" "$STICK/bilder" "$STICK/dokumente"
sudo -u "$BENUTZER" touch "$STICK/.esv-stick"
# Übernahme aus der PC-Version (falls data/ oder fotos/ im Paket liegen und der Stick noch leer ist)
if [ -f "$QUELLE/data/daten.json" ] && [ ! -f "$STICK/data/daten.json" ]; then
  sudo -u "$BENUTZER" cp -r "$QUELLE/data/." "$STICK/data/"; gruen "  Daten aus der PC-Version übernommen"
fi
if [ -d "$QUELLE/fotos" ] && [ -z "$(ls -A "$STICK/fotos" 2>/dev/null)" ]; then
  sudo -u "$BENUTZER" cp -r "$QUELLE/fotos/." "$STICK/fotos/" 2>/dev/null || true
fi
sudo -u "$BENUTZER" cp -n "$QUELLE/fotos/LIESMICH.txt" "$STICK/fotos/" 2>/dev/null || true
sudo -u "$BENUTZER" cp -rn "$QUELLE/dokumente/." "$STICK/dokumente/" 2>/dev/null || true

info "5/6  Dienst einrichten (startet automatisch beim Einschalten) …"
cat > /etc/systemd/system/esv-grein.service <<EOF
[Unit]
Description=ESV Grein Webseite
After=network-online.target local-fs.target
Wants=network-online.target
RequiresMountsFor=$STICK

[Service]
User=$BENUTZER
WorkingDirectory=$ZIEL
Environment=ESV_DATEN=$STICK
Environment=ESV_PORT=80
Environment=PYTHONUNBUFFERED=1
ExecStart=/usr/bin/python3 $ZIEL/server.py --netzwerk --kein-browser
Restart=always
RestartSec=15
AmbientCapabilities=CAP_NET_BIND_SERVICE
NoNewPrivileges=true
ProtectSystem=full
ProtectHome=read-only

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable esv-grein >/dev/null
systemctl restart esv-grein

info "6/6  Rechnername „$RECHNERNAME“ …"
if [ "$(hostname)" != "$RECHNERNAME" ]; then
  ALT=$(hostname)
  ANTWORT=j
  if [ "$ALT" != "raspberrypi" ] && [ -t 0 ] && [ "${ESV_UMBENENNEN:-}" != "ja" ]; then
    read -r -p "  Der Pi heißt derzeit „$ALT“. In „$RECHNERNAME“ umbenennen? (j/n) " ANTWORT
  fi
  if [ "$ANTWORT" = "j" ] || [ "$ANTWORT" = "J" ]; then
    hostnamectl set-hostname "$RECHNERNAME"
    if grep -q "^127.0.1.1" /etc/hosts; then
      sed -i "s/^127.0.1.1.*/127.0.1.1\t$RECHNERNAME/" /etc/hosts
    else
      echo -e "127.0.1.1\t$RECHNERNAME" >> /etc/hosts
    fi
    systemctl restart avahi-daemon || true
    echo "  Rechnername von „$ALT“ auf „$RECHNERNAME“ geändert."
  else
    RECHNERNAME=$ALT
    echo "  Rechnername bleibt „$ALT“ (Adresse: http://$ALT.local)."
  fi
fi

sleep 3
IP=$(hostname -I | awk '{print $1}')
echo
TEST=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/daten || true)
if systemctl is-active --quiet esv-grein && [ "$TEST" = "200" ]; then
  gruen "=================================================================="
  gruen " Fertig! Die Webseite läuft."
  gruen "=================================================================="
  echo "  In der Halle (LAN/WLAN):  http://$RECHNERNAME.local   oder  http://$IP"
  echo "  Verwaltung:               http://$RECHNERNAME.local/verwaltung.html  (erste Anmeldung: 1234, dann eigenes Passwort)"
  echo "  Daten-Stick:              $STICK"
  echo "  Vollbild-Präsentation:    sudo bash $ZIEL/pi/praesentation.sh ein"
  echo
  echo "  Status:   sudo systemctl status esv-grein"
  echo "  Protokoll: journalctl -u esv-grein -n 50"
else
  rot "Die Webseite antwortet nicht (Test: $TEST). Protokoll:"
  journalctl -u esv-grein -n 30 --no-pager
fi
