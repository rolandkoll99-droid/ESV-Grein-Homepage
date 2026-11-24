# -*- coding: utf-8 -*-
"""Erzeugt Mitgliedsantrag und Probetraining-Anmeldung des ESV Grein als
ausfüllbare PDFs (am PC ausfüllbar ODER ausdrucken und per Hand ausfüllen).
Vereinsdaten unten in VEREIN anpassen und Skript erneut ausführen."""
import sys
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.pdfmetrics import stringWidth

VEREIN = {
    "adresse": "[Straße Hausnummer], 4360 Grein",
    "email": "[E-Mail-Adresse]",
    "telefon": "[Telefonnummer]",
    "zvr": "[ZVR-Zahl]",
    "iban": "[IBAN des Vereins]",
    "beitrag_aktiv": "[Betrag] €",
    "beitrag_unterstuetzend": "[Betrag] €",
    "beitrag_jugend": "[Betrag] €",
    "trainingszeiten": "[z. B. Dienstag und Freitag ab 18:00 Uhr]",
    "webseite": "rolandkoll99-droid.github.io/esv-grein",
}

BLAU = HexColor("#0F2A44")
BLAU_M = HexColor("#1F5A8A")
AKZENT = HexColor("#F2B544")
GRAU = HexColor("#4A5868")
LINIE = HexColor("#9AA8B6")
FELD = HexColor("#F3F6F9")
W, H = A4
RAND = 18 * mm
BREITE = W - 2 * RAND


