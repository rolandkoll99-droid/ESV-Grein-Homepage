# ESV Grein Webseite auf dem Raspberry Pi

> **Derzeit: Präsentationsbetrieb, noch keine Veröffentlichung.** Für die Vorführung genügt **PRAESENTATION.md**: Installation direkt am Pi vom Stick, Vollbild, Ablauf. Schritt 5 (Fernzugriff/esv-grein.com) erst bei der Veröffentlichung.

Die Webseite läuft auf einem Raspberry Pi in der Stockhalle, angeschlossen per LAN-Kabel.
**Alle Daten** (Termine, Ergebnisse, Neuigkeiten, Fotos, Bilder, PDFs) liegen auf einem **USB-Stick direkt am Pi**.

```
  Internet ──► Cloudflare (https://esv-grein.com) ──► Tunnel ──┐
                                                               ▼
  Handy/Laptop in der Halle ──► http://esv-grein.local ──► Raspberry Pi ──► USB-Stick „ESV-DATEN“
                                                          (Programm auf SD-Karte)  (alle Daten + Fotos)
```

| Wo | Adresse |
|---|---|
| In der Halle (LAN/WLAN) | **http://esv-grein.local** (oder die IP-Adresse des Pi) |
| Von überall | **https://esv-grein.com** (nach Schritt 5) |
| Verwaltung | jeweils **/verwaltung.html**, oder oben rechts auf der Webseite „Verwaltung“ |

---

## 1. Was wird benötigt

- Raspberry Pi 4 (oder 3B+ / 5) mit **Original-Netzteil**
- microSD-Karte ab 16 GB
- **USB-Stick** ab 32 GB, Markenware, am besten USB 3.0
- LAN-Kabel zum Router in der Halle
- Internetzugang in der Halle (für esv-grein.com und die Wetteranzeige)
- Ein PC für die Einrichtung

## 2. SD-Karte vorbereiten (am PC, ca. 10 Minuten)

1. **Raspberry Pi Imager** installieren (raspberrypi.com/software) und starten.
2. Gerät: dein Pi-Modell · Betriebssystem: **Raspberry Pi OS Lite (64-bit)** · Speicher: die SD-Karte.
3. Bei **Einstellungen anpassen**:
   - Hostname: **esv-grein**
   - Benutzername und Passwort festlegen (gut aufheben!)
   - Zeitzone: Europe/Vienna, Tastatur: de
   - Reiter *Dienste*: **SSH aktivieren** (mit Passwort)
4. Schreiben, SD-Karte in den Pi, LAN-Kabel anstecken, Strom an. Nach 1–2 Minuten ist der Pi bereit.

## 3. USB-Stick vorbereiten (am PC)

1. Stick anstecken → im Explorer Rechtsklick → **Formatieren**
   - Dateisystem: **exFAT**
   - Volumebezeichnung: **ESV-DATEN** (genau so schreiben)
2. **Daten aus der PC-Version übernehmen** (falls schon etwas eingetragen wurde):
   Aus dem PC-Ordner `esv-grein-webseite` diese Ordner direkt auf den Stick kopieren:
   `data`, `fotos` und aus `bilder` die selbst hochgeladenen Bilder (`vereinsheim.jpg`, `logo.png`, Ordner `neuigkeiten`, `vorstand`) in einen Ordner `bilder` auf dem Stick.
3. Stick am PC auswerfen und am **Pi** anstecken.

## 4. Webseite auf dem Pi installieren

**Einfachster Weg, per Doppelklick am Windows-PC** (im selben Netzwerk wie der Pi):

1. ZIP-Datei `ESV_Grein_Webseite_V2.1.zip` entpacken.
2. Im entpackten Ordner **„Auf Pi installieren.bat“** doppelklicken.
3. Adresse des Pi bestätigen (Enter = `esv-grein.local`) und den **Benutzernamen** aus Schritt 2 eingeben.
4. Zweimal das **Passwort des Pi** eingeben. Beim Tippen ist nichts zu sehen, das ist normal. Beim allerersten Mal mit `yes` bestätigen.
5. Warten, bis **„Fertig! Die Webseite läuft.“** erscheint (einige Minuten).

