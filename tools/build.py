# -*- coding: utf-8 -*-
"""
CigarScope Japan — サイト生成スクリプト（第2段階）

入力:  data/articles.yaml（唯一の情報源） + src/bodies/<slug>.html（本文）
出力:  site-gen/ 以下にステージング用HTMLを生成する。

設計上の注意:
- 本スクリプトは生成までを行い、公開は一切しない（生成と公開の分離）。
- 決定的生成: 現在時刻・乱数・実行環境依存の値を生成物に含めない。
  並び順は listing_order() の決定的キーで固定する。
- features/ は生成対象外。site-gen には含めない。assets/・img/・style-v2.css・en/ 等の
  静的ファイルも site-gen には含めない。これらは公開スナップショット作成時に
  原稿側から別途コピーされる設計（ROLLBACK.md 参照）。その際も features/myfather.html は
  絶対に含めないこと。
- status が draft の記事は、詳細ページ・一覧・トップのいずれにも一切出力しない。
- トップページは index-v2.html をテンプレートとし、ニュース由来の区画
  （Breaking / Top Stories / Latest News / Country News / Brand News /
    New Releases / Industry & Market）だけをデータから再生成して差し込む。
  ヘッダー・特集・フッター等はテンプレートのまま一切触らない。
"""
import os
import re
import shutil
import sys

import yaml

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data', 'articles.yaml')
BODIES = os.path.join(BASE, 'src', 'bodies')
OUT = os.path.join(BASE, 'site-gen')
TOP_TEMPLATE = os.path.join(BASE, 'index-v2.html')

PRODUCT_CATS = ['新製品', '限定品']
CATEGORY_PAGES = {
    'new-releases': {
        'cats': ['新製品', '限定品'],
        'title': '新製品・限定品',
        'en': 'NEW RELEASES',
        'desc': '世界の葉巻業界の新製品・限定品ニュースの一覧です。',
    },
    'market': {
        'cats': ['市場・流通', '経営'],
        'title': '市場・流通・経営',
        'en': 'INDUSTRY &amp; MARKET',
        'desc': '葉巻業界の市場・流通・経営に関するニュースの一覧です。',
    },
}
STATIC_COPIES = ['about.html', 'policy.html', 'sources.html', 'contact.html', 'privacy.html']
DATELINE_TEXT = '2026年11月8日（日）'  # テンプレート由来の固定文字列（生成時刻は使わない）


def jp_date(iso):
    """'2026-11-08' -> '2026年11月8日'"""
    y, m, d = str(iso).split('-')
    return '%d年%d月%d日' % (int(y), int(m), int(d))


def load_data():
    with open(DATA, encoding='utf-8') as f:
        data = yaml.safe_load(f)
    for a in data['articles']:
        for k in ('source_date', 'publish_date'):
            v = a.get(k)
            if v is not None and not isinstance(v, str):
                a[k] = v.isoformat()  # YAML が date 型として読んだ場合の正規化
    return data


def listing_order(articles):
    """決定的な掲載順（2026-11-08 編集者決定の正式ルール）:
    ① 掲載日（publish_date）降順 → ② 発表日（source_date）降順
    → ③ top_story 優先（lead→mid→なし） → ④ slug 昇順。

    既存8記事は publish_date が全て同一（2026-11-08）のため、このルールでも
    移行前の表示順と完全一致する（data/MIGRATION-NOTES.md 参照）。
    """
    rank = {'lead': 0, 'mid': 1}
    return sorted(
        articles,
        key=lambda a: (
            tuple(-int(x) for x in str(a['publish_date']).split('-')),
            tuple(-int(x) for x in str(a['source_date']).split('-')),
            rank.get(a.get('top_story'), 2),
            a['slug'],
        ),
    )


