#!/usr/bin/env python3
# CigarScope Japan — EN edition checker.
# Validates en-admin data, audit files and the generated site/ tree.
# Exit code 0 = all build checks pass. Approval status is REPORTED,
# not gated here (approval is the publisher's act, not the builder's).
from __future__ import annotations

import datetime
import json
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
ADMIN = ROOT / "en-admin"
SITE = ROOT / "site"
EN = SITE / "en"

sys.path.insert(0, str(ADMIN / "tools"))
import approval_hash_en  # noqa: E402

failures: list[str] = []
warnings: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def is_date(v) -> bool:
    return isinstance(v, datetime.date) and not isinstance(v, datetime.datetime)


def scan_floats(obj, path: str) -> None:
    if isinstance(obj, float):
        fail(f"float value in EN data at {path}: {obj!r} (floats are banned)")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            scan_floats(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            scan_floats(v, f"{path}[{i}]")


def check_nfc(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if unicodedata.normalize("NFC", text) != text:
        fail(f"non-NFC text: {path.relative_to(ROOT)}")
    for i, line in enumerate(text.split("\n"), 1):
        if line != line.rstrip():
            warn(f"trailing whitespace: {path.relative_to(ROOT)}:{i}")


def main() -> int:
    data = load_yaml(ADMIN / "data" / "articles-en.yaml")
    masters = load_yaml(ADMIN / "data" / "masters.yaml")
    sources_doc = load_yaml(ADMIN / "data" / "sources-en.yaml")
    corrections_doc = load_yaml(ADMIN / "data" / "corrections.yaml") or {}
    manifest = load_yaml(ADMIN / "data" / "jp-url-manifest.yaml")

    for name, doc in (("articles-en", data), ("masters", masters),
                      ("sources-en", sources_doc),
                      ("corrections", corrections_doc)):
        scan_floats(doc, name)

    # --- source registry: unique names (final-audit item 1) ---
    source_names = [s["name"] for s in sources_doc["sources"]]
    if len(source_names) != len(set(source_names)):
        dupes = {n for n in source_names if source_names.count(n) > 1}
        fail(f"duplicate source names in sources-en.yaml: {sorted(dupes)}")
    registry = {s["name"]: s for s in sources_doc["sources"]}

    countries = {c["id"] for c in masters["countries"]}
    makers = {m["id"] for m in masters["makers"]}
    manifest_slugs = {e["jp_slug"] for e in manifest["entries"]}
    manifest_urls = {e["jp_url"] for e in manifest["entries"]}

    articles = data["articles"]
    slugs = [a["slug"] for a in articles]
    if len(slugs) != len(set(slugs)):
        fail("duplicate article slugs")

    published = []
    for a in articles:
        slug = a["slug"]
        where = f"article {slug}"
        for field in ("title", "summary", "description", "category",
                      "country_ids", "maker_id", "source_name", "source_url",
                      "source_date", "publish_date", "status"):
            v = a.get(field)
            if v is None or (isinstance(v, str) and not v.strip()):
                fail(f"{where}: required field missing/empty: {field}")
        if a["status"] not in ("draft", "published"):
            fail(f"{where}: unknown status {a['status']!r}")
        for field in ("source_date", "publish_date"):
            if not is_date(a.get(field)):
                fail(f"{where}: {field} must be a YAML date (unquoted), "
                     f"got {type(a.get(field)).__name__}")
        rd = a.get("release_date")
        if a["category"] in ("new-release", "limited-edition"):
            if rd is None:
                fail(f"{where}: release_date is required for product stories "
                     f"(use the string 'n/a' when not applicable)")
        if rd is not None and rd != "n/a" and not is_date(rd) \
                and not (isinstance(rd, dict) and rd.get("label")):
            fail(f"{where}: release_date must be a date, 'n/a', or a labelled dict")
        for cid in a.get("country_ids") or []:
            if cid not in countries:
                fail(f"{where}: unknown country id {cid}")
        if a.get("maker_id") not in makers:
            fail(f"{where}: unknown maker id {a.get('maker_id')}")
        for h in a.get("history") or []:
            if not is_date(h.get("date")):
                fail(f"{where}: history date must be a YAML date")
            if h.get("type") not in ("correction", "update", "minor"):
                fail(f"{where}: history type must be correction/update/minor")
        text_blob = " ".join(str(a.get(k) or "") for k in
                             ("title", "summary", "description"))
        if re.search(r"TODO|TBD|lorem|placeholder|仮の|ダミー", text_blob, re.I):
            fail(f"{where}: placeholder-like text in published data fields")
        if a["status"] != "published":
            continue
        published.append(a)

        # --- publication gates ---
        if a["source_name"] not in registry:
            fail(f"{where}: source not registered in sources-en.yaml: "
                 f"{a['source_name']}")
        if "Cigar Journal" in (a["source_name"] or ""):
            fail(f"{where}: excluded outlet used as source")
        sc = str(a.get("source_checked") or "")
        if not re.search(r"\d{4}-\d{2}-\d{2}", sc) or "OK" not in sc:
            fail(f"{where}: source_checked must record the access-check "
                 f"date and result, got {sc!r}")
        body_path = ADMIN / "src" / "bodies" / f"{slug}.html"
        if not body_path.exists():
            fail(f"{where}: body fragment missing: {body_path}")
        else:
            check_nfc(body_path)
            body = body_path.read_text(encoding="utf-8")
            if re.search(r"TODO|TBD|lorem ipsum|仮の文章", body, re.I):
                fail(f"{where}: placeholder-like text in body")
            if "Cigar Journal" in body:
                fail(f"{where}: excluded outlet named in body")
        claims_path = ROOT / "audits" / "claims-en" / f"{slug}.md"
        if not claims_path.exists():
            fail(f"{where}: claims table missing: audits/claims-en/{slug}.md")
        else:
            check_nfc(claims_path)
            claims = claims_path.read_text(encoding="utf-8")
            if "UNRESOLVED" in claims or "MISMATCH" in claims:
                fail(f"{where}: claims table has unresolved rows")
            rows = [ln for ln in claims.splitlines()
                    if ln.startswith("| C")]
            if not rows:
                fail(f"{where}: claims table has no claim rows")
            for row in rows:
                if not row.rstrip().endswith("VERIFIED |"):
                    fail(f"{where}: claim row not verified: {row[:60]}...")
            if not re.search(r"Source accessed: \d{4}-\d{2}-\d{2}", claims):
                fail(f"{where}: claims table lacks the source-access record")
        if a.get("image"):
            img = SITE / a["image"]
            if not img.exists():
                fail(f"{where}: image file not found: {a['image']}")
            if not (a.get("image_credit") or "").strip():
                fail(f"{where}: image_credit is mandatory when an image is set")
        jpc = a.get("jp_counterpart")
        if jpc is not None and jpc not in manifest_slugs:
            fail(f"{where}: jp_counterpart not in jp-url-manifest: {jpc}")

    # --- corrections consistency ---
    for c in corrections_doc.get("corrections") or []:
        if not is_date(c.get("date")):
            fail(f"correction {c.get('article_slug')}: date must be a YAML date")
        target = next((a for a in articles
                       if a["slug"] == c.get("article_slug")), None)
        if target is None:
            fail(f"correction refers to unknown article {c.get('article_slug')}")
        elif not any(h.get("type") == "correction"
                     and str(h.get("date")) == str(c["date"])
                     for h in target.get("history") or []):
            fail(f"correction for {c['article_slug']} has no matching "
                 f"article history entry")

    # --- generated site checks ---
    if not EN.exists():
        fail("generated en/ tree missing — run build-en.py first")
    else:
        for page in sorted(EN.rglob("*.html")):
            check_nfc(page)
            text = page.read_text(encoding="utf-8")
            if 'href="#"' in text:
                fail(f"{page.relative_to(SITE)}: contains href=\"#\"")
            if 'lang="en"' not in text:
                fail(f"{page.relative_to(SITE)}: missing lang=\"en\"")
            for m in re.finditer(r'(?:href|src)="([^"#]+)"', text):
                url = m.group(1)
                if url.startswith(("http://", "https://", "mailto:")):
                    continue
                target = (page.parent / url.split("#")[0]).resolve()
                if not target.exists():
                    fail(f"{page.relative_to(SITE)}: broken internal link {url}")
        # search index consistency
        idx_path = EN / "search-index.json"
        if not idx_path.exists():
            fail("en/search-index.json missing")
        else:
            idx = json.loads(idx_path.read_text(encoding="utf-8"))
            idx_urls = {e["url"] for e in idx}
            for a in published:
                if f"news/{a['slug']}.html" not in idx_urls:
                    fail(f"search index missing article {a['slug']}")
            for e in idx:
                target = (EN / e["url"]).resolve()
                if not target.exists():
                    fail(f"search index URL does not resolve: {e['url']}")
        # sitemap: XML syntax + xhtml namespace (final-audit item 2)
        sm_path = SITE / "sitemap.xml"
        if not sm_path.exists():
            fail("sitemap.xml missing")
        else:
            try:
                tree = ET.parse(sm_path)
            except ET.ParseError as e:
                fail(f"sitemap.xml is not well-formed XML: {e}")
                tree = None
            if tree is not None:
                ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
                      "xhtml": "http://www.w3.org/1999/xhtml"}
                root = tree.getroot()
                if not root.tag.endswith("urlset"):
                    fail("sitemap root is not <urlset>")
                locs = [el.text for el in root.findall("sm:url/sm:loc", ns)]
                if len(locs) != len(set(locs)):
                    fail("sitemap has duplicate <loc> entries")
                pair_map: dict[str, dict[str, str]] = {}
                for url_el in root.findall("sm:url", ns):
                    loc = url_el.find("sm:loc", ns).text
                    alts = {}
                    for link in url_el.findall("xhtml:link", ns):
                        alts[link.get("hreflang")] = link.get("href")
                    pair_map[loc] = alts
                    for lang, href in alts.items():
                        if lang == "ja" and href not in manifest_urls \
                                and href != manifest["jp_top_url"]:
                            fail(f"sitemap: Japanese URL not in manifest: {href}")
                for a in published:
                    en_url = f"https://cigarscope-japan.github.io/en/news/{a['slug']}.html"
                    if en_url not in pair_map:
                        fail(f"sitemap: missing EN entry for {a['slug']}")
                        continue
                    jpc = a.get("jp_counterpart")
                    if jpc:
                        jp_url = next(e["jp_url"] for e in manifest["entries"]
                                      if e["jp_slug"] == jpc)
                        if pair_map[en_url].get("ja") != jp_url:
                            fail(f"sitemap: {a['slug']} EN entry lacks ja alternate")
                        if jp_url not in pair_map:
                            fail(f"sitemap: missing JP entry for {a['slug']}")
                        elif pair_map[jp_url].get("en") != en_url:
                            fail(f"sitemap: {a['slug']} JP entry lacks en alternate")
                    else:
                        if "ja" in pair_map[en_url]:
                            fail(f"sitemap: {a['slug']} has ja alternate but "
                                 f"jp_counterpart is null")

    # --- approval status (report only) ---
    print("== approval status (report only) ==")
    for a in published:
        current = approval_hash_en.is_approved(a["slug"])
        has = bool(a.get("approval"))
        state = "APPROVED (current)" if current else \
            ("STALE — re-approval required" if has else "not yet approved")
        print(f"  {a['slug']}: {state}")

    for w in warnings:
        print(f"WARNING: {w}")
    if failures:
        print(f"\n== RESULT: FAIL ({len(failures)}) ==")
        for f in failures:
            print(f"  FAIL: {f}")
        return 1
    print(f"\n== RESULT: PASS ({len(published)} published articles, "
          f"{len(warnings)} warnings) ==")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
