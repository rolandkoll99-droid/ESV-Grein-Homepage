/* =====================================================================
   ESV GREIN – GRUNDEINSTELLUNGEN UND ERSATZDATEN
   ---------------------------------------------------------------------
   Termine, Ergebnisse usw. werden im Normalfall in der GOOGLE-TABELLE
   gepflegt (siehe ANLEITUNG). Dazu unten bei "googleTabelleId" die ID
   der Tabelle eintragen – das ist nur EINMAL nötig.

   Die Listen in dieser Datei werden nur verwendet, wenn keine Tabelle
   eingerichtet ist oder sie nicht erreichbar ist.

   Regeln:
   - Datum immer im Format "JJJJ-MM-TT", z. B. "2026-11-14"
   - Texte in Anführungszeichen "..."
   - Nach jedem Eintrag ein Komma, außer beim letzten
   - Was in [eckigen Klammern] steht, bitte ersetzen
   ===================================================================== */

window.ESV = {

  /* ---------- Vereinsdaten ---------- */
  verein: {
    // ID der Google-Tabelle: der lange Teil der Adresse zwischen /d/ und /edit
    // z. B. https://docs.google.com/spreadsheets/d/1AbC...XyZ/edit  ->  "1AbC...XyZ"
    googleTabelleId: "1rU-i2-Xa2wXp14xaiQcz3mx8cChRfsdEIW96wivYP9g",

    name: "ESV Grein",
    untertitel: "Eisstocksport an der Donau",
    adresse: "[Straße Hausnummer]",
    plzOrt: "4360 Grein",
    telefon: "[Telefonnummer]",
    email: "[E-Mail-Adresse]",
    // Trainingszeiten-Text wird automatisch aus "regelTraining" (unten) erzeugt.
    // Nur ausfüllen, wenn ein eigener Text angezeigt werden soll.
    trainingszeiten: "",
    mitgliedsbeitrag: "[Betrag] € pro Jahr",

    // Link zur Facebook-Seite (Button auf der Webseite)
    facebook: "https://www.facebook.com/share/19qc47PZg9/",

    // Für die eingebettete Beitragsliste: die "echte" Seitenadresse,
    // z. B. "https://www.facebook.com/esvgrein" (siehe ANLEITUNG).
    // Leer lassen = nur Button, keine eingebetteten Beiträge.
    facebookSeite: "",

    // Optional: öffentliche Google-Kalender-ID (siehe ANLEITUNG).
    // Wenn ausgefüllt, wird der Google-Kalender zusätzlich angezeigt.
    googleKalenderId: "",

    // Link zum Anmeldeformular (PDF im Ordner "dokumente")
    anmeldeformular: "dokumente/anmeldeformular.pdf",

    // Link zur Anmeldung Probetraining (PDF im Ordner "dokumente")
    probetraining: "dokumente/probetraining.pdf"
  },

  /* ---------- Regelmäßiges Training (automatisch) ----------
     Diese Trainings erscheinen jede Woche automatisch im Kalender und
     als "Nächster Termin". An Tagen mit einem eigenen Termin oder einer
     Veranstaltung (siehe unten) entfällt das Training automatisch.
     wochentag: 1 = Montag, 2 = Dienstag, ... 5 = Freitag, 6 = Samstag, 7 = Sonntag
     zeit: "HH:MM" oder "" (ohne Uhrzeit)
  */
  regelTraining: [
    { wochentag: 1, zeit: "", titel: "Seniorentraining", ort: "Stockbahn Grein" },
    { wochentag: 5, zeit: "18:00", titel: "Training", ort: "Stockbahn Grein" }
  ],

  // Wie viele Wochen im Voraus die Trainings im Kalender stehen
  regelWochen: 4,

  /* Tage OHNE Training (Feiertage, Bahn gesperrt, Urlaub ...)
     Beispiel: trainingsfrei: ["2026-12-25", "2027-01-01"],
  */
  trainingsfrei: [
    "2026-12-25", "2027-01-01"
  ],

  /* ---------- Neuigkeiten ----------
     wichtig: true = oben angeheftet
  */
  neuigkeiten: [
    { datum: "2026-10-28", titel: "Unsere neue Webseite ist online", text: "Ab sofort findet ihr hier alle Termine, Ergebnisse und Fotos des ESV Grein.", bild: "", wichtig: false }
  ],

  /* ---------- Termine ----------
     Eigene Termine (Meisterschaft, Turnier, Fest, Sondertraining).
     Fällt ein Termin auf einen Trainingstag, entfällt dort das Regeltraining.
     art: "training" | "meisterschaft" | "turnier" | "fest"
     Vergangene Termine werden automatisch ausgeblendet.
     Beispiel:
     { datum: "2026-11-14", zeit: "18:00", titel: "Vereinstraining", ort: "Stockbahn Grein", art: "training" },
  */
  termine: [
  ],

  /* ---------- Ergebnisse ----------
     platz: Zahl, teilnehmer: Anzahl Mannschaften (oder null, wenn unbekannt)
     pdf: Link zur Ergebnisliste (optional, z. B. "dokumente/rechberg-2026.pdf")
  */
  ergebnisse: [
    { datum: "2026-07-17", bewerb: "Mix Rechberg 2026", ort: "Rechberg", mannschaft: "ÖTSU Grein", platz: 4, teilnehmer: 9, punkte: "8:8", saison: "Sommer 2026", pdf: "" },
    { datum: "2026-05-02", bewerb: "Vereinsturnier 2026 – Herrenturnier", ort: "Perg (ASKÖ Prinz Brunnenbau Perg)", mannschaft: "Union Grein", platz: 8, teilnehmer: null, punkte: "8:12", saison: "Sommer 2026", pdf: "" },
    { datum: "2026-04-24", bewerb: "Frühlingsturnier Dimbach", ort: "Stockhalle Dimbach", mannschaft: "Union Grein", platz: 1, teilnehmer: 7, punkte: "10:2", saison: "Sommer 2026", pdf: "" }
  ],

  /* ---------- Veranstaltungen ----------
     bild: z. B. "bilder/turnier.jpg" (optional)
     ausschreibung: Link zur Ausschreibung (optional)
     Beispiel:
     { datum: "2027-01-10", titel: "Ortsturnier Grein", text: "Für alle Vereine und Hobbymannschaften. Nenngeld [Betrag].", bild: "", ausschreibung: "dokumente/ausschreibung-ortsturnier.pdf" },
  */
  veranstaltungen: [
  ],

  /* ---------- Fotos ----------
     Normalerweise im Blatt "Fotos" der Google-Tabelle gepflegt.
     Beispiel: { datum: "2026-07-17", album: "Mix Rechberg 2026", gross: "bilder/galerie/rechberg1.jpg", text: "Siegerehrung" },
  */
  fotos: [
  ],

  /* ---------- Vorstand ----------
     Fotos und Namen nur mit Einwilligung der Personen veröffentlichen!
     foto: z. B. "bilder/vorstand/obmann.jpg" (optional)
  */
  vorstand: [
    { funktion: "Obmann", name: "[Name]", foto: "" },
    { funktion: "Obmann-Stellvertreter", name: "[Name]", foto: "" },
    { funktion: "Kassier", name: "[Name]", foto: "" },
    { funktion: "Schriftführer", name: "[Name]", foto: "" },
    { funktion: "Sportwart", name: "[Name]", foto: "" }
  ]
};
