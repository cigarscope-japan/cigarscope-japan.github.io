#!/usr/bin/env python3
# CigarScope Japan — EN edition approval helper.
# Records a publication approval on an article: computes the approval
# hash over the CURRENT data and writes
#   approval: {approved_by, approved_date, approved_version, hash_spec_version}
# into articles-en.yaml. Run ONLY on the publisher's explicit instruction.
# After approval, any change to a hashed target makes the approval stale
# (check-en.py reports it; publication of a stale article is blocked).
from __future__ import annotations

import datetime
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import approval_hash_en as ah  # noqa: E402

DATA = ah.DATA


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: approve-en.py <slug> <approved_by>")
        return 2
    slug, approver = sys.argv[1], sys.argv[2]
    doc = yaml.safe_load(DATA.read_text(encoding="utf-8"))
    articles = doc["articles"] if isinstance(doc, dict) else doc
    article = next((a for a in articles if a["slug"] == slug), None)
    if article is None:
        print(f"article not found: {slug}")
        return 1
    version = ah.article_hash(slug)
    article["approval"] = {
        "approved_by": approver,
        "approved_date": datetime.date.today(),
        "approved_version": version,
        "hash_spec_version": ah.HASH_SPEC_VERSION,
    }
    DATA.write_text(
        yaml.safe_dump(doc, allow_unicode=True, sort_keys=False,
                       default_flow_style=False),
        encoding="utf-8")
    print(f"approved {slug}: {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
