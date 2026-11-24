# ESV Grein Webseite – Vorführung auf dem Raspberry Pi

**Zweck:** Vorstellung für Vorstand und Vereinsmitglieder in der Stockhalle.
**Noch keine Veröffentlichung:** Die Webseite ist nur im Hallen-Netzwerk erreichbar. Sie hat keinen Internet-Zugang von außen, steht in keiner Suchmaschine und zeigt oben das Band „VORSCHAU – noch nicht veröffentlicht“.

---

## 1. Was du brauchst

| | |
|---|---|
| Raspberry Pi 4 mit **Raspberry Pi OS mit Desktop** | eigener Pi empfohlen, nicht der Anzeige-Pi einer Bahn |
| Monitor, Fernseher oder Beamer (HDMI) + Tastatur/Maus | für die Vollbild-Anzeige und zum Einrichten |
| USB-Stick, exFAT, Name **ESV-DATEN** | darauf liegt auch das Webseiten-Paket |
| LAN-Kabel zum Hallen-Router | Internet nur für die Wetteranzeige nötig |
| Laptop oder Tablet | zum Vorführen der Verwaltung |

## 2. Installation direkt am Pi (ca. 10 Minuten)

1. Am privaten PC: ZIP-Datei **entpacken** und den Ordner `ESV_Grein_Webseite_V2.3` auf den Stick **ESV-DATEN** kopieren.
2. Stick am Pi anstecken, am Pi-Desktop das **Terminal** öffnen (schwarzes Symbol oben).
3. Eingeben (der Stick erscheint am Desktop unter `/media/BENUTZER/ESV-DATEN`):
   ```
   sudo bash /media/$USER/ESV-DATEN/ESV_Grein_Webseite_V2.3/pi/installieren.sh
   ```
4. Warten, bis **„Fertig! Die Webseite läuft.“** erscheint. Das Skript zeigt auch die **IP-Adresse** des Pi an. Bitte notieren.
5. **Vollbild-Präsentation einschalten:**
   ```
   sudo bash /opt/esv-grein/pi/praesentation.sh ein
   sudo reboot
   ```
   Nach dem Neustart erscheint die Webseite im Vollbild. **Alt+F4** beendet das Vollbild, **F5** lädt die Seite neu.

> Hat der Pi schon einen anderen Namen oder läuft dort bereits eine Anzeige, fragt bzw. warnt das Skript, statt etwas zu überschreiben.

## 3. Vorbereitung (am Tag davor, 15 Minuten)

Am Laptop in der Halle `http://esv-grein.local/verwaltung.html` öffnen (oder `http://IP-ADRESSE/verwaltung.html`).

- [ ] Erste Anmeldung mit **1234** und eigenes Passwort festlegen. Das Passwort notieren, es kommt nicht in die Präsentation.
- [ ] *Einstellungen → Präsentation* → **Beispieldaten laden**. Neuigkeiten, Termine und eine Veranstaltung erscheinen, gekennzeichnet mit „Beispiel“.
- [ ] *Verein* → **Titelbild** (z. B. Vereinsheim) und **Logo** hochladen
- [ ] *Fotos* → ein Album mit 5–10 echten Fotos anlegen, z. B. vom letzten Turnier
- [ ] *Training* → Uhrzeit für das Seniorentraining eintragen
- [ ] Auf dem Handy testen: Knopf **„Am Handy ansehen“** → QR-Code scannen (das Handy muss im Hallen-WLAN sein)

## 4. Ablauf der Vorführung (ca. 15 Minuten)

| Min. | Was zeigen | Wo | Botschaft |
|---|---|---|---|
| 0–3 | **Startseite**: Neuigkeiten, nächster Termin, Kalender mit Training, Ergebnisse, Fotos, Probetraining/Kontakt | Bildschirm | „Alles Wichtige auf einen Blick, auch für Interessierte“ |
| 3–5 | **Am Handy ansehen**: QR-Code zeigen, Mitglieder scannen selbst | Bildschirm + Handys | „Funktioniert auf jedem Handy“ |
| 5–10 | **Verwaltung live**: *+ Termin eintragen* → speichern → Webseite neu laden (F5) → Termin ist da. Danach *+ Ergebnis eintragen*, *Fotos hochladen*. | Laptop | „Ohne EDV-Kenntnisse: Formular ausfüllen, Speichern, fertig“ |
| 10–12 | **Sicherheitsnetz**: einen Eintrag löschen → **Rückgängig**. **Entwurf**-Häkchen zeigen. *Einstellungen → Änderungsprotokoll* | Laptop | „Man kann nichts kaputt machen“ |
| 12–15 | **Wie geht es weiter?** Freigabe-Checkliste (PRUEFBERICHT_V2.1.md, Abschnitt 5), Fragen | – | „Was braucht es für die Veröffentlichung?“ |

**Tipps:**
- Die Verwaltung am Laptop vorführen, nicht am Hallen-Bildschirm. So bleibt das Passwort unsichtbar.
- Den Bildschirm nach der Live-Eingabe mit **F5** neu laden (oder kurz die Tastatur am Pi verwenden).
- Ohne Internet in der Halle zeigt die Wetteranzeige nur „nicht verfügbar“. Alles andere funktioniert offline.

## 5. Nach der Vorführung

- [ ] *Einstellungen → Präsentation* → **Beispieldaten entfernen**. Eigene Einträge bleiben erhalten.
- [ ] Rückmeldungen von Vorstand und Mitgliedern notieren
- [ ] Vorstandsbeschluss zur **Freigabe** (Checkliste im Prüfbericht V2.1)
- [ ] Vollbild ausschalten, falls der Pi anders genutzt wird: `sudo bash /opt/esv-grein/pi/praesentation.sh aus`

**Später, bei der Veröffentlichung:** Domain registrieren, Fernzugriff einrichten (ANLEITUNG-PI.md, Schritt 5), Vorschau-Band ausschalten (*Einstellungen → Präsentation*) und in `index.html` die Zeile `<meta name="robots" content="noindex, nofollow">` entfernen.
