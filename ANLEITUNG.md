# ESV Grein Webseite – Anleitung

## 0. PC-Version (am einfachsten – zum Testen und Präsentieren)

Die Webseite läuft direkt auf einem Vereins-PC. Termine, Ergebnisse, Training und Fotos werden in einfachen Formularen eingetragen. Google, Tabellen und Internet sind nicht nötig, nur für die Wetteranzeige.

**Einmalig:** Python installieren (kostenlos, https://www.python.org/downloads/, beim Installieren **„Add Python to PATH“** anhaken).

**Starten:** Doppelklick auf **„Webseite starten.bat“**
- Ein schwarzes Fenster öffnet sich (nicht schließen, solange die Webseite läuft), danach öffnet sich der Browser mit der Webseite.
- Oben rechts auf der Webseite: **Verwaltung**, oder direkt http://localhost:8420/verwaltung.html
- **Erste Anmeldung:** Start-PIN **1234**. Danach fordert die Verwaltung sofort ein **eigenes Passwort (mind. 8 Zeichen)**. Dieses an alle weitergeben, die die Webseite pflegen.
- Bei jeder Anmeldung den **eigenen Namen** eintragen. So sieht man im Änderungsprotokoll, wer was geändert hat.
- Nach **60 Minuten ohne Aktion** wird man automatisch abgemeldet.

**In der Verwaltung:**

| Reiter | Was |
|---|---|
| Übersicht | Startseite der Verwaltung: Schnellknöpfe „+ Neuigkeit / Termin / Ergebnis / Fotos“, Zahlen, nächste Termine |
| Neuigkeiten | Meldungen ganz oben auf der Webseite, mit Bild. „Oben anheften“ für Wichtiges |
| Termine | Turniere, Meisterschaften, Feste. An diesem Tag entfällt das Training automatisch. |
| Ergebnisse | Platzierungen. Das neueste erscheint auf der Startseite. |
| Veranstaltungen | Größere Veranstaltungen mit Beschreibung |
| Training | Wöchentliches Training (Mo Seniorentraining, Fr 18:00) und trainingsfreie Tage |
| Fotos | Album pro Veranstaltung anlegen → **+ Fotos hinzufügen**. Oder Fotos direkt in den Ordner `fotos/<Datum Veranstaltung>` kopieren. |
| Vorstand | Funktionen und Namen |
| Verein | Kontakt, Beitrag, Wetter-Ort, **Titelbild und Logo hochladen** |
| Einstellungen | Passwort ändern, **Änderungsprotokoll**, Export für die Online-Webseite, Sicherungen |

- Jede Änderung wird sofort gespeichert („Gespeichert ✓“). Auf der Webseite die Seite neu laden (F5).
- **Versehentlich gelöscht?** Direkt danach in der Meldung unten auf **Rückgängig** klicken.
- **Entwurf:** Bei Neuigkeiten, Terminen und Veranstaltungen das Häkchen „Entwurf“ setzen. Dann ist der Eintrag gespeichert, aber noch nicht öffentlich sichtbar, z. B. bis der Vorstand zugestimmt hat.
- **Saison** bei Ergebnissen kann leer bleiben, sie wird aus dem Datum ergänzt (z. B. „Winter 2026/27“).
- Arbeiten zwei Personen gleichzeitig, verhindert die Verwaltung, dass eine die Eingaben der anderen überschreibt. Es erscheint ein Hinweis, die Daten werden neu geladen.
- Am **Handy** wählt man den Bereich oben aus der Liste, Einträge erscheinen als Karten.
- **Sicherungen** entstehen automatisch (`data/sicherung`). Gelöschte Fotos landen in `fotos/_papierkorb`.
- **Auf USB-Stick sichern / auf anderen PC mitnehmen:** einfach den ganzen Ordner kopieren.
- **Im Vereinsheim auf Handys/Tablets zeigen:** „Webseite im WLAN starten.bat“ und am Handy `http://<IP-Adresse des PCs>:8420` öffnen.
- **Online stellen:** *Einstellungen → Export erstellen* → der Ordner `export/esv-grein-online` (bzw. die ZIP-Datei) ist eine fertige Webseite für GitHub Pages (Punkt 3).
- **Datum, Uhrzeit und Wetter** stehen oben auf der Startseite (Wetter: Open-Meteo, braucht Internet).

Die folgenden Punkte 1–7 beschreiben die **Online-Version mit Google-Tabelle**. Für die PC-Version werden sie nicht benötigt.

---

**Kurz gesagt:** Die Webseite wird einmal eingerichtet (Punkte 2–4, Technik). Danach pflegt der Obmann oder jede Person mit Admin-Rechten Termine und Ergebnisse in einer **Google-Tabelle**, die wie Excel funktioniert (Punkt 5). Dafür braucht man keinen Texteditor und keine Programmierkenntnisse.

---

## 1. Inhalt des Pakets

```
esv-grein-webseite/
├── index.html          Startseite
├── admin.html          Verwaltung (Status, Prüfung, Link zur Tabelle) – nicht verlinkt, als Lesezeichen speichern
├── impressum.html      Impressum (Platzhalter ausfüllen!)
├── datenschutz.html    Datenschutzerklärung (Platzhalter ausfüllen!)
├── css/style.css       Gestaltung (Farben ganz oben)
├── js/daten.js         Grundeinstellungen + Ersatzdaten (nur bei Einrichtung anfassen)
├── js/tabelle.js       Liest die Google-Tabelle (nicht ändern)
├── js/main.js          Seitenlogik (nicht ändern)
├── bilder/             Logo, Titelbild, Vorstandsfotos
├── dokumente/          Mitgliedsantrag, Probetraining (PDF)
└── formulare/          Skript zum Neu-Erzeugen der PDF-Formulare
```
Dazu gehört die Vorlage **ESV_Grein_Webseite_Daten.xlsx** (separat geliefert).

## 2. Bilder einfügen

| Datei | Was |
|---|---|
| `bilder/vereinsheim.jpg` | Großes Bild oben, z. B. das Facebook-Titelbild in voller Auflösung, Querformat, mind. 1600 px breit |
| `bilder/logo.png` | Vereinslogo, quadratisch, mind. 200 × 200 px |

Fehlt ein Bild, bleibt die Seite trotzdem sauber.

## 3. Online stellen mit GitHub Pages (kostenlos)

1. Auf github.com: **New repository** → Name `esv-grein` → **Public** → Create.
2. **Add file → Upload files** → den *Inhalt* des Ordners hineinziehen → **Commit changes**.
3. **Settings → Pages** → *Deploy from a branch* → Branch `main`, Ordner `/ (root)` → Save.
4. Nach 1–2 Minuten ist die Seite online: **https://rolandkoll99-droid.github.io/esv-grein/**

## 4. Google-Tabelle einrichten (einmalig, ca. 10 Minuten)

1. **drive.google.com** öffnen (mit dem Google-Konto des Vereins oder deinem eigenen).
2. **Neu → Datei hochladen** → `ESV_Grein_Webseite_Daten.xlsx` wählen.
3. Die hochgeladene Datei doppelklicken → oben **Datei → Als Google Tabellen speichern**.
   *Wichtig: Es muss eine echte Google-Tabelle sein (grünes Symbol, kein „.XLSX“-Schild neben dem Namen). Sonst kann die Webseite sie nicht lesen.*
4. In der neuen Google-Tabelle: **Freigeben** (rechts oben) →
   - *Allgemeiner Zugriff:* **Jeder, der über den Link verfügt** → Rolle **Betrachter**
     (Damit kann die Webseite die Daten lesen. Ändern kann niemand.)
5. Die Adresse der Tabelle kopieren. Sie sieht so aus:
   `https://docs.google.com/spreadsheets/d/`**`1AbCdEf…XyZ`**`/edit`
   Der fett markierte Teil zwischen `/d/` und `/edit` ist die **Tabellen-ID**.
6. In `js/daten.js` ganz oben eintragen:
   ```js
   googleTabelleId: "1AbCdEf…XyZ",
   ```
   Auf GitHub: Datei öffnen → Stift-Symbol → ändern → *Commit changes*. Das ist die **einzige** Änderung im Code.
7. Kontrolle: **…/esv-grein/admin.html** öffnen. Dort sollte stehen: *„Alles in Ordnung – die Tabelle ist verbunden.“*

### Admin-Rechte vergeben (intern)

In der Google-Tabelle **Freigeben** → E-Mail-Adresse der Person eintragen → Rolle **Bearbeiter** → Senden.
- Die Person bekommt eine E-Mail mit dem Link und kann sofort eintragen, am PC im Browser oder am Handy mit der App *Google Tabellen*.
- Rechte entziehen: **Freigeben** → bei der Person **Zugriff entfernen**.
- Wer was geändert hat und alte Stände: **Datei → Versionsverlauf**. Ein Fehler lässt sich so jederzeit rückgängig machen.
- Geeignet sind z. B. Obmann, Schriftführer und Sportwart. Eine Google-Adresse (Gmail) ist am einfachsten.

## 5. Termine und Ergebnisse eintragen (für den Obmann)

1. **admin.html** öffnen (Lesezeichen) → **Tabelle bearbeiten**.
2. Unten das Blatt wählen: **Termine**, **Ergebnisse**, **Veranstaltungen**, **Regeltraining**, **Trainingsfrei**, **Vorstand**, **Verein**.
3. In die nächste freie Zeile schreiben:
   - Datum: **14.11.2026**
   - Uhrzeit: **18:00** (oder leer)
   - Art: aus der Auswahlliste (Training / Meisterschaft / Turnier / Vereinsfest)
4. Fertig. Google speichert automatisch. Nach **1–5 Minuten** steht es auf der Webseite.
5. Unsicher? In admin.html auf **Eingaben prüfen** klicken. Fehler wie ein falsches Datum werden mit Zeilennummer angezeigt.

**Automatisch erledigt die Webseite:**
- Jeden Montag Seniorentraining und jeden Freitag ab 18:00 Training (Blatt *Regeltraining*)
- An Tagen mit Termin oder Veranstaltung entfällt das Training.
- Feiertage aus dem Blatt *Trainingsfrei* werden übersprungen.
- Vergangene Termine verschwinden, die Kachel „Nächster Termin“ springt weiter.
- Ergebnisse werden nach Datum sortiert, mit Filterknöpfen pro Saison.

**Bitte nicht ändern:** Blattnamen und Spaltenüberschriften (blaue Zeile).
**Achtung:** Die Tabelle ist öffentlich lesbar. Keine privaten Daten eintragen.

*Ohne Internet oder wenn die Tabelle nicht erreichbar ist, zeigt die Webseite die Ersatzdaten aus `js/daten.js`.*

## 5b. Fotos auf die Webseite bringen (ein Ordner pro Veranstaltung)

Die Fotos liegen in **Google Drive**. Pro Veranstaltung gibt es einen Ordner. Ein kleines Skript in der Google-Tabelle sucht die Fotos jede Stunde automatisch zusammen. Einzelne Links muss niemand eintragen.

```
ESV Grein Webseite Fotos/            ← Hauptordner (freigegeben)
├── 2026-07-17 Mix Rechberg/          ← Album „Mix Rechberg“, Datum 17.07.2026
├── 2026-04-24 Frühlingsturnier Dimbach/
└── Training Sommer/                  ← ohne Datum: Erstelldatum des Ordners
```

### Einmalig einrichten (ca. 10 Minuten, Roland)

1. **Hauptordner anlegen:** In Google Drive **Neu → Neuer Ordner** „ESV Grein Webseite Fotos“.
   Rechtsklick → **Teilen** → *Allgemeiner Zugriff:* **Jeder, der über den Link verfügt** → Betrachter → Link kopieren.
   Alle Unterordner und Fotos sind damit automatisch freigegeben.
2. **Google-Tabelle ergänzen** (falls sie schon existiert):
   - Blatt **Verein**: neue Zeile `Foto-Ordner-Link`, daneben den kopierten Ordner-Link einfügen.
   - Neues Blatt **Fotos** anlegen (unten **+**, genau so benennen). Das Skript legt die Überschriften selbst an.
3. **Skript einfügen:** In der Tabelle **Erweiterungen → Apps Script** → den vorhandenen Inhalt löschen → den kompletten Inhalt der Datei `google-apps-script/Fotos.gs` einfügen → **Speichern** (Diskettensymbol).
4. Tabelle neu laden (F5). Oben erscheint das Menü **ESV Grein** → **Automatik einschalten (stündlich)**.
5. Google fragt beim ersten Mal nach einer Berechtigung:
   **Weiter** → dein Konto wählen → *„Google hat diese App nicht überprüft“* → **Erweitert** → **Zu „…“ wechseln (unsicher)** → **Zulassen**.
   Das ist normal bei eigenen Skripten. Es greift nur auf deine eigene Tabelle und Drive zu und gibt nichts weiter.
6. Kontrolle: Im Blatt **Fotos** stehen jetzt die Fotos (Spalte *Quelle* = „Ordner“). Auf **admin.html → Eingaben prüfen** zählt „Fotos“ mit.

*Tipp:* Das Skript sollte mit dem Google-Konto eingerichtet werden, dem der Foto-Ordner gehört, am besten ein eigenes Vereinskonto.

### Fotos hinzufügen (Obmann)

1. Im Ordner „ESV Grein Webseite Fotos“ **Neu → Neuer Ordner**, Name **Datum + Veranstaltung**, z. B. `2026-11-14 Bezirksmeisterschaft`.
2. Fotos hineinladen. Am Handy geht das mit der Google-Drive-App: **+ → Hochladen**.
3. Fertig. Spätestens nach einer Stunde sind die Fotos auf der Webseite. Sofort geht es über **ESV Grein → Fotos jetzt aktualisieren** in der Tabelle.

- **Reihenfolge** der Fotos = Dateiname (z. B. 01.jpg, 02.jpg …)
- **Bildunterschrift:** in Drive Rechtsklick aufs Foto → *Dateiinformationen → Details* → Beschreibung
- **Entfernen:** Foto oder Ordner in Drive löschen, die Webseite übernimmt das automatisch
- Pro Album werden 8 Vorschaubilder gezeigt, alle per Diashow. „Ganzes Album ansehen“ öffnet den Drive-Ordner.
- Die **besten 10–30 Fotos** pro Veranstaltung reichen. Das Skript übernimmt höchstens 60 je Ordner.
- Einzelne Fotos können weiterhin auch von Hand ins Blatt *Fotos* eingetragen werden (Spalte *Quelle* leer lassen).
- **Titelbild der Startseite:** Blatt *Verein* → *Titelbild-Link* (Drive-Link zu einem Foto).
- Nur Fotos verwenden, bei denen die abgebildeten Personen einverstanden sind.

## 6. Webseite in die Facebook-Seite einbinden

**a) Webseite im Profil:** Facebook → zur Seite ESV Grein wechseln → **Profil bearbeiten** → *Kontaktinfo / Details* → **Website hinzufügen** → Adresse eintragen.