class Formular:
    def __init__(self, datei, titel, untertitel):
        self.c = canvas.Canvas(datei, pagesize=A4)
        self.c.setTitle(f"ESV Grein – {titel}")
        self.c.setAuthor("ESV Grein")
        self.c.setSubject(titel)
        self.feldnr = 0
        self.kopf(titel, untertitel)
        self.y = H - 48 * mm

    # ---------- Grundelemente ----------
    def kopf(self, titel, untertitel):
        c = self.c
        c.setFillColor(BLAU)
        c.rect(0, H - 38 * mm, W, 38 * mm, stroke=0, fill=1)
        c.setFillColor(AKZENT)
        c.rect(0, H - 39.5 * mm, W, 1.5 * mm, stroke=0, fill=1)
        # einfaches Stock-Symbol
        x0, y0 = RAND + 7 * mm, H - 21 * mm
        c.setFillColor(AKZENT)
        c.ellipse(x0 - 7 * mm, y0 - 9 * mm, x0 + 7 * mm, y0 - 4 * mm, stroke=0, fill=1)
        c.setFillColor(white)
        c.roundRect(x0 - 1.1 * mm, y0 - 6 * mm, 2.2 * mm, 12 * mm, 1 * mm, stroke=0, fill=1)
        c.roundRect(x0 - 3.5 * mm, y0 + 4.5 * mm, 7 * mm, 2.8 * mm, 1.2 * mm, stroke=0, fill=1)
        c.setFont("Helvetica-Bold", 24)
        c.drawString(RAND + 19 * mm, H - 18 * mm, "ESV GREIN")
        c.setFont("Helvetica", 9.5)
        c.setFillColor(HexColor("#D6E3EE"))
        c.drawString(RAND + 19 * mm, H - 24 * mm, "Eisstocksport an der Donau · " + VEREIN["adresse"])
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 17)
        c.drawRightString(W - RAND, H - 18 * mm, titel)
        c.setFont("Helvetica", 9.5)
        c.setFillColor(HexColor("#D6E3EE"))
        c.drawRightString(W - RAND, H - 24 * mm, untertitel)

    def abschnitt(self, text):
        c = self.c
        self.y -= 3 * mm
        c.setFillColor(BLAU)
        c.setFont("Helvetica-Bold", 11.5)
        c.drawString(RAND, self.y, text.upper())
        c.setStrokeColor(AKZENT)
        c.setLineWidth(1.4)
        c.line(RAND, self.y - 2 * mm, RAND + stringWidth(text.upper(), "Helvetica-Bold", 11.5), self.y - 2 * mm)
        self.y -= 7 * mm

    def _name(self):
        self.feldnr += 1
        return f"f{self.feldnr}"

    def feld(self, x, breite, beschriftung, name=None, hoehe=8 * mm):
        """Beschriftung oben, darunter Feld mit Linie (druck- und ausfüllbar)."""
        c = self.c
        c.setFillColor(GRAU)
        c.setFont("Helvetica", 8)
        c.drawString(x, self.y, beschriftung)
        fy = self.y - 1.5 * mm - hoehe
        c.setFillColor(FELD)
        c.rect(x, fy, breite, hoehe, stroke=0, fill=1)
        c.setStrokeColor(LINIE)
        c.setLineWidth(0.8)
        c.line(x, fy, x + breite, fy)
        c.acroForm.textfield(name=name or self._name(), tooltip=beschriftung, x=x, y=fy, width=breite,
                             height=hoehe, borderWidth=0, fillColor=None, textColor=BLAU,
                             fontName="Helvetica", fontSize=10.5, forceBorder=False)
        return fy

    def zeile(self, felder, hoehe=8 * mm, abstand=4 * mm):
        """felder: Liste von (anteil, beschriftung)."""
        gesamt = sum(a for a, _ in felder)
        verfuegbar = BREITE - abstand * (len(felder) - 1)
        x = RAND
        for anteil, text in felder:
            b = verfuegbar * anteil / gesamt
            self.feld(x, b, text, hoehe=hoehe)
            x += b + abstand
        self.y -= hoehe + 7 * mm

    def kaestchen(self, x, y, text, groesse=4.2 * mm, fett=False, schrift=10):
        c = self.c
        c.setStrokeColor(BLAU)
        c.setLineWidth(0.9)
        c.setFillColor(white)
        c.rect(x, y - 1 * mm, groesse, groesse, stroke=1, fill=1)
        c.acroForm.checkbox(name=self._name(), tooltip=text, x=x, y=y - 1 * mm, size=groesse,
                            buttonStyle="check", borderWidth=0, fillColor=None, textColor=BLAU,
                            forceBorder=False)
        c.setFillColor(BLAU if fett else HexColor("#1C2733"))
        c.setFont("Helvetica-Bold" if fett else "Helvetica", schrift)
        c.drawString(x + groesse + 2.5 * mm, y, text)

    def kaestchenreihe(self, texte, spalten=None):
        spalten = spalten or len(texte)
        sb = BREITE / spalten
        for i, t in enumerate(texte):
            if i and i % spalten == 0:
                self.y -= 7 * mm
            self.kaestchen(RAND + (i % spalten) * sb, self.y, t)
        self.y -= 9 * mm

    def absatz(self, html, groesse=8.8, farbe="#1C2733", x=None, breite=None, nachher=3 * mm):
        st = ParagraphStyle("p", fontName="Helvetica", fontSize=groesse, leading=groesse * 1.38,
                            textColor=HexColor(farbe))
        p = Paragraph(html, st)
        x = RAND if x is None else x
        breite = BREITE if breite is None else breite
        _, h = p.wrap(breite, 500)
        p.drawOn(self.c, x, self.y - h + groesse)
        self.y -= h + nachher
        return h

    def einwilligung(self, html, groesse=8.8):
        """Kästchen + mehrzeiliger Text."""
        k = 4.2 * mm
        self.c.setStrokeColor(BLAU)
        self.c.setFillColor(white)
        self.c.setLineWidth(0.9)
        self.c.rect(RAND, self.y - 1 * mm, k, k, stroke=1, fill=1)
        self.c.acroForm.checkbox(name=self._name(), tooltip="Einwilligung", x=RAND, y=self.y - 1 * mm,
                                 size=k, buttonStyle="check", borderWidth=0, fillColor=None,
                                 textColor=BLAU, forceBorder=False)
        self.absatz(html, groesse=groesse, x=RAND + k + 3 * mm, breite=BREITE - k - 3 * mm, nachher=2.5 * mm)

    def unterschriften(self, links, rechts):
        b = (BREITE - 10 * mm) / 2
        self.y -= 10 * mm
        c = self.c
        for i, text in enumerate((links, rechts)):
            x = RAND + i * (b + 10 * mm)
            if i == 0:
                # Ort/Datum ausfüllbar
                c.acroForm.textfield(name=self._name(), tooltip=text, x=x, y=self.y, width=b,
                                     height=8 * mm, borderWidth=0, fillColor=None, textColor=BLAU,
                                     fontName="Helvetica", fontSize=10.5)
            c.setStrokeColor(BLAU)
            c.setLineWidth(0.9)
            c.line(x, self.y, x + b, self.y)
            c.setFillColor(GRAU)
            c.setFont("Helvetica", 8)
            c.drawString(x, self.y - 4 * mm, text)
        self.y -= 10 * mm

    def fuss(self, text):
        c = self.c
        c.setStrokeColor(HexColor("#D5DDE5"))
        c.setLineWidth(0.6)
        c.line(RAND, 14 * mm, W - RAND, 14 * mm)
        c.setFillColor(GRAU)
        c.setFont("Helvetica", 7.5)
        c.drawString(RAND, 10 * mm, text)
        c.drawRightString(W - RAND, 10 * mm, "ZVR " + VEREIN["zvr"])

    def vereinsbox(self, titel, felder, hoehe=24 * mm):
        c = self.c
        top = self.y
        c.setFillColor(FELD)
        c.setStrokeColor(HexColor("#C9D4DF"))
        c.setLineWidth(0.8)
        c.roundRect(RAND, top - hoehe, BREITE, hoehe, 2.5 * mm, stroke=1, fill=1)
        c.setFillColor(BLAU)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(RAND + 4 * mm, top - 5.5 * mm, titel)
        self.y = top - 11 * mm
        inner = BREITE - 8 * mm
        b = (inner - 4 * mm * (len(felder) - 1)) / len(felder)
        for i, t in enumerate(felder):
            x = RAND + 4 * mm + i * (b + 4 * mm)
            c.setFillColor(GRAU)
            c.setFont("Helvetica", 8)
            c.drawString(x, self.y, t)
            c.setStrokeColor(LINIE)
            c.line(x, self.y - 9 * mm, x + b, self.y - 9 * mm)
        self.y = top - hoehe - 4 * mm

    def speichern(self):
        self.c.showPage()
        self.c.save()


