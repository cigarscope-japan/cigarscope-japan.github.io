# -*- coding: utf-8 -*-
"""
CigarScope Japan — 公開前検査スクリプト（第2段階＋編集管理基盤）

対象: site-gen/（tools/build.py の生成物）と data/articles.yaml 等の編集管理データ。
1項目でも不合格なら終了コード非ゼロで終了し、公開手順に進めない。
結果は標準出力と <root>/tools/CHECK-REPORT.md に出力する。

使い方: python3 tools/check.py [--root <対象ツリーのルート>]
  --root を省略すると、このスクリプトのあるツリー自体を対象にする。
  テストではコピーしたフィクスチャツリーに対して実行できる。

記事の flow_version による扱い:
  - legacy（既存8記事）: 新ゲート（9〜13）は警告扱い。移行は別途承認。
  - standard（今後の新規記事）: 新ゲートは全て必須。不合格なら公開不可。

検査項目:
  1. href="#" が全生成ページで 0 件
  2. 内部リンク・画像・CSS の参照が全て実ファイルに解決する
  3. draft 記事の slug が生成物のどこにも現れない
  4. features/ 3本のチェックサムがバックアップ時点のベースラインと一致
  5. myfather への言及・リンクが生成物に無い
  6. published 記事の品質ゲート（出典URL・原文確認済み・必須項目）
  7. 決定的生成（build.py を2回実行し全生成ファイルのハッシュが完全一致）
  8. Cigar Journal の不使用（文字列走査: articles.yaml・src/bodies・site-gen/news）
  9. 情報源レジストリ（standard: source_name の登録必須／除外媒体の使用禁止）
 10. 主張対応表（standard published: 必須、未解決行があれば公開不可）
 11. 報道ベース明示ゲート（standard published: 機械条件＋人間の編集確認の両方が必要）
 12. Cigar Journal 不使用確認記録（standard published: cj-checks の記録が必須）
 13. 公開承認記録（standard published: approval 必須、ハッシュ不一致は再承認待ち）
 14. 訂正履歴の整合性（standard: 本文の訂正表記と history の対応）
"""
import argparse
import hashlib
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yaml

import approval_hash

FEATURES_BASELINE = {
    'joya.html': 'acd326a615bbf063d201c098187a242cf2051d9bd0db046f74d8a3a5862034d6',
    'padron.html': 'fdbc456b1f8438e556c4a7062683bc2c54683e8f25f1ce9e9757396fe907311c',
    'opusx.html': 'dfd1ed86bfb92d4f6f092488e99bed2cd959bcc48f851a4d31e3ee391ae3ef8c',
}

# 報道ベース明示の機械検査で使う帰属表現の定義リスト（近似であり、十分さは人間が確認する）
ATTRIBUTION_EXPRESSIONS = ('によると', '報じた', '報じられ', '伝えられ',
                           'が伝えた', 'の報道')

UNRESOLVED_CLAIM_RESULTS = ('相違あり', '対応箇所なし')

results = []   # (項目名, 合否, 詳細リスト)
warnings = []  # legacy 移行警告など、合否に影響しない注意


def record(name, ok, details=None):
    results.append((name, ok, details or []))
    print('[%s] %s' % ('PASS' if ok else 'FAIL', name))
    for d in (details or []):
        print('       - %s' % d)


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()


