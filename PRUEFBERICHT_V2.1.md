# ESV Grein Webseite – Prüfbericht V2.0 → V2.1

**Stand:** 28.10.2026 · **Geprüft:** V2.0 Präsentation · **Ergebnis:** V2.1 (alle Änderungen getestet)
**Blickwinkel:** Webdesigner und Administrator · Maßstab: Bedienung durch Vereinskollegen ohne EDV-Kenntnisse

## 1. Kurzfassung

V2.0 ist für eine Vorführung gut geeignet. Für den Alltag mit mehreren Laien als Redakteuren gab es drei Hindernisse:

1. **Sicherheit:** Die Start-PIN 1234 stand öffentlich auf der Anmeldeseite und wurde im Klartext gespeichert.
2. **Handy:** 10 Reiter füllten den ganzen Bildschirm, in den Listen waren „Bearbeiten/Löschen“ abgeschnitten.
3. **Fehlertoleranz:** Kein Rückgängig, keine Warnung bei ungespeicherten Eingaben, gleichzeitiges Bearbeiten überschrieb Daten.

Alle drei sind in V2.1 behoben. Offen sind Punkte, die eine Entscheidung des Vorstands brauchen (Abschnitt 5).

## 2. Befunde und Umsetzung

| Nr | Befund V2.0 | Gewicht | V2.1 |
|---|---|---|---|
| 1 | Start-PIN „1234“ auf der öffentlichen Anmeldeseite genannt | hoch | ✅ entfernt; erste Anmeldung **erzwingt** eigenes Passwort (mind. 8 Zeichen, zweimal eingeben, leichte Passwörter abgelehnt) |
| 2 | Passwort im Klartext in `einstellungen.json` | hoch | ✅ verschlüsselt (scrypt mit Salt); alte PIN wird beim nächsten Anmelden automatisch umgestellt |
| 3 | PIN wurde bei jeder Anfrage mitgeschickt und im Browser gespeichert | mittel | ✅ Sitzungs-Schlüssel; **automatische Abmeldung nach 60 min** ohne Aktion; „Abmelden“ beendet die Sitzung am Server |
| 4 | Uploads nur nach Dateiname geprüft | mittel | ✅ Prüfung des echten Bildinhalts (JPG/PNG/GIF/WebP) |
| 5 | Gleichzeitiges Bearbeiten: Letzter überschreibt alles | hoch | ✅ Versionsprüfung: Hinweis „Inzwischen hat jemand anderer gespeichert“ + automatisches Neuladen |
| 6 | Niemand sieht, wer was geändert hat | mittel | ✅ **Änderungsprotokoll** (Name bei Anmeldung, Anzeige unter Einstellungen + „Zuletzt geändert“ in der Übersicht) |
| 7 | Handy: 10 Reiter = ganzer Bildschirm | hoch | ✅ Auswahlliste „Bereich wählen“; am PC 5 Hauptbereiche + „Weitere ▾“ |
| 8 | Handy: Tabelle zu breit, Knöpfe nicht sichtbar | hoch | ✅ Einträge als Karten, Knöpfe groß und immer sichtbar |
| 9 | Versehentlich gelöscht = weg | hoch | ✅ **„Rückgängig“** in der Meldung nach dem Löschen (8 s) |
| 10 | Formular halb ausgefüllt, Bereich gewechselt = Eingaben weg | mittel | ✅ Rückfrage vor dem Verlassen (auch beim Schließen des Fensters) |
| 11 | Feld „Saison“ für Laien unklar | niedrig | ✅ wird aus dem Datum ergänzt (Apr–Sep = Sommer, sonst Winter) |
| 12 | Kein Vorbereiten von Inhalten möglich | mittel | ✅ **Entwurf**-Häkchen bei Neuigkeiten, Terminen, Veranstaltungen: gespeichert, aber nicht öffentlich (auch nicht im Export) |
| 13 | Übersicht ohne „Veranstaltung“ | niedrig | ✅ ergänzt; Hinweis auf offene Entwürfe und vollen Speicher |
| 14 | Hinweistext auf Anmeldeseite lang | niedrig | ✅ auf eine Zeile „So geht's“ gekürzt |

**Beibehalten aus V2.0:** Startseite ohne Aktionsknöpfe, Export nur öffentlicher Vereinsfelder, GitHub-Anleitung.

## 3. Stand der Empfehlungen aus Prüfbericht V1.2