def mitgliedsantrag(datei):
    f = Formular(datei, "Antrag auf Mitgliedschaft", "Bitte in Blockschrift ausfüllen")

    f.abschnitt("Persönliche Daten")
    f.zeile([(1, "Vorname"), (1, "Nachname"), (0.6, "Geburtsdatum")])
    f.zeile([(2, "Straße, Hausnummer"), (0.6, "PLZ"), (1.2, "Ort")])
    f.zeile([(1, "Telefon / Handy"), (1.4, "E-Mail"), (0.6, "Mitglied ab (Datum)")])

    f.abschnitt("Art der Mitgliedschaft")
    f.kaestchen(RAND, f.y, "Aktives Mitglied", fett=True)
    f.c.setFont("Helvetica", 9); f.c.setFillColor(GRAU)
    f.c.drawRightString(W - RAND, f.y, "Jahresbeitrag " + VEREIN["beitrag_aktiv"])
    f.y -= 7 * mm
    f.kaestchen(RAND, f.y, "Unterstützendes Mitglied", fett=True)
    f.c.setFont("Helvetica", 9); f.c.setFillColor(GRAU)
    f.c.drawRightString(W - RAND, f.y, "Jahresbeitrag " + VEREIN["beitrag_unterstuetzend"])
    f.y -= 7 * mm
    f.kaestchen(RAND, f.y, "Jugendmitglied (unter 18 Jahre)", fett=True)
    f.c.setFont("Helvetica", 9); f.c.setFillColor(GRAU)
    f.c.drawRightString(W - RAND, f.y, "Jahresbeitrag " + VEREIN["beitrag_jugend"])
    f.y -= 7 * mm

    f.abschnitt("Mitgliedsbeitrag")
    f.absatz(f"Der Jahresbeitrag ist nach Aufnahme bzw. jeweils zu Jahresbeginn fällig und wird "
             f"überwiesen auf das Vereinskonto <b>IBAN {VEREIN['iban']}</b> "
             f"(Verwendungszweck: Mitgliedsbeitrag + Name).", nachher=4 * mm)

    f.abschnitt("Erklärung und Datenschutz")
    f.absatz("Ich beantrage die Aufnahme in den ESV Grein und erkenne die Statuten des Vereins an. "
             "Der Austritt ist jeweils zum Jahresende schriftlich möglich. Meine Daten werden zur "
             "Mitgliederverwaltung, für den Spiel- und Wettkampfbetrieb sowie für die Meldung an den "
             "zuständigen Fachverband verarbeitet (Art. 6 Abs. 1 lit. b DSGVO). Die Datenschutzerklärung "
             f"ist unter {VEREIN['webseite']}/datenschutz.html abrufbar.", nachher=3 * mm)
    f.y += 1 * mm
    f.absatz("<b>Freiwillig</b> – bitte ankreuzen, jederzeit widerrufbar:", groesse=8.8, nachher=2.5 * mm)
    f.einwilligung("Ich bin einverstanden, dass <b>Fotos</b> von mir, die bei Vereinsveranstaltungen entstehen, "
                   "auf der Webseite und der Facebook-Seite des ESV Grein veröffentlicht werden.")
    f.einwilligung("Ich bin einverstanden, dass mein <b>Name</b> in Mannschaftsaufstellungen und Ergebnislisten "
                   "auf der Webseite und der Facebook-Seite des ESV Grein genannt wird.")
    f.einwilligung("Ich möchte Vereinsinformationen per E-Mail bzw. WhatsApp erhalten.")

    f.y += 2 * mm
    f.unterschriften("Ort, Datum", "Unterschrift Antragsteller/in")
    f.absatz("Bei Minderjährigen zusätzlich:", groesse=8.5, farbe="#4A5868", nachher=0)
    f.y += 2 * mm
    f.unterschriften("Name Erziehungsberechtigte/r", "Unterschrift Erziehungsberechtigte/r")

    f.vereinsbox("Vom Verein auszufüllen", ["Aufgenommen am", "Mitgliedsnummer", "Unterschrift Obmann"],
                 hoehe=19 * mm)
    f.fuss("ESV Grein · " + VEREIN["adresse"] + " · " + VEREIN["email"] + " · " + VEREIN["telefon"])
    f.speichern()