def read_text(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


# ---------------------------------------------------------------- 主張対応表
def parse_claims_table(path):
    """主張対応表（Markdown テーブル）を読み、行の dict のリストを返す。

    ヘッダー名で列を対応付けるため、列順の変更に耐える。
    ファイルが無い・テーブルが無い場合は None を返す。
    """
    if not os.path.isfile(path):
        return None
    lines = read_text(path).split('\n')
    header = None
    rows = []
    for line in lines:
        s = line.strip()
        if not s.startswith('|'):
            if header is not None and rows:
                break
            continue
        cells = [c.strip() for c in s.strip('|').split('|')]
        if header is None:
            if '主張ID' in cells and '照合結果' in cells:
                header = cells
            continue
        if all(set(c) <= set('-: ') for c in cells):
            continue  # 罫線行
        if len(cells) != len(header):
            continue
        row = dict(zip(header, cells))
        if not row.get('主張ID'):
            continue
        rows.append(row)
    if header is None:
        return None
    return rows


def secondary_only_rows(rows):
    """裏付け区分が「二次報道のみ」の行を返す（機械集計）。"""
    return [r for r in rows if '二次報道のみ' in (r.get('裏付け区分') or '')]


def unresolved_rows(rows):
    """照合結果が未解決（相違あり／対応箇所なし／空欄）の行を返す。"""
    out = []
    for r in rows:
        v = (r.get('照合結果') or '').strip()
        if v == '' or v in UNRESOLVED_CLAIM_RESULTS:
            out.append(r)
    return out


def body_paragraphs(body_html):
    """本文 HTML から段落テキスト（タグ除去済み）のリストを返す。"""
    paras = re.findall(r'<p\b[^>]*>(.*?)</p>', body_html, re.S)
    texts = []
    for p in paras:
        t = re.sub(r'<[^>]+>', '', p)
        texts.append(re.sub(r'\s+', '', t))
    return texts


def locate_paragraph(paras, row):
    """主張行の「記事内の場所」から対象段落を特定する。見つからなければ None。"""
    place = row.get('記事内の場所') or ''
    m = re.search(r'第\s*(\d+)\s*段落', place)
    if m:
        idx = int(m.group(1)) - 1
        if 0 <= idx < len(paras):
            return paras[idx]
        return None
    key = re.sub(r'\s+', '', row.get('主張の内容') or '')[:12]
    if key:
        for p in paras:
            if key in p:
                return p
    return None


# ---------------------------------------------------------------- メイン
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default=None,
                    help='対象ツリーのルート（省略時はこのスクリプトのあるツリー）')
    args = ap.parse_args()
    if args.root:
        base = os.path.abspath(args.root)
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(base, 'site-gen')
    data_path = os.path.join(base, 'data', 'articles.yaml')
    report_path = os.path.join(base, 'tools', 'CHECK-REPORT.md')
    build_path = os.path.join(base, 'tools', 'build.py')

    with open(data_path, encoding='utf-8') as f:
        data = yaml.safe_load(f)
    articles = data['articles']
    published = [a for a in articles if a.get('status') == 'published']
    drafts = [a for a in articles if a.get('status') != 'published']
    std_published = [a for a in published if a.get('flow_version') == 'standard']
    legacy_published = [a for a in published if a.get('flow_version') != 'standard']

    sources_data = None
    sources_path = os.path.join(base, 'data', 'sources.yaml')
    if os.path.isfile(sources_path):
        with open(sources_path, encoding='utf-8') as f:
            sources_data = yaml.safe_load(f)
    exclusions_data = None
    exclusions_path = os.path.join(base, 'data', 'exclusions.yaml')
    if os.path.isfile(exclusions_path):
        with open(exclusions_path, encoding='utf-8') as f:
            exclusions_data = yaml.safe_load(f)

    def gen_files():
        out = []
        for root, _dirs, files in os.walk(out_dir):
            for fn in sorted(files):
                out.append(os.path.join(root, fn))
        return sorted(out)

    if not os.path.isdir(out_dir):
        record('生成物の存在', False, ['site-gen/ がありません。先に tools/build.py を実行してください'])
        return finish(report_path)

    html_files = [p for p in gen_files() if p.endswith('.html')]

    # 1. href="#"
    bad = []
    for p in html_files:
        n = read_text(p).count('href="#"')
        if n:
            bad.append('%s: %d件' % (os.path.relpath(p, out_dir), n))
    record('1. href="#" が 0 件', not bad, bad or ['対象 %d ページ全て 0 件' % len(html_files)])

    # 2. 内部参照の解決
    unresolved = []
    checked = 0
    for p in html_files:
        rel = os.path.relpath(p, out_dir)
        text = read_text(p)
        for ref in re.findall(r'(?:href|src)="([^"]+)"', text):
            if ref.startswith(('http://', 'https://', 'mailto:', 'data:')):
                continue
            filepart, _, frag = ref.partition('#')
            if not filepart:
                continue
            checked += 1
            target = os.path.normpath(os.path.join(os.path.dirname(rel), filepart))
            if not (os.path.isfile(os.path.join(out_dir, target)) or os.path.isfile(os.path.join(base, target))):
                unresolved.append('%s -> %s' % (rel, ref))
                continue
            if frag:
                tpath = os.path.join(out_dir, target)
                if not os.path.isfile(tpath):
                    tpath = os.path.join(base, target)
                if 'id="%s"' % frag not in read_text(tpath):
                    unresolved.append('%s -> %s (アンカーなし)' % (rel, ref))
    record('2. 内部リンク・画像・CSS が全て実ファイルに解決', not unresolved,
           unresolved or ['参照 %d 件を検査し全て解決' % checked])

    # 3. draft の混入
    leaks = []
    for p in gen_files():
        text = read_text(p) if p.endswith('.html') else ''
        for d in drafts:
            if d['slug'] in text or d['title'] in text:
                leaks.append('%s に draft「%s」が混入' % (os.path.relpath(p, out_dir), d['slug']))
            if os.path.basename(p) == d['slug'] + '.html':
                leaks.append('draft の詳細ページが生成されている: %s' % os.path.relpath(p, out_dir))
    record('3. draft 記事が生成物に一切現れない', not leaks,
           leaks or ['draft %d 件（%s）の slug・タイトルとも検出なし'
                     % (len(drafts), ', '.join(d['slug'] for d in drafts))])

    # 4. features ベースライン
    fbad = []
    for name, want in FEATURES_BASELINE.items():
        path = os.path.join(base, 'features', name)
        got = sha256(path) if os.path.isfile(path) else 'ファイルなし'
        if got != want:
            fbad.append('features/%s: ベースラインと不一致' % name)
    record('4. 特集3本のチェックサムがベースラインと一致', not fbad,
           fbad or ['joya / padron / opusx の3本とも一致（無変更）'])

    # 5. myfather
    mbad = []
    for p in gen_files():
        if p.endswith('.html') and 'myfather' in read_text(p).lower():
            mbad.append(os.path.relpath(p, out_dir))
    if os.path.exists(os.path.join(out_dir, 'features', 'myfather.html')):
        mbad.append('site-gen/features/myfather.html が存在')
    record('5. myfather への言及・リンクが生成物に無い', not mbad,
           mbad or ['全生成ファイルに "myfather" の文字列なし'])

    # 6. 品質ゲート
    qbad = []
    for a in published:
        for k in ('source_date', 'publish_date', 'category', 'country', 'maker'):
            if not a.get(k):
                qbad.append('%s: %s が欠落' % (a['slug'], k))
        if not a.get('source_url') or not str(a['source_url']).startswith('http'):
            qbad.append('%s: source_url がない／不正' % a['slug'])
        if a.get('source_checked') != '原文確認済み':
            qbad.append('%s: 原文未確認のため公開不可' % a['slug'])
        body = os.path.join(base, 'src', 'bodies', a['slug'] + '.html')
        if not os.path.isfile(body):
            qbad.append('%s: 本文ファイルがない' % a['slug'])
        if not os.path.isfile(os.path.join(out_dir, 'news', a['slug'] + '.html')):
            qbad.append('%s: 詳細ページが生成されていない' % a['slug'])
    record('6. published 記事の品質ゲート（出典・原文確認・必須項目）', not qbad,
           qbad or ['published %d 件全て充足' % len(published)])

    # 7. 決定的生成
    def snapshot_hashes():
        return {os.path.relpath(p, out_dir): sha256(p) for p in gen_files()}

    before = snapshot_hashes()
    r1 = subprocess.run([sys.executable, build_path], capture_output=True, text=True)
    h1 = snapshot_hashes()
    r2 = subprocess.run([sys.executable, build_path], capture_output=True, text=True)
    h2 = snapshot_hashes()
    ok = (r1.returncode == 0 and r2.returncode == 0 and h1 == h2 == before)
    det = ['生成ファイル %d 件のハッシュが、実行前・1回目・2回目で完全一致' % len(h2)] if ok else []
    if h1 != h2:
        det.append('2回の生成で差異: %s' % [k for k in h1 if h1.get(k) != h2.get(k)])
    if h1 != before:
        det.append('実行前の生成物と再生成で差異: %s' % [k for k in h1 if h1.get(k) != before.get(k)])
    if r1.returncode != 0 or r2.returncode != 0:
        det.append('build.py の実行に失敗')
    record('7. 決定的生成（同一入力から常に同一HTML）', ok, det)

    # 8. Cigar Journal の不使用（文字列走査）
    cj_patterns = ('cigar journal', 'cigarjournal')
    cj_hits = []
    scan_targets = [data_path]
    bodies_dir = os.path.join(base, 'src', 'bodies')
    if os.path.isdir(bodies_dir):
        scan_targets += [os.path.join(bodies_dir, fn)
                         for fn in sorted(os.listdir(bodies_dir)) if fn.endswith('.html')]
    news_dir = os.path.join(out_dir, 'news')
    if os.path.isdir(news_dir):
        scan_targets += [os.path.join(news_dir, fn)
                         for fn in sorted(os.listdir(news_dir)) if fn.endswith('.html')]
    for p in scan_targets:
        text = read_text(p).lower()
        for pat in cj_patterns:
            if pat in text:
                cj_hits.append('%s に "%s" を検出' % (os.path.relpath(p, base), pat))
    record('8. Cigar Journal の不使用（文字列走査）', not cj_hits,
           cj_hits or ['走査対象 %d ファイルに混入なし' % len(scan_targets)])

    # 9. 情報源レジストリ
    reg_bad = []
    registered = set()
    if sources_data:
        registered = {s.get('name') for s in sources_data.get('sources', [])}
    excluded_names = set()
    if exclusions_data:
        excluded_names = {e.get('name') for e in exclusions_data.get('exclusions', [])}
    for a in std_published:
        if a.get('source_name') not in registered:
            reg_bad.append('%s: source_name「%s」が sources.yaml に未登録'
                           % (a['slug'], a.get('source_name')))
    for a in articles:
        if a.get('flow_version') == 'standard' and a.get('source_name') in excluded_names:
            reg_bad.append('%s: 除外媒体「%s」を source_name に使用'
                           % (a['slug'], a.get('source_name')))
    for a in legacy_published:
        if a.get('source_name') not in registered:
            warnings.append('legacy: %s の source_name「%s」は未登録（移行時に要対応）'
                            % (a['slug'], a.get('source_name')))
    record('9. 情報源レジストリ（standard: 登録必須／除外媒体の使用禁止）', not reg_bad,
           reg_bad or ['standard published %d 件の出典は全て登録済み' % len(std_published)])

    # 10. 主張対応表
    claims_bad = []
    claims_by_slug = {}
    for a in std_published:
        rows = parse_claims_table(os.path.join(base, 'audits', 'claims', a['slug'] + '.md'))
        claims_by_slug[a['slug']] = rows
        if rows is None:
            claims_bad.append('%s: 主張対応表（audits/claims/%s.md）がない' % (a['slug'], a['slug']))
            continue
        un = unresolved_rows(rows)
        if un:
            claims_bad.append('%s: 未解決行 %d 件（主張ID: %s）'
                              % (a['slug'], len(un), ', '.join(r.get('主張ID', '?') for r in un)))
    if legacy_published:
        warnings.append('legacy: published %d 件の主張対応表は未作成（移行は別途承認）'
                        % len(legacy_published))
    record('10. 主張対応表（standard published: 必須・未解決行なし）', not claims_bad,
           claims_bad or ['standard published %d 件全て充足' % len(std_published)])

    # 11. 報道ベース明示ゲート（機械条件＋人間の編集確認）
    framing_bad = []
    for a in std_published:
        rows = claims_by_slug.get(a['slug'])
        if rows is None:
            framing_bad.append('%s: 主張対応表がないため報道ベース明示を検証できない' % a['slug'])
            continue
        sec = secondary_only_rows(rows)
        if not sec:
            continue  # 二次報道のみの主張がなければゲート対象外
        body_path = os.path.join(base, 'src', 'bodies', a['slug'] + '.html')
        paras = body_paragraphs(read_text(body_path)) if os.path.isfile(body_path) else []
        for r in sec:
            para = locate_paragraph(paras, r)
            if para is None:
                framing_bad.append('%s: 主張ID %s の該当段落を特定できない'
                                   % (a['slug'], r.get('主張ID')))
            elif not any(e in para for e in ATTRIBUTION_EXPRESSIONS):
                framing_bad.append('%s: 主張ID %s の段落に帰属表現がない（機械条件不合格）'
                                   % (a['slug'], r.get('主張ID')))
        page_path = os.path.join(out_dir, 'news', a['slug'] + '.html')
        if not (os.path.isfile(page_path) and a.get('source_url') in read_text(page_path)):
            framing_bad.append('%s: 詳細ページに出典表示（原文リンク）がない' % a['slug'])
        ed = a.get('reported_framing_editorial')
        if not (isinstance(ed, dict) and ed.get('checked_by') and ed.get('date')):
            framing_bad.append('%s: 人間の編集確認（reported_framing_editorial）の記録がない'
                               % a['slug'])
    record('11. 報道ベース明示ゲート（機械条件＋人間の編集確認）', not framing_bad,
           framing_bad or ['対象の standard published 全て充足'])

    # 12. CJ 不使用確認記録
    cjrec_bad = []
    for a in std_published:
        p = os.path.join(base, 'audits', 'cj-checks', a['slug'] + '.md')
        if not os.path.isfile(p):
            cjrec_bad.append('%s: 不使用確認記録（audits/cj-checks/%s.md）がない'
                             % (a['slug'], a['slug']))
            continue
        text = read_text(p)
        if a['slug'] not in text or not re.search(r'結果\s*[:：]\s*使用なし', text):
            cjrec_bad.append('%s: 不使用確認記録に「結果: 使用なし」の記載がない' % a['slug'])
    record('12. Cigar Journal 不使用確認記録（standard published: 必須）', not cjrec_bad,
           cjrec_bad or ['standard published %d 件全て記録あり' % len(std_published)])

    # 13. 公開承認記録とハッシュ照合
    appr_bad = []
    for a in std_published:
        appr = a.get('approval')
        if not isinstance(appr, dict):
            appr_bad.append('%s: 公開承認記録（approval）がない' % a['slug'])
            continue
        for k in ('approved_by', 'approved_date', 'approved_version'):
            if not appr.get(k):
                appr_bad.append('%s: approval.%s が欠落' % (a['slug'], k))
        if appr.get('hash_spec_version') != approval_hash.HASH_SPEC_VERSION:
            appr_bad.append('%s: hash_spec_version が現行仕様（%d）と異なる'
                            % (a['slug'], approval_hash.HASH_SPEC_VERSION))
        if appr.get('approved_version'):
            try:
                current = approval_hash.compute_version(base, a, sources_data)
            except FileNotFoundError as e:
                appr_bad.append('%s: 承認ハッシュの対象が欠けている（%s）' % (a['slug'], e))
                continue
            if current != appr['approved_version']:
                appr_bad.append('%s: 承認ハッシュ不一致（再承認待ち）' % a['slug'])
    if legacy_published:
        warnings.append('legacy: published %d 件の承認記録は未登録（移行は別途承認）'
                        % len(legacy_published))
    record('13. 公開承認記録（standard published: 必須・ハッシュ一致）', not appr_bad,
           appr_bad or ['standard published %d 件全て承認記録と一致' % len(std_published)])

    # 14. 訂正履歴の整合性（standard の全記事）
    hist_bad = []
    marker_re = re.compile(r'(【訂正】|class="[^"]*correction)')
    for a in articles:
        if a.get('flow_version') != 'standard':
            continue
        body_path = os.path.join(base, 'src', 'bodies', a['slug'] + '.html')
        has_marker = bool(os.path.isfile(body_path)
                          and marker_re.search(read_text(body_path)))
        hist = a.get('history') or []
        has_correction = any(isinstance(h, dict) and h.get('type') == 'correction'
                             for h in hist)
        if has_marker and not has_correction:
            hist_bad.append('%s: 本文に訂正表記があるが history に correction がない' % a['slug'])
        if has_correction and not has_marker:
            hist_bad.append('%s: history に correction があるが本文に訂正表記がない' % a['slug'])
    record('14. 訂正履歴の整合性（standard: 訂正表記と history の対応）', not hist_bad,
           hist_bad or ['standard の記事全て整合'])

    return finish(report_path)


def finish(report_path):
    all_ok = all(ok for _name, ok, _d in results)
    lines = ['# 公開前検査結果（CHECK-REPORT）', '']
    lines.append('対象: site-gen/（tools/build.py の生成物）＋ data/articles.yaml 等の編集管理データ')
    lines.append('')
    for name, ok, details in results:
        lines.append('## [%s] %s' % ('合格' if ok else '不合格', name))
        for d in details:
            lines.append('- %s' % d)
        lines.append('')
    if warnings:
        lines.append('## 注意（合否に影響しない警告）')
        for w in warnings:
            lines.append('- %s' % w)
        lines.append('')
    lines.append('## 総合判定: %s' % ('合格（全項目パス）' if all_ok else '不合格（公開手順に進めない）'))
    lines.append('')
    with open(report_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))
    print('総合判定: %s' % ('合格' if all_ok else '不合格'))
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())
