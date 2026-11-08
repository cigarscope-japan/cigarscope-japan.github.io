#!/usr/bin/env python3
# CigarScope Japan — EN edition static generator.
#
# Inputs : en-admin/ ONLY (data, bodies, formal fragments, templates).
#          The Japanese tree is never read. Japanese URLs come from
#          en-admin/data/jp-url-manifest.yaml (descriptive data).
# Outputs: site/en/** and site/sitemap.xml.
# Rules  : deterministic — no build timestamps, no environment-dependent
#          values, no random values are embedded in generated pages.
#          style-en.css is LINKED, never embedded in article pages.
from __future__ import annotations

import html
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
ADMIN = ROOT / "en-admin"
SITE = ROOT / "site"
EN = SITE / "en"
TPL = ADMIN / "TEMPLATES"
BASE = "https://cigarscope-japan.github.io"

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

CATEGORY_LABELS = {
    "new-release": "New Release",
    "limited-edition": "Limited Edition",
    "industry": "Industry",
    "market": "Market & Distribution",
}
CATEGORY_GROUPS = {
    "new-releases": ("New Releases", {"new-release", "limited-edition"}),
    "market": ("Industry & Market", {"industry", "market"}),
}

NAV = [
    ("news", "NEWS", "news/"),
    ("industry", "INDUSTRY", "category/market.html"),
    ("brands", "BRANDS", "brands/"),
    ("countries", "COUNTRIES", "country/"),
    ("about", "ABOUT", "about.html"),
]


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def fmt_date(value) -> str:
    if value is None:
        return ""
    y, m, d = str(value).split("-")
    return f"{MONTHS[int(m) - 1]} {int(d)}, {y}"


def esc(text) -> str:
    return html.escape(str(text), quote=True)


def rel_prefix(depth: int) -> str:
    """Path prefix from a page `depth` levels below the site root back to root."""
    return "../" * depth


def img_src(logical: str, depth: int) -> str:
    return rel_prefix(depth) + logical


def header(prefix_en: str, active: str, title_suffix: str, depth: int,
           description: str, canonical: str, alternates: str = "",
           og_image: str = "", jp_path: str = "") -> str:
    tpl = (TPL / "header.html").read_text(encoding="utf-8")
    nav_items = []
    for key, label, href in NAV:
        cls = ' class="active"' if key == active else ""
        nav_items.append(f'<li><a href="{prefix_en}{href}"{cls}>{label}</a></li>')
    og = ""
    if og_image:
        og = (f'\n  <meta property="og:image" content="{og_image}">'
              f'\n  <meta name="twitter:card" content="summary_large_image">')
    else:
        og = '\n  <meta name="twitter:card" content="summary">'
    return (tpl.replace("{{TITLE}}", esc(title_suffix))
               .replace("{{DESCRIPTION}}", esc(description))
               .replace("{{CANONICAL}}", canonical)
               .replace("{{ALTERNATES}}", alternates)
               .replace("{{OG_EXTRA}}", og)
               .replace("{{ROOT}}", rel_prefix(depth))
               .replace("{{EN}}", prefix_en)
               .replace("{{NAV_ITEMS}}", "\n          ".join(nav_items))
               .replace("{{JP_LINK}}", rel_prefix(depth) + jp_path))


def footer(prefix_en: str, depth: int) -> str:
    tpl = (TPL / "footer.html").read_text(encoding="utf-8")
    return (tpl.replace("{{ROOT}}", rel_prefix(depth))
               .replace("{{EN}}", prefix_en))


def render(template: str, mapping: dict) -> str:
    out = template
    for key, value in mapping.items():
        out = out.replace("{{" + key + "}}", value)
    return out


def listing_order(articles: list[dict]) -> list[dict]:
    prio = {"lead": 0, "mid": 1}
    return sorted(
        articles,
        key=lambda a: (
            _neg_date(a["publish_date"]),
            _neg_date(a["source_date"]),
            prio.get(a.get("top_story"), 2),
            a["slug"],
        ),
    )