def probetraining(datei):
    f = Formular(datei, "Anmeldung Probetraining", "Kostenlos und unverbindlich")

    f.absatz("Schön, dass du den Stocksport ausprobieren möchtest! Bitte fülle das Formular aus und gib es "
             "beim Training ab oder schick es uns per E-Mail an <b>" + VEREIN["email"] + "</b>. "
             "Trainingszeiten: <b>" + VEREIN["trainingszeiten"] + "</b>.", groesse=9.5, nachher=5 * mm)

    f.abschnitt("Deine Daten")
    f.zeile([(1, "Vorname"), (1, "Nachname"), (0.6, "Geburtsdatum")])
    f.zeile([(1, "Telefon / Handy"), (1.4, "E-Mail")])
    f.zeile([(1.4, "Wohnort"), (1, "Wunschtermin für das Probetraining")])

    f.abschnitt("Erfahrung im Stocksport")
    f.kaestchenreihe(["Noch nie gespielt", "Hobby / gelegentlich", "Früher im Verein"], spalten=3)

    f.abschnitt("Wie bist du auf uns aufmerksam geworden?")
    f.kaestchenreihe(["Freunde / Bekannte", "Facebook", "Webseite", "Veranstaltung"], spalten=4)
    f.zeile([(1, "Sonstiges")])

    f.abschnitt("Gut zu wissen")
    tipps = [
        "<b>Ausrüstung:</b> Sportschuhe mit flacher, sauberer Sohle und wetterfeste Kleidung. "
        "Stöcke stellt der Verein zur Verfügung.",
        "<b>Kosten:</b> Das Probetraining ist kostenlos und unverbindlich (bis zu [Anzahl] Termine).",
        "<b>Haftung:</b> Die Teilnahme erfolgt auf eigene Verantwortung. Bitte gib Bescheid, wenn "
        "gesundheitliche Einschränkungen bestehen, auf die wir achten sollen.",
    ]
    for t in tipps:
        f.c.setFillColor(AKZENT)
        f.c.circle(RAND + 1.3 * mm, f.y + 1.1 * mm, 1.1 * mm, stroke=0, fill=1)
        f.absatz(t, x=RAND + 5 * mm, breite=BREITE - 5 * mm, nachher=2 * mm)
    f.y -= 2 * mm

    f.abschnitt("Datenschutz")
    f.absatz("Deine Angaben verwenden wir nur zur Organisation des Probetrainings und zur Kontaktaufnahme. "
             "Trittst du dem Verein nicht bei, löschen wir sie spätestens 3 Monate nach dem letzten Training.",
             nachher=3 * mm)
    f.einwilligung("Freiwillig: Ich bin einverstanden, dass beim Probetraining entstandene <b>Fotos</b> von mir "
                   "auf der Webseite und der Facebook-Seite des ESV Grein veröffentlicht werden "
                   "(jederzeit widerrufbar).")

    f.unterschriften("Ort, Datum", "Unterschrift (bei Minderjährigen: Erziehungsberechtigte/r)")

    f.vereinsbox("Vom Verein auszufüllen", ["Probetraining am", "Betreut von", "Mitgliedsantrag ausgegeben"],
                 hoehe=22 * mm)
    f.fuss("ESV Grein · " + VEREIN["adresse"] + " · " + VEREIN["email"] + " · " + VEREIN["telefon"])
    f.speichern()


if __name__ == "__main__":
    ziel = sys.argv[1] if len(sys.argv) > 1 else "."
    mitgliedsantrag(f"{ziel}/anmeldeformular.pdf")
    probetraining(f"{ziel}/probetraining.pdf")
    print("fertig")
