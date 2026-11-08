# 公開承認ハッシュ仕様（hash_spec_version: 1）

公開承認の対象バージョン（approved_version）の計算方法を固定する文書。
承認後に対象のいずれかが変更された場合は再計算で不一致となり、「再承認待ち」として公開不可になる
（tools/check.py で検査）。仕様を変更する場合は hash_spec_version を上げて版管理し、
過去の承認記録は当時のバージョンの仕様で再現できるようにする。

## 対象と順序（固定）
1. `article_record` — data/articles.yaml の当該記事レコード（ただし `approval` キー自体は除く。除かないと自己参照になるため）
2. `body` — src/bodies/<slug>.html
3. `claims` — audits/claims/<slug>.md
4. `source` — 出典情報（当該記事の source_name / source_url / source_checked / source_type と、data/sources.yaml の該当媒体レコード）
5. `detail_page` — site-gen/news/<slug>.html（公開用に生成された詳細ページ）

一覧ページやトップのような共有ページは対象に含めない。共有ページは「承認済みの入力から
決定的に生成される」こと（build.py の決定的生成の検査）で担保する。参考値として
site-gen 全体のツリーハッシュを併記できるが、拘束力は持たない。

## 正規化（固定）
- テキストは UTF-8 として読み、改行を LF に統一し、末尾に改行が無ければ1つ付ける。
- YAML レコード（対象1・4）は、パースしたオブジェクトをキーソート済みの YAML
  （yaml.safe_dump、allow_unicode=True、sort_keys=True）として直列化してから上記の正規化を行う。

## 計算方法（固定）
1. 各対象について正規化済みバイト列の SHA-256 を取る。
2. 「対象名（上記のラベル）\t個別ハッシュ」の行を上記の固定順序で並べ、LF で連結し末尾に改行を付ける。
3. その全体の SHA-256 を取り、16進文字列を approved_version とする。

## 実装
- 計算は tools/approval_hash.py（compute_version）に集約し、tools/approve.py（承認記録の補助）と
  tools/check.py（照合）の双方が同じ実装を使う。
- approve.py は対象ファイルが1つでも欠けている場合は承認記録を書かない。