def _neg_date(value) -> tuple:
    y, m, d = str(value).split("-")
    return (-int(y), -int(m), -int(d))


def card(article: dict, depth: int, prefix_en: str, countries: dict,
         makers: dict) -> str:
    country_names = " · ".join(countries[c]["name_en"]
                                for c in article["country_ids"])
    figure = ""
    if article.get("image"):
        figure = (f'<img src="{img_src(article["image"], depth)}" '
                  f'alt="{esc(article.get("image_alt") or article["title"])}" loading="lazy">')
    return f"""<article class="card">
      <a class="card-media" href="{prefix_en}news/{article['slug']}.html">{figure}</a>
      <p class="kicker">{esc(CATEGORY_LABELS[article['category']])} · {esc(country_names)}</p>
      <h3><a href="{prefix_en}news/{article['slug']}.html">{esc(article['title'])}</a></h3>
      <p class="card-summary">{esc(article['summary'])}</p>
      <p class="card-meta">{esc(makers[article['maker_id']]['name_en'])} · {fmt_date(article['publish_date'])}</p>
      <p class="card-more"><a class="read-more" href="{prefix_en}news/{article['slug']}.html">Read the full story ›</a></p>
    </article>"""


def main() -> None:
    data = load_yaml(ADMIN / "data" / "articles-en.yaml")
    masters = load_yaml(ADMIN / "data" / "masters.yaml")
    corrections_doc = load_yaml(ADMIN / "data" / "corrections.yaml") or {}
    manifest = load_yaml(ADMIN / "data" / "jp-url-manifest.yaml")
    countries = {c["id"]: c for c in masters["countries"]}
    makers = {m["id"]: m for m in masters["makers"]}
    features = masters.get("features", [])
    jp_urls = {e["jp_slug"]: e["jp_url"] for e in manifest["entries"]}
    jp_top = manifest["jp_top_url"]

    articles = [a for a in data["articles"] if a["status"] == "published"]
    ordered = listing_order(articles)
    by_slug = {a["slug"]: a for a in articles}

    (EN / "news").mkdir(parents=True, exist_ok=True)
    (EN / "country").mkdir(parents=True, exist_ok=True)
    (EN / "brands").mkdir(parents=True, exist_ok=True)
    (EN / "category").mkdir(parents=True, exist_ok=True)

    sitemap_entries: list[tuple[str, list[tuple[str, str]]]] = []

    def alternates_for(en_url: str, jp_url: str | None) -> list[tuple[str, str]]:
        if not jp_url:
            return []
        return [("ja", jp_url), ("en", en_url), ("x-default", en_url)]

    def alt_links(pairs: list[tuple[str, str]]) -> str:
        if not pairs:
            return ""
        lines = [f'\n  <link rel="alternate" hreflang="{lang}" href="{url}">'
                 for lang, url in pairs]
        return "".join(lines)

    # ---------- article pages ----------
    article_tpl = (TPL / "article.html").read_text(encoding="utf-8")
    for a in ordered:
        depth = 2  # site/en/news/<slug>.html
        prefix_en = "../"
        jp_url = jp_urls.get(a["jp_counterpart"]) if a.get("jp_counterpart") else None
        en_url = f"{BASE}/en/news/{a['slug']}.html"
        pairs = alternates_for(en_url, jp_url)
        sitemap_entries.append((en_url, pairs))
        if jp_url:
            sitemap_entries.append((jp_url, [("ja", jp_url), ("en", en_url),
                                             ("x-default", en_url)]))
        body = (ADMIN / "src" / "bodies" / f"{a['slug']}.html").read_text(encoding="utf-8")
        hero = ""
        if a.get("image"):
            hero = (f"""<figure class="hero-figure">
        <img src="{img_src(a['image'], depth)}" alt="{esc(a.get('image_alt') or a['title'])}">
        <figcaption>{esc(a.get('image_credit') or '')}</figcaption>
      </figure>""")
        note = ""
        if a.get("editorial_note"):
            note = (f'<aside class="editorial-note"><h2>Editorial note</h2>'
                    f"<p>{esc(a['editorial_note'])}</p></aside>")
        corr = ""
        corr_items = [h for h in a.get("history") or []
                      if h.get("type") == "correction"]
        if corr_items:
            items = "".join(
                f"<li><strong>{fmt_date(h['date'])}:</strong> {esc(h['note'])}</li>"
                for h in corr_items)
            corr = f'<aside class="correction-box"><h2>Correction</h2><ul>{items}</ul></aside>'
        jp_link = ""
        if jp_url:
            jp_link = (f'<p class="jp-link">Japanese version: '
                       f'<a href="{jp_url}">Read this story in Japanese</a></p>')
        related_cards = "\n      ".join(
            card(by_slug[s], depth, prefix_en, countries, makers)
            for s in (a.get("related") or []) if s in by_slug)
        country_names = " · ".join(countries[c]["name_en"] for c in a["country_ids"])
        release = ""
        if a.get("release_date") and a["release_date"] != "n/a":
            rd = a["release_date"]
            if isinstance(rd, dict):
                release = (f"<div><dt>Release</dt><dd>{esc(rd['label'])}</dd></div>")
            else:
                release = f"<div><dt>Release</dt><dd>{fmt_date(rd)}</dd></div>"
        page = render(article_tpl, {
            "HEADER": header(prefix_en, "news", a["title"], depth,
                             a["description"], en_url, alt_links(pairs),
                             f"{BASE}/{a['image']}" if a.get("image") else "",
                             jp_url[len(BASE) + 1:] if jp_url else ""),
            "FOOTER": footer(prefix_en, depth),
            "KICKER": f"{esc(CATEGORY_LABELS[a['category']])} · {esc(country_names)}",
            "TITLE": esc(a["title"]),
            "STANDFIRST": esc(a["summary"]),
            "PUBLISHED": fmt_date(a["publish_date"]),
            "ANNOUNCED": fmt_date(a["source_date"]),
            "RELEASE_META": release,
            "MAKER": esc(makers[a["maker_id"]]["name_en"]),
            "HERO": hero,
            "BODY": body,
            "EDITORIAL_NOTE": note,
            "CORRECTION_BOX": corr,
            "SOURCE_NAME": esc(a["source_name"]),
            "SOURCE_URL": esc(a["source_url"]),
            "JP_LINK": jp_link,
            "RELATED": related_cards,
        })
        (EN / "news" / f"{a['slug']}.html").write_text(page, encoding="utf-8")

    listing_tpl = (TPL / "listing.html").read_text(encoding="utf-8")

    def listing_page(path: Path, depth: int, prefix_en: str, active: str,
                     title: str, intro: str, items: list[dict],
                     canonical: str) -> None:
        cards = "\n      ".join(
            card(a, depth, prefix_en, countries, makers) for a in items)
        page = render(listing_tpl, {
            "HEADER": header(prefix_en, active, title, depth,
                             intro, canonical, jp_path=path.relative_to(EN).as_posix()),
            "FOOTER": footer(prefix_en, depth),
            "TITLE": esc(title),
            "INTRO": esc(intro),
            "CARDS": cards,
            "EMPTY_NOTE": "" if items else
                '<p class="empty-note">No stories have been published in this section yet.</p>',
        })
        path.write_text(page, encoding="utf-8")
        sitemap_entries.append((canonical, []))

    # ---------- news index ----------
    listing_page(EN / "news" / "index.html", 2, "../", "news",
                 "Latest News",
                 "Every story from the CigarScope Japan English desk, newest first.",
                 ordered, f"{BASE}/en/news/")

    # ---------- country pages ----------
    countries_index_items = []
    for cid, c in countries.items():
        items = [a for a in ordered if cid in a["country_ids"]]
        if not items:
            continue
        countries_index_items.append((c, len(items)))
        listing_page(EN / "country" / f"{cid}.html", 2, "../", "countries",
                     f"{c['name_en']} — Cigar News",
                     f"Premium cigar news from {c['name_en']}.",
                     items, f"{BASE}/en/country/{cid}.html")
    country_links = "\n      ".join(
        f'<article class="card country-card"><h3><a href="../country/{c["id"]}.html">'
        f'{esc(c["name_en"])}</a></h3><p class="card-meta">{n} '
        f'{"story" if n == 1 else "stories"}</p></article>'
        for c, n in countries_index_items)
    page = render(listing_tpl, {
        "HEADER": header("../", "countries", "Countries & Regions", 2,
                         "Browse CigarScope Japan coverage by country and region.",
                         f"{BASE}/en/country/"),
        "FOOTER": footer("../", 2),
        "TITLE": "Countries &amp; Regions",
        "INTRO": "Coverage organised by the country a story belongs to.",
        "CARDS": country_links,
        "EMPTY_NOTE": "",
    })
    (EN / "country" / "index.html").write_text(page, encoding="utf-8")
    sitemap_entries.append((f"{BASE}/en/country/", []))

    # ---------- brand pages ----------
    brand_items = []
    for mid, m in makers.items():
        items = [a for a in ordered if a["maker_id"] == mid]
        if not items:
            continue
        brand_items.append((m, len(items)))
        listing_page(EN / "brands" / f"{mid}.html", 2, "../", "brands",
                     f"{m['name_en']} — News & Releases",
                     f"CigarScope Japan coverage of {m['name_en']} ({m['base_en']}).",
                     items, f"{BASE}/en/brands/{mid}.html")
    brand_links = "\n      ".join(
        f'<article class="card country-card"><h3><a href="../brands/{m["id"]}.html">'
        f'{esc(m["name_en"])}</a></h3><p class="card-meta">{esc(m["base_en"])} · {n} '
        f'{"story" if n == 1 else "stories"}</p></article>'
        for m, n in brand_items)
    page = render(listing_tpl, {
        "HEADER": header("../", "brands", "Brands & Makers", 2,
                         "Browse CigarScope Japan coverage by brand and maker.",
                         f"{BASE}/en/brands/", jp_path="brands/index.html"),
        "FOOTER": footer("../", 2),
        "TITLE": "Brands &amp; Makers",
        "INTRO": "Coverage organised by brand and maker.",
        "CARDS": brand_links,
        "EMPTY_NOTE": "",
    })
    (EN / "brands" / "index.html").write_text(page, encoding="utf-8")
    sitemap_entries.append((f"{BASE}/en/brands/", []))

    # ---------- category group pages ----------
    for key, (label, keys) in CATEGORY_GROUPS.items():
        items = [a for a in ordered if a["category"] in keys]
        active = "industry" if key == "market" else "news"
        listing_page(EN / "category" / f"{key}.html", 2, "../", active,
                     label, f"{label} from the world premium cigar industry.",
                     items, f"{BASE}/en/category/{key}.html")

    # ---------- top page ----------
    index_tpl = (TPL / "index.html").read_text(encoding="utf-8")
    lead = next((a for a in ordered if a.get("top_story") == "lead"), ordered[0])
    latest = [a for a in ordered if a["slug"] != lead["slug"]][:3]
    digest = [a for a in ordered if a["slug"] not in
              {lead["slug"]} | {x["slug"] for x in latest}][:5]
    industry_items = [a for a in ordered if a["category"] in {"industry", "market"}][:2]
    brand_spot = next((a for a in ordered if a.get("image")), lead)
    lead_figure = ""
    if lead.get("image"):
        lead_figure = (f'<img src="{img_src(lead["image"], 1)}" '
                       f'alt="{esc(lead.get("image_alt") or lead["title"])}">'
                       f'<figcaption>{esc(lead.get("image_credit") or "")}</figcaption>')
    digest_rows = "\n        ".join(
        f'<li><a href="news/{a["slug"]}.html">{esc(a["title"])}</a>'
        f'<span class="digest-meta">{esc(makers[a["maker_id"]]["name_en"])} · '
        f'{fmt_date(a["publish_date"])}</span></li>' for a in digest)
    tiles = "\n      ".join(
        f'<a class="tile" href="country/{c["id"]}.html"><span>{esc(c["name_en"])}</span></a>'
        for c, _ in countries_index_items)
    feature_cards = "\n      ".join(
        f"""<article class="card">
      <a class="card-media" href="{f['url']}"><img src="{img_src(f['image'], 1)}" alt="{esc(f['title'])}" loading="lazy"></a>
      <p class="kicker">Feature · In Japanese</p>
      <h3><a href="{f['url']}">{esc(f['title'])}</a></h3>
      <p class="card-summary">{esc(f['summary'])}</p>
      <p class="card-more"><a class="read-more" href="{f['url']}">Read the full story ›</a></p>
    </article>""" for f in features)
    industry_cards = "\n      ".join(
        card(a, 1, "", countries, makers) for a in industry_items)
    page = render(index_tpl, {
        "HEADER": header("", "", "CigarScope Japan — World Cigar News & Intelligence",
                         1,
                         "CigarScope Japan is an independent Japanese editorial desk "
                         "covering the world premium cigar industry in English: news, "
                         "new releases, brands and markets, beyond Havana and beyond borders.",
                         f"{BASE}/en/",
                         alt_links([("ja", jp_top), ("en", f"{BASE}/en/"),
                                    ("x-default", f"{BASE}/en/")]),
                         f"{BASE}/{lead['image']}" if lead.get("image") else ""),
        "FOOTER": footer("", 1),
        "LEAD_FIGURE": lead_figure,
        "LEAD_KICKER": f"{esc(CATEGORY_LABELS[lead['category']])} · "
                       + " · ".join(countries[c]["name_en"] for c in lead["country_ids"]),
        "LEAD_TITLE": esc(lead["title"]),
        "LEAD_URL": f"news/{lead['slug']}.html",
        "LEAD_SUMMARY": esc(lead["summary"]),
        "LEAD_META": f"{esc(makers[lead['maker_id']]['name_en'])} · {fmt_date(lead['publish_date'])}",
        "LATEST_CARDS": "\n      ".join(
            card(a, 1, "", countries, makers) for a in latest),
        "DIGEST_ROWS": digest_rows,
        "INDUSTRY_CARDS": industry_cards,
        "BRAND_IMAGE": img_src(brand_spot["image"], 1) if brand_spot.get("image") else "",
        "BRAND_IMAGE_ALT": esc(brand_spot.get("image_alt") or brand_spot["title"]),
        "BRAND_TITLE": esc(brand_spot["title"]),
        "BRAND_URL": f"news/{brand_spot['slug']}.html",
        "BRAND_SUMMARY": esc(brand_spot["summary"]),
        "TILES": tiles,
        "FEATURE_CARDS": feature_cards,
    })
    (EN / "index.html").write_text(page, encoding="utf-8")
    sitemap_entries.append((f"{BASE}/en/", [("ja", jp_top), ("en", f"{BASE}/en/"),
                                            ("x-default", f"{BASE}/en/")]))
    sitemap_entries.append((jp_top, [("ja", jp_top), ("en", f"{BASE}/en/"),
                                     ("x-default", f"{BASE}/en/")]))

    # ---------- formal pages ----------
    formal_tpl = (TPL / "formal-page.html").read_text(encoding="utf-8")
    formal_meta = {
        "about": ("About CigarScope Japan", "What CigarScope Japan is, who edits it, and how it works."),
        "policy": ("Editorial Policy", "How CigarScope Japan selects, verifies and corrects its stories."),
        "sources": ("Sources", "The sources CigarScope Japan relies on, and how they are graded."),
        "contact": ("Contact", "How to reach the CigarScope Japan desk."),
        "privacy": ("Privacy Policy", "How CigarScope Japan handles reader data."),
    }
    for key, (title, desc) in formal_meta.items():
        body = (ADMIN / "src" / "formal" / f"{key}.html").read_text(encoding="utf-8")
        page = render(formal_tpl, {
            "HEADER": header("", "about" if key == "about" else "", title, 1,
                             desc, f"{BASE}/en/{key}.html",
                             jp_path=f"{key}.html"),
            "FOOTER": footer("", 1),
            "TITLE": esc(title),
            "BODY": body,
        })
        (EN / f"{key}.html").write_text(page, encoding="utf-8")
        sitemap_entries.append((f"{BASE}/en/{key}.html", []))

    corrections = corrections_doc.get("corrections") or []
    if corrections:
        rows = "\n".join(
            f"<tr><td>{fmt_date(c['date'])}</td>"
            f'<td><a href="news/{c["article_slug"]}.html">{esc(c["article_title"])}</a></td>'
            f"<td>{esc(c['change'])}</td><td>{esc(c['reason'])}</td></tr>"
            for c in corrections)
        corr_body = (f"<p>Every correction CigarScope Japan has published is "
                     f"recorded here, with the date, the article, what changed "
                     f"and why.</p><table class=\"corr-table\"><thead><tr>"
                     f"<th>Date</th><th>Article</th><th>Correction</th>"
                     f"<th>Reason</th></tr></thead><tbody>{rows}</tbody></table>")
    else:
        corr_body = ((ADMIN / "src" / "formal" / "corrections.html")
                     .read_text(encoding="utf-8"))
    page = render(formal_tpl, {
        "HEADER": header("", "", "Corrections", 1,
                         "CigarScope Japan's public record of corrections.",
                         f"{BASE}/en/corrections.html"),
        "FOOTER": footer("", 1),
        "TITLE": "Corrections",
        "BODY": corr_body,
    })
    (EN / "corrections.html").write_text(page, encoding="utf-8")
    sitemap_entries.append((f"{BASE}/en/corrections.html", []))

    # ---------- search page + index ----------
    search_tpl = (TPL / "search.html").read_text(encoding="utf-8")
    page = render(search_tpl, {
        "HEADER": header("", "", "Search", 1,
                         "Search CigarScope Japan's English coverage.",
                         f"{BASE}/en/search.html"),
        "FOOTER": footer("", 1),
    })
    (EN / "search.html").write_text(page, encoding="utf-8")

    index_entries = []
    for a in ordered:
        index_entries.append({
            "title": a["title"],
            "summary": a["summary"],
            "category": CATEGORY_LABELS[a["category"]],
            "countries": [countries[c]["name_en"] for c in a["country_ids"]],
            "maker": makers[a["maker_id"]]["name_en"],
            "type": "News",
            "date": str(a["publish_date"]),
            "url": f"news/{a['slug']}.html",
        })
    for f in features:
        index_entries.append({
            "title": f["title"], "summary": f["summary"],
            "category": "Feature", "countries": [f["country"]],
            "maker": f["maker"], "type": "Feature (Japanese)",
            "date": f["date"], "url": f["url"],
        })
    (EN / "search-index.json").write_text(
        json.dumps(index_entries, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")

    # ---------- sitemap ----------
    seen: set[str] = set()
    url_blocks = []
    for loc, pairs in sitemap_entries:
        if loc in seen:
            continue
        seen.add(loc)
        alts = "".join(
            f'\n    <xhtml:link rel="alternate" hreflang="{lang}" href="{url}"/>'
            for lang, url in pairs)
        url_blocks.append(f"  <url>\n    <loc>{loc}</loc>{alts}\n  </url>")
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
               'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
               + "\n".join(url_blocks) + "\n</urlset>\n")
    (SITE / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    print(f"built: {len(ordered)} articles, sitemap {len(url_blocks)} urls")


if __name__ == "__main__":
    main()
