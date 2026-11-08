#!/usr/bin/env python3
# CigarScope Japan — EN edition approval hash.
#
# The algorithm is IDENTICAL to the Japanese edition v1
# (~/workspace/cigar-site/tools/APPROVAL-HASH-SPEC.md, hash_spec_version 1):
# targets in fixed order, spec normalization, combination method.
# Only the file locations differ (EN data tree). The Japanese tools are
# never modified by this file.
#
# Targets:
#   1. article_record : the article's record in articles-en.yaml, minus `approval`
#   2. body           : en-admin/src/bodies/<slug>.html
#   3. claims         : audits/claims-en/<slug>.md
#   4. source         : {article_source: {...}, registry: <sources-en.yaml record
#                        whose name == source_name>}
#   5. detail_page    : site/en/news/<slug>.html (whole generated file)
#
# Input invariants (enforced by check-en.py, NOT by transforming inputs here):
# dates are YAML date type, no floats in EN data, hashed texts are NFC.
from __future__ import annotations

import hashlib
import sys
import unicodedata
from pathlib import Path

import yaml

HASH_SPEC_VERSION = 1

ROOT = Path(__file__).resolve().parents[2]  # en-site-work/
DATA = ROOT / "en-admin" / "data" / "articles-en.yaml"
SOURCES = ROOT / "en-admin" / "data" / "sources-en.yaml"
BODIES = ROOT / "en-admin" / "src" / "bodies"
CLAIMS = ROOT / "audits" / "claims-en"
PAGES = ROOT / "site" / "en" / "news"


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if not text.endswith("\n"):
        text += "\n"
    return text


def canonical_yaml(obj) -> str:
    dumped = yaml.safe_dump(obj, allow_unicode=True, sort_keys=True,
                            default_flow_style=False)
    return normalize_text(dumped)


def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def load_articles() -> list[dict]:
    doc = yaml.safe_load(DATA.read_text(encoding="utf-8"))
    return doc["articles"] if isinstance(doc, dict) else doc


def load_sources() -> list[dict]:
    if not SOURCES.exists():
        return []
    doc = yaml.safe_load(SOURCES.read_text(encoding="utf-8"))
    return doc["sources"] if isinstance(doc, dict) else doc


def article_hash(slug: str) -> str:
    articles = load_articles()
    sources = load_sources()
    article = next((a for a in articles if a["slug"] == slug), None)
    if article is None:
        raise KeyError(f"article not found: {slug}")

    parts: list[tuple[str, str]] = []

    record = {k: v for k, v in article.items() if k != "approval"}
    parts.append(("article_record", sha256_hex(canonical_yaml(record))))

    body_path = BODIES / f"{slug}.html"
    parts.append(("body", sha256_hex(normalize_text(
        body_path.read_text(encoding="utf-8")))))

    claims_path = CLAIMS / f"{slug}.md"
    parts.append(("claims", sha256_hex(normalize_text(
        claims_path.read_text(encoding="utf-8")))))

    registry = next((s for s in sources
                     if s.get("name") == article.get("source_name")), None)
    source_obj = {
        "article_source": {
            "source_name": article.get("source_name"),
            "source_url": article.get("source_url"),
            "source_checked": article.get("source_checked"),
            "source_type": article.get("source_type"),
        },
        "registry": registry,
    }
    parts.append(("source", sha256_hex(canonical_yaml(source_obj))))

    page_path = PAGES / f"{slug}.html"
    parts.append(("detail_page", sha256_hex(normalize_text(
        page_path.read_text(encoding="utf-8")))))

    combined = normalize_text(
        "\n".join(f"{label}\t{digest}" for label, digest in parts))
    return sha256_hex(combined)


def is_approved(slug: str) -> bool:
    """An article is approval-current iff approval.approved_version equals
    the hash computed from the CURRENT data (and hash spec versions match).
    Any post-approval change to a target makes it stale."""
    articles = load_articles()
    article = next((a for a in articles if a["slug"] == slug), None)
    if article is None:
        return False
    approval = article.get("approval")
    if not approval:
        return False
    if approval.get("hash_spec_version") != HASH_SPEC_VERSION:
        return False
    try:
        return approval.get("approved_version") == article_hash(slug)
    except (FileNotFoundError, KeyError):
        return False


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: approval_hash_en.py <slug>")
        raise SystemExit(2)
    print(article_hash(sys.argv[1]))
