# CigarScope Japan

世界のプレミアムシガー産業のニュースを日本語で紹介する、独立系ニュースメディア（非商用）。

- 公開サイト: https://koinu-bunko.github.io
- タグライン: WORLD CIGAR NEWS & INTELLIGENCE
- ブランドメッセージ: BEYOND HAVANA. BEYOND BORDERS.（世界の葉巻を、もっと広く、もっと深く。）
- 編集人: 仔犬（マスコットはハンチング帽と蝶ネクタイの編集長スタイル）

## 編集方針

- キューバを特別扱いせず、世界の葉巻産地を公平に扱う（Cuba / Nicaragua / Dominican Republic / Honduras / United States / Mexico / Ecuador / Brazil / Indonesia / Philippines ほか）。
- 出典を明記し、独自の日本語要約を掲載する。発表日と掲載日を分けて表示する。
- 特定のメーカーやブランドに偏らない。Habanos 以外のメーカー（My Father、AJ Fernandez、Arturo Fuente、Davidoff、Oliva、Padrón、Drew Estate、J.C. Newman、La Aurora、Rocky Patel、Plasencia、Foundation、E.P. Carrillo、Maya Selva ほか）と新興・ブティックブランドを積極的に紹介する。

## サイト構成

- `index.html` — トップページ（ヘッダー／グローバルナビ／Breaking News／Top Stories／Latest News／Country News／Brand News／New Releases／Industry & Market／Features／フッター）
- `news/` — ニュース記事の詳細ページ（共通フォーマット：タイトル／カテゴリー・対象国／発表日・掲載日／独自の日本語要約／出典・原文リンク／関連ニュース）と全記事一覧
- `country/` — 国別一覧（キューバ、ニカラグア、ドミニカ共和国、ホンジュラス、アメリカ）
- `brands/` — メーカー別一覧と索引
- `category/` — カテゴリー別一覧（新製品・限定品、市場・流通・経営）
- `about.html` / `policy.html` / `sources.html` / `contact.html` / `privacy.html` — サイトについて、編集方針、情報源・著作権ポリシー、お問い合わせ、プライバシーポリシー
- `features/` — 深掘り特集
  - `opusx.html` 第1弾 Opus X（2026-11-06 公開、改訂版を準備中）
  - `padron.html` 第2弾 パドロン（2026-11-07 公開）
  - `joya.html` 第3弾 ホヤ・デ・ニカラグア（2026-11-08 公開）
- `en/index.html` — 英語版トップページ（特集の英語版は順次追加）
- `assets/` — 公式ロゴ・マスコット・favicon（`cigarscope-japan-logo-master.png` が原本）
- `img/` — 記事・特集の写真（出典は各ページ内に記載）

## 技術

- 静的 HTML/CSS（フレームワークなし）、GitHub Pages で配信。
- 日本語／英語の切替は各ページのヘッダーのトグルから。

## 主な情報源

Habanos S.A. 公式、Cigar Aficionado、Halfwheel、Cigar Coop、Smokin Tabacco、Cigar Dojo、Premium Cigar Association、Tobacco Reporter、メーカー公式発表・公式 SNS ほか。各記事に出典と発表日を明記する。

## 更新履歴

- 2026-11-08: 「仔犬の葉巻文庫」として深掘り特集3本で公開開始。
- 2026-11-08: CigarScope Japan へ改称。公式ロゴ（編集長の仔犬）採用、トップページをニュースメディア型デザインへ刷新、編集方針（世界全体を公平に扱う）を明文化。
- 2026-11-08: 実用化アップデート（ChatGPT 初回監査の反映）— ニュース詳細ページ8本、国別・メーカー別・カテゴリー別一覧、フッター正式ページ5本を新設し、仮リンクを解消。

## 監査・確認にあたっての注記

- トップページのニュース項目は、日刊「世界の葉巻ニュース」2026-11-08 号の実記事です（出典・発表日つき）。全てのカード・ナビゲーションは実在の記事詳細ページまたは一覧ページへ接続しています（仮リンクはありません）。
- 英語版トップページは旧デザインのままで、順次新デザインへ統一します。
