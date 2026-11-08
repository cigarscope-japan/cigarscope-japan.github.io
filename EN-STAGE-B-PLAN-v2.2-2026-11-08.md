# CigarScope Japan 英語版 — Stage B ファイル別実装計画（最終版 v2.2）

作成: 2026-11-08（v2.1 に対する ChatGPT 最終技術監査の指摘3項目を反映。監査判定： 条件付き合格）
位置づけ: **本書は実装計画であり、実装・公開の承認ではない。** 提出をもって停止し、カズと ChatGPT の確認による最終承認を待つ。Stage C の実装、原稿ツリー・公開ツリーへの反映、既存 HTML/CSS/JavaScript の変更、公開は一切行わない。Inter の調達方式 A/B/C は決定しない。
状態表記： 各項目に「解決済み」「設計確定」「実装時確認」「外部確認待ち」「カズの判断待ち」のいずれかを明記する。

## A. v2.1 からの差分一覧

| # | 修正項目 | 内容 | 状態 |
|---|---|---|---|
| 1 | sitemap の日本語 URL エントリー明文化 | §3 に、対応ペアは日英それぞれ独立した `<url>` エントリーとして両方を載せ、各エントリーに自己＋相手の hreflang を書くことを明記。null の場合の扱いと check-en.py の検査項目を具体化 | 設計確定 |
| 2 | フォント取得記録の再現性強化 | §1.5 に取得記録の必須項目（リクエスト URL、User-Agent、実際の WOFF2 URL、取得日時、SHA-256、サイズ、内部名、ライセンスと保存先）を定め、今回の取得分は実値を記録した。再取得時にハッシュが変わった場合の扱い（黙って上書きせず差分を記録して再確認）も明記。Inter は引き続き外部確認待ち、A/B/C は未決定 | 設計確定（Inter の法的確定は外部確認待ち） |
| 3 | 承認ハッシュの入力範囲の明確化 | §2.5 を新設： 除外は approval のみ（history も対象内）、source レコードの選択条件（source_name 一致）、detail_page の依存範囲（テンプレート・データ・CSS の扱い）、生成物への日時・環境依存値・ランダム値の混入禁止、検証テスト T8（テンプレート変更の反映）・T9（クリーン環境での同一ハッシュ）を追加 | 設計確定（テストは実装時確認） |

上記以外の v2.1 の内容（検索仕様、品質ゲート、レイアウト、ファイル構成、検収の継承項目）は変更していない。

## 1. フォントライセンスと取得記録

### 1.1–1.4（v2.1 から変更なし。要点）
- 配布元は Google Fonts CSS API v2。取得ファイルは Google が生成したサブセット可変フォント WOFF2 で、上流原版とバイト一致しない（グリフ数 Cormorant 373 / Inter 518 で実証）。構成は2ファイル・計 85,896 B。
- Cormorant Garamond: 上流 OFL.txt に Reserved Font Name の指定なし。**解決済み**。
- Inter: 上流文書間で RFN の表記が一致せず、法的な確証は得られていない。**外部確認待ち**。調達方式は A（Google WOFF2 無改変再配布）／ B（上流原版 TTF を無改変配布）／ C（自前サブセット＋改名）の3案を比較提示済みで、**選択は行わない**。公開（Stage D）前に確定することをゲートとする。デザイン指定の Inter は変更しない。
- ライセンス文書の同梱： en/fonts/ に上流ライセンス文（Inter = rsms/inter の LICENSE.txt、Cormorant = CatharsisFonts の OFL.txt）と FONTS-NOTICE.txt を置く。

### 1.5 フォント取得記録の仕様（FONTS-NOTICE.txt の記録項目）
フォントを取得するたびに、次の項目を FONTS-NOTICE.txt に記録する（ファミリーごとに1セクション）。

- Google Fonts CSS API への正確なリクエスト URL
- 取得時の User-Agent
- CSS API が返した実際の WOFF2 ファイル URL
- 取得日時（JST）
- SHA-256
- ファイルサイズ
- 内部フォント名（ファミリー名・フルネーム・バージョン）
- 使用ライセンスと、ライセンス文書の保存先（パス）

