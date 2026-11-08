# -*- coding: utf-8 -*-
"""
CigarScope Japan — 編集管理基盤の必須テスト

実データのコピー（フィクスチャツリー）に対して検証する。実ツリーへの変更は
テスト8（build.py の再生成と比較）のみで、生成物は従来とバイト一致する前提。
結果は tools/TEST-REPORT.md に保存する。

テスト項目:
  1. 二次報道のみの主張を正しく検出する（主張対応表からの機械集計）
  2. 報道ベース明示のフラグだけでは公開条件を満たさない
     （帰属表現なし→不合格／人間確認の記録なし→不合格／両方あり→合格）
  3. 主張対応表に未解決行があれば公開不可になる
  4. Cigar Journal の不使用確認が機能する（混入→不合格、クリーン→合格）
  5. 承認後に対象ファイルを変更するとハッシュ不一致になる
  6. 再承認するまで公開可能状態に戻らない（変更→不合格のまま、再承認→合格）
  7. バックアップから正常に復元できる（特集3本＋articles.yaml の照合）
  8. 実ツリーの生成29ファイルが従来（原稿）とバイト単位で一致する
"""
import hashlib
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tarfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(BASE, 'tools')
BACKUP = os.path.expanduser(
    '~/workspace/backups/cigar-site-backup-2026-11-08-prefoundation.tar.gz')
# バックアップ作成時点（移行前）の data/articles.yaml の SHA-256。
# 移行で現行ファイルは正当に変化しているため、復元確認はこの記録値と照合する。
BACKUP_ARTICLES_YAML_SHA256 = \
    '1b7f6190b6a2515d00473eeae5cc038ddbee053dd7e601ee9002ee0e07da59b1'

TMP = '/tmp/cigarscope-foundation-tests'
PRISTINE = os.path.join(TMP, 'pristine')
PREPARED = os.path.join(TMP, 'prepared')
SLUG = 'fixture-standard-001'

results = []


def record(name, ok, evidence):
    results.append((name, ok, evidence))
    print('[%s] %s' % ('PASS' if ok else 'FAIL', name))
    for e in evidence:
        print('       - %s' % e)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()


def copy_tree(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst,
                    ignore=shutil.ignore_patterns('logo-candidates', '__pycache__'))


def run_check(root):
    rc, out = run([sys.executable, os.path.join(TOOLS, 'check.py'),
                   '--root', root])
    items = {}
    for m in re.finditer(r'\[(PASS|FAIL)\] (\d+)\.', out):
        items[int(m.group(2))] = (m.group(1) == 'PASS')
    return rc, items, out


def run_build(root):
    return run([sys.executable, os.path.join(root, 'tools', 'build.py')])


def run_approve(root):
    return run([sys.executable, os.path.join(TOOLS, 'approve.py'),
                '--root', root, '--slug', SLUG,
                '--by', 'テスト承認者', '--date', '2026-11-08'])


FIXTURE_ARTICLE_YAML = """- slug: fixture-standard-001
  title: 【テスト】フィクスチャ標準記事
  summary: 編集管理基盤のテスト用フィクスチャ記事です。
  description: 編集管理基盤のテスト用フィクスチャ記事です。
  category: 市場・流通
  country: キューバ
  country_id: cuba
  country_en: CUBA
  country_ids:
  - cuba
  maker: Habanos S.A.（ハバノス）
  maker_id: habanos
  source_name: Halfwheel
  source_url: https://halfwheel.com/
  source_checked: 原文確認済み
  source_date: '2026-11-07'
  publish_date: '2026-11-08'
  status: published
  flow_version: standard
  source_type: secondary
  history: []
  approval: null
  reported_framing_editorial:
    checked_by: テスト編集者
    date: '2026-11-08'
  breaking: false
  top_story: null
  image: null
  related:
  - bvi-habanos
  - fifth-avenue
  top_country_blocks:
  - cuba
  mini_titles:
    cuba: 【テスト】フィクスチャ標準記事
  brand_title: null
  market_title: 【テスト】フィクスチャ標準記事（市場面）
"""

FIXTURE_BODY = """<div class="article-body">
<p>テスト商会は新製品の価格を1本10ドルに設定した。Halfwheelが報じたところによると、発売は2026年12月を予定している。</p>
<p>生産数は5,000本限定と、メーカー公式発表で確認した。</p>
</div>
"""

FIXTURE_CLAIMS = """# 主張対応表: fixture-standard-001

- 対象記事（slug）: fixture-standard-001
- 出典（媒体名／原文URL）: Halfwheel / https://halfwheel.com/

| 主張ID | 記事内の場所 | 主張の内容 | 主張の種別 | 原文の該当箇所 | 出典種別 | 裏付け区分 | 照合結果 |
|---|---|---|---|---|---|---|---|
| 1 | 第1段落 | 価格は1本10ドル | 数値 | Halfwheel 記事冒頭 | secondary | 二次報道のみ | 一致 |
| 2 | 第2段落 | 生産数は5,000本限定 | 数値 | メーカー公式発表 | primary | 一次情報で確認済み | 一致 |
"""

