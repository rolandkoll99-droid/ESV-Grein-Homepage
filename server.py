# -*- coding: utf-8 -*-
"""
ESV Grein – Vereins-Webserver (Raspberry Pi oder PC)
===================================================
PC:  Doppelklick auf "Webseite starten.bat"         -> http://localhost:8420/
Pi:  läuft als Dienst (siehe pi/installieren.sh)     -> http://esv-grein.local/  bzw.  https://esv-grein.com/

Optionen (oder Umgebungsvariablen):
  --daten PFAD   (ESV_DATEN)  Speicherort für Daten, Fotos, Bilder, Dokumente – z. B. der USB-Stick
  --port N       (ESV_PORT)   Port, Standard 8420 (Pi: 80)
  --netzwerk                  im ganzen Netzwerk erreichbar (sonst nur dieser Rechner)
  --kein-browser              keinen Browser öffnen

Nur Python-Standardbibliothek.
"""
import hashlib, hmac, json, os, re, secrets, socket, sys, shutil, threading, webbrowser, time, mimetypes
from datetime import datetime, date
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, quote, unquote

VERSION = "2.3 Veröffentlichung"
BASIS = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__))


def _option(name, umgebung, standard):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return os.environ.get(umgebung) or standard


PORT = int(_option("--port", "ESV_PORT", "8420"))
DATENORT = os.path.abspath(_option("--daten", "ESV_DATEN", BASIS))
AUF_STICK = DATENORT != BASIS
MARKER = os.path.join(DATENORT, ".esv-stick")

DATA = os.path.join(DATENORT, "data")
SICHERUNG = os.path.join(DATA, "sicherung")
DATEN = os.path.join(DATA, "daten.json")
EINST = os.path.join(DATA, "einstellungen.json")
FOTOS = os.path.join(DATENORT, "fotos")
PAPIERKORB = os.path.join(FOTOS, "_papierkorb")
BILDER = os.path.join(DATENORT, "bilder")          # hochgeladene Bilder (Titelbild, Logo, Neuigkeiten)
DOKUMENTE = os.path.join(DATENORT, "dokumente")
EXPORT = os.path.join(DATENORT, "export")
SD_KOPIE = os.path.join(BASIS, "sicherung-sd")     # Zweitkopie der Daten auf der SD-Karte (nur Stick-Betrieb)
PROTOKOLL = os.path.join(DATA, "protokoll.jsonl")  # Änderungsprotokoll

BILDTYPEN = (".jpg", ".jpeg", ".png", ".webp", ".gif")
ERLAUBT = (".html", ".css", ".js", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".pdf", ".ico", ".woff2")
MAX_UPLOAD = 30 * 1024 * 1024
SPERRE = threading.Lock()
FEHLVERSUCHE = {}            # IP -> [Anzahl, gesperrt_bis]
SITZUNGEN = {}               # Token -> {"bis": Zeit, "name": Bearbeiter}
SITZUNG_LEERLAUF = 60 * 60   # automatische Abmeldung nach 60 Minuten ohne Aktion
ENTWURF_LISTEN = ("neuigkeiten", "termine", "veranstaltungen")
MAX_FEHLVERSUCHE, SPERRZEIT = 5, 15 * 60