<details><summary>Alternativ von Hand (für Technik-Admins)</summary>

```
scp ESV_Grein_Webseite_V2.1.zip BENUTZER@esv-grein.local:
ssh BENUTZER@esv-grein.local
unzip -o ESV_Grein_Webseite_V2.1.zip
sudo bash ESV_Grein_Webseite_V2.1/pi/installieren.sh
```
</details>

**Gut zu wissen:**
- Das Skript bricht ab, wenn auf dem Pi schon ein anderes Programm die Webseiten-Adresse (Port 80) belegt, z. B. eine Anzeige. **Empfehlung: ein eigener Pi für die Webseite.**
- Heißt der Pi nicht „raspberrypi“, fragt das Skript, bevor es ihn in „esv-grein“ umbenennt.
- Am Ende prüft das Skript selbst, ob die Webseite antwortet.

Das Skript erledigt alles automatisch: Programm nach `/opt/esv-grein`, Stick dauerhaft einbinden, Datenordner anlegen, Webseite als Dienst starten (auch nach Stromausfall automatisch), Rechnername `esv-grein`.

**Test:** Am Handy oder Laptop in der Halle **http://esv-grein.local** öffnen.
Verwaltung → Start-PIN **1234** → die Verwaltung verlangt sofort ein **eigenes Passwort (mind. 8 Zeichen)**. Erst danach ist auch der Fernzugriff möglich.

> Android-Handys kennen „.local“-Adressen nicht immer. Dann die IP-Adresse verwenden, die das Installationsskript am Ende anzeigt. Am besten im Router eine feste IP für den Pi einstellen.

## 5. Fernzugriff über esv-grein.com (einmalig, ca. 20 Minuten)

Der Fernzugriff läuft über einen **Cloudflare-Tunnel**:
- Am Router muss **nichts freigegeben** werden, keine Portweiterleitung.
- Funktioniert auch mit Handy-/LTE-Internet in der Halle.
- Die Verbindung ist automatisch **verschlüsselt (https)**.
- Cloudflare ist für diesen Zweck kostenlos.

### 5a. Domain und Cloudflare-Konto
1. Auf **cloudflare.com** ein kostenloses Konto anlegen, am besten mit der Vereins-E-Mail.
2. Domain **esv-grein.com**:
   - **Noch nicht registriert:** direkt bei Cloudflare registrieren (*Domain Registration*) oder bei einem beliebigen Anbieter.
   - **Schon registriert:** in Cloudflare **„Domain hinzufügen“**, kostenlosen Plan wählen, beim bisherigen Anbieter die beiden angezeigten **Cloudflare-Nameserver** eintragen. Die Aktivierung dauert meist Minuten bis wenige Stunden.

### 5b. Tunnel anlegen
1. Im Cloudflare-Dashboard: **Zero Trust → Networks → Tunnels → Tunnel erstellen** → Typ **Cloudflared** → Name z. B. `esv-grein-halle`.
2. Es wird ein Installationsbefehl angezeigt. Darin steht nach `service install` ein langer **Token**. Diesen Token kopieren.
3. Auf dem Pi (per `ssh` wie in Schritt 4):
   ```
   sudo bash /opt/esv-grein/pi/fernzugriff-einrichten.sh DEIN-TOKEN
   ```
4. Zurück im Dashboard beim Tunnel eine **öffentliche Adresse** (*Public Hostname* bzw. *Published application route*) hinzufügen:
   - Domain: **esv-grein.com** (Subdomain leer)
   - Dienst: **HTTP** · URL: **localhost:80**
   - Dasselbe noch einmal mit Subdomain **www**
5. Test mit dem Handy **ohne WLAN**: **https://esv-grein.com**

*Die Menüpunkte bei Cloudflare werden gelegentlich umbenannt. Gemeint ist immer: Tunnel anlegen, Token auf dem Pi verwenden, esv-grein.com auf localhost:80 zeigen lassen.*