# ---------------------------------------------------------------- chrome
NAV_ITEMS = [
    ('top', '../index.html', 'TOP'),
    ('news', '../news/index.html', 'NEWS'),
    ('cuba', '../country/cuba.html', 'CUBA'),
    ('nicaragua', '../country/nicaragua.html', 'NICARAGUA'),
    ('dominican', '../country/dominican.html', 'DOMINICAN'),
    ('brands', '../brands/index.html', 'BRANDS'),
    ('new-releases', '../category/new-releases.html', 'NEW RELEASES'),
    ('market', '../category/market.html', 'MARKET'),
]
NAV_COUNTRIES = {'cuba', 'nicaragua', 'dominican'}


def nav_html(cur):
    lines = []
    for key, href, label in NAV_ITEMS:
        cls = ' class="cur"' if key == cur else ''
        lines.append('<li><a%s href="%s">%s</a></li>' % (cls, href, label))
    lines.append('<li><a href="../index.html#features">FEATURES</a></li>')
    return '\n'.join(lines)


def head_html(title, desc):
    return (
        '<!DOCTYPE html>\n'
        '<html lang="ja"><head><meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>%s</title>\n'
        '<meta name="description" content="%s">\n'
        '<link rel="icon" type="image/x-icon" href="../assets/favicon.ico">\n'
        '<link rel="icon" type="image/png" sizes="64x64" href="../assets/favicon-64.png">\n'
        '<link rel="apple-touch-icon" href="../assets/cigarscope-mascot-512.png">\n'
        '<link rel="stylesheet" href="../style-v2.css">\n'
        '</head><body>\n'
    ) % (title, desc)


def header_html(cur):
    return (
        '\n'
        '<header class="site-header">\n'
        '<div class="column">\n'
        '<div class="util-row">\n'
        '<span class="dateline" id="dateline">%s</span>\n'
        '<div class="lang-switch"><span class="cur">日本語</span><span class="sep">|</span><a href="../en/index.html">EN</a></div>\n'
        '</div>\n'
        '<div class="masthead">\n'
        '<div class="site-logo-wrap"><a href="../index.html"><span class="sr-only">CigarScope Japan — WORLD CIGAR NEWS &amp; INTELLIGENCE</span>\n'
        '<picture><source srcset="../assets/cigarscope-japan-logo-mobile.webp" type="image/webp" media="(max-width: 640px)"><source srcset="../assets/cigarscope-japan-logo.webp" type="image/webp"><img class="site-logo" src="../assets/cigarscope-japan-logo-web.png" alt="CigarScope Japan — World Cigar News"></picture>\n'
        '</a></div>\n'
        '<p class="tagline">WORLD CIGAR NEWS &amp; INTELLIGENCE</p>\n'
        '<p class="brand-msg"><span class="en">BEYOND HAVANA. BEYOND BORDERS.</span><span class="ja">世界の葉巻を、もっと広く、もっと深く。</span></p>\n'
        '</div>\n'
        '</div>\n'
        '<hr class="masthead-rule">\n'
        '<nav class="gnav" aria-label="グローバルナビゲーション">\n'
        '<div class="gnav-inner">\n'
        '<input class="gnav-toggle" type="checkbox" id="gnav-toggle">\n'
        '<label class="gnav-button" for="gnav-toggle"><span class="bars">☰</span>MENU</label>\n'
        '<ul>\n'
        '%s\n'
        '</ul>\n'
        '</div>\n'
        '</nav>\n'
        '</header>\n'
        '<script>\n'
        '(function(){var d=new Date();var w="\\u65e5\\u6708\\u706b\\u6c34\\u6728\\u91d1\\u571f"[d.getDay()];var el=document.getElementById("dateline");if(el){el.textContent=d.getFullYear()+"\\u5e74"+(d.getMonth()+1)+"\\u6708"+d.getDate()+"\\u65e5\\uff08"+w+"\\uff09";}})();\n'
        '</script>\n'
    ) % (DATELINE_TEXT, nav_html(cur))


