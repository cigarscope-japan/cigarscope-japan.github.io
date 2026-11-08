# -*- coding: utf-8 -*-
"""
CigarScope Japan — 公開承認ハッシュの計算（仕様: tools/APPROVAL-HASH-SPEC.md）

hash_spec_version: 1
approve.py（承認記録）と check.py（照合）が共有する唯一の実装。
"""
import hashlib
import os

import yaml

HASH_SPEC_VERSION = 1

# 対象の固定順序とラベル
TARGET_LABELS = ('article_record', 'body', 'claims', 'source', 'detail_page')


def normalize_text(text):
    """UTF-8 テキストを LF 改行・末尾改行ありに正規化する。"""
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    if not text.endswith('\n'):
        text += '\n'
    return text


def normalize_bytes(raw):
    return normalize_text(raw.decode('utf-8')).encode('utf-8')


def sha256_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical_yaml(obj):
    """オブジェクトを決定的な YAML テキスト（キーソート済み）にして正規化する。"""
    text = yaml.safe_dump(obj, allow_unicode=True, sort_keys=True,
                          default_flow_style=False)
    return normalize_text(text).encode('utf-8')


def _read_normalized(path):
    with open(path, 'rb') as f:
        return normalize_bytes(f.read())


def compute_targets(root, article, sources_data):
    """承認ハッシュの対象ごとの (ラベル, ハッシュ) を固定順序で返す。

    対象ファイルが欠けている場合は FileNotFoundError を送出する。
    """
    slug = article['slug']
    targets = []

    # 1. 記事レコード（approval キー自体は除く）
    record = {k: v for k, v in article.items() if k != 'approval'}
    targets.append(('article_record', sha256_bytes(canonical_yaml(record))))

    # 2. 本文
    body_path = os.path.join(root, 'src', 'bodies', slug + '.html')
    if not os.path.isfile(body_path):
        raise FileNotFoundError('本文ファイルがありません: %s' % body_path)
    targets.append(('body', sha256_bytes(_read_normalized(body_path))))

    # 3. 主張対応表
    claims_path = os.path.join(root, 'audits', 'claims', slug + '.md')
    if not os.path.isfile(claims_path):
        raise FileNotFoundError('主張対応表がありません: %s' % claims_path)
    targets.append(('claims', sha256_bytes(_read_normalized(claims_path))))

    # 4. 出典情報（記事の出典項目＋レジストリの該当レコード）
    registry = None
    for s in (sources_data or {}).get('sources', []):
        if s.get('name') == article.get('source_name'):
            registry = s
            break
    source_obj = {
        'article_source': {k: article.get(k) for k in
                           ('source_name', 'source_url', 'source_checked',
                            'source_type')},
        'registry': registry,
    }
    targets.append(('source', sha256_bytes(canonical_yaml(source_obj))))

    # 5. 生成された詳細ページ
    page_path = os.path.join(root, 'site-gen', 'news', slug + '.html')
    if not os.path.isfile(page_path):
        raise FileNotFoundError('生成された詳細ページがありません: %s' % page_path)
    targets.append(('detail_page', sha256_bytes(_read_normalized(page_path))))

    return targets


def combine_targets(targets):
    lines = ['%s\t%s' % (label, h) for label, h in targets]
    blob = normalize_text('\n'.join(lines)).encode('utf-8')
    return sha256_bytes(blob)


def compute_version(root, article, sources_data):
    """approved_version（対象を連結した SHA-256）を返す。"""
    return combine_targets(compute_targets(root, article, sources_data))


def tree_hash(root):
    """site-gen 全体のツリーハッシュ（参考値、拘束力なし）。"""
    out = os.path.join(root, 'site-gen')
    entries = []
    for dirpath, _dirs, files in os.walk(out):
        for fn in sorted(files):
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, out)
            with open(p, 'rb') as f:
                entries.append('%s\t%s' % (rel, sha256_bytes(f.read())))
    return sha256_bytes(normalize_text('\n'.join(sorted(entries))).encode('utf-8'))