START_DATEN = {
    "verein": {"adresse": "", "plzOrt": "4360 Grein", "telefon": "", "email": "", "mitgliedsbeitrag": "",
               "trainingszeiten": "", "facebook": "https://www.facebook.com/share/19qc47PZg9/",
               "wetterOrt": "Grein", "wetterLat": 48.229, "wetterLon": 14.856,
               "vorschau": False},
    "neuigkeiten": [
        {"datum": "2026-10-28", "titel": "Unsere neue Webseite ist online", "text": "Ab sofort findet ihr hier alle Termine, Ergebnisse und Fotos des ESV Grein. Schaut regelmäßig vorbei!", "bild": "", "wichtig": False},
    ],
    "termine": [],
    "ergebnisse": [
        {"datum": "2026-07-17", "bewerb": "Mix Rechberg 2026", "ort": "Rechberg", "mannschaft": "ÖTSU Grein",
         "platz": 4, "teilnehmer": 9, "punkte": "8:8", "saison": "Sommer 2026", "pdf": ""},
        {"datum": "2026-05-02", "bewerb": "Vereinsturnier 2026 – Herrenturnier", "ort": "Perg (ASKÖ Prinz Brunnenbau Perg)",
         "mannschaft": "Union Grein", "platz": 8, "teilnehmer": None, "punkte": "8:12", "saison": "Sommer 2026", "pdf": ""},
        {"datum": "2026-04-24", "bewerb": "Frühlingsturnier Dimbach", "ort": "Stockhalle Dimbach", "mannschaft": "Union Grein",
         "platz": 1, "teilnehmer": 7, "punkte": "10:2", "saison": "Sommer 2026", "pdf": ""},
    ],
    "veranstaltungen": [],
    "regelTraining": [
        {"wochentag": 1, "zeit": "", "titel": "Seniorentraining", "ort": "Stockbahn Grein"},
        {"wochentag": 5, "zeit": "18:00", "titel": "Training", "ort": "Stockbahn Grein"},
    ],
    "trainingsfrei": ["2026-12-25", "2027-01-01"],
    "vorstand": [{"funktion": f, "name": "", "foto": ""} for f in
                 ["Obmann", "Obmann-Stellvertreter", "Kassier", "Schriftführer", "Sportwart"]],
    "albumTexte": {},
}
# Beispieldaten für die Vorführung (werden mit "beispiel": true markiert und lassen sich wieder entfernen)
BEISPIELDATEN = {
    "neuigkeiten": [
        {"datum": "2026-10-25", "titel": "Wintersaison startet im November", "text": "Ab November trainieren wir wieder regelmäßig in der Halle: Montag Seniorentraining, Freitag ab 18:00 Uhr Training für alle. Neue Schützinnen und Schützen sind herzlich willkommen!", "bild": "", "wichtig": True},
        {"datum": "2026-10-10", "titel": "Danke für die Unterstützung beim Hallenputz", "text": "Vielen Dank an alle Helferinnen und Helfer – die Halle ist bereit für die neue Saison.", "bild": "", "wichtig": False},
    ],
    "termine": [
        {"datum": "2026-11-14", "zeit": "09:00", "titel": "Bezirksmeisterschaft (Beispiel)", "ort": "[Ort]", "art": "meisterschaft"},
        {"datum": "2026-11-28", "zeit": "13:00", "titel": "Vereinsturnier (Beispiel)", "ort": "Stockhalle Grein", "art": "turnier"},
        {"datum": "2026-12-11", "zeit": "19:00", "titel": "Weihnachtsfeier (Beispiel)", "ort": "[Gasthaus]", "art": "fest"},
    ],
    "veranstaltungen": [
        {"datum": "2027-01-16", "titel": "Ortsturnier für Hobbymannschaften (Beispiel)", "text": "Für Firmen, Vereine und Freundesrunden – Mannschaften mit 4 Personen. Nenngeld und Anmeldung: [Details].", "bild": "", "ausschreibung": ""},
    ],
}

LISTEN = ["neuigkeiten", "termine", "ergebnisse", "veranstaltungen", "regelTraining", "trainingsfrei", "vorstand"]


