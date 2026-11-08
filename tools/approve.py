# -*- coding: utf-8 -*-
"""
CigarScope Japan — 公開承認記録の補助ツール

指定した記事について、承認対象のハッシュ（仕様: tools/APPROVAL-HASH-SPEC.md）を計算し、
承認記録（approved_by / approved_date / approved_version / hash_spec_version）を
data/articles.yaml に書き込む。

これは「承認の記録」を補助するツールであり、承認そのものではない。
承認は編集者（カズ）の明示的な意思表示に基づいてのみ行うこと。
対象ファイル（本文・主張対応表・生成ページ等）が1つでも欠けていれば書き込まない。

使い方:
  python3 tools/approve.py --slug <slug> --by <承認者> --date <YYYY-MM-DD> [--root <ルート>]
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yaml

import approval_hash


def find_article_span(lines, slug):
    """articles.yaml の行リストから対象記事ブロックの (開始行, 終了行) を返す。

    開始行は '- slug: <slug>' の行、終了行は次の記事・トップレベルキーの直前。
    """
    start = None
    for i, line in enumerate(lines):
        if line.strip() == '- slug: %s' % slug:
            start = i
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        line = lines[j]
        if line.startswith('- slug:') or re.match(r'^[a-z_]+:', line):
            end = j
            break
    return start, end


def approval_block_lines(by, date, version):
    return [
        '  approval:',
        '    approved_by: %s' % by,
        "    approved_date: '%s'" % date,
        '    approved_version: %s' % version,
        '    hash_spec_version: %d' % approval_hash.HASH_SPEC_VERSION,
    ]


def write_approval(data_path, slug, by, date, version):
    """articles.yaml の対象記事に承認記録を書き込む（書式を保ったテキスト編集）。"""
    with open(data_path, encoding='utf-8') as f:
        text = f.read()
    lines = text.split('\n')
    span = find_article_span(lines, slug)
    if span is None:
        raise ValueError('記事が見つかりません: %s' % slug)
    start, end = span

    # 既存の approval 行（null またはブロック）を特定する
    appr_idx = None
    for i in range(start + 1, end):
        if re.match(r'^  approval:', lines[i]):
            appr_idx = i
            break
    block = approval_block_lines(by, date, version)
    if appr_idx is not None:
        # 既存ブロックの終わり（インデント4以上の行が続く間）を求める
        j = appr_idx + 1
        if lines[appr_idx].strip() == 'approval:':
            while j < end and (lines[j].startswith('    ') or lines[j].strip() == ''):
                if lines[j].strip() == '':
                    break
                j += 1
        lines[appr_idx:j] = block
    else:
        # status 行の後に挿入する
        ins = end
        for i in range(start + 1, end):
            if re.match(r'^  status: ', lines[i]):
                ins = i + 1
                break
        lines[ins:ins] = block

    with open(data_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--slug', required=True)
    ap.add_argument('--by', required=True, help='承認者（編集者の意思表示に基づいて記録する）')
    ap.add_argument('--date', required=True, help='承認日 YYYY-MM-DD')
    ap.add_argument('--root', default=None)
    args = ap.parse_args()

    if args.root:
        root = os.path.abspath(args.root)
    else:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(root, 'data', 'articles.yaml')

    with open(data_path, encoding='utf-8') as f:
        data = yaml.safe_load(f)
    article = None
    for a in data['articles']:
        if a['slug'] == args.slug:
            article = a
            break
    if article is None:
        print('記事が見つかりません: %s' % args.slug)
        return 1

    sources_data = None
    sources_path = os.path.join(root, 'data', 'sources.yaml')
    if os.path.isfile(sources_path):
        with open(sources_path, encoding='utf-8') as f:
            sources_data = yaml.safe_load(f)

    try:
        version = approval_hash.compute_version(root, article, sources_data)
    except FileNotFoundError as e:
        print('承認記録を書き込めません: %s' % e)
        return 1

    write_approval(data_path, args.slug, args.by, args.date, version)
    print('承認記録を書き込みました: %s' % args.slug)
    print('  approved_by: %s' % args.by)
    print('  approved_date: %s' % args.date)
    print('  approved_version: %s' % version)
    print('  hash_spec_version: %d' % approval_hash.HASH_SPEC_VERSION)
    try:
        print('  site-gen ツリーハッシュ（参考値）: %s' % approval_hash.tree_hash(root))
    except Exception:
        pass
    return 0


if __name__ == '__main__':
    sys.exit(main())
