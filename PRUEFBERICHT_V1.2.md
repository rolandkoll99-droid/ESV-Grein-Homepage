# ESV Grein – Prüfung PC V1.1 und Empfehlungen für V1.2

## Zusammenfassung
Die hochgeladene PC V1.1 enthält eine öffentliche Webseite, eine Adminoberfläche mit Bereichen für Neuigkeiten, Termine, Ergebnisse, Veranstaltungen, Training, Fotos, Vorstand und Verein, einen Python-Webserver, JSON-Dateispeicherung und Installationsskripte für den Raspberry Pi. Für eine lokale Vorführung ist dies eine gute Grundlage. Für einen dauerhaft von mehreren Vereinskollegen bedienten und aus dem Internet erreichbaren Betrieb fehlen wesentliche Sicherheits- und Bedienungsfunktionen.

## Kritisch – vor Internetfreigabe
1. **Standard-PIN 1234**: In `server.py` wird ohne gespeicherte Einstellung auf `1234` zurückgegriffen. Unbedingt bei der ersten Inbetriebnahme ändern; besser wäre eine erzwungene Ersteinrichtung ohne Standard-PIN.
2. **Passwort im Klartext**: `einstellungen.json` enthält den PIN direkt. Auf gesalzenes Passwort-Hashing (Argon2id oder scrypt) umstellen.
3. **PIN bei jedem API-Aufruf**: `js/verwaltung.js` speichert den PIN in `sessionStorage` und sendet ihn in `X-PIN`. Für Fernzugriff sichere Sitzungen mit HttpOnly-/Secure-/SameSite-Cookies, Ablaufzeit, CSRF-Schutz und HTTPS verwenden.
4. **Keine individuellen Benutzerkonten**: Derzeit teilen sich alle Administratoren eine PIN. Benötigt werden individuelle Konten mit Rollen (Hauptadmin, Redakteur) und Änderungsprotokoll.
5. **Datei-Uploads**: Bilddateien werden anhand des Dateinamens angenommen; der Server prüft den tatsächlichen Bildinhalt nicht. Datei-Header, Größen-/Pixelgrenzen, Bilddekodierung und serverseitige Neukodierung ergänzen. Im Bereich `bild` werden Uploads pauschal als JPG gespeichert, selbst wenn der Inhalt PNG ist.
6. **Dateispeicher statt SQLite**: `data/daten.json` ist für einen kleinen Einzelbetrieb möglich, aber parallele Bearbeitungen können sich gegenseitig überschreiben. SQLite mit Transaktionen und regelmäßigen Sicherungen ist für den Pi-Mehrbenutzerbetrieb sinnvoll.
7. **Internetfreigabe**: Nicht den Python-HTTP-Server direkt ins Internet freigeben. Reverse Proxy/Tunnel, HTTPS, Zugriffsschutz, Updates und Monitoring vorsehen.

## Hohe Priorität – Bedienung für Laien
1. Dashboard mit sechs großen Kacheln: Neuigkeit, Termin, Ergebnis, Veranstaltung, Training, Fotos. Vorstand/Verein/Einstellungen unter „Weitere Verwaltung“.
2. Pro Bereich: klare Schaltfläche „Neu hinzufügen“, Formular mit wenigen Pflichtfeldern, eindeutige Meldung „Gespeichert“, „Abbrechen“ und „Vorschau“.
3. Ergebnislisten: Suchfeld, Saisonfilter, 10 Einträge je Seite, Bearbeiten/Löschen mit Bestätigungsdialog.
4. Kalender: zunächst die nächsten fünf Termine statt einer langen Ansicht; Monatskalender optional aufklappbar.
5. Fotos: Mehrfachauswahl, Vorschau, automatische Verkleinerung, klare Albumzuordnung, Papierkorb mit Wiederherstellung.
6. Vorstandsverwaltung: Name, Funktion, Foto und Reihenfolge; Bildzuschnitt vor dem Speichern.
7. Fehlertexte in Alltagssprache und eine eingebaute Hilfe „So funktioniert die Verwaltung“.
8. Veröffentlichungsstatus (Entwurf/veröffentlicht) und optional Vier-Augen-Freigabe für wichtige Inhalte.

## Daten und Sicherung
- Raspberry Pi 4: Programm auf SD, Daten und Fotos auf dauerhaft eingebundenem USB-Stick.
- Keine leere Ersatzdatenbank erzeugen, wenn der Stick fehlt; diese Schutzprüfung ist im aktuellen Server bereits angelegt.
- Tägliche automatische Sicherung auf **ein zweites Medium**; Sicherungen nur auf demselben Stick schützen nicht bei Defekt oder Verlust.
- Wiederherstellung regelmäßig testen; Speicherplatzwarnung und Sicherungsstatus in die Adminübersicht aufnehmen.
- Google Sheets und lokale JSON-Daten sind unterschiedliche Datenquellen. Eine führende Datenquelle festlegen, um widersprüchliche Termine und Ergebnisse zu vermeiden.

## Umgesetzte Sofortverbesserung in dieser Prüfversion
- Direkt auf der Anmeldeseite steht eine kurze Einstiegshilfe für Vereinskollegen.
- Eine sichtbare Warnung erinnert daran, die voreingestellte PIN zu ändern und den Testserver nicht öffentlich freizugeben.
- Das bestehende öffentliche Design und die vorhandene Funktionslogik wurden nicht verändert.

## Prüfstatus
Statische Codeprüfung und Paketinspektion; kein vollständiger Browser-, Last- oder Raspberry-Pi-Hardwaretest. Die genannten Sicherheitsmaßnahmen sind Empfehlungen, **nicht** alle in dieser Prüfversion implementiert. Diese ZIP-Datei ist weiterhin eine lokale Testversion und keine internetfertige Produktionsversion.