| Empfehlung V1.2 | Stand V2.1 |
|---|---|
| Keine Standard-PIN / erzwungene Ersteinrichtung | ✅ umgesetzt |
| Passwort-Hashing | ✅ scrypt |
| Sichere Sitzungen mit Ablauf | ✅ Sitzungsschlüssel + 60 min Ablauf · ⏳ HttpOnly-Cookie/CSRF: bei Betrieb über Cloudflare Access nicht zwingend, für V3 vorgesehen |
| Individuelle Konten mit Rollen | ⏳ teilweise: Name + Protokoll. Eigene Konten je Person → V3, falls der Vorstand das wünscht |
| Upload-Prüfung | ✅ Inhaltsprüfung · ⏳ serverseitiges Neukodieren (braucht Zusatzpaket) |
| SQLite statt JSON | ⏳ nicht nötig für die Vereinsgröße; Überschreiben ist durch die Versionsprüfung verhindert |
| Nicht direkt ins Internet | ✅ nur über Cloudflare-Tunnel (ANLEITUNG-PI.md) |
| Dashboard mit großen Kacheln | ✅ |
| Rückgängig / Bestätigung beim Löschen | ✅ |
| Ergebnisse: Suche, 10 pro Seite | ⏳ Webseite zeigt 5 + „Alle anzeigen“; Suche in der Verwaltung bei Bedarf in V3 |
| Kalender: nächste 5 Termine | ✅ (seit V1.x) |
| Fotos: Mehrfachauswahl, Verkleinerung, Papierkorb | ✅ · ⏳ Wiederherstellen aus Papierkorb nur über den Ordner |
| Vorstand: Bildzuschnitt, Reihenfolge | ⏳ runder Zuschnitt automatisch; Reihenfolge = Reihenfolge der Einträge |
| Entwurf / Vier-Augen-Freigabe | ✅ Entwurf · ⏳ Vier-Augen-Freigabe nur bei Bedarf |
| Zweites Sicherungsmedium | ✅ Pi: tägliche Kopie auf SD-Karte · Stick monatlich auf PC kopieren |
| Eine führende Datenquelle | ✅ Empfehlung: **Verwaltung (PC/Pi) ist führend**; Google-Tabelle nicht parallel verwenden |

## 4. Getestet (28.10.2026)

| Test | Ergebnis |
|---|---|
| Anmeldeseite enthält keine Start-PIN | ✅ |
| Erste Anmeldung → Pflicht-Passwort; zu kurz / ungleich / „12345678“ abgelehnt | ✅ |
| Alte Klartext-PIN → automatisch verschlüsselt | ✅ |
| Fernzugriff mit Start-PIN gesperrt, mit Passwort erlaubt | ✅ |
| Entwurf nicht öffentlich, aber in der Verwaltung sichtbar | ✅ |
| Löschen → Rückgängig stellt den Eintrag wieder her | ✅ |
| Warnung bei ungespeicherten Eingaben | ✅ |
| Zwei Personen gleichzeitig → Konfliktmeldung, nichts überschrieben | ✅ |
| Änderungsprotokoll mit Namen | ✅ |
| Ungültige/abgelaufene Sitzung → saubere Abmeldung mit Hinweis | ✅ |
| Datei, die kein Bild ist → abgelehnt | ✅ |
| Handy 390 px: Auswahlliste, Karten, kein seitliches Scrollen | ✅ |
| Raspberry Pi echt / Cloudflare-Tunnel | ⏳ noch offen (nur simuliert) |

## 5. Für die Freigabe durch den Vorstand

Vor der Veröffentlichung entscheiden bzw. erledigen:

- [ ] **Betrieb:** vorerst GitHub Pages (Export) oder gleich Raspberry Pi in der Halle mit **esv-grein.com**? Die Domain ist noch nicht registriert.
- [ ] **Domain** esv-grein.com registrieren, auf den Verein, nicht auf eine Privatperson
- [ ] **Redakteure festlegen:** wer pflegt die Webseite (Empfehlung 2–3 Personen); Weitergabe des Passworts
- [ ] **Technik-Verantwortlicher + Vertretung**
- [ ] **Impressum** vervollständigen: ZVR-Zahl, Obmann, Adresse
- [ ] **Datenschutzerklärung** gegenlesen lassen, z. B. über den Landesverband (Cloudflare, Open-Meteo, Facebook, Google Maps sind genannt)
- [ ] **Fotos und Namen:** Regel beschließen. Einwilligung über Mitgliedsantrag, Widerruf → Entfernung
- [ ] **Vorstandsfotos und -namen** nur mit Zustimmung der Personen
- [ ] **Kontaktdaten, Mitgliedsbeitrag, Trainingszeiten** (Seniorentraining: Uhrzeit?) prüfen
- [ ] **Startseite:** V2.0 hat die Knöpfe „Probetraining anfragen / Zu den Terminen“ entfernt. Soll **ein** Knopf „Probetraining“ wieder rein? (Neue Mitglieder sind ein Hauptziel der Seite.)
- [ ] **Facebook:** Webseiten-Link auf der Facebook-Seite eintragen, sobald die Adresse feststeht
- [ ] **Demo-Daten löschen** (Beispielneuigkeit, Testtermine, Testfotos)

**Freigabe:** ☐ erteilt ☐ mit Änderungen · Datum: ________ · Obmann: ______________________