FOOTER_HTML = (
    '\n'
    '<footer class="site-footer">\n'
    '<div class="footer-inner">\n'
    '<div class="footer-logo-plate"><img src="../assets/cigarscope-japan-logo-web.png" alt="CigarScope Japan — World Cigar News" loading="lazy"></div>\n'
    '<p class="footer-tag">WORLD CIGAR NEWS &amp; INTELLIGENCE</p>\n'
    '<nav class="footer-nav" aria-label="フッターナビゲーション">\n'
    '<a href="../about.html">サイトについて</a>\n'
    '<a href="../policy.html">編集方針</a>\n'
    '<a href="../sources.html">情報源・著作権ポリシー</a>\n'
    '<a href="../contact.html">お問い合わせ</a>\n'
    '<a href="../privacy.html">プライバシーポリシー</a>\n'
    '</nav>\n'
    '<div class="copyright">© 2026 CigarScope Japan — 世界の葉巻ニュースを日本語で紹介する独立系メディア</div>\n'
    '</div>\n'
    '</footer>\n'
    '\n'
    '</body></html>\n'
)


def page(title, desc, cur, main_html):
    return head_html(title, desc) + header_html(cur) + main_html + FOOTER_HTML


# ---------------------------------------------------------------- parts
def row_card(a, prefix, alt=None):
    """一覧用行カード。prefix は '../'（サブページ）または ''（トップ）。"""
    if a.get('image'):
        thumb = '<img class="thumb" src="%s%s" alt="%s" loading="lazy">' % (prefix, a['image'], alt or a['title'])
    else:
        thumb = '<div class="ph">◆</div>'
    return (
        '<article>\n'
        '<a class="row-card" href="%snews/%s.html">\n'
        '%s\n'
        '<div>\n'
        '<div class="meta-line"><span class="cat">%s</span><span class="country">%s</span></div>\n'
        '<h3>%s</h3>\n'
        '<p class="summary">%s</p>\n'
        '<div class="meta-line dates"><span class="source">%s</span><span class="src-date">%s</span><span class="pub">%s</span></div>\n'
        '<span class="read-more">記事全文を読む ›</span>\n'
        '</div>\n'
        '</a>\n'
        '</article>'
    ) % (
        prefix, a['slug'], thumb, a['category'], a['country'], a['title'],
        a['summary'], a['source_name'], jp_date(a['source_date']), jp_date(a['publish_date']),
    )


def list_page(title, desc, cur, head_en, head_ja, aria, articles):
    cards = '\n'.join(row_card(a, '../') for a in articles)
    main = (
        '\n<main>\n'
        '<section class="section list-section" aria-label="%s">\n'
        '<div class="section-head"><span class="en">%s</span><span class="ja">%s</span><span class="deco">◆ ◆ ◆</span></div>\n'
        '\n'
        '<div class="latest-list">\n'
        '%s\n'
        '</div>\n'
        '<p class="back-links"><a href="../index.html">トップページへ戻る</a></p>\n'
        '</section>\n'
        '</main>\n'
    ) % (aria, head_en, head_ja, cards)
    return page(title, desc, cur, main)


def auto_related(a, published):
    """related 未指定記事向けの自動選出（同一メーカー→同一国→同一カテゴリー）。"""
    scored = []
    order = {x['slug']: i for i, x in enumerate(listing_order(published))}
    for b in published:
        if b['slug'] == a['slug']:
            continue
        score = 0
        if b['maker_id'] == a['maker_id']:
            score += 4
        if b['country_id'] == a['country_id']:
            score += 2
        if b['category'] == a['category']:
            score += 1
        if score:
            scored.append((-score, order[b['slug']], b['slug']))
    scored.sort()
    return [s[2] for s in scored[:3]]