FIXTURE_CJ_CHECK = """# Cigar Journal 不使用確認記録: fixture-standard-001

- 対象記事（slug）: fixture-standard-001
- 確認者: テスト確認者
- 確認日: 2026-11-08
- 確認方法: 記事データと主張対応表の出典欄、本文、出典リンクに Cigar Journal が無いことを照合した
- 結果: 使用なし
"""


def prepare_fixture():
    """実ツリーのコピーに standard のフィクスチャ記事を構築し、承認まで済ませる。"""
    copy_tree(BASE, PRISTINE)
    copy_tree(PRISTINE, PREPARED)
    with open(os.path.join(PREPARED, 'data', 'articles.yaml'),
              'a', encoding='utf-8', newline='\n') as f:
        f.write(FIXTURE_ARTICLE_YAML)
    with open(os.path.join(PREPARED, 'src', 'bodies', SLUG + '.html'),
              'w', encoding='utf-8', newline='\n') as f:
        f.write(FIXTURE_BODY)
    with open(os.path.join(PREPARED, 'audits', 'claims', SLUG + '.md'),
              'w', encoding='utf-8', newline='\n') as f:
        f.write(FIXTURE_CLAIMS)
    with open(os.path.join(PREPARED, 'audits', 'cj-checks', SLUG + '.md'),
              'w', encoding='utf-8', newline='\n') as f:
        f.write(FIXTURE_CJ_CHECK)
    rc, out = run_build(PREPARED)
    if rc != 0:
        raise RuntimeError('フィクスチャの生成に失敗: %s' % out)
    rc, out = run_approve(PREPARED)
    if rc != 0:
        raise RuntimeError('フィクスチャの承認記録に失敗: %s' % out)


def work_copy(name):
    dst = os.path.join(TMP, name)
    copy_tree(PREPARED, dst)
    return dst


def replace_in(path, old, new):
    with open(path, encoding='utf-8') as f:
        text = f.read()
    assert old in text, '%s に対象文字列がありません' % path
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text.replace(old, new, 1))


