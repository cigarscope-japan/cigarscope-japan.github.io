# 公開前検査結果（CHECK-REPORT）

対象: site-gen/（tools/build.py の生成物）＋ data/articles.yaml 等の編集管理データ

## [合格] 1. href="#" が 0 件
- 対象 29 ページ全て 0 件

## [合格] 2. 内部リンク・画像・CSS が全て実ファイルに解決
- 参照 849 件を検査し全て解決

## [合格] 3. draft 記事が生成物に一切現れない
- draft 1 件（sample-draft-unpublished）の slug・タイトルとも検出なし

## [合格] 4. 特集3本のチェックサムがベースラインと一致
- joya / padron / opusx の3本とも一致（無変更）

## [合格] 5. myfather への言及・リンクが生成物に無い
- 全生成ファイルに "myfather" の文字列なし

## [合格] 6. published 記事の品質ゲート（出典・原文確認・必須項目）
- published 8 件全て充足

## [合格] 7. 決定的生成（同一入力から常に同一HTML）
- 生成ファイル 29 件のハッシュが、実行前・1回目・2回目で完全一致

## [合格] 8. Cigar Journal の不使用（文字列走査）
- 走査対象 19 ファイルに混入なし

## [合格] 9. 情報源レジストリ（standard: 登録必須／除外媒体の使用禁止）
- standard published 0 件の出典は全て登録済み

## [合格] 10. 主張対応表（standard published: 必須・未解決行なし）
- standard published 0 件全て充足

## [合格] 11. 報道ベース明示ゲート（機械条件＋人間の編集確認）
- 対象の standard published 全て充足

## [合格] 12. Cigar Journal 不使用確認記録（standard published: 必須）
- standard published 0 件全て記録あり

## [合格] 13. 公開承認記録（standard published: 必須・ハッシュ一致）
- standard published 0 件全て承認記録と一致

## [合格] 14. 訂正履歴の整合性（standard: 訂正表記と history の対応）
- standard の記事全て整合

## 注意（合否に影響しない警告）
- legacy: published 8 件の主張対応表は未作成（移行は別途承認）
- legacy: published 8 件の承認記録は未登録（移行は別途承認）

## 総合判定: 合格（全項目パス）
