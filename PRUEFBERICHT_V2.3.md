# ESV Grein Webseite – Prüfbericht V2.2 → V2.3 (Veröffentlichung)

**Stand:** 30.10.2026 · **Geprüft:** V2.2 Präsentation · **Ergebnis:** V2.3 Veröffentlichung
**Blickwinkel:** Webdesigner · Web-Admin · Vereinsmitglied

## 1. Behobene Fehler

| Nr | Befund V2.2 | Rolle | V2.3 |
|---|---|---|---|
| 1 | Suchmaschinen-Sperre `noindex, nofollow` in `index.html` – die Seite wäre nach der Veröffentlichung bei Google nicht auffindbar | Admin | ✅ entfernt (Impressum/Datenschutz bleiben bewusst `noindex`) |
| 2 | Vorschau-Band bei Neuinstallation standardmäßig **an** | Admin | ✅ Standard jetzt **aus** (`server.py`) |
| 3 | Verwaltung zeigte das Häkchen „Vorschau“ als **an**, obwohl das Band bei älteren Daten gar nicht angezeigt wurde | Admin | ✅ Häkchen entspricht jetzt der tatsächlichen Anzeige |
| 4 | Platzhalter wie „[Telefonnummer]“, „[E-Mail-Adresse]“, „[Betrag] € pro Jahr“ wurden öffentlich angezeigt; „Anrufen“/Mail-Link führten ins Leere | Mitglied | ✅ nicht ausgefüllte Angaben werden ausgeblendet statt angezeigt |
| 5 | Vorstand: leere Karten ohne Namen bzw. „[Name]“ | Mitglied | ✅ nur Personen mit Namen; ohne Namen wird der Bereich „Vorstand“ ausgeblendet |
| 6 | Datenschutzerklärung: Google Tabelle / Google Drive (Laden von Inhalten und Bildern) nicht erwähnt | Admin | ✅ Abschnitt ergänzt |
| 7 | Datenschutzerklärung: „Stand: [Monat Jahr]“ | Admin | ✅ „Oktober 2026“ |
| 8 | Handy-Menü: Beschriftung blieb nach Klick auf einen Menüpunkt „Menü schließen“; kein Schließen mit Esc | Webdesign | ✅ korrigiert |
| 9 | Kalender: ungültige ARIA-Struktur (`grid` ohne Zeilen) – Vorlese-Programme melden Fehler | Webdesign | ✅ vereinfacht, jeder Tag bleibt ein beschrifteter Knopf |
| 10 | Server: ungültige/negative `Content-Length` konnte eine Anfrage hängen lassen | Admin | ✅ wird abgewiesen |

## 2. Getestet (30.10.2026, lokaler Server)

| Test | Ergebnis |
|---|---|
| Startseite lädt ohne Skriptfehler, kein seitliches Scrollen bei 375 px | ✅ |
| Kein `noindex` auf der Startseite, kein Vorschau-Band | ✅ |
| Ohne Kontaktdaten: keine Platzhalter sichtbar; mit Kontaktdaten: `tel:`/`mailto:`-Links korrekt | ✅ |
| Vorstand ohne Namen ausgeblendet | ✅ |
| Erste Anmeldung → eigenes Passwort → Speichern → Export | ✅ |
| Export enthält kein `noindex`, keine Google-Tabellen-ID, kein Vorschau-Band | ✅ |
| Raspberry Pi echt / Cloudflare-Tunnel | ⏳ nicht getestet |

## 3. Vor dem Online-Stellen – nur der Verein kann das ausfüllen

**Pflicht (gesetzlich):**
- [ ] `impressum.html`: Straße/Hausnummer, **ZVR-Zahl**, Name des Obmanns, Telefon, E-Mail, Vereinszweck laut Statuten
- [ ] `datenschutz.html`: Straße/Hausnummer und E-Mail des Verantwortlichen
- [ ] Wird statt des Pi **GitHub Pages** verwendet: Abschnitt „Hosting“ in `datenschutz.html` anpassen (Anbieter GitHub statt Cloudflare)

**In der Verwaltung (Bereich Verein / Vorstand):**
- [ ] Adresse, Telefon, E-Mail, Mitgliedsbeitrag
- [ ] Uhrzeit Seniorentraining
- [ ] Vorstandsnamen (nur mit Zustimmung der Personen)
- [ ] **Titelbild** (`vereinsheim.jpg`) und **Logo** (`logo.png`) hochladen – beide fehlen im Paket
- [ ] Neuigkeit „Unsere neue Webseite ist online“: Datum auf den Tag der Veröffentlichung setzen
- [ ] Beispieldaten entfernen (Einstellungen → Präsentation), falls geladen
- [ ] Prüfen, dass das Häkchen „Vorschau-Hinweis“ **aus** ist

**Technik:**
- [ ] Domain **esv-grein.com** registrieren (auf den Verein). Bis dahin zeigen `og:url`/`og:image` in `index.html` ins Leere (nur Linkvorschau bei Facebook/WhatsApp betroffen)
- [ ] Eigenes Passwort ist vergeben, **bevor** der Pi im Hallen-WLAN für Gäste erreichbar ist (bis dahin gilt die Start-PIN)
- [ ] `js/daten.js` enthält noch die ID der Google-Tabelle. Nur relevant, wenn die Dateien direkt (ohne Pi/Export) online gestellt werden – dann lädt die Seite Inhalte von Google
