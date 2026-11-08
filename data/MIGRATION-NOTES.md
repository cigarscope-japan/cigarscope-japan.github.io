# データ移行記録（第1段階: 既存8記事 → articles.yaml + src/bodies/）

移行日: 2026-11-08 ／ 移行元は既存の詳細ページ（news/ 配下）が正本。既存ファイルは一切変更していない。

## 対応表

| slug | 移行元（正本） | メタデータの主な抽出元 | 本文（src/bodies/） |
|---|---|---|---|
| feral-flying-pig | news/feral-flying-pig.html | 詳細ページの h1・メタ行・出典ボックス、要約は news/index.html のカード | 詳細ページの本文部分（ヒーロー画像〜article-body）をそのまま抽出 |
| petit-edition | news/petit-edition.html | 同上 | 同上 |
| elegante | news/elegante.html | 同上 | 同上 |
| brick-house-taa-2026 | news/brick-house-taa-2026.html | 同上 | 同上 |
| battleborn-2026 | news/battleborn-2026.html | 同上 | 同上 |
| bvi-habanos | news/bvi-habanos.html | 同上（写真なし） | 同上（模式図を含む本文部分） |
| fifth-avenue | news/fifth-avenue.html | 同上（写真なし、出典ボックスに第一報の併記あり） | 同上 |
| el-tigre-factory | news/el-tigre-factory.html | 同上（写真なし、Breaking 指定） | 同上（模式図を含む本文部分） |

- 日付は YAML では ISO 形式（YYYY-MM-DD）で保持し、表示時に「2026年11月8日」形式へ変換する。
- meta description は詳細ページの現行値を `description` フィールドにそのまま保持（自動切り詰めはしない）。

## source_checked（原文確認済み）の根拠

既存8記事はすべて、日刊「世界の葉巻ニュース」2026-11-08号の制作時に、出典の原文
（Halfwheel / Tobacco Reporter の各記事）を実際に読んで作成された記事である。
そのため移行にあたり、全8記事に `source_checked: 原文確認済み` を付与した。
今後追加する記事については、実際に原文を確認した場合にのみこのステータスを付けること
（未確認の記事は tools/check.py の品質ゲートで公開不可になる）。

## 追加フィールド（設計書の基本項目に加えて移行で必要になったもの）

- `description`: 詳細ページの meta description 現行値。
- `country_id` / `country_ids`: 国ページの振り分け用ID。`country` は表示名。
  brick-house-taa-2026 はニカラグア産だが米国TAA限定品のため、現行サイトでも
  country/nicaragua.html と country/usa.html の両方に掲載されており、`country_ids` に両方を保持した。
- `related`: 関連ニュースは現行ページの掲載内容をそのまま固定移行した
  （属性ベースの自動選出では現行の並び・選択を再現できないため）。
  将来の新規記事で `related` を省略した場合は、build.py が
  「同一メーカー→同一国→同一カテゴリー」の優先度で自動選出する。
- トップページ専用の表示バリエーション（現行トップの手編集を再現するための任意項目）:
  `top_country_blocks`（トップの国別ブロックへの掲載先。petit-edition は現行トップの国別ブロックに
  掲載されていないため空）、`mini_titles`（ブロックごとの短縮見出し）、`brand_title`（メーカー別リスト用見出し）、
  `market_title`（業界・市場欄の見出し）、`release_title` / `release_summary` / `release_alt`（新製品欄のカード）、
  `top_alt`（Top Stories カードの alt）、`hide_top_country`（petit-edition のトップカードには国名ラベルがない現行仕様の再現）、
  `latest_alt`（トップの Latest News 行カード専用の alt。brick-house-taa-2026 と battleborn-2026 のみに存在し、
  一覧ページの行カードでは記事タイトルが alt になる）。また battleborn-2026 のトップ国別ブロック見出しは
  短縮形のため `mini_titles.dominican` に保持した。
- `source_extra_html`: fifth-avenue の出典ボックスにある「第一報」併記行を保持するための任意項目。
- レジストリ: `countries`（国ID・日本語名・英語名。dominican の英語名は国ページ見出しでは
  DOMINICAN REPUBLIC、トップのブロックとナビでは DOMINICAN のため `en` / `en_short` を分けた）と、
  `makers`（メーカーID・日本語名・英語名・短縮名・拠点表記。brands/index.html の一覧表示に使用）。

## 特記事項

- fifth-avenue は記事の対象表示が「ドイツ」（欧州流通の話）だが、現行サイトでは
  country/cuba.html（キューバ＝ハバノス権益の文脈）に分類されている。現行どおり
  `country: ドイツ`、`country_id: cuba` とした。
- el-tigre-factory と feral-flying-pig は出典URLが同一（Halfwheel の同一記事が両記事の一次情報）。
  現行ページの記載どおりに保持した。

## 並び順について（要確認の判断事項）

実施指示では「並び順は publish_date 降順→slug 昇順」とされたが、既存8記事は publish_date が
全て同一（2026-11-08）のため、その規則をそのまま適用すると全ての一覧の並びが現行サイトと
変わってしまい、「移行前後の差分実質ゼロ」という絶対条件と両立しない。
現行サイトの実際の並びは「発表日（source_date）の新しい順」であり、これが読者向けの
最新順としても自然であるため、生成順序は決定的順序として
**source_date 降順 → top_story（lead→mid→指定なし）→ slug 昇順** を採用し、現行順を完全再現した。
この判断の是非は最終承認時に確認されたい（変更は build.py のソートキー1か所で可能）。

## テスト用 draft サンプルについて

articles.yaml には動作確認用の `sample-draft-unpublished`（status: draft、source_checked: 未確認）を
1件残してある。これは公開データではなく、tools/check.py が「draft が生成物に一切現れないこと」を
検証するための常設サンプルである。本文は src/bodies/sample-draft-unpublished.html。
不要になれば articles.yaml からこの1件と本文ファイルを削除するだけでよい。
