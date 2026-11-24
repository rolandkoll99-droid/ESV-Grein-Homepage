/**
 * ESV Grein – Fotos automatisch aus Google-Drive-Ordnern übernehmen
 * ---------------------------------------------------------------
 * Einmal in die Google-Tabelle einfügen: Erweiterungen → Apps Script
 * (Anleitung: ANLEITUNG.md, Punkt 5b).
 *
 * So funktioniert es:
 *  - Im Blatt "Verein" steht bei "Foto-Ordner-Link" der Link zum Hauptordner,
 *    z. B. "ESV Grein Webseite Fotos".
 *  - Darin pro Veranstaltung ein Unterordner, z. B.
 *        2026-07-17 Mix Rechberg 2026
 *        24.04.2026 Frühlingsturnier Dimbach
 *        Training Sommer            (ohne Datum -> Erstelldatum des Ordners)
 *  - Das Skript schreibt alle Fotos ins Blatt "Fotos" (Spalte Quelle = "Ordner").
 *    Von Hand eingetragene Zeilen (Quelle leer) bleiben unverändert.
 *  - Läuft stündlich automatisch oder über das Menü "ESV Grein".
 */

var BLATT_FOTOS = 'Fotos';
var BLATT_VEREIN = 'Verein';
var KOPF = ['Datum', 'Album', 'Bild-Link', 'Beschreibung', 'Album-Link', 'Quelle'];
var QUELLE = 'Ordner';
var MAX_FOTOS_PRO_ALBUM = 60;

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('ESV Grein')
    .addItem('Fotos jetzt aktualisieren', 'fotosAktualisierenMitMeldung')
    .addItem('Automatik einschalten (stündlich)', 'automatikEinschalten')
    .addItem('Automatik ausschalten', 'automatikAusschalten')
    .addToUi();
}

function fotosAktualisierenMitMeldung() {
  var ergebnis = fotosAktualisieren();
  SpreadsheetApp.getUi().alert('Fotos aktualisiert',
    ergebnis.fotos + ' Fotos in ' + ergebnis.alben + ' Alben übernommen.' +
    (ergebnis.hinweis ? '\n\n' + ergebnis.hinweis : ''),
    SpreadsheetApp.getUi().ButtonSet.OK);
}

function fotosAktualisieren() {
  var ss = SpreadsheetApp.getActive();
  var haupt = hauptordnerFinden_(ss);
  var hinweis = '';

  // Freigabe prüfen: die Webseite kann nur öffentlich lesbare Fotos anzeigen
  try {
    var zugriff = haupt.getSharingAccess();
    if (zugriff !== DriveApp.Access.ANYONE_WITH_LINK && zugriff !== DriveApp.Access.ANYONE) {
      hinweis = 'Achtung: Der Foto-Ordner ist nicht für „Jeder mit dem Link“ freigegeben – ' +
        'die Fotos werden auf der Webseite nicht angezeigt.';
    }
  } catch (e) { /* Prüfung nicht möglich – ignorieren */ }

  var neu = [];
  var albenZahl = 0;

  // Fotos direkt im Hauptordner -> Album "Allgemein"
  var lose = fotosAusOrdner_(haupt);
  if (lose.length) {
    albenZahl++;
    lose.forEach(function (f) { neu.push([f.datum, 'Allgemein', f.link, f.text, '', QUELLE]); });
  }

  // Unterordner = Alben
  var ordner = haupt.getFolders();
  while (ordner.hasNext()) {
    var o = ordner.next();
    var info = ordnerName_(o.getName(), o.getDateCreated());
    var fotos = fotosAusOrdner_(o).slice(0, MAX_FOTOS_PRO_ALBUM);
    if (!fotos.length) continue;
    albenZahl++;
    fotos.forEach(function (f) {
      neu.push([info.datum, info.album, f.link, f.text, o.getUrl(), QUELLE]);
    });
  }

  // Blatt vorbereiten, Handeinträge behalten
  var blatt = ss.getSheetByName(BLATT_FOTOS) || ss.insertSheet(BLATT_FOTOS);
  blatt.getRange(1, 1, 1, KOPF.length).setValues([KOPF]).setFontWeight('bold');
  var letzte = blatt.getLastRow();
  var behalten = [];
  if (letzte > 1) {
    blatt.getRange(2, 1, letzte - 1, KOPF.length).getValues().forEach(function (z) {
      var leer = z.every(function (w) { return w === '' || w === null; });
      if (!leer && String(z[5]) !== QUELLE) behalten.push(z);
    });
    blatt.getRange(2, 1, letzte - 1, KOPF.length).clearContent();
  }
  var alle = behalten.concat(neu);
  if (alle.length) {
    blatt.getRange(2, 1, alle.length, KOPF.length).setValues(alle);
    blatt.getRange(2, 1, alle.length, 1).setNumberFormat('dd.MM.yyyy');
  }
  return { fotos: neu.length, alben: albenZahl, hinweis: hinweis };
}