def detail_page(a, by_slug, published):
    with open(os.path.join(BODIES, a['slug'] + '.html'), encoding='utf-8') as f:
        body = f.read().rstrip('\n')
    rel_slugs = a.get('related')
    if rel_slugs is None:
        rel_slugs = auto_related(a, published)
    rel_items = '\n'.join(
        '<li><a href="../news/%s.html"><span class="d">発表 %s ／ %s</span>%s</a></li>'
        % (s, jp_date(by_slug[s]['source_date']), by_slug[s]['source_name'], by_slug[s]['title'])
        for s in rel_slugs
    )
    extra = a.get('source_extra_html')
    extra_block = (extra + '\n') if extra else '\n'
    main = (
        '\n<main>\n'
        '<div class="column">\n'
        '<article class="article">\n'
        '<p class="back-top"><a href="../news/index.html">← ニュース一覧</a></p>\n'
        '<h1>%s</h1>\n'
        '<div class="meta-line article-meta"><span class="cat">%s</span><a class="country" href="../country/%s.html">%s</a><a class="brand-link" href="../brands/%s.html">%s</a></div>\n'
        '<div class="meta-line dates article-dates"><span class="src-date">発表 %s</span><span class="pub">掲載 %s</span></div>\n'
        '%s\n'
        '<div class="source-box">\n'
        '<p class="source-head">出典・原文</p>\n'
        '<p>出典：%s（発表 %s）</p>\n'
        '<p>原文：<a href="%s" target="_blank" rel="noopener">%s</a></p>\n'
        '%s'
        '<p class="source-note">本記事は上記の情報源をもとに、当サイトが独自に編集した日本語要約です。原文の転載ではありません。価格の円換算は1ドル＝158.5円です。</p>\n'
        '</div>\n'
        '<section class="related" aria-label="関連ニュース">\n'
        '<h2>関連ニュース</h2>\n'
        '<ul class="mini-list">\n'
        '%s\n'
        '</ul>\n'
        '</section>\n'
        '<p class="back-links"><a href="../news/index.html">← ニュース一覧へ</a><span class="sep">／</span><a href="../index.html">トップページへ戻る</a></p>\n'
        '</article>\n'
        '</div>\n'
        '</main>\n'
    ) % (
        a['title'], a['category'], a['country_id'], a['country'],
        a['maker_id'], a['maker'], jp_date(a['source_date']), jp_date(a['publish_date']),
        body, a['source_name'], jp_date(a['source_date']), a['source_url'], a['source_url'],
        extra_block, rel_items,
    )
    return page(
        '%s | CigarScope Japan' % a['title'], a['description'], 'news', main)