# ---------------------------------------------------------------- Daten
def json_lesen(pfad, standard):
    try:
        with open(pfad, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return standard


def json_schreiben(pfad, wert):
    tmp = pfad + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(wert, f, ensure_ascii=False, indent=1)
        f.flush()
        os.fsync(f.fileno())  # wichtig bei USB-Sticks
    os.replace(tmp, pfad)


def daten_lesen():
    d = json_lesen(DATEN, None)
    if not isinstance(d, dict):
        d = json.loads(json.dumps(START_DATEN))
    for k, v in START_DATEN.items():
        d.setdefault(k, json.loads(json.dumps(v)))
    return d


class Konflikt(Exception):
    pass


def daten_speichern(neu, rev=None):
    """rev: Stand, den der Bearbeiter geladen hat. Weicht er ab, hat inzwischen jemand anderer gespeichert."""
    with SPERRE:
        alt = daten_lesen()
        if rev is not None and int(rev) != int(alt.get("_rev", 0)):
            raise Konflikt()
        if any(k in neu for k in LISTEN + ["verein"]):
            alt["_rev"] = int(alt.get("_rev", 0)) + 1
        for k in LISTEN + ["albumTexte"]:
            if k in neu:
                alt[k] = neu[k]
        if "verein" in neu and isinstance(neu["verein"], dict):
            alt["verein"].update(neu["verein"])
        if os.path.exists(DATEN):  # Sicherung der bisherigen Datei (die letzten 50 bleiben)
            os.makedirs(SICHERUNG, exist_ok=True)
            shutil.copy2(DATEN, os.path.join(SICHERUNG, "daten-" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".json"))
            for x in sorted(os.listdir(SICHERUNG))[:-50]:
                try:
                    os.remove(os.path.join(SICHERUNG, x))
                except OSError:
                    pass
        json_schreiben(DATEN, alt)
        if AUF_STICK:  # Zweitkopie auf der SD-Karte, falls der Stick einmal ausfällt
            try:
                os.makedirs(SD_KOPIE, exist_ok=True)
                json_schreiben(os.path.join(SD_KOPIE, "daten-" + date.today().isoformat() + ".json"), alt)
                for x in sorted(os.listdir(SD_KOPIE))[:-30]:
                    os.remove(os.path.join(SD_KOPIE, x))
            except OSError:
                pass
        return alt


def _hash(pw, salt):
    return hashlib.scrypt(pw.encode("utf-8"), salt=bytes.fromhex(salt), n=2 ** 14, r=8, p=1, dklen=32).hex()


def passwort_setzen(pw):
    salt = secrets.token_hex(16)
    e = json_lesen(EINST, {})
    e.pop("pin", None)  # alte Klartext-PIN entfernen
    e.update({"pwSalt": salt, "pwHash": _hash(pw, salt), "pwLaenge": len(pw), "geaendert": datetime.now().isoformat(timespec="seconds")})
    json_schreiben(EINST, e)


def ersteinrichtung():
    """Noch kein eigenes Passwort vergeben (Start-PIN 1234)."""
    e = json_lesen(EINST, {})
    return not e.get("pwHash") and str(e.get("pin", "1234")) == "1234"


def passwort_pruefen(pw):
    e = json_lesen(EINST, {})
    pw = str(pw)
    if e.get("pwHash"):
        return hmac.compare_digest(_hash(pw, e["pwSalt"]), e["pwHash"])
    alt = str(e.get("pin", "1234"))  # ältere Version: Klartext-PIN -> wird beim Anmelden umgestellt
    ok = hmac.compare_digest(pw.encode("utf-8"), alt.encode("utf-8"))
    if ok and alt != "1234":
        passwort_setzen(pw)
    return ok


def passwort_laenge():
    e = json_lesen(EINST, {})
    return int(e.get("pwLaenge") or len(str(e.get("pin", "1234"))))


def protokoll(name, text):
    try:
        os.makedirs(DATA, exist_ok=True)
        with open(PROTOKOLL, "a", encoding="utf-8") as f:
            f.write(json.dumps({"zeit": datetime.now().strftime("%d.%m.%Y %H:%M"), "name": name or "–", "text": str(text)[:300]}, ensure_ascii=False) + "\n")
        if os.path.getsize(PROTOKOLL) > 300_000:  # nicht endlos wachsen lassen
            with open(PROTOKOLL, encoding="utf-8") as f:
                zeilen = f.readlines()[-1000:]
            with open(PROTOKOLL, "w", encoding="utf-8") as f:
                f.writelines(zeilen)
    except OSError:
        pass


def protokoll_lesen(n=30):
    try:
        with open(PROTOKOLL, encoding="utf-8") as f:
            zeilen = f.readlines()[-n:]
        return [json.loads(z) for z in reversed(zeilen) if z.strip()]
    except (OSError, ValueError):
        return []


def oeffentlich(d):
    """Entwürfe und interne Felder nicht veröffentlichen."""
    d = dict(d)
    for k in ENTWURF_LISTEN:
        d[k] = [x for x in d.get(k, []) if not (isinstance(x, dict) and x.get("entwurf"))]
    d.pop("_rev", None)
    d.pop("albumTexte", None)
    return d


def ist_bilddatei(roh):
    return (roh[:3] == b"\xff\xd8\xff" or roh[:8] == b"\x89PNG\r\n\x1a\n" or roh[:6] in (b"GIF87a", b"GIF89a")
            or (roh[:4] == b"RIFF" and roh[8:12] == b"WEBP"))


# ---------------------------------------------------------------- Fotos
def sauber(name, max_len=80):
    name = re.sub(r"[^\w äöüÄÖÜß.\-()&,]", "", str(name), flags=re.UNICODE).strip(" .")
    name = re.sub(r"\s+", " ", name)
    return name[:max_len]


def album_info(ordnername, pfad):
    m = re.match(r"^\s*(\d{4})-(\d{1,2})-(\d{1,2})[\s_\-–]*(.*)$", ordnername)
    if m:
        return "%s-%02d-%02d" % (m.group(1), int(m.group(2)), int(m.group(3))), (m.group(4).strip() or ordnername)
    m = re.match(r"^\s*(\d{1,2})\.(\d{1,2})\.(\d{2,4})[\s_\-–]*(.*)$", ordnername)
    if m:
        j = int(m.group(3)); j = j + 2000 if j < 100 else j
        return "%d-%02d-%02d" % (j, int(m.group(2)), int(m.group(1))), (m.group(4).strip() or ordnername)
    return date.fromtimestamp(os.path.getmtime(pfad)).isoformat(), ordnername.strip()


def natsort(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def ist_bild(f):
    return f.lower().endswith(BILDTYPEN) and not f.startswith((".", "_"))


def alben_lesen():
    os.makedirs(FOTOS, exist_ok=True)
    texte = daten_lesen().get("albumTexte", {})
    alben = []
    for ordner in sorted(os.listdir(FOTOS)):
        pfad = os.path.join(FOTOS, ordner)
        if not os.path.isdir(pfad) or ordner.startswith(("_", ".")) or ordner == "System Volume Information":
            continue
        datum, name = album_info(ordner, pfad)
        bilder = sorted([f for f in os.listdir(pfad) if ist_bild(f)], key=natsort)
        alben.append({"ordner": ordner, "datum": datum, "album": name, "bilder": bilder, "texte": texte.get(ordner, {})})
    lose = sorted([f for f in os.listdir(FOTOS) if ist_bild(f)], key=natsort)
    if lose:
        alben.append({"ordner": "", "datum": "", "album": "Allgemein", "bilder": lose, "texte": texte.get("", {})})
    return alben


def foto_url(ordner, datei):
    return "fotos/" + (quote(ordner) + "/" if ordner else "") + quote(datei)


def fotos_liste():
    liste = []
    for a in alben_lesen():
        for b in a["bilder"]:
            u = foto_url(a["ordner"], b)
            liste.append({"datum": a["datum"], "album": a["album"], "gross": u, "klein": u,
                          "text": a["texte"].get(b, ""), "albumLink": ""})
    return liste


def im_fotoordner(*teile):
    pfad = os.path.abspath(os.path.join(FOTOS, *teile))
    if not pfad.startswith(os.path.abspath(FOTOS) + os.sep) and pfad != os.path.abspath(FOTOS):
        raise ValueError("ungültiger Pfad")
    return pfad


# ---------------------------------------------------------------- Export (statische Kopie der Webseite)
def export_erstellen():
    d = daten_lesen()
    ziel = os.path.join(EXPORT, "esv-grein-online")
    if os.path.exists(ziel):
        shutil.rmtree(ziel)
    os.makedirs(ziel)
    for name in ["index.html", "impressum.html", "datenschutz.html"]:
        shutil.copy2(os.path.join(BASIS, name), ziel)
    for ordner in ["css", "js", "bilder", "dokumente"]:
        if os.path.isdir(os.path.join(BASIS, ordner)):
            shutil.copytree(os.path.join(BASIS, ordner), os.path.join(ziel, ordner))
    for ordner, quelle in (("bilder", BILDER), ("dokumente", DOKUMENTE)):
        if AUF_STICK and os.path.isdir(quelle):
            shutil.copytree(quelle, os.path.join(ziel, ordner), dirs_exist_ok=True)
    fotos = []
    for a in alben_lesen():
        for b in a["bilder"]:
            zo = os.path.join(ziel, "fotos", a["ordner"]) if a["ordner"] else os.path.join(ziel, "fotos")
            os.makedirs(zo, exist_ok=True)
            shutil.copy2(os.path.join(FOTOS, a["ordner"], b), zo)
            u = foto_url(a["ordner"], b)
            fotos.append({"datum": a["datum"], "album": a["album"], "gross": u, "klein": u,
                          "text": a["texte"].get(b, ""), "albumLink": ""})
    # Nur freigegebene öffentliche Vereinsfelder exportieren. Keine Admin-Zugangsdaten.
    oeffentliche_felder = {"name", "untertitel", "adresse", "plzOrt", "telefon", "email", "mitgliedsbeitrag", "trainingszeiten", "facebook", "wetterOrt", "wetterLat", "wetterLon"}
    verein = {k: v for k, v in d["verein"].items() if k in oeffentliche_felder}
    verein["googleTabelleId"] = ""
    verein.setdefault("name", "ESV Grein")
    inhalt = {"verein": verein, "regelWochen": 4, "fotos": fotos}
    d = oeffentlich(d)
    for k in LISTEN:
        inhalt[k] = d[k]
    with open(os.path.join(ziel, "js", "daten.js"), "w", encoding="utf-8") as f:
        f.write("/* Automatisch erzeugt am " + datetime.now().strftime("%d.%m.%Y %H:%M") + " */\n")
        f.write("window.ESV = " + json.dumps(inhalt, ensure_ascii=False, indent=1) + ";\n")
    zip_basis = os.path.join(EXPORT, "esv-grein-online")
    shutil.make_archive(zip_basis, "zip", EXPORT, "esv-grein-online")
    return ziel, zip_basis + ".zip", len(fotos)


def ordner_oeffnen(pfad):
    try:
        if sys.platform.startswith("win"):
            os.startfile(pfad)  # noqa
        elif sys.platform == "darwin":
            os.system('open "%s"' % pfad)
        elif os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
            os.system('xdg-open "%s" >/dev/null 2>&1 &' % pfad)
        else:
            return False
        return True
    except Exception:
        return False


def kann_ordner_oeffnen():
    return sys.platform.startswith("win") or sys.platform == "darwin" or bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def eigene_adressen():
    ips = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        ips.append(s.getsockname()[0])
        s.close()
    except OSError:
        pass
    return ips


# ---------------------------------------------------------------- HTTP
class Handler(SimpleHTTPRequestHandler):
    server_version = "ESV-Grein"
    sys_version = ""

    def __init__(self, *a, **kw):
        super().__init__(*a, directory=BASIS, **kw)

    def log_message(self, fmt, *args):
        pass

    # Fotos, hochgeladene Bilder und Dokumente kommen vom Datenort (USB-Stick)
    def translate_path(self, path):
        standard = super().translate_path(path)
        rel = os.path.relpath(standard, BASIS)
        teile = rel.split(os.sep)
        if teile[0] == "fotos":
            return os.path.join(DATENORT, rel)
        if teile[0] in ("bilder", "dokumente") and AUF_STICK:
            kandidat = os.path.join(DATENORT, rel)
            if os.path.exists(kandidat):
                return kandidat
        return standard

    def list_directory(self, path):  # keine Ordnerlisten
        self.send_error(404)
        return None

    def end_headers(self):
        if self.path.startswith("/fotos/"):
            self.send_header("Cache-Control", "public, max-age=604800")
        else:
            self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        super().end_headers()

    def antwort(self, wert, code=200):
        body = json.dumps(wert, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def fehler(self, text, code=400):
        self.antwort({"ok": False, "fehler": text}, code)

    # ---- Zugriffsschutz
    def ueber_internet(self):
        """Anfrage kam über den Cloudflare-Tunnel (also aus dem Internet)?"""
        return self.client_address[0] in ("127.0.0.1", "::1") and bool(self.headers.get("CF-Connecting-IP"))

    def client_ip(self):
        return self.headers.get("CF-Connecting-IP") if self.ueber_internet() else self.client_address[0]

    def gesperrt(self):
        e = FEHLVERSUCHE.get(self.client_ip())
        return bool(e and e[1] > time.time())

    def passwort_ok(self, gegeben):
        ip = self.client_ip()
        if self.gesperrt():
            return "gesperrt"
        if passwort_pruefen(gegeben):
            FEHLVERSUCHE.pop(ip, None)
            return "ok"
        e = FEHLVERSUCHE.setdefault(ip, [0, 0])
        e[0] += 1
        if e[0] >= MAX_FEHLVERSUCHE:
            e[0], e[1] = 0, time.time() + SPERRZEIT
        time.sleep(1)
        return "falsch"

    def fern_erlaubt(self):
        """Aus dem Internet nur mit sicherem Passwort (mind. 8 Zeichen)."""
        return not self.ueber_internet() or (not ersteinrichtung() and passwort_laenge() >= 8)

    def sitzung(self):
        tok = self.headers.get("X-Token", "")
        s = SITZUNGEN.get(tok)
        if not s or s["bis"] < time.time():
            SITZUNGEN.pop(tok, None)
            return None
        s["bis"] = time.time() + SITZUNG_LEERLAUF
        return s

    def do_GET(self):
        p = urlparse(self.path)
        pfad = unquote(p.path)
        if pfad == "/api/daten":
            d = oeffentlich(daten_lesen())
            d["fotos"] = fotos_liste()
            d["esvLokal"] = True
            if not self.ueber_internet():  # für den QR-Code „Am Handy ansehen“
                port = "" if PORT == 80 else ":%d" % PORT
                d["lokaleAdressen"] = ["http://%s%s/" % (ip, port) for ip in eigene_adressen()]
            return self.antwort(d)
        if pfad.startswith("/api/"):
            if pfad.startswith("/api/admin/"):
                if not self.sitzung():
                    return self.fehler("Sitzung abgelaufen – bitte neu anmelden.", 403)
                if pfad == "/api/admin/daten":
                    d = daten_lesen()
                    d.pop("albumTexte", None)
                    d["_rev"] = int(d.get("_rev", 0))
                    return self.antwort(d)
                if pfad == "/api/admin/protokoll":
                    return self.antwort({"ok": True, "eintraege": protokoll_lesen()})
                if pfad == "/api/admin/alben":
                    return self.antwort({"ok": True, "alben": alben_lesen()})
                if pfad == "/api/admin/status":
                    try:
                        du = shutil.disk_usage(DATENORT)
                        frei, gesamt = round(du.free / 1e9, 1), round(du.total / 1e9, 1)
                    except OSError:
                        frei = gesamt = None
                    return self.antwort({"ok": True, "aufStick": AUF_STICK, "speicherort": DATENORT, "freiGB": frei,
                                         "gesamtGB": gesamt, "ordnerOeffnen": kann_ordner_oeffnen(),
                                         "ueberInternet": self.ueber_internet(), "version": VERSION,
                                         "rechner": socket.gethostname(), "ersteinrichtung": ersteinrichtung(),
                                         "sichererFernzugriff": not ersteinrichtung() and passwort_laenge() >= 8})
            return self.fehler("unbekannt", 404)
        if not self.statisch_erlaubt(pfad):
            return self.fehler("nicht gefunden", 404)
        return super().do_GET()

    @staticmethod
    def statisch_erlaubt(pfad):
        """nur erlaubte Dateitypen, keine versteckten/internen Pfade"""
        teile = [t for t in pfad.split("/") if t]
        return pfad == "/" or (pfad.lower().endswith(ERLAUBT) and not any(t.startswith((".", "_")) for t in teile))

    def do_HEAD(self):
        if not self.statisch_erlaubt(unquote(urlparse(self.path).path)):
            self.send_error(404)
            return
        return super().do_HEAD()

    def do_POST(self):
        p = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(p.query).items()}
        try:
            laenge = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            laenge = -1
        if laenge < 0:
            return self.fehler("ungültige Anfrage")
        if laenge > MAX_UPLOAD:
            return self.fehler("Datei zu groß")
        roh = self.rfile.read(laenge) if laenge else b""

        if p.path == "/api/admin/anmelden":
            try:
                w = json.loads(roh or b"{}")
                gegeben, name = str(w.get("pin", "")), sauber(w.get("name", ""), 40)
            except ValueError:
                gegeben, name = "", ""
            pr = self.passwort_ok(gegeben)
            if pr == "gesperrt":
                return self.fehler("Zu viele Fehlversuche – bitte 15 Minuten warten.", 429)
            if pr != "ok":
                return self.fehler("PIN falsch", 403)
            if not self.fern_erlaubt():
                return self.fehler("Fernzugriff gesperrt: Bitte zuerst vor Ort in der Halle ein eigenes Passwort (mindestens 8 Zeichen) vergeben.", 403)
            for t in [t for t, s in SITZUNGEN.items() if s["bis"] < time.time()]:
                SITZUNGEN.pop(t, None)
            token = secrets.token_urlsafe(32)
            SITZUNGEN[token] = {"bis": time.time() + SITZUNG_LEERLAUF, "name": name}
            protokoll(name, "angemeldet" + (" (Fernzugriff)" if self.ueber_internet() else ""))
            return self.antwort({"ok": True, "token": token, "ersteinrichtung": ersteinrichtung()})

        if not p.path.startswith("/api/admin/"):
            return self.fehler("unbekannte Aktion", 404)
        sitzung = self.sitzung()
        if not sitzung:
            return self.fehler("Sitzung abgelaufen – bitte neu anmelden.", 403)
        if not self.fern_erlaubt():
            return self.fehler("Fernzugriff gesperrt (kein sicheres Passwort).", 403)
        aktion = p.path[len("/api/admin/"):]
        wer = sitzung.get("name", "")
        if ersteinrichtung() and aktion not in ("pin", "abmelden"):
            return self.antwort({"ok": False, "fehler": "Bitte zuerst ein eigenes Passwort festlegen.", "ersteinrichtung": True}, 403)
        try:
            if aktion == "abmelden":
                SITZUNGEN.pop(self.headers.get("X-Token", ""), None)
                return self.antwort({"ok": True})

            if aktion == "speichern":
                w = json.loads(roh.decode("utf-8"))
                rev = w.pop("_rev", None)
                text = w.pop("_aenderung", "")
                try:
                    d = daten_speichern(w, rev)
                except Konflikt:
                    return self.fehler("Inzwischen hat jemand anderer etwas gespeichert. Die Daten werden neu geladen – bitte die letzte Eingabe wiederholen.", 409)
                if text:
                    protokoll(wer, text)
                return self.antwort({"ok": True, "gespeichert": datetime.now().strftime("%H:%M:%S"), "_rev": d.get("_rev", 0)})

            if aktion in ("beispiel-laden", "beispiel-entfernen"):
                d = daten_lesen()
                neu = {}
                for k in BEISPIELDATEN:
                    ohne = [x for x in d.get(k, []) if not (isinstance(x, dict) and x.get("beispiel"))]
                    if aktion == "beispiel-laden":
                        ohne += [dict(x, beispiel=True) for x in BEISPIELDATEN[k]]
                    neu[k] = ohne
                d = daten_speichern(neu)
                protokoll(wer, "Beispieldaten geladen" if aktion == "beispiel-laden" else "Beispieldaten entfernt")
                return self.antwort({"ok": True, "_rev": d.get("_rev", 0)})

            if aktion == "protokoll":
                protokoll(wer, json.loads(roh.decode("utf-8")).get("text", ""))
                return self.antwort({"ok": True})

            if aktion == "pin":
                neu = str(json.loads(roh.decode("utf-8")).get("pin", "")).strip()
                if len(neu) < 8 or len(neu) > 60:
                    return self.fehler("Das Passwort muss mindestens 8 Zeichen haben.")
                if neu.lower() in ("12345678", "passwort", "password", "esvgrein", "esv-grein", "11111111"):
                    return self.fehler("Dieses Passwort ist zu leicht zu erraten. Bitte ein anderes wählen.")
                passwort_setzen(neu)
                protokoll(wer, "Passwort geändert")
                return self.antwort({"ok": True, "fernzugriff": True})

            if aktion == "album":
                w = json.loads(roh.decode("utf-8"))
                name = sauber(w.get("name", ""))
                datum = w.get("datum", "")
                if not name:
                    return self.fehler("Bitte einen Namen für das Album eingeben.")
                ordner = sauber((datum + " " if re.fullmatch(r"\d{4}-\d{2}-\d{2}", datum or "") else "") + name, 100)
                os.makedirs(im_fotoordner(ordner), exist_ok=True)
                protokoll(wer, "Fotoalbum angelegt: " + ordner)
                return self.antwort({"ok": True, "ordner": ordner})

            if aktion in ("foto", "bild") and not ist_bilddatei(roh):
                return self.fehler("Die Datei ist kein unterstütztes Bild (JPG, PNG, GIF oder WebP).")

            if aktion == "foto":
                ordner = sauber(q.get("ordner", ""), 100)
                datei = sauber(q.get("name", "foto.jpg"))
                if not datei.lower().endswith(BILDTYPEN):
                    datei += ".jpg"
                pfad = im_fotoordner(ordner, datei) if ordner else im_fotoordner(datei)
                basis, endung = os.path.splitext(pfad); n = 2
                while os.path.exists(pfad):
                    pfad = "%s-%d%s" % (basis, n, endung); n += 1
                os.makedirs(os.path.dirname(pfad), exist_ok=True)
                with open(pfad, "wb") as f:
                    f.write(roh); f.flush(); os.fsync(f.fileno())
                return self.antwort({"ok": True, "datei": os.path.basename(pfad)})

            if aktion == "bild":  # Titelbild / Logo / Bild zu einer Neuigkeit
                art = q.get("art", "")
                ziel_ordner = BILDER if AUF_STICK else os.path.join(BASIS, "bilder")
                unterordner = {"neuigkeit": "neuigkeiten", "vorstand": "vorstand"}.get(art)
                if unterordner:
                    ordner = os.path.join(ziel_ordner, unterordner)
                    os.makedirs(ordner, exist_ok=True)
                    name = datetime.now().strftime("%Y%m%d-%H%M%S-%f") + ".jpg"
                    with open(os.path.join(ordner, name), "wb") as f:
                        f.write(roh); f.flush(); os.fsync(f.fileno())
                    return self.antwort({"ok": True, "pfad": "bilder/" + unterordner + "/" + name})
                ziel = {"titelbild": "vereinsheim.jpg", "logo": "logo.png"}.get(art)
                if not ziel:
                    return self.fehler("unbekannt")
                os.makedirs(ziel_ordner, exist_ok=True)
                pfad = os.path.join(ziel_ordner, ziel)
                if os.path.exists(pfad):
                    shutil.copy2(pfad, pfad + ".alt")
                with open(pfad, "wb") as f:
                    f.write(roh); f.flush(); os.fsync(f.fileno())
                return self.antwort({"ok": True})

            if aktion == "foto-loeschen":
                w = json.loads(roh.decode("utf-8"))
                ordner, datei = w.get("ordner", ""), w.get("datei", "")
                quelle = im_fotoordner(ordner, datei) if datei else im_fotoordner(ordner)
                if not os.path.exists(quelle) or os.path.abspath(quelle) == os.path.abspath(FOTOS):
                    return self.fehler("nicht gefunden", 404)
                os.makedirs(PAPIERKORB, exist_ok=True)
                ziel = os.path.join(PAPIERKORB, datetime.now().strftime("%Y%m%d-%H%M%S-") + (ordner + "_" if datei else "") + os.path.basename(quelle))
                shutil.move(quelle, ziel)
                protokoll(wer, ("Foto gelöscht: " + ordner + "/" + datei) if datei else ("Fotoalbum gelöscht: " + ordner))
                return self.antwort({"ok": True})

            if aktion == "fototext":
                w = json.loads(roh.decode("utf-8"))
                t = daten_lesen().get("albumTexte", {})
                t.setdefault(w.get("ordner", ""), {})[w.get("datei", "")] = str(w.get("text", ""))[:200]
                daten_speichern({"albumTexte": t})
                return self.antwort({"ok": True})

            if aktion == "ordner-oeffnen":
                ordner = q.get("ordner", "")
                pfad = im_fotoordner(ordner) if ordner else FOTOS
                os.makedirs(pfad, exist_ok=True)
                return self.antwort({"ok": ordner_oeffnen(pfad)})

            if aktion == "export":
                ordner, zipdatei, n = export_erstellen()
                protokoll(wer, "Export für die Online-Webseite erstellt")
                ordner_oeffnen(EXPORT)
                return self.antwort({"ok": True, "ordner": ordner, "zip": zipdatei, "fotos": n})
        except ValueError as e:
            return self.fehler(str(e))
        except OSError as e:
            return self.fehler("Dateifehler: " + str(e), 500)
        return self.fehler("unbekannte Aktion", 404)


def main():
    netz = "--netzwerk" in sys.argv
    if AUF_STICK and not os.path.exists(MARKER):
        print("FEHLER: Daten-Stick nicht gefunden (%s fehlt)." % MARKER)
        print("Ist der USB-Stick „ESV-DATEN“ angesteckt? Danach: sudo mount -a && sudo systemctl restart esv-grein")
        sys.exit(3)
    for ordner in (DATA, FOTOS):
        os.makedirs(ordner, exist_ok=True)
    if AUF_STICK:
        for ordner in (BILDER, DOKUMENTE):
            os.makedirs(ordner, exist_ok=True)
    if not os.path.exists(DATEN):
        json_schreiben(DATEN, START_DATEN)
    mimetypes.add_type("text/javascript", ".js")
    adresse = ("0.0.0.0" if netz else "127.0.0.1", PORT)
    try:
        server = ThreadingHTTPServer(adresse, Handler)
    except OSError:
        print("Die Webseite läuft bereits (oder Port %d ist belegt)." % PORT)
        if "--kein-browser" not in sys.argv:
            webbrowser.open("http://localhost:%d/" % PORT)
            time.sleep(3)
        sys.exit(1)
    url = "http://localhost%s/" % ("" if PORT == 80 else ":%d" % PORT)
    print("=" * 64)
    print(" ESV Grein – Webseite läuft  (Version %s)" % VERSION)
    print(" Webseite:    " + url)
    print(" Verwaltung:  " + url + "verwaltung.html")
    print(" Daten:       " + DATENORT + ("  (USB-Stick)" if AUF_STICK else ""))
    if netz:
        for ip in eigene_adressen():
            print(" Im Netzwerk: http://%s%s/" % (ip, "" if PORT == 80 else ":%d" % PORT))
    print("=" * 64)
    sys.stdout.flush()
    if "--kein-browser" not in sys.argv:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
