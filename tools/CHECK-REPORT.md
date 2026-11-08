# 公開前検査結果（CHECK-REPORT）

対象: site-gen/（tools/build.py の生成物）＋ data/articles.yaml 等の編集管理データ

## [合格] 1. href="#" が 0 件
- 対象 125 ページ全て 0 件

## [合格] 2. 内部リンク・画像・CSS が全て実ファイルに解決
- 参照 4128 件を検査し全て解決

## [合格] 3. draft 記事が生成物に一切現れない
- draft 1 件（sample-draft-unpublished）の slug・タイトルとも検出なし

## [合格] 4. 特集3本のチェックサムがベースラインと一致
- joya / padron / opusx の3本とも一致（無変更）

## [合格] 5. myfather への言及・リンクが生成物に無い
- 全生成ファイルに "myfather" の文字列なし

## [合格] 6. published 記事の品質ゲート（出典・原文確認・必須項目）
- published 79 件全て充足

## [合格] 7. 決定的生成（同一入力から常に同一HTML）
- 生成ファイル 125 件のハッシュが、実行前・1回目・2回目で完全一致

## [合格] 8. 除外媒体 CigarNavi の不使用（文字列走査）
- 走査対象 161 ファイルに混入なし

## [合格] 9. 情報源レジストリ（standard: 登録必須／除外媒体の使用禁止）
- standard published 0 件の出典は全て登録済み

## [合格] 10. 主張対応表（standard published: 必須・未解決行なし）
- standard published 0 件全て充足

## [合格] 11. 報道ベース明示ゲート（機械条件＋人間の編集確認）
- 対象の standard published 全て充足

## [合格] 12. 除外媒体不使用確認記録（standard published: 必須）
- standard published 0 件全て記録あり

## [合格] 13. 公開承認記録（standard published: 必須・ハッシュ一致）
- standard published 0 件全て承認記録と一致

## [合格] 14. 訂正履歴の整合性（standard: 訂正表記と history の対応）
- standard の記事全て整合

