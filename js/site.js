/* ============================================================
   August Pi-Suñer — shared site behaviour
   - footer year
   - home hero play/pause
   - bibliography: render from window.PAPERS, group by decade, live search
   - biography: table-of-contents scrollspy
   ============================================================ */
(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    setFooterYear();
    initHeroVideo();
    initBibliography();
    initScrollSpy();
  });

  /* ---- footer year ---- */
  function setFooterYear() {
    document.querySelectorAll("[data-year]").forEach(function (el) {
      el.textContent = new Date().getFullYear();
    });
  }

  /* ---- home hero video ---- */
  function initHeroVideo() {
    var video = document.querySelector("[data-hero-video]");
    var btn = document.querySelector("[data-hero-play]");
    if (!video) return;
    function sync() {
      if (!btn) return;
      btn.innerHTML = video.paused ? "&#x25B6;" : "&#x2759;&#x2759;";
      btn.setAttribute("aria-label", video.paused ? "Reprodueix el vídeo" : "Pausa el vídeo");
    }
    function toggle() { video.paused ? video.play() : video.pause(); }
    if (btn) btn.addEventListener("click", toggle);
    video.addEventListener("click", toggle);
    video.addEventListener("play", sync);
    video.addEventListener("pause", sync);
    sync();
  }

  /* ---- bibliography ---- */
  function initBibliography() {
    var mount = document.getElementById("biblio");
    if (!mount || !Array.isArray(window.PAPERS)) return;

    var papers = window.PAPERS.slice().sort(function (a, b) {
      return a.year - b.year || a.title.localeCompare(b.title, "ca");
    });

    // group by decade
    var groups = {};
    papers.forEach(function (p) {
      var d = Math.floor(p.year / 10) * 10;
      (groups[d] = groups[d] || []).push(p);
    });

    var frag = document.createDocumentFragment();
    Object.keys(groups).map(Number).sort(function (a, b) { return a - b; }).forEach(function (d) {
      var sec = el("section", "decade");
      sec.dataset.decade = d;
      var h2 = el("h2");
      h2.appendChild(text(d + "s"));
      var n = el("span", "n"); n.textContent = "(" + groups[d].length + ")";
      h2.appendChild(n);
      sec.appendChild(h2);
      groups[d].forEach(function (p) { sec.appendChild(renderPaper(p)); });
      frag.appendChild(sec);
    });
    mount.appendChild(frag);

    // no-results element
    var none = el("p", "no-results");
    none.textContent = "No s'ha trobat cap publicació amb aquests termes.";
    mount.appendChild(none);

    wireSearch(mount, papers.length);
  }

  function renderPaper(p) {
    var row = el("article", "paper");
    var href = p.slug + ".html";

    var yr = el("div", "yr"); yr.textContent = p.year; row.appendChild(yr);

    var body = el("div", "body");
    var a = el("a", "title"); a.href = href; a.textContent = p.title;
    body.appendChild(a);
    var meta = el("div", "meta");
    if (p.authors) { var au = el("span", "authors"); au.textContent = p.authors; meta.appendChild(au); }
    if (p.venue) {
      if (p.authors) meta.appendChild(text(" · "));
      var v = el("span", "venue"); v.textContent = cleanVenue(p.venue); meta.appendChild(v);
    }
    body.appendChild(meta);
    row.appendChild(body);

    var action = el("div", "action");
    if (p.available) {
      var pill = el("a", "pill"); pill.href = href; pill.textContent = "Consulta →";
      action.appendChild(pill);
    } else {
      var dis = el("span", "pill disabled"); dis.textContent = "PDF no disponible";
      dis.title = "El PDF d'aquesta publicació encara no està disponible.";
      action.appendChild(dis);
    }
    row.appendChild(action);

    row.dataset.haystack = [p.title, p.authors, p.venue, p.year, p.citation]
      .join(" ").toLowerCase();
    return row;
  }

  function wireSearch(mount, total) {
    var input = document.getElementById("biblio-search");
    var count = document.getElementById("biblio-count");
    var none = mount.querySelector(".no-results");
    if (count) count.textContent = total + " publicacions";
    if (!input) return;

    input.addEventListener("input", function () {
      var q = normalize(input.value.trim());
      var shown = 0;
      mount.querySelectorAll(".decade").forEach(function (sec) {
        var visibleInSec = 0;
        sec.querySelectorAll(".paper").forEach(function (row) {
          var match = !q || normalize(row.dataset.haystack).indexOf(q) !== -1;
          row.style.display = match ? "" : "none";
          if (match) { visibleInSec++; shown++; }
        });
        sec.style.display = visibleInSec ? "" : "none";
      });
      if (none) none.style.display = shown ? "none" : "block";
      if (count) count.textContent = q
        ? shown + " de " + total + " publicacions"
        : total + " publicacions";
    });
  }

  /* ---- biography scrollspy ---- */
  function initScrollSpy() {
    var links = Array.prototype.slice.call(document.querySelectorAll(".toc a[href^='#']"));
    if (!links.length) return;
    var map = {};
    links.forEach(function (l) {
      var t = document.getElementById(l.getAttribute("href").slice(1));
      if (t) map[t.id] = l;
    });
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          links.forEach(function (l) { l.classList.remove("active"); });
          if (map[e.target.id]) map[e.target.id].classList.add("active");
        }
      });
    }, { rootMargin: "-30% 0px -60% 0px" });
    Object.keys(map).forEach(function (id) { obs.observe(document.getElementById(id)); });
  }

  /* ---- helpers ---- */
  function el(tag, cls) { var e = document.createElement(tag); if (cls) e.className = cls; return e; }
  function text(t) { return document.createTextNode(t); }
  function cleanVenue(v) { return v.replace(/\.$/, "").replace(/^\(([^)]*)\)\.?\s*/, ""); }
  function normalize(s) {
    return s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  }
})();
