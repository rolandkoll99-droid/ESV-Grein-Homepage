@echo off
chcp 65001 >nul
title ESV Grein - Webseite auf den Raspberry Pi installieren
cd /d "%~dp0"
echo.
echo  ==============================================================
echo   ESV Grein - Webseite auf den Raspberry Pi installieren
echo  ==============================================================
echo.
echo   Voraussetzungen:
echo    - Raspberry Pi mit Raspberry Pi OS ist eingeschaltet und per LAN
echo      im selben Netzwerk wie dieser PC (SSH aktiviert)
echo    - USB-Stick "ESV-DATEN" (exFAT) steckt am Pi
echo.

where ssh >nul 2>nul
if errorlevel 1 (
  echo  FEHLER: Der OpenSSH-Client fehlt auf diesem PC.
  echo  Windows-Einstellungen ^> Apps ^> Optionale Features ^> "OpenSSH-Client" hinzufuegen.
  pause
  exit /b 1
)
where tar >nul 2>nul
if errorlevel 1 (
  echo  FEHLER: "tar" fehlt. Bitte Windows 10 ab Version 1803 oder Windows 11 verwenden.
  pause
  exit /b 1
)

set "PI="
set /p PI=  Adresse des Pi [Enter = esv-grein.local]:
if "%PI%"=="" set "PI=esv-grein.local"
set "BEN="
set /p BEN=  Benutzername am Pi (aus dem Raspberry Pi Imager):
if "%BEN%"=="" (
  echo  Kein Benutzername eingegeben.
  pause
  exit /b 1
)

echo.
echo  Verbindung zu %PI% wird geprueft ...
ping -n 1 -w 3000 %PI% >nul 2>nul
if errorlevel 1 (
  echo  Der Pi "%PI%" antwortet nicht.
  echo  - Ist er eingeschaltet und per LAN-Kabel verbunden?
  echo  - Versuche statt des Namens die IP-Adresse (steht im Router, z. B. 192.168.1.50).
  pause
  exit /b 1
)

echo.
echo  [1/2] Dateien werden auf den Pi kopiert.
echo        Bitte das PASSWORT des Pi eingeben (beim Tippen ist nichts zu sehen).
echo        Beim allerersten Mal ggf. mit "yes" bestaetigen.
tar -cf - --exclude=data --exclude=export --exclude=sicherung-sd . | ssh -o StrictHostKeyChecking=accept-new %BEN%@%PI% "rm -rf ~/esv-grein-v21 && mkdir -p ~/esv-grein-v21 && tar -xf - -C ~/esv-grein-v21"
if errorlevel 1 (
  echo.
  echo  Kopieren fehlgeschlagen. Benutzername/Passwort pruefen und erneut starten.
  pause
  exit /b 1
)

echo.
echo  [2/2] Installation auf dem Pi (dauert einige Minuten).
echo        Ggf. nochmals das Passwort des Pi eingeben.
ssh -t %BEN%@%PI% "sudo bash ~/esv-grein-v21/pi/installieren.sh"

echo.
echo  --------------------------------------------------------------
echo   Wenn oben "Fertig! Die Webseite laeuft." steht:
echo   Im Browser  http://esv-grein.local  oeffnen.
echo   Verwaltung: http://esv-grein.local/verwaltung.html
echo   (erste Anmeldung mit 1234, danach eigenes Passwort festlegen)
echo  --------------------------------------------------------------
pause
