#!/usr/bin/env python3
"""バックナンバー31件＋ハバノス42件を data/articles.yaml へ統合する（ステージング→本番）。"""
import os, re, sys, yaml
from PIL import Image, ImageDraw, ImageFont

ROOT = '/home/hatch/workspace/cigar-site'
BN = os.path.join(ROOT, 'backnumbers')
IMG_OUT = os.path.join(ROOT, 'img/news-sample')
os.makedirs(IMG_OUT, exist_ok=True)

AI_CAPTIONS = {
    'festival-habano-2026-postponed': 'イラスト：AI生成 — 開催延期となったフェスティバルの会場（イメージ図）',
    'festival-habano-2026-cancelled': 'イラスト：AI生成 — ハバナの劇場前（イメージ図）',
    'bat-leaves-cuba': 'イラスト：AI生成 — ピナール・デル・リオのタバコ畑と乾燥小屋（イメージ図）',
    'davidoff-year-of-the-sheep-2027': 'イラスト：AI生成 — 羊の角を描いたアールデコ調の図案とヒュミドール（イメージ図）',
    'ecuador-tobacco-crop-el-nino': 'イラスト：AI生成 — エルニーニョの雨雲とエクアドルのタバコ畑（イメージ図）',
    'fratello-sweden-kind-cigars': 'イラスト：AI生成 — 北欧の葉巻店内（イメージ図）',
    'gellis-piece-unique-emerald-sky': 'イラスト：AI生成 — エメラルドの布に置かれた希少な葉巻（イメージ図）',
    'us-cigar-imports-2026-honduras': 'イラスト：AI生成 — コンテナ港の朝景（イメージ図）',
    'villiger-taa-exclusive-2026': 'イラスト：AI生成 — 会員制ラウンジのカウンター（イメージ図）',
    'world-cigar-show-dubai-2026': 'イラスト：AI生成 — ドバイの見本市会場（イメージ図）',
}
AI_ALTS = {
    'festival-habano-2026-postponed': 'フェスティバル会場のイラスト（AI生成）',
    'festival-habano-2026-cancelled': 'ハバナの劇場前のイラスト（AI生成）',
    'bat-leaves-cuba': 'タバコ畑と乾燥小屋のイラスト（AI生成）',
    'davidoff-year-of-the-sheep-2027': '羊の角の図案とヒュミドールのイラスト（AI生成）',
    'ecuador-tobacco-crop-el-nino': '雨雲とタバコ畑のイラスト（AI生成）',
    'fratello-sweden-kind-cigars': '北欧の葉巻店内のイラスト（AI生成）',
    'gellis-piece-unique-emerald-sky': 'エメラルドの布の上の葉巻のイラスト（AI生成）',
    'us-cigar-imports-2026-honduras': 'コンテナ港のイラスト（AI生成）',
    'villiger-taa-exclusive-2026': '会員制ラウンジのイラスト（AI生成）',
    'world-cigar-show-dubai-2026': 'ドバイの見本市会場のイラスト（AI生成）',
}

