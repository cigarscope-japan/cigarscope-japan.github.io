#!/usr/bin/env python3
# CigarScope Japan — EN edition acceptance tests (Stage B plan v2.2).
# T1 approval registers and validates; T2 approval-write invariance;
# T3 body change detected; T4 claims change detected; T5 source change
# detected; T6 YAML representation invariance; T7 deterministic build;
# T8 template change reflected in the article hash; T9 clean-copy
# rebuild produces identical hashes. Destructive tests run on throwaway
# copies; the real tree is never mutated.
from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SLUG = "feral-flying-pig"
results: list[tuple[str, bool, str]] = []


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def hash_of(copy: Path, slug: str = SLUG) -> str:
    r = run([sys.executable, "en-admin/tools/approval_hash_en.py", slug], copy)
    return r.stdout.strip()


def is_approved(copy: Path, slug: str = SLUG) -> bool:
    code = (f"import sys; sys.path.insert(0, {str(copy / 'en-admin/tools')!r}); "
            f"import approval_hash_en as ah; print(ah.is_approved({slug!r}))")
    r = run([sys.executable, "-c", code], copy)
    return r.stdout.strip() == "True"


def approve(copy: Path, slug: str = SLUG) -> None:
    r = run([sys.executable, "en-admin/tools/approve-en.py", slug,
             "Test Approver"], copy)
    assert r.returncode == 0, r.stderr


def build(copy: Path) -> None:
    r = run([sys.executable, "en-admin/tools/build-en.py"], copy)
    assert r.returncode == 0, r.stderr


def tree_digest(base: Path) -> str:
    h = hashlib.sha256()
    for p in sorted((base / "site/en").rglob("*")):
        if p.is_file():
            h.update(str(p.relative_to(base)).encode())
            h.update(p.read_bytes())
    sm = base / "site/sitemap.xml"
    if sm.exists():
        h.update(b"sitemap.xml")
        h.update(sm.read_bytes())
    return h.hexdigest()


def record(name: str, ok: bool, note: str = "") -> None:
    results.append((name, ok, note))
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {note}")


def fresh_copy(tmp: Path, name: str) -> Path:
    dst = tmp / name
    shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns(
        "__pycache__", "tests"))
    return dst


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="en-tests-"))
    try:
        # --- T1/T2 on copy A ---
        a = fresh_copy(tmp, "a")
        build(a)
        before = hash_of(a)
        approve(a)
        record("T1 approval registers and validates", is_approved(a))
        record("T2 approval write does not change the hash",
               hash_of(a) == before and is_approved(a))

        # --- T3 body change ---
        body = a / "en-admin/src/bodies" / f"{SLUG}.html"
        orig = body.read_text(encoding="utf-8")
        body.write_text(orig + "<p>Change.</p>\n", encoding="utf-8")
        record("T3 body change makes approval stale", not is_approved(a))
        body.write_text(orig, encoding="utf-8")
        build(a)
        record("T3-restore approval current again", is_approved(a))

        # --- T4 claims change ---
        claims = a / "audits/claims-en" / f"{SLUG}.md"
        orig = claims.read_text(encoding="utf-8")
        claims.write_text(orig + "\nNote: wording adjusted.\n", encoding="utf-8")
        record("T4 claims change makes approval stale", not is_approved(a))
        claims.write_text(orig, encoding="utf-8")
        record("T4-restore approval current again", is_approved(a))

        # --- T5 source change (registry record) ---
        reg = a / "en-admin/data/sources-en.yaml"
        orig = reg.read_text(encoding="utf-8")
        reg.write_text(orig.replace("corrections track record",
                                    "corrections record"), encoding="utf-8")
        record("T5 source-registry change makes approval stale",
               not is_approved(a))
        reg.write_text(orig, encoding="utf-8")
        record("T5-restore approval current again", is_approved(a))

        # --- T6 YAML representation invariance ---
        code = (
            "import yaml, pathlib; "
            "p = pathlib.Path('en-admin/data/articles-en.yaml'); "
            "doc = yaml.safe_load(p.read_text(encoding='utf-8')); "
            "p.write_text(yaml.safe_dump(doc, allow_unicode=True, "
            "sort_keys=True, default_flow_style=False), encoding='utf-8')")
        r = run([sys.executable, "-c", code], a)
        assert r.returncode == 0, r.stderr
        record("T6 YAML reformat (key order/style) keeps the hash",
               hash_of(a) == before and is_approved(a))

        # --- T7 deterministic build ---
        d1 = tree_digest(a)
        build(a)
        record("T7 rebuilding produces identical output bytes",
               tree_digest(a) == d1)

        # --- T8 template change reflection ---
        tpl = a / "en-admin/TEMPLATES/article.html"
        orig = tpl.read_text(encoding="utf-8")
        tpl.write_text(orig.replace('<article class="article">',
                                    '<article class="article"><!-- v2 -->'),
                       encoding="utf-8")
        build(a)
        record("T8 template change changes the article hash",
               hash_of(a) != before and not is_approved(a))
        tpl.write_text(orig, encoding="utf-8")
        build(a)

        # --- T9 clean-copy rebuild identity ---
        b = fresh_copy(tmp, "b")
        build(b)
        record("T9 clean copy rebuild: identical tree digest",
               tree_digest(b) == tree_digest(ROOT))
        record("T9 clean copy rebuild: identical article hash",
               hash_of(b) == hash_of(ROOT))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    failed = [r for r in results if not r[1]]
    print(f"\n== {len(results) - len(failed)}/{len(results)} passed ==")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