# ---------------------------------------------------------------- top page
def top_sections(data, published):
    """index-v2.html のニュース区画をデータから再生成する（セグメント差し替え方式）。"""
    ordered = listing_order(published)
    countries = data['countries']
    makers = {m['id']: m for m in data['makers']}
    maker_order = [m['id'] for m in data['makers']]

    # Breaking
    breaking = [a for a in ordered if a.get('breaking')]
    b_blocks = []
    for a in breaking:
        b_blocks.append(
            '<div class="column">\n'
            '<div class="breaking">\n'
            '<span class="b-label">BREAKING</span>\n'
            '<a class="b-title" href="news/%s.html">%s</a>\n'
            '<span class="b-meta">出典 %s ／ 発表 %s</span>\n'
            '</div>\n'
            '</div>' % (a['slug'], a['title'], a['source_name'], jp_date(a['source_date'])))
    seg_breaking = '<!-- Breaking News -->\n' + '\n'.join(b_blocks) + '\n\n'

    # Top Stories
    def top_card(a):
        cls = 'lead-card' if a.get('top_story') == 'lead' else 'mid-card'
        lazy = '' if cls == 'lead-card' else ' loading="lazy"'
        country_span = '' if a.get('hide_top_country') else '<span class="country">%s</span>' % a['country']
        return (
            '<article>\n'
            '<a class="card %s" href="news/%s.html">\n'
            '<img class="thumb" src="%s" alt="%s"%s>\n'
            '<div class="meta-line"><span class="cat">%s</span>%s</div>\n'
            '<h3>%s</h3>\n'
            '<p class="summary">%s</p>\n'
            '<div class="meta-line dates"><span class="source">%s</span><span class="src-date">%s</span><span class="pub">%s</span></div>\n'
            '<span class="read-more">記事全文を読む ›</span>\n'
            '</a>\n'
            '</article>'
        ) % (cls, a['slug'], a['image'], a.get('top_alt', a['title']), lazy,
             a['category'], country_span, a['title'], a['summary'],
             a['source_name'], jp_date(a['source_date']), jp_date(a['publish_date']))

    # Top Stories は lead を先頭に、その中で掲載順（発表日降順）を維持する
    _rank = {'lead': 0, 'mid': 1}
    _idx = {a['slug']: i for i, a in enumerate(ordered)}
    tops = sorted(
        [a for a in ordered if a.get('top_story')],
        key=lambda a: (_rank.get(a.get('top_story'), 2), _idx[a['slug']]))
    seg_top = (
        '<!-- Top Stories -->\n'
        '<section class="section" aria-label="主要ニュース">\n'
        '<div class="section-head"><span class="en">TOP STORIES</span><span class="ja">主要ニュース</span><span class="deco">◆ ◆ ◆</span></div>\n'
        '<div class="top-grid">\n\n'
        + '\n\n'.join(top_card(a) for a in tops)
        + '\n\n</div>\n</section>\n\n'
    )

    # Latest News（製品カテゴリーで top_story / breaking に入っていない記事）
    latest = [a for a in ordered
              if a['category'] in PRODUCT_CATS and not a.get('top_story') and not a.get('breaking')]
    seg_latest = (
        '<!-- Latest News -->\n'
        '<section class="section" aria-label="最新ニュース">\n'
        '<div class="section-head"><span class="en">LATEST NEWS</span><span class="ja">最新ニュース</span><span class="deco">◆ ◆ ◆</span></div>\n'
        '<div class="latest-list">\n\n'
        + '\n\n'.join(row_card(a, '', a.get('latest_alt')) for a in latest)
        + '\n\n</div>\n</section>\n\n'
    )

    # Country News
    blocks = []
    for c in countries:
        items = []
        for a in ordered:
            if c['id'] in (a.get('top_country_blocks') or []):
                mt = (a.get('mini_titles') or {}).get(c['id'], a['title'])
                items.append((mt, a))
        if not items:
            continue
        items.sort(key=lambda t: t[0])
        lis = '\n'.join(
            '<li><a href="news/%s.html"><span class="d">発表 %s ／ %s</span>%s</a></li>'
            % (a['slug'], jp_date(a['source_date']), a['source_name'], mt)
            for mt, a in items)
        blocks.append(
            '<div class="country-block">\n'
            '<h3>%s<span class="ja">%s</span></h3>\n'
            '<ul class="mini-list">\n'
            '%s\n'
            '</ul>\n'
            '</div>' % (c['en_short'], c['ja'], lis))
    seg_country = (
        '<!-- Country News -->\n'
        '<section class="section" aria-label="国別ニュース">\n'
        '<div class="section-head"><span class="en">COUNTRY NEWS</span><span class="ja">国別ニュース</span><span class="deco">◆ ◆ ◆</span></div>\n'
        '<div class="country-grid">\n\n'
        + '\n\n'.join(blocks)
        + '\n\n</div>\n</section>\n\n'
    )

    # Brand News
    chip_makers = []
    for mid in maker_order:
        if any(a['maker_id'] == mid and a['category'] in PRODUCT_CATS for a in published):
            chip_makers.append(mid)
    chips = '\n'.join(
        '<a class="chip" href="brands/%s.html">%s</a>' % (mid, makers[mid]['ja'])
        for mid in chip_makers)
    brand_items = []
    for mid in maker_order:
        arts = [a for a in published if a['maker_id'] == mid and a.get('brand_title')]
        arts.sort(key=lambda a: a['brand_title'])
        for a in arts:
            brand_items.append(
                '<li><span class="bname">%s</span><a href="news/%s.html">%s</a></li>'
                % (makers[mid]['short'], a['slug'], a['brand_title']))
    seg_brand = (
        '<!-- Brand News -->\n'
        '<section class="section" aria-label="メーカー別ニュース">\n'
        '<div class="section-head"><span class="en">BRAND NEWS</span><span class="ja">メーカー別ニュース</span><span class="deco">◆ ◆ ◆</span></div>\n'
        '<div class="brand-chips">\n'
        + chips + '\n'
        '</div>\n'
        '<ul class="brand-list">\n'
        + '\n'.join(brand_items) + '\n'
        '</ul>\n'
        '</section>\n\n'
    )

    # New Releases（release_* を持つ記事 = Top Stories と同じ顔ぶれ）
    def release_card(a):
        country_span = '' if a.get('hide_top_country') else '<span class="country">%s</span>' % a['country']
        return (
            '<article>\n'
            '<a class="card" href="news/%s.html">\n'
            '<img class="thumb" src="%s" alt="%s" loading="lazy">\n'
            '<div class="meta-line"><span class="cat">%s</span>%s</div>\n'
            '<h3>%s</h3>\n'
            '<p class="summary">%s</p>\n'
            '<div class="meta-line dates"><span class="source">%s</span><span class="src-date">%s</span><span class="pub">%s</span></div>\n'
            '<span class="read-more">記事全文を読む ›</span>\n'
            '</a>\n'
            '</article>'
        ) % (a['slug'], a['image'], a.get('release_alt', a['title']),
             a['category'], country_span, a['release_title'], a['release_summary'],
             a['source_name'], jp_date(a['source_date']), jp_date(a['publish_date']))

    releases = [a for a in tops if a.get('release_title')]
    seg_releases = (
        '<!-- New Releases -->\n'
        '<section class="section" aria-label="新製品・限定品">\n'
        '<div class="section-head"><span class="en">NEW RELEASES</span><span class="ja">新製品・限定品</span><span class="deco">◆ ◆ ◆</span></div>\n'
        '<div class="release-grid">\n\n'
        + '\n\n'.join(release_card(a) for a in releases)
        + '\n\n</div>\n</section>\n\n'
    )

    # Industry & Market
    market = [a for a in ordered if a['category'] in CATEGORY_PAGES['market']['cats']]
    m_items = []
    for a in market:
        m_items.append(
            '<li>\n'
            '<a href="news/%s.html">%s</a>\n'
            '<p class="summary">%s</p>\n'
            '<div class="meta-line dates"><span class="cat">%s</span><span class="country">%s</span><span class="source">%s</span><span class="src-date">%s</span><span class="pub">%s</span></div>\n'
            '</li>'
            % (a['slug'], a.get('market_title', a['title']), a['summary'], a['category'],
               a['country'], a['source_name'], jp_date(a['source_date']), jp_date(a['publish_date'])))
    seg_market = (
        '<!-- Industry & Market -->\n'
        '<section class="section" aria-label="業界・市場">\n'
        '<div class="section-head"><span class="en">INDUSTRY &amp; MARKET</span><span class="ja">業界・市場分析</span><span class="deco">◆ ◆ ◆</span></div>\n'
        '<ul class="market-list">\n'
        + '\n'.join(m_items) + '\n'
        '</ul>\n'
        '</section>\n\n'
    )

    return {
        'Breaking News': seg_breaking,
        'Top Stories': seg_top,
        'Latest News': seg_latest,
        'Country News': seg_country,
        'Brand News': seg_brand,
        'New Releases': seg_releases,
        'Industry & Market': seg_market,
    }


