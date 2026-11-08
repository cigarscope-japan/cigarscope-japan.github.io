/* CigarScope Japan — English edition search.
   Client-side only (Stage B plan v2.2, section B1):
   - The query is NEVER transmitted: the search index is fetched without
     any query string, matching runs in the browser, and cross-page
     hand-off uses the URL fragment (#q=...), which browsers never send
     to a server.
   - Results are built with textContent / createElement only (no
     innerHTML with unescaped data). */
(function () {
  "use strict";

  var INDEX_URL = null; // resolved relative to this script's location
  var indexPromise = null;

  function scriptBase() {
    var s = document.currentScript;
    if (!s) {
      var all = document.getElementsByTagName("script");
      for (var i = 0; i < all.length; i++) {
        if (/search\.js$/.test(all[i].src)) { s = all[i]; break; }
      }
    }
    return s ? s.src.replace(/search\.js$/, "") : "";
  }

  function loadIndex() {
    if (!indexPromise) {
      if (INDEX_URL === null) INDEX_URL = scriptBase() + "search-index.json";
      indexPromise = fetch(INDEX_URL).then(function (r) { return r.json(); });
    }
    return indexPromise;
  }

  function matches(entry, terms) {
    var hay = (entry.title + " " + entry.summary + " " + entry.category +
      " " + entry.maker + " " + entry.type + " " +
      (entry.countries || []).join(" ")).toLowerCase();
    return terms.every(function (t) { return hay.indexOf(t) !== -1; });
  }

  function renderResults(container, entries, query) {
    while (container.firstChild) container.removeChild(container.firstChild);
    var count = document.createElement("p");
    count.className = "search-count";
    count.textContent = entries.length + (entries.length === 1 ? " result" : " results") +
      " for \u201C" + query + "\u201D";
    container.appendChild(count);
    entries.forEach(function (e) {
      var hit = document.createElement("article");
      hit.className = "search-hit";
      var kick = document.createElement("p");
      kick.className = "kicker";
      kick.textContent = e.category + " \u00B7 " + (e.countries || []).join(" \u00B7 ") +
        " \u00B7 " + e.type;
      var h = document.createElement("h3");
      var a = document.createElement("a");
      a.href = resolveUrl(e.url);
      a.textContent = e.title;
      h.appendChild(a);
      var p = document.createElement("p");
      p.textContent = e.summary;
      hit.appendChild(kick); hit.appendChild(h); hit.appendChild(p);
      container.appendChild(hit);
    });
  }

  function resolveUrl(url) {
    // Index URLs are relative to the English edition root. Feature URLs
    // start with ../ and are also relative to that root.
    return scriptBase() + url;
  }

  function runSearch(query, container) {
    var terms = query.toLowerCase().split(/\s+/).filter(Boolean);
    if (!terms.length) return;
    loadIndex().then(function (index) {
      renderResults(container, index.filter(function (e) {
        return matches(e, terms);
      }), query);
    }).catch(function () {
      while (container.firstChild) container.removeChild(container.firstChild);
      var p = document.createElement("p");
      p.textContent = "The search index could not be loaded. Please browse the sections from the navigation instead.";
      container.appendChild(p);
    });
  }

  function goToSearchPage(query) {
    // Fragment hand-off: #q= travels in the browser only, never in a request.
    window.location.href = scriptBase() + "search.html#q=" + encodeURIComponent(query);
  }

  document.addEventListener("DOMContentLoaded", function () {
    var headerForm = document.querySelector(".header-search");
    if (headerForm) {
      headerForm.addEventListener("submit", function (ev) {
        ev.preventDefault();
        var q = headerForm.querySelector("input").value.trim();
        if (!q) return;
        var onSearchPage = /search\.html$/.test(window.location.pathname);
        if (onSearchPage) {
          history.replaceState(null, "", "#q=" + encodeURIComponent(q));
          var c = document.getElementById("search-results");
          var input = document.getElementById("search-q");
          if (input) input.value = q;
          if (c) runSearch(q, c);
        } else {
          goToSearchPage(q);
        }
      });
    }
    var form = document.getElementById("search-form");
    var results = document.getElementById("search-results");
    if (form && results) {
      form.addEventListener("submit", function (ev) {
        ev.preventDefault();
        var q = document.getElementById("search-q").value.trim();
        if (!q) return;
        history.replaceState(null, "", "#q=" + encodeURIComponent(q));
        runSearch(q, results);
      });
      var m = /#q=([^&]*)/.exec(window.location.hash || "");
      if (m) {
        var q0 = decodeURIComponent(m[1]);
        document.getElementById("search-q").value = q0;
        runSearch(q0, results);
      }
    }
  });
})();