def badge_and_save(src, dest):
    im = Image.open(src).convert('RGB')
    if im.width > 1200:
        im = im.resize((1200, round(im.height * 1200 / im.width)), Image.LANCZOS)
    d = ImageDraw.Draw(im, 'RGBA')
    text = 'AI生成イラスト'
    font = None
    for fp, idx in (('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', 0),
                    ('/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc', 0)):
        if os.path.exists(fp):
            try:
                font = ImageFont.truetype(fp, size=max(20, im.width // 34), index=idx)
                break
            except Exception:
                continue
    if font is None:
        font = ImageFont.load_default()
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 16, 9
    x1, y1 = im.width - 18, im.height - 18
    x0, y0 = x1 - tw - pad_x * 2, y1 - th - pad_y * 2
    d.rounded_rectangle([x0, y0, x1, y1], radius=10, fill=(20, 16, 8, 215), outline=(183, 154, 99, 255), width=2)
    d.text((x0 + pad_x - bbox[0], y0 + pad_y - bbox[1]), text, font=font, fill=(255, 244, 214, 255))
    im.save(dest, quality=88)

def save_img(src, dest):
    im = Image.open(src).convert('RGB')
    if im.width > 1200:
        im = im.resize((1200, round(im.height * 1200 / im.width)), Image.LANCZOS)
    im.save(dest, quality=88)

def trim(text, limit=140):
    if not text or len(text) <= limit:
        return text
    cut = text[:limit]
    if '。' in cut:
        cut = cut[:cut.rfind('。') + 1]
    return cut

def load_staging(path):
    d = yaml.safe_load(open(path, encoding='utf-8'))
    return d['articles']

main = yaml.safe_load(open(os.path.join(ROOT, 'data/articles.yaml'), encoding='utf-8'))
existing_slugs = {a['slug'] for a in main['articles']}
existing_countries = {c['id'] for c in main['countries']}
existing_makers = {m['id'] for m in main['makers']}

bn = load_staging(os.path.join(BN, 'articles-backnumbers.yaml'))
hab = load_staging(os.path.join(BN, 'articles-habanos2026.yaml'))

DROP = {'checkpoints-2026-11-06', 'checkpoints-2026-11-07'}
bn = [a for a in bn if a['slug'] not in DROP]
print('back numbers to integrate:', len(bn), '| habanos:', len(hab))

COUNTRY_FIX = {
    'ecuador-tobacco-crop-el-nino': ('ecuador', 'エクアドル'),
    'world-cigar-show-dubai-2026': ('uae', 'ドバイ'),
    'intertabac-2027-dates': ('germany', 'ドイツ'),
}
NEW_COUNTRIES = [
    {'id': 'ecuador', 'ja': 'エクアドル', 'en': 'ECUADOR', 'en_short': 'ECUADOR'},
    {'id': 'germany', 'ja': 'ドイツ', 'en': 'GERMANY', 'en_short': 'GERMANY'},
    {'id': 'uae', 'ja': 'ドバイ', 'en': 'DUBAI', 'en_short': 'DUBAI'},
]
PRODUCT_CATS = ['新製品', '限定品']
new_makers = {}

def register_maker(a):
    mid = a.get('maker_id')
    if mid and mid not in existing_makers and mid not in new_makers:
        ja = a.get('maker') or mid
        en = re.split(r'（', ja)[0].strip()
        new_makers[mid] = {'id': mid, 'ja': ja, 'en': en, 'short': ja, 'base': a.get('country') or ''}

def finalize(a, body_src_dir, photo_dir):
    slug = a['slug']
    assert slug not in existing_slugs, f'slug clash: {slug}'
    if slug in COUNTRY_FIX:
        cid, cja = COUNTRY_FIX[slug]
        a['country_id'] = cid
        a['country'] = cja
        a['country_ids'] = [cid]
    if slug == 'us-cigar-imports-2026-honduras':
        a['maker_id'] = 'industry-stats'
        a['maker'] = '業界統計'
    register_maker(a)
    if a.get('category') in PRODUCT_CATS:
        a.setdefault('release_title', a['title'])
        a.setdefault('release_summary', a.get('summary'))
        a.setdefault('release_alt', a['title'])
    a['summary'] = trim(a.get('summary'))
    if a.get('description'):
        a['description'] = trim(a['description'])
    # image handling
    body_path = os.path.join(body_src_dir, slug + '.html')
    body = open(body_path, encoding='utf-8').read()
    if slug in AI_CAPTIONS:
        src = os.path.join(BN, 'ai-img', slug + '.jpg')
        badge_and_save(src, os.path.join(IMG_OUT, slug + '.jpg'))
        a['image'] = f'img/news-sample/{slug}.jpg'
        hero = (f'<img class="article-hero" src="../img/news-sample/{slug}.jpg" alt="{AI_ALTS[slug]}">\n'
                f'<p class="article-caption">{AI_CAPTIONS[slug]}</p>\n')
        if '<img class="article-hero"' not in body:
            body = hero + body
    elif a.get('image'):
        img_field = a['image']
        if img_field.startswith('photos-hab/'):
            src = os.path.join(BN, img_field)
            save_img(src, os.path.join(IMG_OUT, slug + '.jpg'))
            a['image'] = f'img/news-sample/{slug}.jpg'
            body = body.replace(f'../{img_field}', f'../img/news-sample/{slug}.jpg')
        else:  # back numbers: img/news-sample/<slug>.jpg form
            base = os.path.basename(img_field)
            src = os.path.join(BN, 'photos', base)
            if not os.path.exists(src):
                png = os.path.join(BN, 'photos', slug + '.png')
                assert os.path.exists(png), f'photo missing for {slug}'
                src = png
            save_img(src, os.path.join(IMG_OUT, slug + '.jpg'))
            # sub images referenced in body
            for m in re.finditer(r'src="\.\./img/news-sample/([^"]+)"', body):
                sub = m.group(1)
                if sub != base:
                    ssrc = os.path.join(BN, 'photos', sub)
                    if not os.path.exists(ssrc):
                        ssrc = os.path.splitext(ssrc)[0] + '.png'
                    save_img(ssrc, os.path.join(IMG_OUT, sub))
    open(os.path.join(ROOT, 'src/bodies', slug + '.html'), 'w', encoding='utf-8').write(body)
    return a

final = []
for a in bn:
    final.append(finalize(a, os.path.join(BN, 'site-bodies'), os.path.join(BN, 'photos')))
for a in hab:
    final.append(finalize(a, os.path.join(BN, 'site-bodies-hab'), os.path.join(BN, 'photos-hab')))
print('final records:', len(final))
print('new makers:', sorted(new_makers))
print('new countries:', [c['id'] for c in NEW_COUNTRIES if c['id'] not in existing_countries])

# text splice into data/articles.yaml
path = os.path.join(ROOT, 'data/articles.yaml')
text = open(path, encoding='utf-8').read()

def dump_list(items):
    return yaml.dump(items, allow_unicode=True, default_flow_style=False, sort_keys=False, width=1000)

new_countries = [c for c in NEW_COUNTRIES if c['id'] not in existing_countries]
if new_countries:
    frag = dump_list(new_countries)
    text = text.replace('\nmakers:\n', '\n' + frag + 'makers:\n', 1)
if new_makers:
    frag = dump_list(list(new_makers.values()))
    text = text.replace('\narticles:\n', '\n' + frag + 'articles:\n', 1)
frag = dump_list(final)
if not text.endswith('\n'):
    text += '\n'
text += frag
open(path, 'w', encoding='utf-8').write(text)

# validate reload
d2 = yaml.safe_load(open(path, encoding='utf-8'))
print('total articles now:', len(d2['articles']), '| countries:', len(d2['countries']), '| makers:', len(d2['makers']))
noimg = [a['slug'] for a in d2['articles'] if a['status'] == 'published' and not a.get('image')]
print('published without image:', noimg)