## 注意（合否に影響しない警告）
- legacy: cohiba-talisman-regular の source_name「Habanos S.A. 公式発表」は未登録（移行時に要対応）
- legacy: davidoff-year-of-the-sheep-2027 の source_name「Cigar Journal」は未登録（移行時に要対応）
- legacy: habanos-executive-appointments の source_name「Habanos S.A. 公式発表」は未登録（移行時に要対応）
- legacy: quai-dorsay-concordia-el-2026 の source_name「Habanos S.A. 公式発表」は未登録（移行時に要対応）
- legacy: world-cigar-show-dubai-2026 の source_name「Cigar Journal」は未登録（移行時に要対応）
- legacy: black-works-killer-bee-buzz-saw-2 の source_name「Cigar Coop」は未登録（移行時に要対応）
- legacy: domain-cigars-test-blend-portal の source_name「Cigar Coop」は未登録（移行時に要対応）
- legacy: intertabac-2027-dates の source_name「Cigar Journal」は未登録（移行時に要対応）
- legacy: jc-newman-cuesta-rey-rebrand の source_name「Cigar Coop」は未登録（移行時に要対応）
- legacy: la-gloria-cubana-gran-legado の source_name「Cigar Coop」は未登録（移行時に要対応）
- legacy: powstanie-war-bear-2026 の source_name「Cigar Coop」は未登録（移行時に要対応）
- legacy: plasencia-holiday-collection-2026 の source_name「Cigar Coop」は未登録（移行時に要対応）
- legacy: selected-tobacco-madrid-hq の source_name「Cigar Coop」は未登録（移行時に要対応）
- legacy: festival-habano-2026-sold-out の source_name「Cigars-connect」は未登録（移行時に要対応）
- legacy: fonseca-du-nord-canada の source_name「Habanos S.A.」は未登録（移行時に要対応）
- legacy: trinidad-corcel-hong-kong の source_name「Habanos S.A.」は未登録（移行時に要対応）
- legacy: cohiba-bhk-58-switzerland の source_name「Cigars-connect」は未登録（移行時に要対応）
- legacy: punch-princesas-switzerland の source_name「Cigars-connect」は未登録（移行時に要対応）
- legacy: festival-habano-2026-postponed の source_name「Habanos S.A.」は未登録（移行時に要対応）
- legacy: cuba-harvest-2025-26 の source_name「Cigars-connect」は未登録（移行時に要対応）
- legacy: lcdh-montreux-opens の source_name「Habanos S.A.」は未登録（移行時に要対応）
- legacy: montecristo-lesprit-portugal の source_name「Habanos S.A.」は未登録（移行時に要対応）
- legacy: lcdh-pall-mall-london の source_name「Cigars-connect」は未登録（移行時に要対応）
- legacy: vietnam-habanos-specialists-open の source_name「Habanos S.A.」は未登録（移行時に要対応）
- legacy: lcdh-milano-20th-anniversary の source_name「Habanos S.A.」は未登録（移行時に要対応）
- legacy: cohiba-novedosos-andorra の source_name「Cigars-connect」は未登録（移行時に要対応）
- legacy: habanos-day-costa-rica-2026 の source_name「Habanos S.A.」は未登録（移行時に要対応）
- legacy: vuelta-abajo-planting-14000 の source_name「Cigars-connect」は未登録（移行時に要対応）
- legacy: dupont-cohiba-60-collection の source_name「Cigars-connect」は未登録（移行時に要対応）
- legacy: cuba-agriculture-liberalization の source_name「Cigars-connect」は未登録（移行時に要対応）
- legacy: lcdh-kreuzlingen-opens の source_name「Habanos S.A.」は未登録（移行時に要対応）
- legacy: bolivar-evento-55-france の source_name「Cigars-connect」は未登録（移行時に要対応）
- legacy: montecristo-herederos-switzerland の source_name「Cigars-connect」は未登録（移行時に要対応）
- legacy: festival-habano-2026-cancelled の source_name「Habanos S.A.」は未登録（移行時に要対応）
- legacy: ft-habanos-premium-strategy の source_name「Financial Times」は未登録（移行時に要対応）
- legacy: trinidad-vigia-reserva-cosecha-2022 の source_name「Habanos S.A.」は未登録（移行時に要対応）
- legacy: montecristo-fragata の source_name「Habanos S.A.」は未登録（移行時に要対応）
- legacy: bat-leaves-cuba の source_name「Cigars-connect」は未登録（移行時に要対応）
- legacy: cuba-tobacco-season-2026-27 の source_name「Cigars-connect」は未登録（移行時に要対応）
- legacy: punch-nectares-ireland の source_name「Cigar Journal」は未登録（移行時に要対応）
- legacy: hoyo-de-monterrey-160th の source_name「Cigar Journal」は未登録（移行時に要対応）
- legacy: cohiba-year-2026 の source_name「Cigar Journal」は未登録（移行時に要対応）
- legacy: cohiba-wide-short-limited-edition の source_name「Cigar Journal」は未登録（移行時に要対応）
- legacy: bogota-cigar-humidor-opens の source_name「Cigar Journal」は未登録（移行時に要対応）
- legacy: la-flor-de-cano-magicos-spain の source_name「Cigar Journal」は未登録（移行時に要対応）
- legacy: lcdh-kuala-lumpur-1st-anniversary の source_name「Cigar Journal」は未登録（移行時に要対応）
- legacy: por-larranaga-intemporales-switzerland の source_name「Cigar Journal」は未登録（移行時に要対応）
- legacy: lgc-serie-brasil-no3 の source_name「Cigar Journal」は未登録（移行時に要対応）
- legacy: counterfeit-habanos-seized-spain の source_name「Cigar Journal」は未登録（移行時に要対応）
- legacy: cohiba-atmosphere-tel-aviv の source_name「Cigar Journal」は未登録（移行時に要対応）
- legacy: cubas-cigar-paradox の source_name「Cigar Journal」は未登録（移行時に要対応）
- legacy: published 79 件の主張対応表は未作成（移行は別途承認）
- legacy: published 79 件の承認記録は未登録（移行は別途承認）

## 総合判定: 合格（全項目パス）
