/* CigarScope Japan — 日本語版サイト内検索。
   英語版と同じ方式（クライアントサイドのみ）:
   - 検索語はサーバーへ送信しない。検索インデックスはクエリ文字列なしで
     取得し、照合はブラウザ内で行う。ページ間の受け渡しは URL フラグメント
     （#q=...）を使い、これはブラウザからサーバーへ送られない。
   - 結果は textContent / createElement のみで構築する（未エスケープの
     innerHTML は使わない）。 */
(function () {
  "use strict";

  var INDEX_URL = null; // このスクリプトの場所から解決する
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
    count.textContent = "「" + query + "」の検索結果：" + entries.length + "件";
    container.appendChild(count);
    entries.forEach(function (e) {
      var hit = document.createElement("article");
      hit.className = "search-hit";
      var kick = document.createElement("p");
      kick.className = "kicker";
      kick.textContent = e.category + " ・ " + (e.countries || []).join(" ・ ") +
        " ・ " + e.type;
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
    // インデックスの URL はサイト（日本語版ルート）相対。
    return scriptBase() + url;
  }

  function runSearch(query, container) {
    var terms = query.toLowerCase().split(/[\s\u3000]+/).filter(Boolean);
    if (!terms.length) return;
    loadIndex().then(function (index) {
      renderResults(container, index.filter(function (e) {
        return matches(e, terms);
      }), query);
    }).catch(function () {
      while (container.firstChild) container.removeChild(container.firstChild);
      var p = document.createElement("p");
      p.textContent = "検索インデックスを読み込めませんでした。お手数ですが、上部メニューの各セクションから辿ってください。";
      container.appendChild(p);
    });
  }

  function goToSearchPage(query) {
    // フラグメント受け渡し: #q= はブラウザ内だけに残り、リクエストには含まれない。
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
