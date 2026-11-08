# 移行前後 差分報告（第3段階）

比較日: 2026-11-08 ／ 比較方法: 生成物（site-gen/）と現行原稿のバイト単位比較（cmp）
比較対象の対応: site-gen/index.html ↔ index-v2.html（現行トップ）、他は同名ファイル同士。

## 結論

**全29ファイルがバイト単位で完全一致（差分ゼロ）。**
本文・見出し・リンク先・画像パス・日付のいずれにも差異はない。空白・属性順などの
無意味な差異も発生しなかったため、読み替え・正規化は一切行っていない。

## ページ別結果

| 生成物 | 比較先（現行原稿） | 結果 |
|---|---|---|
| index.html | index-v2.html | 一致 |
| news/feral-flying-pig.html | news/feral-flying-pig.html | 一致 |
| news/petit-edition.html | news/petit-edition.html | 一致 |
| news/elegante.html | news/elegante.html | 一致 |
| news/brick-house-taa-2026.html | news/brick-house-taa-2026.html | 一致 |
| news/battleborn-2026.html | news/battleborn-2026.html | 一致 |
| news/bvi-habanos.html | news/bvi-habanos.html | 一致 |
| news/fifth-avenue.html | news/fifth-avenue.html | 一致 |
| news/el-tigre-factory.html | news/el-tigre-factory.html | 一致 |
| news/index.html | news/index.html | 一致 |
| country/cuba.html | country/cuba.html | 一致 |
| country/nicaragua.html | country/nicaragua.html | 一致 |
| country/dominican.html | country/dominican.html | 一致 |
| country/honduras.html | country/honduras.html | 一致 |
| country/usa.html | country/usa.html | 一致 |
| brands/index.html | brands/index.html | 一致 |
| brands/drew-estate.html | brands/drew-estate.html | 一致 |
| brands/selected-tobacco.html | brands/selected-tobacco.html | 一致 |
| brands/aladino.html | brands/aladino.html | 一致 |
| brands/jc-newman.html | brands/jc-newman.html | 一致 |
| brands/casa-carrillo.html | brands/casa-carrillo.html | 一致 |
| brands/habanos.html | brands/habanos.html | 一致 |
| category/new-releases.html | category/new-releases.html | 一致 |
| category/market.html | category/market.html | 一致 |
| about.html | about.html | 一致（バイトコピー） |
| policy.html | policy.html | 一致（バイトコピー） |
| sources.html | sources.html | 一致（バイトコピー） |
| contact.html | contact.html | 一致（バイトコピー） |
| privacy.html | privacy.html | 一致（バイトコピー） |

## 生成対象外（site-gen に含めないもの）

- features/（特集3本＋myfather.html）: 生成対象外。公開時は原稿から別途コピーする設計。
- assets/、img/、style-v2.css、style.css、en/: 静的ファイルとして生成対象外（同上）。

## 初回生成で検出され、データ／スクリプト側で吸収した差異（記録）

初回ビルドではトップページのみ46行の差分があった。いずれも現行トップの手編集仕様であり、
本文データの誤りではないため、以下のとおり移行データと生成規則に取り込んで解消した。

1. Top Stories / New Releases のカード順: 現行は lead（feral-flying-pig）が先頭。
   生成順を「top_story の lead→mid 優先、同順位は掲載順」に修正。
2. トップの Latest News 行カードの alt が記事タイトルではなく専用文言だった
   （brick-house-taa-2026 / battleborn-2026）。`latest_alt` フィールドを追加して保持。
3. トップの国別ブロックで battleborn-2026 の見出しが短縮形だった。
   `mini_titles.dominican` に現行文言を保持。

これらの追加フィールドは data/MIGRATION-NOTES.md にも記録した。
