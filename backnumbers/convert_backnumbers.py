# -*- coding: utf-8 -*-
"""バックナンバー31件のステージング変換（公開しない）。
入力: bodies-draft/*.html, PHOTO-MANIFEST.md の区分
出力: articles-backnumbers.yaml, site-bodies/<slug>.html
data/articles.yaml 本体・サイト生成物には触れない。
"""
import re, os, html as htmlmod
import yaml

BASE = os.path.dirname(os.path.abspath(__file__))
DRAFTS = os.path.join(BASE, 'bodies-draft')
OUT_BODIES = os.path.join(BASE, 'site-bodies')
os.makedirs(OUT_BODIES, exist_ok=True)

EXCLUDED = {'petit-edition-selected-tobacco', 'fifth-avenue-insolvency',
            'germany-cuban-distribution-halt'}

# PHOTO-MANIFEST: 実写真あり (True) / AI生成対応 (False)
PHOTO = {
    'davidoff-year-of-the-sheep-2027': False,
    'plasencia-year-of-the-goat': True,
    'tatuaje-boris-karloff-2026': True,
    'quai-dorsay-concordia-el-2026': True,
    'cohiba-talisman-regular': True,
    'bolivar-safari-regional-africa': True,
    'ecuador-tobacco-crop-el-nino': False,
    'us-cigar-imports-2026-honduras': False,
    'world-cigar-show-dubai-2026': False,
    'habanos-executive-appointments': True,
    'marvin-shanken-obituary': True,
    'powstanie-war-bear-2026': True,
    'la-gloria-cubana-gran-legado': True,
    'black-works-killer-bee-buzz-saw-2': True,
    'gellis-piece-unique-emerald-sky': False,
    'villiger-taa-exclusive-2026': False,
    'jc-newman-cuesta-rey-rebrand': True,
    'fratello-sweden-kind-cigars': False,
    'intertabac-2027-dates': True,
    'domain-cigars-test-blend-portal': True,
    'checkpoints-2026-11-06': False,
    'crowned-heads-las-calaveras-decimo-2026': True,
    'san-luis-rey-eiroa-30th-maduro': True,
    'dunbarton-shokai-bushido': True,
    'plasencia-holiday-collection-2026': True,
    'brolo-cigar-co-debut': True,
    'oliva-melanio-anio-2026': True,
    'stg-hoyo-epicure-delisting': True,
    'selected-tobacco-madrid-hq': True,
    'big-smoke-las-vegas-30th': True,
    'checkpoints-2026-11-07': False,
}