**再取得時の規則**: 再取得したファイルの SHA-256 が既存記録と異なる場合は、記録を黙って上書きしない。旧値と新値を併記して差分を記録し、変更の理由（Google 側のバージョン更新等）を確認してから新値を正とする。この確認が済むまで、そのフォントを使う公開は行わない。

### 1.6 現在の取得記録（2026-11-08、試作時の取得分。Stage C で再取得し直す）
- リクエスト URL: `https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap`
- User-Agent: `Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36`
- 取得日時: 2026-11-08 17:50 JST
- Cormorant Garamond（latin サブセット、unicode-range: U+0000-00FF, U+0131, U+0152-0153, …）
- WOFF2 URL: `https://fonts.gstatic.com/s/cormorantgaramond/v21/co3bmX5slCNuHLi8bLeY9MK7whWMhyjYqXtK.woff2`
- SHA-256: d80df8ff5aecd299a61549f9e29ab1ed0b9b05f4ea71d50fe978e07d5240b235 ／ 37,640 B
- 内部名： Cormorant Garamond Light ／ Version 4.001
- ライセンス： SIL OFL 1.1（RFN なし）。文書の保存先（予定）: en/fonts/OFL-CormorantGaramond.txt
- Inter（latin サブセット、同 unicode-range）
- WOFF2 URL: `https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa1ZL7.woff2`
- SHA-256: 3100e775e8616cd2611beecfa23a4263d7037586789b43f035236a2e6fbd4c62 ／ 48,256 B
- 内部名： Inter Regular ／ Version 4.001;git-66647c0bb
- ライセンス： SIL OFL 1.1（RFN の扱いは外部確認待ち）。文書の保存先（予定）: en/fonts/LICENSE-Inter.txt

状態： 記録仕様は設計確定。記録の実値は解決済み（実測）。Inter の法的確定は外部確認待ち。

## 2. 承認ハッシュ仕様

### 2.1–2.4（v2.1 から変更なし。要点）
- 計算方法は日本語版 v1（仕様書 tools/APPROVAL-HASH-SPEC.md と実装 tools/approval_hash.py の双方と照合済み）と同一。対象は article_record（approval を除く）/ body / claims（audits/claims-en/）/ source / detail_page の5点、固定順序、正規化は UTF-8・LF・末尾改行、YAML は safe_dump(sort_keys=True, allow_unicode=True)。hash_spec_version: 1。日本語版のアルゴリズムは変更しない。
- 入力側の不変条件： 日付は YAML 日付型で書く、浮動小数点数を使わない、ハッシュ対象テキストは NFC で作成、行末空白は計算で除去せず作成時に警告。
- 基準環境： Python 3.12.3 / PyYAML 6.0.1（実測）。テストベクタと T1–T7 を Stage C で実施する。
- 互換性の表現は「アルゴリズム同一＋入力不変条件の追加」とする。

### 2.5 入力範囲の明確化（追加）
1. **除外フィールド**: article_record から除外するのは **`approval` のみ**とする。それ以外の全フィールド（history を含む）はハッシュ対象であり、訂正・更新で history が変われば再承認待ちになる（日本語実装の挙動と同一）。
2. **source レコードの選択条件**: sources-en.yaml の収載レコードのうち、**`name` が当該記事の `source_name` と完全一致する1件**を選ぶ（日本語実装の選択条件と同一）。一致するレコードが無い場合、ハッシュ計算上は registry=null として扱う（日本語実装と同一）が、英語版では**未登録の出典を使う記事は公開不可**とするゲートを check-en.py に置く（計算方法は変えず、公開条件で縛る）。
3. **detail_page の依存範囲**: 詳細ページの生成に効く入力は次のとおりであり、これらが変われば生成バイトが変わり、ハッシュ不一致＝再承認待ちになるのが正しい挙動である。
- TEMPLATES/article.html および共通部品（ヘッダー・フッター等の取り込み元テンプレート）
- 当該記事のレコード（articles-en.yaml）と本文（src/bodies/）
- masters.yaml（国・ブランドの表示名）、sources-en.yaml（出典表示）、corrections.yaml（記事内に表示される訂正注記）
- build-en.py の生成ロジック
- **CSS（style-en.css）は詳細ページに埋め込まず、リンク参照のみとする**。したがって CSS の変更は detail_page のハッシュに影響しない（見た目だけの変更で再承認を強制しない）。この区別を仕様として固定する。
4. **生成物への混入禁止**: build-en.py は生成ページに**ビルド日時・実行環境依存情報（絶対パス、ツールや Python のバージョン文字列等）・ランダム値を一切埋め込まない**。同じ入力からは常に同じバイト列が生成されること（決定的生成）を仕様とする。
5. **クリーン環境での同一性検証（テスト T9）**: 基準環境とは別のクリーンな作業コピー（新規展開＋基準バージョンの Python/PyYAML）で同じフィクスチャから生成し、detail_page の SHA-256 が一致することを確認する。
6. **テンプレート変更の反映確認（テスト T8）**: フィクスチャのテンプレートを1か所変更して再生成すると、detail_page のハッシュが変わり、check が再承認待ちを検出することを確認する（テンプレート変更が承認の網をすり抜けないことの検証）。

