/* =====================================================================
   ESV GREIN – Verwaltung auf GitHub Pages
   Läuft nur, wenn die Webseite auf GitHub Pages liegt (…github.io)
   oder unten bei ESV_GITHUB ein Repository eingetragen ist.
   Dann beantwortet diese Datei die Anfragen der Verwaltung (api/…)
   selbst und speichert über die GitHub-Schnittstelle direkt im
   Repository:  data/daten.json, bilder/…, fotos/<Album>/…
   Jede Änderung ist ein Eintrag in der GitHub-Versionsgeschichte
   (= Änderungsprotokoll, alles wiederherstellbar).
   Anmeldung: persönlicher GitHub-Schlüssel (Fine-grained Token,
   nur dieses Repository, Recht „Contents: Read and write“).
   ===================================================================== */
(function () {
  "use strict";

  // Nur bei eigener Domain nötig, z. B. { besitzer: "esvgrein", repo: "webseite", zweig: "main", pfad: "" }
  var EINSTELLUNG = window.ESV_GITHUB || null;

  var host = location.hostname.toLowerCase();
  if (!EINSTELLUNG && !/\.github\.io$/.test(host)) return; // PC / Pi: normale Verwaltung über server.py
  window.ESV_GITHUB_AKTIV = true;

  var API = "https://api.github.com";
  var VERSION = "2.4 GitHub";
  var DATEI = "data/daten.json";
  var SCHLUESSEL_SPEICHER = "esvGithubSchluessel";
  var LISTEN = ["neuigkeiten", "termine", "ergebnisse", "veranstaltungen", "regelTraining", "trainingsfrei", "vorstand"];
  var BILDTYPEN = /\.(jpe?g|png|gif|webp)$/i;

  /* ---------- Repository aus der Adresse ableiten ---------- */
  function repoAusAdresse() {
    if (EINSTELLUNG && EINSTELLUNG.besitzer && EINSTELLUNG.repo) return { besitzer: EINSTELLUNG.besitzer, repo: EINSTELLUNG.repo };
    var besitzer = host.replace(/\.github\.io$/, "");
    var erstes = location.pathname.split("/")[1] || "";
    var repo = erstes && erstes.indexOf(".") < 0 ? decodeURIComponent(erstes) : besitzer + ".github.io";
    return { besitzer: besitzer, repo: repo };
  }
  var REPO = repoAusAdresse();

  /* ---------- kleine Hilfen ---------- */
  function antwort(wert, status) {
    return new Response(JSON.stringify(wert), { status: status || 200, headers: { "Content-Type": "application/json" } });
  }
  function fehler(text, status) { return antwort({ ok: false, fehler: text }, status || 400); }
  function GitFehler(text, status) { var e = new Error(text); e.status = status; return e; }
  function jetzt() { var d = new Date(); return ("0" + d.getHours()).slice(-2) + ":" + ("0" + d.getMinutes()).slice(-2) + ":" + ("0" + d.getSeconds()).slice(-2); }
  function zeitDE(iso) {
    var d = new Date(iso); if (isNaN(d)) return "";
    function z(n) { return ("0" + n).slice(-2); }
    return z(d.getDate()) + "." + z(d.getMonth() + 1) + "." + d.getFullYear() + " " + z(d.getHours()) + ":" + z(d.getMinutes());
  }
  function sauber(name, max) {
    name = String(name || "").replace(/[^\wäöüÄÖÜß .\-()&,]/g, "").replace(/\s+/g, " ").trim().replace(/^[. ]+|[. ]+$/g, "");
    return name.slice(0, max || 80);
  }
  function textZuB64(text) {
    var bytes = new TextEncoder().encode(text), s = "";
    for (var i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
    return btoa(s);
  }
  function b64ZuText(b64) {
    var bin = atob(String(b64).replace(/\s/g, "")), bytes = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    return new TextDecoder().decode(bytes);
  }
  function blobZuB64(blob) {
    return blob.arrayBuffer().then(function (buf) {
      var bytes = new Uint8Array(buf), s = "";
      for (var i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
      return { b64: btoa(s), kopf: bytes.subarray(0, 12) };
    });
  }
  function istBild(k) {
    return (k[0] === 0xFF && k[1] === 0xD8 && k[2] === 0xFF) || (k[0] === 0x89 && k[1] === 0x50 && k[2] === 0x4E && k[3] === 0x47) ||
      (k[0] === 0x47 && k[1] === 0x49 && k[2] === 0x46) || (k[0] === 0x52 && k[1] === 0x49 && k[2] === 0x46 && k[3] === 0x46 && k[8] === 0x57 && k[9] === 0x45 && k[10] === 0x42 && k[11] === 0x50);
  }
  function kopie(o) { return JSON.parse(JSON.stringify(o)); }

  /* ---------- Vorschau frisch hochgeladener Bilder ----------
     GitHub Pages veröffentlicht neue Dateien erst nach 1–2 Minuten. Bis dahin zeigt die
     Verwaltung das Bild aus dem Speicher des Browsers an. */
  var VORSCHAU = {};
  function vorschauMerken(pfad, blob) { VORSCHAU[pfad] = URL.createObjectURL(blob); }
  function bildAustauschen(img) {
    var src = img.getAttribute("src"); if (!src || src.indexOf("blob:") === 0) return;
    var pfad; try { pfad = decodeURIComponent(src.split("?")[0]); } catch (e) { return; }
    if (VORSCHAU[pfad]) { img.src = VORSCHAU[pfad]; img.hidden = false; }
  }
  new MutationObserver(function (liste) {
    liste.forEach(function (m) {
      if (m.type === "attributes" && m.target.tagName === "IMG") bildAustauschen(m.target);
      (m.addedNodes || []).forEach(function (n) {
        if (n.nodeType !== 1) return;
        if (n.tagName === "IMG") bildAustauschen(n);
        if (n.querySelectorAll) n.querySelectorAll("img").forEach(bildAustauschen);
      });
    });
  }).observe(document.documentElement, { childList: true, subtree: true, attributes: true, attributeFilter: ["src"] });

  /* ---------- GitHub-Schnittstelle ---------- */
  var INFO = {}; // je Schlüssel: Promise { zweig, prefix, besitzer, repo }
  function gh(token, pfad, opt) {
    opt = opt || {};
    var kopf = { "Accept": "application/vnd.github+json", "Authorization": "Bearer " + token };
    if (opt.body) kopf["Content-Type"] = "application/json";
    return window.__esvFetch(API + pfad, { method: opt.method || "GET", headers: kopf, body: opt.body ? JSON.stringify(opt.body) : undefined, cache: "no-store" })
      .catch(function () { throw GitFehler("Keine Verbindung zu GitHub. Bitte Internetverbindung prüfen.", 503); })
      .then(function (r) {
        return r.text().then(function (t) {
          var j = null; try { j = t ? JSON.parse(t) : null; } catch (e) { /* kein JSON */ }
          if (!r.ok) {
            var meldung = (j && j.message) || ("GitHub-Fehler " + r.status);
            if (r.status === 401) meldung = "Der GitHub-Schlüssel ist ungültig oder abgelaufen. Bitte neu anmelden.";
            if (r.status === 403 && /rate limit/i.test(meldung)) meldung = "GitHub hat zu viele Anfragen gezählt. Bitte in ein paar Minuten erneut versuchen.";
            else if (r.status === 403) meldung = "Der GitHub-Schlüssel hat dafür keine Berechtigung (benötigt: Contents – Read and write).";
            throw GitFehler(meldung, r.status);
          }
          return j;
        });
      });
  }
  function repoPfad(info, rest) { return "/repos/" + encodeURIComponent(info.besitzer) + "/" + encodeURIComponent(info.repo) + rest; }
  function info(token) {
    if (!INFO[token]) {
      var basis = { besitzer: REPO.besitzer, repo: REPO.repo };
      INFO[token] = gh(token, repoPfad(basis, "")).then(function (r) {
        if (!r.permissions || !r.permissions.push) throw GitFehler("Dieser GitHub-Schlüssel darf im Repository „" + basis.repo + "“ nur lesen. Er braucht „Contents: Read and write“.", 403);
        var i = { besitzer: r.owner.login, repo: r.name, zweig: (EINSTELLUNG && EINSTELLUNG.zweig) || r.default_branch, prefix: "" };
        if (EINSTELLUNG && EINSTELLUNG.pfad != null) { i.prefix = String(EINSTELLUNG.pfad).replace(/^\/+|\/+$/g, ""); i.prefix = i.prefix ? i.prefix + "/" : ""; return i; }
        // Von welchem Zweig/Ordner veröffentlicht GitHub Pages? (braucht Leserecht „Pages“ – sonst Standard)
        return gh(token, repoPfad(i, "/pages")).then(function (p) {
          if (p && p.source) {
            if (p.source.branch) i.zweig = p.source.branch;
            var pf = String(p.source.path || "/").replace(/^\/+|\/+$/g, "");
            i.prefix = pf ? pf + "/" : "";
          }
          return i;
        }, function () { return i; });
      }, function (e) {
        delete INFO[token];
        if (e.status === 404) throw GitFehler("Kein Zugriff auf das Repository „" + basis.besitzer + "/" + basis.repo + "“. Der Schlüssel muss für genau dieses Repository erstellt sein.", 403);
        throw e;
      });
    }
    return INFO[token];
  }

  function datenLesen(token, i, ref) {
    return gh(token, repoPfad(i, "/contents/" + i.prefix + DATEI + "?ref=" + encodeURIComponent(ref || i.zweig))).then(function (j) {
      var d = JSON.parse(b64ZuText(j.content));
      return grundform(d);
    }, function (e) { if (e.status === 404) return grundform({}); throw e; });
  }
  function grundform(d) {
    d = d && typeof d === "object" ? d : {};
    d.verein = d.verein || {};
    LISTEN.forEach(function (k) { if (!Array.isArray(d[k])) d[k] = []; });
    d.albumTexte = d.albumTexte || {};
    d.fotoAlben = Array.isArray(d.fotoAlben) ? d.fotoAlben : [];
    d._rev = parseInt(d._rev, 10) || 0;
    return d;
  }

  /* Eine Änderung = ein Commit (Dateien + data/daten.json gemeinsam). Hat in der Zwischenzeit
     jemand anderer gespeichert, wird die Änderung auf den neuesten Stand gesetzt und wiederholt. */
  function aendern(token, nachricht, arbeit) {
    return info(token).then(function (i) {
      function versuch(n) {
        var eltern, baum;
        return gh(token, repoPfad(i, "/git/ref/heads/" + encodeURIComponent(i.zweig)))
          .then(function (r) { eltern = r.object.sha; return gh(token, repoPfad(i, "/git/commits/" + eltern)); })
          .then(function (c) { baum = c.tree.sha; return datenLesen(token, i, eltern); })
          .then(function (d) {
            var vorher = JSON.stringify(d);
            return Promise.resolve(arbeit(d)).then(function (erg) {
              erg = erg || {};
              var dateien = (erg.dateien || []).slice();
              if (JSON.stringify(d) !== vorher) dateien.push({ pfad: DATEI, b64: textZuB64(JSON.stringify(d, null, 1) + "\n") });
              if (!dateien.length) return { daten: d, ergebnis: erg };
              return Promise.all(dateien.map(function (f) {
                if (f.loeschen) return Promise.resolve({ path: i.prefix + f.pfad, mode: "100644", type: "blob", sha: null });
                return gh(token, repoPfad(i, "/git/blobs"), { method: "POST", body: { content: f.b64, encoding: "base64" } })
                  .then(function (b) { return { path: i.prefix + f.pfad, mode: "100644", type: "blob", sha: b.sha }; });
              }))
                .then(function (eintraege) { return gh(token, repoPfad(i, "/git/trees"), { method: "POST", body: { base_tree: baum, tree: eintraege } }); })
                .then(function (t) { return gh(token, repoPfad(i, "/git/commits"), { method: "POST", body: { message: nachricht, tree: t.sha, parents: [eltern] } }); })
                .then(function (c) { return gh(token, repoPfad(i, "/git/refs/heads/" + encodeURIComponent(i.zweig)), { method: "PATCH", body: { sha: c.sha, force: false } }); })
                .then(function () { return { daten: d, ergebnis: erg }; });
            });
          })
          .catch(function (e) {
            if ((e.status === 422 || e.status === 409) && n < 3) return versuch(n + 1); // jemand war schneller
            throw e;
          });
      }
      return versuch(1);
    });
  }

  function nachricht(name, text) { return (name ? name + ": " : "") + (text || "Daten gespeichert"); }
  function alben(d) {
    return d.fotoAlben.map(function (a) {
      return { ordner: a.ordner, datum: a.datum || "", album: a.album || a.ordner || "Allgemein", bilder: (a.bilder || []).slice(), texte: d.albumTexte[a.ordner || ""] || {} };
    });
  }
  function albumFinden(d, ordner) {
    var a = d.fotoAlben.filter(function (x) { return (x.ordner || "") === ordner; })[0];
    if (!a) {
      var m = /^(\d{4}-\d{2}-\d{2})\s*(.*)$/.exec(ordner);
      a = { ordner: ordner, datum: m ? m[1] : "", album: m ? (m[2] || ordner) : (ordner || "Allgemein"), bilder: [] };
      d.fotoAlben.push(a);
    }
    a.bilder = a.bilder || [];
    return a;
  }
  function fotoPfad(ordner, datei) { return "fotos/" + (ordner ? ordner + "/" : "") + datei; }

  /* ---------- Anfragen der Verwaltung beantworten ---------- */
  function name() { try { return sessionStorage.getItem("esvGhName") || ""; } catch (e) { return ""; } }

  function bearbeiten(url, opt) {
    var u = new URL(url, location.href);
    var aktion = u.pathname.split("/api/admin/")[1] || "";
    var q = {}; u.searchParams.forEach(function (v, k) { q[k] = v; });
    var methode = (opt.method || "GET").toUpperCase();
    var kopf = opt.headers || {};
    var token = kopf["X-Token"] || kopf["x-token"] || "";
    function json() { try { return JSON.parse(opt.body || "{}"); } catch (e) { return {}; } }

    if (aktion === "anmelden") {
      var w = json();
      var schluessel = String(w.pin || "").trim();
      if (!schluessel) { try { schluessel = localStorage.getItem(SCHLUESSEL_SPEICHER) || ""; } catch (e) { /* ohne */ } }
      if (!schluessel) return Promise.resolve(fehler("Bitte beim ersten Mal den GitHub-Schlüssel eingeben.", 403));
      return info(schluessel).then(function () {
        try {
          sessionStorage.setItem("esvGhName", sauber(w.name, 40));
          var merken = document.getElementById("gh-merken");
          if (!merken || merken.checked) localStorage.setItem(SCHLUESSEL_SPEICHER, schluessel);
        } catch (e) { /* egal */ }
        return antwort({ ok: true, token: schluessel, ersteinrichtung: false });
      }, function (e) {
        if (e.status === 401) {
          try { localStorage.removeItem(SCHLUESSEL_SPEICHER); } catch (x) { /* egal */ }
          return fehler("Der GitHub-Schlüssel ist ungültig oder abgelaufen. Bitte prüfen bzw. beim Administrator einen neuen holen.", 403);
        }
        return fehler(e.message, 403);
      });
    }
    if (!token) return Promise.resolve(fehler("Bitte neu anmelden.", 403));
    if (aktion === "abmelden") return Promise.resolve(antwort({ ok: true }));

    var p;
    if (methode === "GET") {
      if (aktion === "status") {
        p = info(token).then(function (i) {
          return { ok: true, aufStick: false, speicherort: "GitHub: " + i.besitzer + "/" + i.repo + " (" + i.zweig + (i.prefix ? ", /" + i.prefix.slice(0, -1) : "") + ")",
            freiGB: null, gesamtGB: null, ordnerOeffnen: false, ueberInternet: true, version: VERSION, rechner: "GitHub Pages",
            ersteinrichtung: false, sichererFernzugriff: true, github: true };
        });
      } else if (aktion === "daten") {
        p = info(token).then(function (i) { return datenLesen(token, i); }).then(function (d) {
          delete d.albumTexte; delete d.fotoAlben; return d;
        });
      } else if (aktion === "alben") {
        p = info(token).then(function (i) { return datenLesen(token, i); }).then(function (d) { return { ok: true, alben: alben(d) }; });
      } else if (aktion === "protokoll") {
        p = info(token).then(function (i) { return gh(token, repoPfad(i, "/commits?sha=" + encodeURIComponent(i.zweig) + "&per_page=30")); }).then(function (liste) {
          return { ok: true, eintraege: (liste || []).map(function (c) {
            var m = (c.commit.message || "").split("\n")[0], t = m.indexOf(": ");
            return { zeit: zeitDE(c.commit.author && c.commit.author.date), name: t > 0 && t < 41 ? m.slice(0, t) : ((c.commit.author && c.commit.author.name) || "–"), text: t > 0 && t < 41 ? m.slice(t + 2) : m };
          }) };
        });
      } else return Promise.resolve(fehler("unbekannt", 404));
    } else {
      var wer = name();
      if (aktion === "speichern") {
        var neu = json(), rev = neu._rev, text = neu._aenderung;
        delete neu._rev; delete neu._aenderung;
        p = aendern(token, nachricht(wer, text), function (d) {
          if (rev != null && parseInt(rev, 10) !== d._rev) throw GitFehler("Inzwischen hat jemand anderer etwas gespeichert. Die Daten werden neu geladen – bitte die letzte Eingabe wiederholen.", 409);
          d._rev += 1;
          LISTEN.forEach(function (k) { if (k in neu) d[k] = neu[k]; });
          if (neu.verein && typeof neu.verein === "object") Object.keys(neu.verein).forEach(function (k) { d.verein[k] = neu.verein[k]; });
        }).then(function (r) { return { ok: true, gespeichert: jetzt(), _rev: r.daten._rev }; });
      } else if (aktion === "protokoll") {
        p = Promise.resolve({ ok: true }); // steht ohnehin in der GitHub-Versionsgeschichte
      } else if (aktion === "album") {
        var a = json(), aname = sauber(a.name), datum = /^\d{4}-\d{2}-\d{2}$/.test(a.datum || "") ? a.datum : "";
        if (!aname) return Promise.resolve(fehler("Bitte einen Namen für das Album eingeben."));
        var ordner = sauber((datum ? datum + " " : "") + aname, 100);
        p = aendern(token, nachricht(wer, "Fotoalbum angelegt: " + ordner), function (d) {
          var al = albumFinden(d, ordner); al.datum = datum; al.album = aname;
        }).then(function () { return { ok: true, ordner: ordner }; });
      } else if (aktion === "foto" || aktion === "bild") {
        var blob = opt.body;
        if (!(blob instanceof Blob)) return Promise.resolve(fehler("Keine Datei erhalten."));
        p = blobZuB64(blob).then(function (b) {
          if (!istBild(b.kopf)) throw GitFehler("Die Datei ist kein unterstütztes Bild (JPG, PNG, GIF oder WebP).", 400);
          if (aktion === "foto") {
            var ord = sauber(q.ordner || "", 100), datei = sauber(q.name || "foto.jpg") || "foto.jpg";
            if (!BILDTYPEN.test(datei)) datei += ".jpg";
            var endgueltig;
            return aendern(token, nachricht(wer, "Foto hinzugefügt: " + (ord || "Allgemein") + "/" + datei), function (d) {
              var al = albumFinden(d, ord), basis = datei.replace(/\.[^.]+$/, ""), endung = datei.slice(basis.length), n = 2;
              endgueltig = datei;
              while (al.bilder.indexOf(endgueltig) >= 0) { endgueltig = basis + "-" + n + endung; n++; }
              al.bilder.push(endgueltig);
              return { dateien: [{ pfad: fotoPfad(ord, endgueltig), b64: b.b64 }] };
            }).then(function () { vorschauMerken(fotoPfad(ord, endgueltig), blob); return { ok: true, datei: endgueltig }; });
          }
          var art = q.art || "", unter = { neuigkeit: "neuigkeiten", vorstand: "vorstand" }[art], ziel;
          if (unter) {
            var s = new Date().toISOString().replace(/[-:T.Z]/g, "").slice(0, 17);
            ziel = "bilder/" + unter + "/" + s.slice(0, 8) + "-" + s.slice(8, 14) + "-" + s.slice(14) + ".jpg";
          } else ziel = { titelbild: "bilder/vereinsheim.jpg", logo: "bilder/logo.png" }[art];
          if (!ziel) throw GitFehler("unbekannt", 400);
          return aendern(token, nachricht(wer, { titelbild: "Titelbild geändert", logo: "Logo geändert" }[art] || "Bild hochgeladen"), function () {
            return { dateien: [{ pfad: ziel, b64: b.b64 }] };
          }).then(function () { vorschauMerken(ziel, blob); return { ok: true, pfad: ziel }; });
        });
      } else if (aktion === "foto-loeschen") {
        var f = json(), fo = f.ordner || "", fd = f.datei || "";
        p = aendern(token, nachricht(wer, fd ? "Foto gelöscht: " + (fo || "Allgemein") + "/" + fd : "Fotoalbum gelöscht: " + fo), function (d) {
          var al = d.fotoAlben.filter(function (x) { return (x.ordner || "") === fo; })[0];
          if (!al) throw GitFehler("nicht gefunden", 404);
          var weg = fd ? [fd] : (al.bilder || []).slice();
          if (fd) al.bilder = al.bilder.filter(function (x) { return x !== fd; });
          else { d.fotoAlben = d.fotoAlben.filter(function (x) { return x !== al; }); delete d.albumTexte[fo]; }
          if (fd && d.albumTexte[fo]) delete d.albumTexte[fo][fd];
          return { dateien: weg.map(function (x) { return { pfad: fotoPfad(fo, x), loeschen: true }; }) };
        }).then(function () { return { ok: true }; });
      } else if (aktion === "fototext") {
        var ft = json();
        p = aendern(token, nachricht(wer, "Fotobeschreibung geändert"), function (d) {
          var o = ft.ordner || "";
          d.albumTexte[o] = d.albumTexte[o] || {};
          d.albumTexte[o][ft.datei || ""] = String(ft.text || "").slice(0, 200);
        }).then(function () { return { ok: true }; });
      } else if (aktion === "pin") {
        return Promise.resolve(fehler("Auf GitHub gibt es kein Vereins-Passwort – jede Person meldet sich mit ihrem eigenen GitHub-Schlüssel an."));
      } else if (aktion === "beispiel-laden" || aktion === "beispiel-entfernen" || aktion === "export" || aktion === "ordner-oeffnen") {
        return Promise.resolve(fehler("Auf GitHub nicht verfügbar."));
      } else return Promise.resolve(fehler("unbekannte Aktion", 404));
    }
    return p.then(function (j) { return antwort(j); }, function (e) {
      var st = e.status === 401 ? 403 : (e.status === 403 ? 400 : (e.status >= 400 && e.status < 600 ? e.status : 500));
      if (e.status === 401) { try { localStorage.removeItem(SCHLUESSEL_SPEICHER); } catch (x) { /* egal */ } }
      return fehler(e.message, st);
    });
  }

  /* ---------- fetch umleiten: nur api/… der Verwaltung ---------- */
  var original = window.fetch.bind(window);
  window.__esvFetch = original;
  window.fetch = function (eingabe, opt) {
    var url = typeof eingabe === "string" ? eingabe : (eingabe && eingabe.url) || "";
    var u; try { u = new URL(url, location.href); } catch (e) { return original(eingabe, opt); }
    if (u.origin === location.origin && /\/api\/admin\//.test(u.pathname)) {
      return bearbeiten(u.href, opt || {}).catch(function (e) { return fehler(e.message || "Fehler", 500); });
    }
    return original(eingabe, opt);
  };

  /* ---------- Anmeldemaske anpassen ---------- */
  function maske() {
    var label = document.querySelector('label[for="pin-eingabe"]'), feld = document.getElementById("pin-eingabe");
    if (!label || !feld) return;
    var gespeichert = false;
    try { gespeichert = !!localStorage.getItem(SCHLUESSEL_SPEICHER); } catch (e) { /* egal */ }
    label.textContent = "GitHub-Schlüssel";
    feld.autocomplete = "off";
    feld.placeholder = gespeichert ? "auf diesem Gerät gespeichert – einfach Anmelden" : "github_pat_…";
    feld.required = !gespeichert;
    var merken = document.createElement("label");
    merken.className = "schalter"; merken.style.fontSize = "15px";
    merken.innerHTML = '<input type="checkbox" id="gh-merken" checked> Schlüssel auf diesem Gerät merken';
    feld.insertAdjacentElement("afterend", merken);
    var hilfe = document.createElement("p");
    hilfe.className = "leise"; hilfe.style.marginTop = "14px";
    hilfe.textContent = "Den Schlüssel gibt es einmalig vom Administrator (Anleitung: GITHUB_VERWALTUNG.md). Nur auf eigenen Geräten merken lassen.";
    var vergessen = document.createElement("button");
    vergessen.type = "button"; vergessen.className = "mini"; vergessen.style.marginLeft = "0"; vergessen.textContent = "Gespeicherten Schlüssel löschen";
    vergessen.hidden = !gespeichert;
    vergessen.addEventListener("click", function () {
      try { localStorage.removeItem(SCHLUESSEL_SPEICHER); } catch (e) { /* egal */ }
      feld.placeholder = "github_pat_…"; feld.required = true; vergessen.hidden = true;
    });
    var form = document.getElementById("anmelde-form");
    form.insertAdjacentElement("afterend", hilfe);
    hilfe.insertAdjacentElement("afterend", vergessen);
    var einstieg = document.querySelector(".hilfe-einstieg");
    if (einstieg) einstieg.insertAdjacentHTML("beforeend", " Gespeicherte Änderungen sind nach <strong>1–2 Minuten</strong> auf der Webseite sichtbar.");
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", maske); else maske();
})();