def build_top(data, published):
    with open(TOP_TEMPLATE, encoding='utf-8') as f:
        html = f.read()
    segs = top_sections(data, published)
    markers = list(segs.keys()) + ['Features']
    # 各マーカー区間 [marker開始, 次マーカー開始) を生成セグメントで置換する
    spans = []
    for i, name in enumerate(markers):
        start = html.index('<!-- %s -->' % name)
        end = html.index('<!-- %s -->' % markers[i + 1]) if i + 1 < len(markers) else len(html)
        spans.append((name, start, end))
    out = []
    pos = 0
    for name, start, end in spans:
        out.append(html[pos:start])
        if name in segs:
            out.append(segs[name])
        else:
            out.append(html[start:end])
        pos = end
    out.append(html[pos:])
    return ''.join(out)


# ---------------------------------------------------------------- main
def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)


def main():
    data = load_data()
    published = [a for a in data['articles'] if a.get('status') == 'published']
    by_slug = {a['slug']: a for a in published}
    countries = {c['id']: c for c in data['countries']}
    makers = {m['id']: m for m in data['makers']}

    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    # 記事詳細 + ニュース一覧
    for a in listing_order(published):
        write(os.path.join(OUT, 'news', a['slug'] + '.html'), detail_page(a, by_slug, published))
    write(os.path.join(OUT, 'news', 'index.html'), list_page(
        'ニュース一覧 | CigarScope Japan',
        'CigarScope Japanのニュース一覧。世界の葉巻業界の新製品・限定品、メーカー動向、市場・流通のニュースを出典明記で紹介します。',
        'news', 'NEWS', 'ニュース一覧', 'ニュース一覧', listing_order(published)))

    # 国別
    for c in data['countries']:
        arts = [a for a in listing_order(published) if c['id'] in (a.get('country_ids') or [])]
        if not arts:
            continue
        cur = c['id'] if c['id'] in NAV_COUNTRIES else None
        write(os.path.join(OUT, 'country', c['id'] + '.html'), list_page(
            '%sのニュース | CigarScope Japan' % c['ja'],
            '%sに関する葉巻業界ニュースの一覧です。' % c['ja'],
            cur, c['en'], '%sのニュース' % c['ja'], '%sのニュース' % c['ja'], arts))

    # メーカー別 + 索引
    brand_items = []
    for m in data['makers']:
        arts = [a for a in listing_order(published) if a['maker_id'] == m['id']]
        if not arts:
            continue
        write(os.path.join(OUT, 'brands', m['id'] + '.html'), list_page(
            '%s | CigarScope Japan' % m['ja'],
            '%s（%s）に関する葉巻業界ニュースの一覧です。' % (m['ja'], m['en']),
            'brands', 'BRAND NEWS', '%sのニュース' % m['ja'], '%sのニュース' % m['ja'], arts))
        brand_items.append(
            '<li><a class="brand-index-link" href="%s.html"><span class="bname">%s</span><span class="bmeta">%s ／ %s ／ %d件</span></a></li>'
            % (m['id'], m['ja'], m['en'], m['base'], len(arts)))
    main_idx = (
        '\n<main>\n'
        '<section class="section list-section" aria-label="メーカー一覧">\n'
        '<div class="section-head"><span class="en">BRANDS</span><span class="ja">メーカー・ブランド一覧</span><span class="deco">◆ ◆ ◆</span></div>\n'
        '<p class="list-note">当サイトでニュースを掲載しているメーカー・ブランドの一覧です。各メーカーのページで関連ニュースを読めます。対象メーカーは順次拡大していきます。</p>\n'
        '<ul class="brand-index">\n'
        + '\n'.join(brand_items) + '\n'
        '</ul>\n'
        '<p class="back-links"><a href="../index.html">トップページへ戻る</a></p>\n'
        '</section>\n'
        '</main>\n'
    )
    write(os.path.join(OUT, 'brands', 'index.html'), page(
        'メーカー・ブランド一覧 | CigarScope Japan',
        'CigarScope Japanがニュースを掲載しているメーカー・ブランドの一覧です。',
        'brands', main_idx))

    # カテゴリー別
    for cid, cfg in CATEGORY_PAGES.items():
        arts = [a for a in listing_order(published) if a['category'] in cfg['cats']]
        write(os.path.join(OUT, 'category', cid + '.html'), list_page(
            '%s | CigarScope Japan' % cfg['title'], cfg['desc'],
            cid, cfg['en'], cfg['title'], cfg['title'], arts))

    # トップ
    write(os.path.join(OUT, 'index.html'), build_top(data, published))

    # 静的ページは現行ファイルをそのままコピー（生成対象外だがサイトとして必要）
    for name in STATIC_COPIES:
        shutil.copyfile(os.path.join(BASE, name), os.path.join(OUT, name))

    print('generated %d published articles -> %s' % (len(published), OUT))
    return 0


if __name__ == '__main__':
    sys.exit(main())