状態： 設計確定。T8・T9 を含むテスト実施は実装時確認。

## 3. sitemap の URL 管理仕様

### 3.1 継承事項（要点）
- build-en.py の入力は en-admin/ のみ。日本語 URL は `en-admin/data/jp-url-manifest.yaml`（公開サイトの観測に基づく記述データ。verified_date / verified_by つき）から取得し、**英語側のビルドが日本語ツリーを読み込むことは禁止**する。
- jp_counterpart の有効性はマニフェスト収載で定義し、未収載は check-en.py が fail にする。日本語 URL は英語側では生成・変更しない。

### 3.2 エントリー形式の明文化（追加）
日本語記事と英語記事が対応する場合、sitemap.xml には**日本語 URL と英語 URL の両方を、それぞれ独立した `<url>` エントリーとして**掲載する。各エントリーには、自分自身と対応する他言語版を示す hreflang（xhtml:link alternate）を記載する。

- 日本語 URL のエントリー: `<loc>` = 日本語 URL。alternate として hreflang="ja" で自分自身、hreflang="en" で対応する英語 URL を記載する。
- 英語 URL のエントリー: `<loc>` = 英語 URL。alternate として hreflang="en" で自分自身、hreflang="ja" で対応する日本語 URL を記載する。
- 日本語トップ（https://koinu-bunko.github.io/）と英語トップ（https://koinu-bunko.github.io/en/）も同様に、両方を独立エントリーとし、相互に hreflang を記載する。
- **jp_counterpart が null の英語記事**は、英語 URL のエントリーだけを掲載し、hreflang の alternate は出力しない。
- 対応する英語版が無い日本語記事は、英語側の sitemap には載せない（日本語側の管理に属するため触れない）。

### 3.3 check-en.py の検査（具体化）
- 対応ペアについて、日英**両方の `<url>` エントリーが存在する**こと。
- 各エントリーの hreflang が、自己参照（自分自身）と相互参照（相手）の2件を正しく含むこと。
- `<loc>` と alternate の URL に重複が無いこと。
- sitemap 内の日本語 URL が**すべてマニフェスト収載**であること（マニフェストにない日本語 URL が混入していないこと）。
- jp_counterpart が null の記事に ja の alternate が付いていないこと。

状態： 設計確定。

## 4. claims-en の配置（v2.1 §4 から変更なし）
配置は **`audits/claims-en/<slug>.md`** に統一（日本語版 audits/claims/ と並列、変更しない）。build-en.py は主張対応表を読まない。check-en.py が存在と全行解決を公開ゲートとして検査し、approval_hash_en.py の対象3のパスもこの配置で固定する。バックアップと復元テストの対象に含める。状態： 設計確定。

## 5. 検索仕様と実通信テスト（v2.1 §5 から変更なし）
方式はページ内完結＋フラグメント（#q=）受け渡し、外部サービス不使用、JS 無効時は静的回遊リンク。実通信テスト T-S1〜T-S6（DevTools Network ログで、検索語を含むリクエストが無いこと等を確認）と、Privacy Policy への「履歴・共有 URL に検索語が残り得る」旨の追加説明を検収に含める。状態： 設計確定（実施は実装時確認）。