**b) Button unter dem Titelbild:** Beim blauen Button („Nachricht senden“) → **Bearbeiten / Button ändern** → z. B. „Mehr erfahren“ bzw. „Website besuchen“ → Webseiten-Adresse. Die Bezeichnungen können je nach App-Version leicht abweichen.

**c) Vorstellungsbeitrag posten und oben fixieren:**
> 🎉 Der ESV Grein hat jetzt eine eigene Webseite! Termine, Ergebnisse und alle Infos zum Probetraining: https://rolandkoll99-droid.github.io/esv-grein/

Ist die Linkvorschau veraltet: https://developers.facebook.com/tools/debug/ → Adresse eingeben → **Erneut scrapen**.

**d) Facebook-Beiträge auf der Webseite (optional):** In `js/daten.js` bei `facebookSeite` die echte Seitenadresse eintragen, die im Browser in der Adresszeile steht, z. B. `https://www.facebook.com/profile.php?id=…`. Die Beiträge laden erst nach einem Klick (Datenschutz).

## 7. Vor dem Online-Gehen erledigen

- [ ] Google-Tabelle einrichten (Punkt 4) und Blatt **Verein** ausfüllen
- [ ] Im Blatt **Regeltraining** die Uhrzeit für das Seniorentraining eintragen
- [ ] Platzhalter in `impressum.html` und `datenschutz.html` ausfüllen (ZVR-Zahl: zvr.bmi.gv.at)
- [ ] Datenschutzerklärung prüfen (Google-Tabelle ist bereits erwähnt). Bitte gegenlesen lassen, die Vorlage ersetzt keine Rechtsberatung.
- [ ] `bilder/vereinsheim.jpg` und `bilder/logo.png` einfügen
- [ ] PDF-Formulare mit Vereinsdaten neu erzeugen (Beiträge, IBAN, Adresse)
- [ ] Einverständnis für Namen und Fotos des Vorstands einholen
