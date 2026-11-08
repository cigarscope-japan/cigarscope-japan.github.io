# CigarScope Japan — ロールバック手順（第2段階・生成フロー移行用）

作成: 2026-11-08 ／ 対象: 第2段階「日刊ニュース追加フローの自動化」移行に伴う復旧手順

## 前提

- 本番サイト（GitHub Pages: koinu-bunko.github.io）の現在の公開内容は、公開スナップショット
  `~/workspace/cigar-site-public-v3/` と一致している（2026-11-08 公開、commit 8e6bbdc）。
- 第2段階の生成物は `~/workspace/cigar-site/site-gen/` にのみ出力され、**本番には未公開**。
  生成フローを採用しないと判断した場合は、手順Aだけで移行を完全になかったことにできる。

## バックアップ

- 完全バックアップ: `~/workspace/backups/cigar-site-backup-2026-11-08.tar.gz`（約35.5MB）
  - 内容: `~/workspace/cigar-site/` 全体 ＋ `~/workspace/cigar-site-public-v3/` 全体（移行開始時点）
- 特集ページのベースライン SHA-256（バックアップ時点）:
  - features/joya.html: `acd326a615bbf063d201c098187a242cf2051d9bd0db046f74d8a3a5862034d6`
  - features/padron.html: `fdbc456b1f8438e556c4a7062683bc2c54683e8f25f1ce9e9757396fe907311c`
  - features/opusx.html: `dfd1ed86bfb92d4f6f092488e99bed2cd959bcc48f851a4d31e3ee391ae3ef8c`
  - （features/myfather.html は非公開ファイル。正本は原稿側にのみ存在し、公開スナップショットには含めない）

## 手順A: 生成フローの採用を取りやめる（本番に何も公開していない場合）

本番は一切変更されていないため、公開側の作業は不要。原稿側は新規追加ファイル
（`data/`、`src/`、`tools/`、`site-gen/`、`ROLLBACK.md`）を削除すれば移行前の状態に戻る。

```bash
cd ~/workspace/cigar-site
rm -rf data src tools site-gen ROLLBACK.md
```

## 手順B: 本番を旧HTML状態に戻す（生成物を将来公開してしまった場合）

公開スナップショット `cigar-site-public-v3` を既存の公開ヘルパーでそのまま再公開すれば、
即座に移行前の公開状態へ戻る。

```bash
cd ~/workspace/custom-connectors/custom.github
python3 bin/github_api.py publish ~/workspace/cigar-site-public-v3 \
  koinu-bunko koinu-bunko.github.io main "Rollback to pre-automation snapshot (public-v3)"
```

公開後、主要URLが 200 を返すことと、features/myfather.html が 404 のままであることを確認する。

## 手順C: 原稿をバックアップから復元する（原稿が壊れた場合）

```bash
cd ~/workspace
mv cigar-site cigar-site-broken-$(date +%Y%m%d)   # 壊れた原稿を退避（日付は手入力）
tar xzf backups/cigar-site-backup-2026-11-08.tar.gz   # cigar-site と cigar-site-public-v3 が復元される
cd cigar-site
sha256sum features/joya.html features/padron.html features/opusx.html   # 上記ベースラインと一致すること
```

## 注意

- `site-gen/` には features/・assets/・img/・CSS・en/ は含まれない（生成対象外）。
  生成物を将来公開する際は、公開スナップショット作成時に原稿側からこれらを別途コピーする設計であり、
  その際も features/myfather.html は絶対に含めないこと（手順Bのスナップショット v3 が正しい見本）。
- ロールバック判断は編集者（カズ）の承認を得てから実行すること。生成と公開は分離されており、
  公開状態への変更は編集者の明示的な承認が必要。

## 追記（2026-11-08 21:46 JST）
現行ライブは public-v5（コミット 811d4ea9、日本語版モバイルのマストヘッド圧縮のみ）。ロールバック先は public-v4（コミット b31aab04）の再 publish。

## 追記（2026-11-08 23:36 JST）
現行ライブは public-v6（コミット ae7bb928、日本語版モバイルのマストヘッド再構成： ロゴ320px＋モバイル専用トリミング済みロゴ素材＋h1余白ゼロ）。ロールバック先は public-v5（コミット 811d4ea9）の再 publish。

### 追記（2026-11-09 00:01 公開分）
現行ライブは public-v7（コミット b2d24120、英語版全ページのヘッダーに日本語切替リンクを追加。差分は en/ 内33件のみ、日本語版は無変更。記事8本は再承認済み＝新ハッシュで全件 current）。ロールバック先は public-v6（コミット ae7bb928）の再 publish。

## v8 — URL migration to cigarscope-japan.github.io (2026-11-09)
- Published snapshot: ~/workspace/cigar-site-public-v8/ (commit d52f7ecb). GitHub account and repository were renamed by Kazu (koinu-bunko → cigarscope-japan; koinu-bunko.github.io → cigarscope-japan.github.io; same repository ID 1450001310, so the existing fine-grained PAT kept working).
- All canonical/OGP/hreflang/sitemap URLs now use https://cigarscope-japan.github.io. EN 8 articles were re-approved under the new hashes before publication (all APPROVED current, check PASS).
- The old Pages URL https://koinu-bunko.github.io returns 404 — GitHub does NOT redirect Pages sites after a rename (repository web/Git URLs do redirect, 301 verified). External links to the old Pages URL must be updated manually (X profile website field still pending at migration time).
- Rollback of content = republish the v7 snapshot; note its canonical URLs point at the retired domain.

## v9 — Read-more buttons on cards (2026-11-09)
- Published snapshot: ~/workspace/cigar-site-public-v9/ (commit 70c3b39a). Adds a gold pill button 「記事全文を読む ›」 to every news card and 「特集全文を読む ›」 to feature cards (JP), and "Read the full story ›" links on EN cards including Related cards on article pages. JP check PASS; EN 8 articles re-approved by Kazu (related-card change) and check-en PASS before publishing.
- Rollback target: v8 snapshot (commit d52f7ecb).

## v10 — EN top lead read-more fix (2026-11-09)
- Published snapshot: ~/workspace/cigar-site-public-v10/ (commit dd178a9e). The EN top page's lead story used a separate template (TEMPLATES/index.html) and had missed the v9 read-more button; Kazu spotted it and the button was added. Only en/index.html changed; EN approvals remained current (article pages untouched).
- Rollback target: v9 snapshot (commit 70c3b39a).