### 5c. Verwaltung von außen
- Funktioniert unter **https://esv-grein.com/verwaltung.html**, sobald vor Ort ein **Passwort mit mindestens 8 Zeichen** vergeben wurde. Mit der Start-PIN ist der Fernzugriff gesperrt. Nach 60 Minuten ohne Aktion wird automatisch abgemeldet.
- Nach **5 Fehlversuchen** wird die Anmeldung für diese Adresse **15 Minuten gesperrt**.
- **Empfohlen, zusätzlich:** Cloudflare Access als zweites Schloss. *Zero Trust → Access → Applications → Self-hosted*:
  - Anwendung 1: `esv-grein.com/verwaltung.html`
  - Anwendung 2: `esv-grein.com/api/admin`
  - Regel: **Allow** → *Emails* → die E-Mail-Adressen der Vereinsadmins

  Dann muss man sich von außen zuerst mit einem Code bestätigen, der per E-Mail kommt, und erst danach mit dem Passwort. In der Halle (esv-grein.local) bleibt alles wie gewohnt.

## 6. Bedienung im Alltag

- **Termine, Neuigkeiten, Ergebnisse, Fotos:** in der Verwaltung, vor Ort oder von zu Hause. Fotos am besten über *Fotos → + Fotos hinzufügen* hochladen, dann wird automatisch verkleinert.
- **Stromausfall:** kein Problem, der Pi startet die Webseite von selbst wieder.
- **Pi ausschalten:** nicht einfach den Stecker ziehen, sondern `sudo shutdown -h now` (per ssh), danach den Strom trennen.

### USB-Stick abziehen (z. B. Fotos am PC kopieren)
```
sudo bash /opt/esv-grein/pi/stick-entfernen.sh
```
Stick abziehen, am PC arbeiten (Ordner `fotos/<Datum Veranstaltung>`), wieder anstecken, dann:
```
sudo bash /opt/esv-grein/pi/stick-einbinden.sh
```
(oder den Pi neu starten). **Den Stick nie im laufenden Betrieb einfach abziehen.** Das kann Daten beschädigen.

## 7. Datensicherung

| Was | Wo | Automatisch? |
|---|---|---|
| Alle Daten + Fotos | USB-Stick | – |
| Sicherung bei jedem Speichern (letzte 50) | Stick: `data/sicherung` | ja |
| Tägliche Kopie der Daten (ohne Fotos, letzte 30 Tage) | SD-Karte: `/opt/esv-grein/sicherung-sd` | ja |
| Gelöschte Fotos | Stick: `fotos/_papierkorb` | ja |
| **Kompletter Stick** | **PC oder zweiter Stick** | **monatlich von Hand** |

Fällt der Stick aus: neuen Stick wie in Schritt 3 vorbereiten, Sicherung zurückkopieren, `sudo bash /opt/esv-grein/pi/installieren.sh` erneut ausführen.

## 8. Aktualisieren

Neue Version entpacken und wieder **„Auf Pi installieren.bat“** doppelklicken. Daten und Fotos auf dem Stick bleiben erhalten.

## 9. Wenn etwas nicht geht

| Problem | Lösung |
|---|---|
| esv-grein.local geht nicht | IP-Adresse des Pi verwenden (im Router nachsehen) |
| Webseite in der Halle nicht erreichbar | `sudo systemctl status esv-grein` · Protokoll: `journalctl -u esv-grein -n 50` |
| „Daten-Stick nicht gefunden“ im Protokoll | Stick anstecken → `sudo bash /opt/esv-grein/pi/stick-einbinden.sh` |
| esv-grein.com geht nicht, Halle schon | Internet in der Halle prüfen · `sudo systemctl status cloudflared` · Tunnel-Status im Cloudflare-Dashboard |
| Verwaltung von außen: „Fernzugriff gesperrt“ | Vor Ort in den Einstellungen ein Passwort mit mind. 8 Zeichen setzen |
| „Zu viele Fehlversuche“ | 15 Minuten warten |
| Passwort vergessen | Am Pi: `rm /media/esv-stick/data/einstellungen.json` → Anmeldung wieder mit 1234, danach neues Passwort festlegen (nur vor Ort) |
| Stick voll | Verwaltung → Einstellungen zeigt den freien Speicher. Alte Fotoordner auf den PC sichern und vom Stick löschen. |