def main():
    if os.path.exists(TMP):
        shutil.rmtree(TMP)
    os.makedirs(TMP)
    prepare_fixture()

    # ---- テスト1: 二次報道のみの主張の機械検出
    spec = importlib.util.spec_from_file_location(
        'check_mod', os.path.join(TOOLS, 'check.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    rows = mod.parse_claims_table(
        os.path.join(PREPARED, 'audits', 'claims', SLUG + '.md'))
    sec = mod.secondary_only_rows(rows or [])
    ok = rows is not None and len(rows) == 2 and len(sec) == 1 \
        and sec[0].get('主張ID') == '1'
    record('1. 二次報道のみの主張を正しく検出する', ok,
           ['主張対応表 %d 行を解析、二次報道のみは主張ID %s の %d 件を検出'
            % (len(rows or []), [r.get('主張ID') for r in sec], len(sec))])

    # ---- テスト2: 報道ベース明示フラグの検証
    ev = []
    rc0, items0, _ = run_check(PREPARED)
    ok_happy = (rc0 == 0 and items0.get(11, False))
    ev.append('両方あり（帰属表現＋人間確認の記録）: check 終了コード %d、項目11 %s'
              % (rc0, 'PASS' if items0.get(11) else 'FAIL'))
    w = work_copy('work-2a')
    replace_in(os.path.join(w, 'src', 'bodies', SLUG + '.html'),
               'Halfwheelが報じたところによると、', '')
    run_build(w)
    _rc, items2a, _ = run_check(w)
    ok_2a = items2a.get(11) is False
    ev.append('帰属表現なし: 項目11 が FAIL になることを確認')
    w = work_copy('work-2b')
    replace_in(os.path.join(w, 'data', 'articles.yaml'),
               '  reported_framing_editorial:\n'
               '    checked_by: テスト編集者\n'
               "    date: '2026-11-08'\n", '')
    _rc, items2b, _ = run_check(w)
    ok_2b = items2b.get(11) is False
    ev.append('人間確認の記録なし: 項目11 が FAIL になることを確認')
    record('2. 報道ベース明示のフラグだけでは公開条件を満たさない',
           ok_happy and ok_2a and ok_2b, ev)

    # ---- テスト3: 未解決行があれば公開不可
    w = work_copy('work-3')
    replace_in(os.path.join(w, 'audits', 'claims', SLUG + '.md'),
               '一次情報で確認済み | 一致', '一次情報で確認済み | 相違あり')
    rc3, items3, _ = run_check(w)
    record('3. 主張対応表に未解決行があれば公開不可になる',
           items3.get(10) is False and rc3 != 0,
           ['照合結果を「相違あり」に変更: 項目10 が FAIL、check 終了コード %d' % rc3])

    # ---- テスト4: CJ 不使用確認
    w = work_copy('work-4')
    with open(os.path.join(w, 'src', 'bodies', SLUG + '.html'),
              'a', encoding='utf-8', newline='\n') as f:
        f.write('<p>Cigar Journal への言及を含む混入テスト段落。</p>\n')
    run_build(w)
    _rc, items4, _ = run_check(w)
    _rc0, items0b, _ = run_check(PREPARED)
    record('4. Cigar Journal の不使用確認が機能する',
           items4.get(8) is False and items0b.get(8) is True,
           ['混入フィクスチャ: 項目8 が FAIL', 'クリーンなフィクスチャ: 項目8 が PASS'])

    # ---- テスト5: 承認後の変更でハッシュ不一致
    w = work_copy('work-56')
    _rc, items_pre, _ = run_check(w)
    pre_ok = items_pre.get(13) is True
    replace_in(os.path.join(w, 'src', 'bodies', SLUG + '.html'),
               '生産数は5,000本限定と', '生産数は6,000本限定と')
    run_build(w)
    _rc, items5, out5 = run_check(w)
    ok5 = pre_ok and items5.get(13) is False and '再承認待ち' in out5
    record('5. 承認後に対象ファイルを変更するとハッシュ不一致になる', ok5,
           ['承認済み状態では項目13 PASS、本文変更後は項目13 FAIL（再承認待ち）'])

    # ---- テスト6: 再承認するまで戻らない
    _rc, items6a, _ = run_check(w)
    still_fail = items6a.get(13) is False
    rc_ap, out_ap = run_approve(w)
    rc6, items6, _ = run_check(w)
    ok6 = still_fail and rc_ap == 0 and items6.get(13) is True and rc6 == 0
    record('6. 再承認するまで公開可能状態に戻らない', ok6,
           ['変更後の再検査でも項目13 FAIL のまま、再承認後に項目13 PASS・総合判定も合格（終了コード %d）' % rc6])

    # ---- テスト7: バックアップからの復元
    restore = os.path.join(TMP, 'restore')
    os.makedirs(restore)
    with tarfile.open(BACKUP, 'r:gz') as tf:
        tf.extractall(restore)
    ev7 = []
    ok7 = True
    for name in ('joya.html', 'padron.html', 'opusx.html'):
        got = sha256(os.path.join(restore, 'cigar-site', 'features', name))
        want = sha256(os.path.join(BASE, 'features', name))
        ev7.append('features/%s: 復元 %s… / 現行 %s… %s'
                   % (name, got[:12], want[:12], '一致' if got == want else '不一致'))
        ok7 = ok7 and got == want
    got_yaml = sha256(os.path.join(restore, 'cigar-site', 'data', 'articles.yaml'))
    ev7.append('data/articles.yaml: 復元 %s… / バックアップ作成時の記録値 %s… %s'
               % (got_yaml[:12], BACKUP_ARTICLES_YAML_SHA256[:12],
                  '一致' if got_yaml == BACKUP_ARTICLES_YAML_SHA256 else '不一致'))
    ok7 = ok7 and got_yaml == BACKUP_ARTICLES_YAML_SHA256
    record('7. バックアップから正常に復元できる', ok7, ev7)

    # ---- テスト8: 実ツリー生成29ファイルのバイト一致
    rc8, out8 = run([sys.executable, os.path.join(TOOLS, 'build.py')])
    gen_dir = os.path.join(BASE, 'site-gen')
    gen_files = []
    for root, _dirs, files in os.walk(gen_dir):
        for fn in files:
            gen_files.append(os.path.relpath(os.path.join(root, fn), gen_dir))
    diffs = []
    for rel in sorted(gen_files):
        counterpart = 'index-v2.html' if rel == 'index.html' else rel
        a = os.path.join(gen_dir, rel)
        b = os.path.join(BASE, counterpart)
        if not os.path.isfile(b) or sha256(a) != sha256(b):
            diffs.append(rel)
    ok8 = rc8 == 0 and len(gen_files) == 29 and not diffs
    record('8. 既存29ファイルの生成結果が従来とバイト単位で一致する', ok8,
           ['生成 %d ファイル、原稿との不一致 %d 件%s'
            % (len(gen_files), len(diffs), ('（%s）' % ', '.join(diffs)) if diffs else '')])

    return finish()


def finish():
    all_ok = all(ok for _n, ok, _e in results)
    lines = ['# 編集管理基盤テスト結果（TEST-REPORT）', '']
    lines.append('実行: tools/run_tests.py（フィクスチャは実データのコピーを /tmp に作成）')
    lines.append('')
    for name, ok, evidence in results:
        lines.append('## [%s] %s' % ('合格' if ok else '不合格', name))
        for e in evidence:
            lines.append('- %s' % e)
        lines.append('')
    lines.append('## 総合判定: %s' % ('全テスト合格' if all_ok else '不合格のテストあり'))
    lines.append('')
    with open(os.path.join(TOOLS, 'TEST-REPORT.md'), 'w',
              encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))
    print('総合判定: %s' % ('全テスト合格' if all_ok else '不合格のテストあり'))
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())
