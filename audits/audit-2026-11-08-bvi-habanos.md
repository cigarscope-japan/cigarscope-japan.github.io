# 実地監査テスト記録（2026-11-08）

- 対象記事： news/bvi-habanos.html「BVI裁判所、陳志氏のハバノス権益を巡る清算命令を解除へ」
- 選定理由： 数値（28.55%、50%、30超の法人）、企業関係（陳志氏→シンプリー・アドバンスト→アライド・シガー→ハバノスS.A.）、裁判・制裁・流通という複合事実を含み、基準1〜8とG群証跡・ガバナンスを一通り試せるため。
- 出典： Tobacco Reporter（2026-11-06）"Court Returns Control of Habanos S.A. to Chen Zhi" — https://tobaccoreporter.com/2026/11/06/court-returns-control-of-habanos-s-a-to-chen-zhi/
- 監査者： Muse（編集）。本監査は確認記録であり、公開承認ではない。
- 制約どおり、記事本文・記事データ・公開サイトは一切変更していない。

## 主張対応表（抜粋ではなく全件照合の要約）
| 主張 | 原文の該当箇所 | 結果 |
|---|---|---|
| 陳志氏の持分28.55%（ハバノスS.A.） | "his 28.55% stake in Habanos S.A." | 一致 |
| 清算命令の対象は30超の法人、解除すべきと判断 | "liquidation orders covering more than 30 entities … should be discharged" | 一致 |
| 検察側が証拠を示せなかった | "the BVI Attorney General failed to provide admissible evidence" | 一致（admissible の限定は落ちている） |
| シンプリー・アドバンストがアライドへの陳氏持分を保有 | "Simply Advanced Ltd., which holds Chen's interest in Allied Cigar Corporation" | 一致 |
| アライドはマドリード所在、ハバノス50%保有 | "the Madrid-based company that owns 50% of Habanos" | 一致 |
| キューバ国外の2工場、ベガフィナ／フロール・デ・コパン保有 | "two major cigar factories outside Cuba, and the VegaFina and Flor de Copán brands" | 一致 |
| 清算人インターパスが1月から管理 | "liquidators from … Interpath had taken control … in January" | 一致 |
| 返還されれば売却計画が止まる可能性 | "The ruling could halt plans to sell Chen's interests" | 一致 |
| 7月のEU制裁で独・墺・波の流通が混乱 | "EU sanctions imposed on Chen in July … disrupted … Austria, Germany, and Poland" | 一致 |
| 5thアベニューは9月初めから出荷できず破産申請 | "unable to ship cigars since early September and has filed for insolvency" | 一致 |
| 陳氏による容疑の否認（Prince Group 報道官経由） | "Chen has denied the allegations through a Prince Group spokesperson" | **記事に欠落** |
| 疑惑の内容（米英による数十億ドル規模の犯罪企業関与の指摘） | "U.S. and British allegations that Chen was involved in a multibillion-dollar criminal enterprise" | **記事に欠落**（背景説明が薄い） |
| 流通再開には時間がかかる | 原文に対応箇所なし | 編集部の見通し（「みられます」と hedged だが、見解としての分離・明示なし） |

## チェックリスト判定（A〜I群）
- A 出典と一次・二次： 出典名・URL の記録とページ表示は合格。ただし出典種別（secondary）のデータ記録がなく、二次報道のみに基づく記事であることの明示（「報じられた」形式）が本文にない → 不合格（重大度B）
- B 原文との整合性： 数値・固有名詞は全件一致（合格）。ただし当事者の否認という意味の変わる重要事実の欠落あり → 修正推奨（B）。主張対応表は標準様式としては未作成（本監査で試験的に作成し、様式が機能することを確認）→ 証跡不足
- C 日付： 発表日2026-11-06・掲載日2026-11-08とも正確（合格）。発売日は裁判ニュースのため該当なし（正しく欠落）
- D 名称・生産国： 固有名詞は全て原文どおり（合格）。対象国「キューバ」の分類理由（資産がハバノスであるため）は記録されていない → 改善点（C）
- E 噂・推測： 可能性表現は hedged されているが、流通再開の見通しが編集部の見解として分離されていない → 不合格（B）
- F 訂正履歴： 本記事に訂正実績なし。history の仕組み自体が未実装 → 証跡不足
- G 情報源の信頼度： Tobacco Reporter は基準7の条件から T3 相当だが、情報源レジストリ自体が未作成で判定根拠の記録がない → 証跡不足。Cigar Journal は本記事の出典に含まれていない（不使用の実態は合格）が、G群の不使用確認記録は作成されていない → 証跡不足
- H AIの架空防止： 架空情報・誤った補完は検出されなかった（合格）。未検証の主張リストの仕組みは未実装 → 証跡不足
- I ガバナンス： 公開は編集者（カズ）の明示的承認に基づいて行われた実態があり、AIの確認と承認の混同は認められない（実態は合格）。ただし承認日の記録欄がデータにない → 証跡不足

## 総括
- 記事内の事実（数値・固有名詞・日付・企業関係）は原文と全件一致し、架空情報はなかった。
- 不合格は2件（A： 報道ベースの明示なし／E： 推測部分の分離なし、いずれも重大度B）。
- 証跡不足が系統的に6件： いずれも「監査基準は設計済みだが、データ項目・レジストリ・記録様式が未実装」であることに起因する。基準の有効性ではなく、実装の有無の問題。
- 基準そのものの改善点： (1) 企業・裁判ニュースの対象国分類ルールの明文化、(2) 当事者の否認・反論の扱い（重要事実の省略の判定に含める）、(3) 発売日が該当しない記事種別の明記、(4) 主張対応表を公開前フローに組み込む手順の確定。