/* ---------- Hilfsfunktionen ---------- */

function hauptordnerFinden_(ss) {
  var verein = ss.getSheetByName(BLATT_VEREIN);
  if (!verein) throw new Error('Blatt „Verein“ fehlt.');
  var werte = verein.getDataRange().getValues();
  for (var i = 0; i < werte.length; i++) {
    var feld = String(werte[i][0]).toLowerCase().replace(/[^a-z]/g, '');
    if (feld === 'fotoordnerlink') {
      var link = String(werte[i][1] || '');
      var m = link.match(/folders\/([\w-]{10,})/) || link.match(/[?&]id=([\w-]{10,})/);
      if (!m) throw new Error('Im Blatt „Verein“ bei „Foto-Ordner-Link“ steht kein gültiger Ordner-Link.');
      return DriveApp.getFolderById(m[1]);
    }
  }
  throw new Error('Im Blatt „Verein“ fehlt die Zeile „Foto-Ordner-Link“.');
}

// "2026-07-17 Mix Rechberg" / "17.07.2026 Mix Rechberg" / "Mix Rechberg"
function ordnerName_(name, erstellt) {
  var m;
  if ((m = name.match(/^\s*(\d{4})-(\d{1,2})-(\d{1,2})[\s_\-–]*(.*)$/))) {
    return { datum: new Date(+m[1], +m[2] - 1, +m[3]), album: m[4].trim() || name };
  }
  if ((m = name.match(/^\s*(\d{1,2})\.(\d{1,2})\.(\d{2,4})[\s_\-–]*(.*)$/))) {
    var j = +m[3] < 100 ? 2000 + +m[3] : +m[3];
    return { datum: new Date(j, +m[2] - 1, +m[1]), album: m[4].trim() || name };
  }
  return { datum: erstellt, album: name.trim() };
}

function fotosAusOrdner_(ordner) {
  var liste = [];
  var dateien = ordner.getFiles();
  while (dateien.hasNext()) {
    var d = dateien.next();
    if (String(d.getMimeType()).indexOf('image/') !== 0) continue; // nur Bilder
    liste.push({
      name: d.getName(),
      link: 'https://drive.google.com/file/d/' + d.getId() + '/view',
      text: d.getDescription() || '',
      datum: d.getDateCreated()
    });
  }
  liste.sort(function (a, b) { return a.name.localeCompare(b.name, 'de', { numeric: true }); });
  return liste;
}

function automatikEinschalten() {
  automatikAusschalten();
  ScriptApp.newTrigger('fotosAktualisieren').timeBased().everyHours(1).create();
  fotosAktualisieren();
  SpreadsheetApp.getUi().alert('Automatik ist eingeschaltet: Die Fotos werden jede Stunde aktualisiert.');
}

function automatikAusschalten() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'fotosAktualisieren') ScriptApp.deleteTrigger(t);
  });
}