# 号の日付 / カテゴリ / 国 / メーカーの判断表
# (publish_date, category, country, country_id, country_en, maker, maker_id)
META = {
    'davidoff-year-of-the-sheep-2027': ('2026-11-05', '限定品', 'ドミニカ共和国', 'dominican', 'DOMINICAN REPUBLIC', 'Davidoff（ダビドフ）', 'davidoff'),
    'plasencia-year-of-the-goat': ('2026-11-05', '限定品', 'ニカラグア', 'nicaragua', 'NICARAGUA', 'Plasencia（プラセンシア）', 'plasencia'),
    'tatuaje-boris-karloff-2026': ('2026-11-05', '限定品', 'ニカラグア', 'nicaragua', 'NICARAGUA', 'Tatuaje（タトゥアヘ）', 'tatuaje'),
    'quai-dorsay-concordia-el-2026': ('2026-11-05', '限定品', 'キューバ', 'cuba', 'CUBA', 'Habanos S.A.（ハバノス）', 'habanos'),
    'cohiba-talisman-regular': ('2026-11-05', '新製品', 'キューバ', 'cuba', 'CUBA', 'Habanos S.A.（ハバノス）', 'habanos'),
    'bolivar-safari-regional-africa': ('2026-11-05', '限定品', 'キューバ', 'cuba', 'CUBA', 'Habanos S.A.（ハバノス）', 'habanos'),
    'ecuador-tobacco-crop-el-nino': ('2026-11-05', '市場・流通', 'エクアドル', None, 'ECUADOR', 'A.S.P. Enterprises（A.S.P.エンタープライゼズ）', 'asp-enterprises'),
    'us-cigar-imports-2026-honduras': ('2026-11-05', '市場・流通', 'アメリカ', 'usa', 'UNITED STATES', '（業界統計）', None),
    'world-cigar-show-dubai-2026': ('2026-11-05', '経営', 'ドバイ（アラブ首長国連邦）', None, 'UNITED ARAB EMIRATES', 'World Cigar Show（ワールド・シガー・ショー）', 'world-cigar-show'),
    'habanos-executive-appointments': ('2026-11-05', '経営', 'キューバ', 'cuba', 'CUBA', 'Habanos S.A.（ハバノス）', 'habanos'),
    'marvin-shanken-obituary': ('2026-11-05', '経営', 'アメリカ', 'usa', 'UNITED STATES', 'M. Shanken Communications（M.シャンケン・コミュニケーションズ）', 'm-shanken'),
    'powstanie-war-bear-2026': ('2026-11-06', '限定品', 'ニカラグア', 'nicaragua', 'NICARAGUA', 'Powstanie（ポウスタニエ）', 'powstanie'),
    'la-gloria-cubana-gran-legado': ('2026-11-06', '限定品', 'ドミニカ共和国', 'dominican', 'DOMINICAN REPUBLIC', 'La Gloria Cubana（ラ・グロリア・クバーナ）', 'la-gloria-cubana'),
    'black-works-killer-bee-buzz-saw-2': ('2026-11-06', '限定品', 'ニカラグア', 'nicaragua', 'NICARAGUA', 'Black Works Studio（ブラック・ワークス・スタジオ）', 'black-works-studio'),
    'gellis-piece-unique-emerald-sky': ('2026-11-06', '限定品', 'ニカラグア', 'nicaragua', 'NICARAGUA', 'Gellis Family Cigars（ゲリス・ファミリー・シガーズ）', 'gellis-family'),
    'villiger-taa-exclusive-2026': ('2026-11-06', '限定品', 'ニカラグア', 'nicaragua', 'NICARAGUA', 'Villiger（ヴィリガー）', 'villiger'),
    'jc-newman-cuesta-rey-rebrand': ('2026-11-06', '新製品', 'ドミニカ共和国', 'dominican', 'DOMINICAN REPUBLIC', 'J.C. Newman（J.C.ニューマン）', 'jc-newman'),
    'fratello-sweden-kind-cigars': ('2026-11-06', '市場・流通', 'スウェーデン', 'nicaragua', 'SWEDEN', 'Fratello Cigars（フラテッロ・シガーズ）', 'fratello'),
    'intertabac-2027-dates': ('2026-11-06', '経営', 'ドイツ', None, 'GERMANY', 'InterTabac（インターバック）', 'intertabac'),
    'domain-cigars-test-blend-portal': ('2026-11-06', '経営', 'ニカラグア', 'nicaragua', 'NICARAGUA', 'Domain Cigars（ドメイン・シガーズ）', 'domain-cigars'),
    'checkpoints-2026-11-06': ('2026-11-06', '経営', '世界', None, 'WORLD', '編集部まとめ', None),
    'crowned-heads-las-calaveras-decimo-2026': ('2026-11-07', '限定品', 'ニカラグア', 'nicaragua', 'NICARAGUA', 'Crowned Heads（クラウン・ヘッズ）', 'crowned-heads'),
    'san-luis-rey-eiroa-30th-maduro': ('2026-11-07', '限定品', 'ホンジュラス', 'honduras', 'HONDURAS', 'Altadis USA（アルタディスUSA）', 'altadis-usa'),
    'dunbarton-shokai-bushido': ('2026-11-07', '新製品', 'ニカラグア', 'nicaragua', 'NICARAGUA', 'Dunbarton Tobacco & Trust（ダンバートン・タバコ＆トラスト）', 'dunbarton'),
    'plasencia-holiday-collection-2026': ('2026-11-07', '限定品', 'ニカラグア', 'nicaragua', 'NICARAGUA', 'Plasencia（プラセンシア）', 'plasencia'),
    'brolo-cigar-co-debut': ('2026-11-07', '新製品', 'アメリカ', 'usa', 'UNITED STATES', 'Brolo Cigar Co.（ブローロ・シガー）', 'brolo-cigar-co'),
    'oliva-melanio-anio-2026': ('2026-11-07', '限定品', 'ニカラグア', 'nicaragua', 'NICARAGUA', 'Oliva（オリバ）', 'oliva'),
    'stg-hoyo-epicure-delisting': ('2026-11-07', '市場・流通', 'アメリカ', 'usa', 'UNITED STATES', 'Scandinavian Tobacco Group（スカンジナビアン・タバコ・グループ）', 'stg'),
    'selected-tobacco-madrid-hq': ('2026-11-07', '経営', 'スペイン', 'usa', 'SPAIN', 'Selected Tobacco（セレクテッド・タバコ）', 'selected-tobacco'),
    'big-smoke-las-vegas-30th': ('2026-11-07', '経営', 'アメリカ', 'usa', 'UNITED STATES', 'Cigar Aficionado（シガー・アフィショナード）', 'cigar-aficionado'),
    'checkpoints-2026-11-07': ('2026-11-07', '経営', '世界', None, 'WORLD', '編集部まとめ', None),
}