## 6. 最終ファイルツリー（v2.1 §6 から変更なし）
en-admin/（TEMPLATES 5型、data = articles-en.yaml / corrections.yaml / sources-en.yaml / masters.yaml / jp-url-manifest.yaml、src/bodies・src/formal、tools 4点）、audits/claims-en/、公開側 en/（生成物＋style-en.css＋fonts（可変フォント2ファイル＋ライセンス文2件＋FONTS-NOTICE.txt）＋search.js）、sitemap.xml（生成）。変更対象の既存ファイルは en/index.html のみ（生成物への置き換え、URL 不変）。日本語版ファイルは一切変更しない。CULTURE と Other Regions は対象記事が発生し、特集は別途承認を得た時点で追加する。

## 7. 検収チェックリスト（更新版）
v2.1 §7（v2 §D の継承分＋指摘7の追加9項目＋v2.1 の追加分）を維持し、以下を加える。

- [] sitemap: §3.2 の形式どおり日英両エントリーが存在し、§3.3 の検査が全て合格すること
- [] フォント: FONTS-NOTICE.txt に §1.5 の全項目が記録され、実ファイルの SHA-256 と一致すること。再取得でハッシュが変わっていた場合は、差分記録と再確認の記録があること
- [] ハッシュ: T8（テンプレート変更の反映）と T9（クリーン環境での同一ハッシュ）が合格すること
- [] Inter の調達方式が未確定のまま公開されていないこと（Stage D のゲート）

## 8. 継承する設計（v2.1 §8 から変更なし。要点）
レイアウト（1200px・非対称、ヒーローはカルーセル禁止、写真を大きく、余白80px級、ゴールドは細罫と小さなラベルに限定、マストヘッド3層、白プレートのロゴ、スマホは1カラム＋CSSトグル式ナビ、デザイン4原則）。記事データ構造と null 規則。初期8記事の品質ゲート10項目。SEO（lang="en"、英語 description、OGP、canonical、hreflang は §3 の sitemap 方式）。バックアップ・復元（全体バックアップ＋SHA-256 マニフェスト、復元テスト、作業中は日本語ツリーのチェックサム一致を継続検査、ロールバックは public-v3 再公開）。方式A（英語編集部の独自要約、機械翻訳転載禁止、出典名＋原文リンク必須、日本語リンクは補助、特集は別途承認制）。Cigar Journal 不使用、マイファザー非公開、未確認情報の断定禁止。

## 9. 未解決事項一覧

| # | 事項 | 状態 |
|---|---|---|
| 1 | 本計画（v2.2）の確認と最終承認 | カズの判断待ち |
| 2 | ChatGPT による v2.2 の確認 | 外部確認待ち |
| 3 | Inter の RFN に関する法的な確証 | 外部確認待ち |
| 4 | Inter の調達方式（A/B/C）の選択 | カズの判断待ち（Stage D の前のゲート。Stage C 開始の前提ではない） |
| 5 | フォントの再取得と取得記録の作成（§1.5） | 実装時確認 |
| 6 | ハッシュのテストベクタと T1–T9 の実施 | 実装時確認 |
| 7 | 初期8記事の原文アクセス確認 | 実装時確認 |
| 8 | jp-url-manifest.yaml の初期作成と実アクセス照合 | 実装時確認 |
| 9 | sources-en.yaml の初期登録 | 実装時確認 |
| 10 | スマートフォン実機での確認 | 実装時確認 |

## 10. Stage C 開始前に残っている承認事項
1. 本計画 v2.2 に対するカズの最終承認。
2. ChatGPT の最終監査で v2.2 が確認済みとなること。
3. Stage C の実施そのものへの承認（範囲は「隔離コピーでの実装と検収提出」まで。原稿ツリーへの反映と公開は含まない）。
なお Inter の調達方式（A/B/C）の選択は Stage C 開始の前提ではなく、公開（Stage D）前のゲートとして残る。

**停止の明記**: 本書（v2.2）の提出をもって作業を停止する。最終承認はカズと ChatGPT が v2.2 を確認した後に行われるものであり、それまで Stage C の実装、ファイル変更、公開は一切行わない。
