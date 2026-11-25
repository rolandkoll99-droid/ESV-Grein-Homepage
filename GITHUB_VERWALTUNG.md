# ESV Grein – Webseite direkt auf GitHub pflegen (V2.4)

Ab V2.4 werden Termine, Ergebnisse, Neuigkeiten und Fotos **direkt auf der GitHub-Webseite** eingetragen:
Webseite öffnen → unten **„Verwaltung“** → anmelden → eintragen → **Speichern**. Nach **1–2 Minuten** ist die Änderung online.
Kein PC muss laufen, kein Export, kein Hochladen mehr. Funktioniert am PC und am Handy.

---

## A. Einmalig: neue Version hochladen (Administrator, ca. 10 Minuten)

1. `ESV_Grein_GitHub_V2.4_Upload.zip` **entpacken**.
2. Im Repository auf GitHub: **Add file → Upload files** → **alle Dateien und Ordner** aus dem entpackten Ordner ins Fenster ziehen
   (nicht die ZIP-Datei, nicht den Ordner selbst). Vorhandene Dateien werden ersetzt.
3. **Commit changes**. Nach 1–2 Minuten die Webseite mit **Strg+F5** laden: unten steht „Stand …“ und der Link **„Verwaltung“**.

Neu im Repository sind dann u. a. `verwaltung.html`, `js/github-verwaltung.js` und **`data/daten.json`** – das ist ab jetzt der Datenspeicher.

> **Wichtig:** Ab jetzt ist GitHub der „Hauptspeicher“. **Keinen Export vom PC mehr hochladen** – er würde die auf GitHub eingetragenen Daten mit dem alten PC-Stand überschreiben.

## B. Einmalig: GitHub-Schlüssel erstellen (Administrator, je Person 3 Minuten)

Der Schlüssel ersetzt das Passwort. **Für jede Person, die eintragen darf, einen eigenen Schlüssel erstellen** – so kann er einzeln wieder entzogen werden.
Erstellt wird er im GitHub-Konto, dem das Repository gehört.

1. github.com → rechts oben Profilbild → **Settings** → ganz unten links **Developer settings**
   → **Personal access tokens** → **Fine-grained tokens** → **Generate new token**.
2. **Token name:** z. B. `ESV Verwaltung – Obmann` · **Expiration:** z. B. 1 Jahr (Erinnerung im Kalender eintragen).
3. **Repository access:** **Only select repositories** → das Repository der Webseite auswählen.
4. **Permissions → Repository permissions:** **Contents → Read and write**.
   (Optional zusätzlich **Pages → Read-only**; nur nötig, wenn die Seite aus einem Unterordner wie `/docs` veröffentlicht wird.)
5. **Generate token** → den Schlüssel (beginnt mit `github_pat_…`) **sofort kopieren** – er wird nur einmal angezeigt.
6. Der Person sicher übergeben (persönlich oder per Nachricht, nicht öffentlich posten).

**Entziehen:** gleiche Stelle → Schlüssel anklicken → **Delete**. Die Person kann danach nichts mehr ändern.

*Die Menüs bei GitHub werden gelegentlich umbenannt. Gemeint ist immer: Fine-grained Token, nur dieses Repository, Contents – Read and write.*

## C. Eintragen (alle Berechtigten)

1. Webseite öffnen → ganz unten **„Verwaltung“** (oder `…/verwaltung.html`).
2. **Dein Name** eingeben (steht im Änderungsprotokoll) und beim ersten Mal den **GitHub-Schlüssel** einfügen.
   Häkchen „Schlüssel auf diesem Gerät merken“ → ab dann genügt **Anmelden** ohne Schlüssel. Nur auf eigenen Geräten merken lassen!
3. Bereich wählen (Neuigkeiten, Termine, Ergebnisse, Fotos, unter „Weitere“: Veranstaltungen, Vorstand, Training, Verein)
   → **+ Neu** bzw. **Bearbeiten** → ausfüllen → **Speichern**.
4. Nach **1–2 Minuten** auf der Webseite sichtbar (ggf. Strg+F5 bzw. am Handy neu laden).

**Fotos:** Fotos → Album anlegen → **+ Fotos hinzufügen** (mehrere auf einmal möglich, werden automatisch verkleinert).

## D. Gut zu wissen

| Thema | |
|---|---|
| Änderungsprotokoll | Einstellungen → Änderungsprotokoll, bzw. auf GitHub unter „Commits“ – jede Änderung mit Name |
| Etwas falsch gelöscht? | Auf GitHub ist jeder frühere Stand gespeichert und kann wiederhergestellt werden (Administrator) |
| Zwei Personen gleichzeitig | Wer später speichert, bekommt einen Hinweis; die Daten werden neu geladen, die Eingabe wiederholen |
| Entwürfe | erscheinen nicht auf der Webseite – stehen aber in `data/daten.json` im öffentlichen Repository |
| Speicherplatz | GitHub empfiehlt Repositories unter 1 GB – das reicht für ca. 2.000 verkleinerte Fotos |
| Schlüssel abgelaufen | Meldung „Schlüssel ungültig oder abgelaufen“ → Administrator erstellt einen neuen (Teil B) |
| Später auf den Pi umziehen | jederzeit möglich: `data/daten.json` und Ordner `fotos` vom Repository auf den Daten-Stick kopieren |