PRIMARY_SOURCES = {'quai-dorsay-concordia-el-2026', 'cohiba-talisman-regular',
                   'habanos-executive-appointments'}

# 原稿に img が無いが PHOTO-MANIFEST で出典ページから写真を確保した3件のキャプション
SYNTH_CAPTIONS = {
    'cohiba-talisman-regular': '写真：Habanos, S.A.',
    'habanos-executive-appointments': '写真：Habanos, S.A.',
    'marvin-shanken-obituary': '写真：Cigar Aficionado',
}

CHECKPOINT_SUMMARIES = {
    'checkpoints-2026-11-06': '今後の主要イベント・発売日のチェックリスト。Big Smoke Las Vegas（11月7日）、ポウスタニエ「ウォーベア 2026」発売（11月11日）、Gellis Family「Emerald Sky」出荷（11月下旬）、PCA Connect Asia（11月30日〜12月6日）、PCA in Korea（12月7〜10日）。',
    'checkpoints-2026-11-07': '今後の主要イベント・発売日のチェックリスト。ワールド・シガー・ショー ドバイ（11月10〜11日）、ポウスタニエ「ウォーベア 2026」発売（11月11日）、プロシガー・ナイト（11月12日）、Cigartopia でのダンバートン「Shokai Bushido」デビュー（11月14日）、Brolo Cigar Co. 発表イベント（11月19日）など。',
}

SOURCE_NAME_MAP = {'halfwheel': 'Halfwheel'}


def strip_tags(s):
    return htmlmod.unescape(re.sub(r'<[^>]+>', '', s)).strip()


def parse_draft(slug):
    src = open(os.path.join(DRAFTS, slug + '.html'), encoding='utf-8').read()
    m = re.search(r'<h3>(.*?)</h3>', src, re.S)
    h3 = re.sub(r'<span class="(?:new|boutique)">.*?</span>', '', m.group(1), flags=re.S)
    title = strip_tags(h3)
    meta = None
    mm = re.search(r'<div class="meta">(.*?)</div>', src, re.S)
    if mm:
        meta = strip_tags(mm.group(1))
    return src, title, meta


def source_fields(slug, meta, body_src, publish_date):
    if meta is None:
        return '編集部まとめ', None, publish_date
    name = meta.split('／')[0].strip()
    name = SOURCE_NAME_MAP.get(name, name)
    url = None
    sm = re.search(r'<p class="src">.*?<a href="([^"]+)"', body_src, re.S)
    if sm:
        url = sm.group(1)
    dm = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', meta)
    if dm:
        date = '%04d-%02d-%02d' % (int(dm.group(1)), int(dm.group(2)), int(dm.group(3)))
    elif slug == 'habanos-executive-appointments':
        date = '2026-10-21'  # meta は「2026年9〜10月」。本文中の最新人事（10月21日品質部長就任）を採用
    else:
        date = publish_date
    return name, url, date


def first_paragraph_text(src):
    m = re.search(r'<p>(.*?)</p>', src, re.S)
    return strip_tags(m.group(1)) if m else ''


