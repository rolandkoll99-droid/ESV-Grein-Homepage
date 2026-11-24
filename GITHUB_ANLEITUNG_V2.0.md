# ESV Grein V2.0 – Präsentation und GitHub Pages

## 1. Lokale Präsentation (Windows)
1. Ordner entpacken und `Webseite starten.bat` doppelklicken (Python 3 erforderlich).
2. Webseite: `http://localhost:8420/`.
3. Verwaltung: `http://localhost:8420/verwaltung.html`. Erste Anmeldung mit 1234, danach wird ein eigenes Passwort verlangt (ab V2.1).
4. Inhalte eingeben, speichern und öffentliche Ansicht neu laden.
5. Unter Verwaltung → Einstellungen/Datensicherung → **Für die Online-Webseite exportieren** die statische Kopie erstellen.

## 2. Vorstandsvorführung
- Navigation oben: Neuigkeiten, Kalender, Ergebnisse, Veranstaltungen, Fotos, Mitglieder, Kontakt.
- Die doppelten Startseitenbuttons für Probetraining und Termine wurden entfernt. Der Abschnitt Probetraining bleibt über Mitglieder/Kontakt erreichbar.
- Beispieltermin und -ergebnis eingeben, Foto hinzufügen, öffentliche Seite prüfen.
- Vor Veröffentlichung alle Demo-Daten und Platzhalter prüfen.

## 3. GitHub Pages
1. Auf GitHub ein neues öffentliches Repository anlegen, z. B. `esv-grein-webseite`.
2. **Nur** den Inhalt des durch die Verwaltung erzeugten Ordners `export/esv-grein-online` hochladen, NICHT das vollständige PC-Paket.
3. Unter Settings → Pages → Deploy from a branch → `main` und `/(root)` wählen.
4. Nach Veröffentlichung die von GitHub angezeigte Pages-URL öffnen und Links, Fotos und Daten prüfen.
5. Nach jeder lokalen Änderung erneut exportieren und die geänderten Dateien auf GitHub aktualisieren. GitHub Pages ist statisch; der Adminbereich läuft dort nicht.

## 4. Sicherheit und Freigabe
- **Keine** `server.py`, `verwaltung.html`, `admin.html`, `data/`, `einstellungen.json`, Backups, Tokens oder private Unterlagen auf GitHub hochladen.
- Öffentliche Repository-Inhalte sind für jedermann einsehbar; Fotos und personenbezogene Daten nur mit erforderlicher Zustimmung/Freigabe veröffentlichen.
- Die Domain `esv-grein.com` ist noch nicht registriert. Vorläufig gilt die GitHub-Pages-Adresse.
- Ab V2.1: Passwort verschlüsselt gespeichert, automatische Abmeldung, Sperre nach Fehlversuchen. Für Internetzugriff trotzdem nur über den Cloudflare-Tunnel (ANLEITUNG-PI.md), nie direkt.
- Der Raspberry-Pi-Betrieb wurde noch nicht getestet; vor Freigabe separat testen.

## 5. Hinweis zur Speicherung
Die lokale Verwaltung speichert Inhalte im lokalen Datenordner des PC-Servers. Der Export ist eine **Momentaufnahme**, keine Live-Synchronisierung mit GitHub oder Google Sheets.