def convert_body(slug, src, title):
    body = src
    body = re.sub(r'<h3>.*?</h3>\s*', '', body, flags=re.S)
    body = re.sub(r'<div class="meta">.*?</div>\s*', '', body, flags=re.S)

    captions = re.findall(r'<div class="caption">(.*?)</div>', body, re.S)
    state = {'img_idx': 0, 'cap_idx': 0}
    hero_lines = []

    def img_sub(m):
        state['img_idx'] += 1
        if state['img_idx'] == 1 and PHOTO[slug]:
            return '\x00HERO\x00'
        return '\x00SUBIMG\x00'

    body = re.sub(r'<img[^>]*>', img_sub, body)

    def cap_sub(m):
        state['cap_idx'] += 1
        inner = m.group(1).strip()
        if state['cap_idx'] == 1 and PHOTO[slug] and state['img_idx'] >= 1 and '\x00HERO\x00' in body:
            hero_lines.append('<p class="article-caption">%s</p>' % inner)
            return '\x00HEROCAP\x00'
        return '<p class="article-caption">%s</p>' % inner

    body = re.sub(r'<div class="caption">(.*?)</div>', cap_sub, body, flags=re.S)
    body = body.replace('\x00HERO\x00\n', '').replace('\x00HERO\x00', '')
    body = body.replace('\x00SUBIMG\x00',
                        '<img src="../img/news-sample/%s-2.jpg" alt="">' % slug)
    body = body.replace('\x00HEROCAP\x00\n', '').replace('\x00HEROCAP\x00', '')
    body = body.replace('<div class="spec">', '<div class="spec-box">')
    body = body.strip()

    if PHOTO[slug] and not hero_lines:
        # 原稿に img/caption が無いが写真を確保した3件
        cap = SYNTH_CAPTIONS.get(slug, '')
        hero_lines = ['<img class="article-hero" src="../img/news-sample/%s.jpg" alt="%s">' % (slug, title)]
        if cap:
            hero_lines.append('<p class="article-caption">%s</p>' % cap)
    elif PHOTO[slug]:
        hero_img = '<img class="article-hero" src="../img/news-sample/%s.jpg" alt="%s">' % (slug, title)
        hero_lines = [hero_img] + hero_lines

    out = ''
    if hero_lines:
        out += '\n'.join(hero_lines) + '\n'
    out += '<div class="article-body">\n' + body + '\n</div>\n'
    return out


records = []
for slug in sorted(META.keys(), key=lambda s: (META[s][0], s)):
    src, title, meta = parse_draft(slug)
    pub, cat, country, cid, cen, maker, mid = META[slug]
    sname, surl, sdate = source_fields(slug, meta, src, pub)
    if slug in CHECKPOINT_SUMMARIES:
        summary = CHECKPOINT_SUMMARIES[slug]
    else:
        summary = first_paragraph_text(src)
    converted = convert_body(slug, src, title)
    with open(os.path.join(OUT_BODIES, slug + '.html'), 'w', encoding='utf-8') as f:
        f.write(converted)
    rec = {
        'slug': slug,
        'title': title,
        'summary': summary,
        'description': summary,
        'category': cat,
        'country': country,
        'country_id': cid,
        'country_en': cen,
        'country_ids': [cid] if cid else [],
        'maker': maker,
        'maker_id': mid,
        'source_name': sname,
        'source_url': surl,
        'source_checked': '原稿確認済み',
        'source_date': sdate,
        'publish_date': pub,
        'status': 'published',
        'flow_version': 'legacy',
        'source_type': 'primary' if slug in PRIMARY_SOURCES else 'secondary',
        'history': [],
        'approval': None,
        'breaking': False,
        'top_story': None,
        'image': ('img/news-sample/%s.jpg' % slug) if PHOTO[slug] else None,
        'related': [],
    }
    records.append(rec)

header = """# バックナンバー記事データ（ステージング用・未公開）
# 元データ: backnumbers/bodies-draft/（Discord「世界の葉巻ニュース」2026-11-05〜11-07号）
# 変換: backnumbers/convert_backnumbers.py
# 注意: これは下準備専用ファイル。本番の data/articles.yaml には未統合。
# 統合時に必要な作業: makers レジストリへの新規メーカー追加、country_id が null の4件の分類確定、
# source_checked の原文再確認、related の設定、AI生成対象9件の画像生成。
"""
with open(os.path.join(BASE, 'articles-backnumbers.yaml'), 'w', encoding='utf-8') as f:
    f.write(header)
    yaml.safe_dump({'articles': records}, f, allow_unicode=True,
                   default_flow_style=False, sort_keys=False, width=10000)

ai = [s for s, v in PHOTO.items() if not v]
print('records:', len(records))
print('site-bodies:', len(os.listdir(OUT_BODIES)))
print('AI-needed (%d):' % len(ai), ', '.join(sorted(ai)))
print('photo (%d)' % sum(1 for v in PHOTO.values() if v))
