# 責務棚卸し Phase 2 Pilot — Guarantee横断比較

作成日: 2026-08-22  
ステータス: Draft / Phase 2 Pilot  
対象: FRB Studio / AI承認駆動開発  
目的: 既存Guaranteeを先に抽象化せず横並びにし、同じ意味を持つ保証が実際に複数責務から現れるかを観察する。

---

## 0. Pilotのルール

このPilotでは、最初からBehavior Pattern名を決めない。

```text
既存Responsibility
        ↓
既存Guaranteeを原文のまま横断比較
        ↓
意味の近いGuaranteeを「候補」として並べる
        ↓
人間レビュー
        ↓
必要ならBehavior Pattern名を付ける
        ↓
TestPattern / Expected生成可能性を評価
```

禁止事項:

- `NO_MUTATION` / `EMPTY_SAFE` / `ORDER_PRESERVE` 等の標準名を先に押し付けない。
- Guaranteeの意味が近そうという理由だけで統合しない。
- TestPatternが存在することを推測しない。
- 責務粒度そのものの変更は、このPilotではまだ行わない。

---

## 1. 入力ソース

最新資材 `FRBStudio_App20260822_193226.zip` 内の次ファイルを入力とする。

`data/json/03_tests/responsibilities/responsibility_data_v0_1.json`

対象責務:

| responsibility_cd | 責務名 | Guarantee数 |
|---|---|---:|
| `grid_column_build` | Grid列生成責務 | 5 |
| `search_filter` | 検索条件評価責務 | 8 |
| `csv_export` | CSV出力責務 | 6 |
| `grid_aggregate` | Grid数値集計責務 | 6 |
| **合計** |  | **25** |

---

## 2. 25 Guarantee 原文一覧

> この表は最新資材の責務JSONから抽出した原文を基準とする。Phase 1 v0.4でレビュー表現を補強した `grid_column_build_g004/g005` の文言は、ここではソースJSON原文を保持する。

| No | responsibility_cd | guarantee_id | type | condition | guarantee | observable_result | expected_def_type | test_pattern_seed |
|---:|---|---|---|---|---|---|---|---|
| 1 | `grid_column_build` | `grid_column_build_g001` | `rule` | fieldsにgrid.visible=falseの項目が含まれる場合 | 当該項目をGrid列へ含めない。 | 返却列のfield一覧に非表示項目が存在しない。 | `RuleExpectedDef` | visible=false除外パターン |
| 2 | `grid_column_build` | `grid_column_build_g002` | `state` | 表示対象フィールドが複数ある場合 | 返却列の順序はViewDef fieldsの順序を維持する。 | 返却field一覧が入力順と一致する。 | `StateExpectedDef` | 表示列の順序維持パターン |
| 3 | `grid_column_build` | `grid_column_build_g003` | `rule` | fieldsが未指定または空配列の場合 | 例外で停止せず空配列を返す。 | 返却値が空配列である。 | `RuleExpectedDef` | fields未指定安全パターン |
| 4 | `grid_column_build` | `grid_column_build_g004` | `interface` | includeField方針が呼出側から指定された場合 | 指定された方針による列採用結果を返す。 | includeFieldの判定結果と返却列が一致する。 | `InterfaceExpectedDef` | カスタムincludeField適用パターン |
| 5 | `grid_column_build` | `grid_column_build_g005` | `no_side_effect` | Grid列を生成した場合 | 入力されたfields定義を変更しない。 | 処理前後のfieldsが同一である。 | `StateExpectedDef` | ViewDef fields非破壊パターン |
| 6 | `search_filter` | `search_filter_g001` | `rule` | 有効な検索条件が1件以上指定された場合 | すべての検索条件に一致する行だけが結果に含まれる。 | 結果行IDが条件一致行IDと一致し、不一致行を含まない。 | `StateExpectedDef` | 条件一致行だけを返す基本パターン |
| 7 | `search_filter` | `search_filter_g002` | `rule` | 文字列contains条件が指定された場合 | 大文字・小文字の違いに依存せず部分一致を評価する。 | Alpha / alpha / ALPHA を同じ検索語で一致確認できる。 | `RuleExpectedDef` | contains検索の大文字小文字差分パターン |
| 8 | `search_filter` | `search_filter_g003` | `state` | 検索結果が生成された場合 | 各結果行は元データ上のIndexを保持する。 | 結果のindexesが元データの位置と一致する。 | `StateExpectedDef` | gte検索で一致行と元Indexを同時確認する |
| 9 | `search_filter` | `search_filter_g004` | `rule` | 数値条件に gte / lte / equals が指定された場合 | 指定された数値比較演算に従って一致判定する。 | 境界値の直前・境界値・直後で期待どおりの行が返る。 | `RuleExpectedDef` | gte/lte/equalsの境界値パターン |
| 10 | `search_filter` | `search_filter_g005` | `rule` | 複数選択値が指定され、対象値が配列の場合 | 指定候補のいずれかを含む行を一致として扱う。 | 選択候補と配列セルの交差がある行だけが返る。 | `RuleExpectedDef` | 複数選択と配列セルの一致パターン |
| 11 | `search_filter` | `search_filter_g006` | `no_side_effect` | 検索条件を評価した場合 | 入力されたrowsを変更しない。 | 評価前後の入力rowsが同一である。 | `StateExpectedDef` | 検索前後の入力非破壊パターン |
| 12 | `search_filter` | `search_filter_g007` | `rule` | 全文検索語が指定された場合 | 行が保持するobject / arrayを再帰走査し、いずれかの文字列値に部分一致すれば親行を結果へ含める。 | 表示列に検索語がなくても、子Grid・詳細・非表示項目の文字列値に一致する親行が返る。 | `RuleExpectedDef` | 子配列の文字列一致で親行が残るパターン |
| 13 | `search_filter` | `search_filter_g008` | `constraint` | 全文検索を評価する場合 | 検索対象は文字列値だけとし、objectのキー名・number・booleanは検索対象へ含めない。 | キー名だけ、または数値・booleanだけに検索語が存在しても一致行にならない。 | `RuleExpectedDef` | キー名と数値を全文検索対象外にするパターン |
| 14 | `csv_export` | `csv_export_g001` | `rule` | keyFieldNameが指定され、表示列にkey列が含まれない場合 | key列をCSV対象列の先頭へ追加する。 | 返却field_namesの先頭がkeyFieldNameと一致する。 | `RuleExpectedDef` | 表示列へkey列を補完するパターン |
| 15 | `csv_export` | `csv_export_g002` | `rule` | key列がすでに対象列へ含まれる場合 | 同じfieldを重複して出力しない。 | CSVヘッダーに同一fieldが一度だけ現れる。 | `RuleExpectedDef` | key列重複防止パターン |
| 16 | `csv_export` | `csv_export_g003` | `rule` | セル値にカンマ・ダブルクォート・改行が含まれる場合 | CSV規則に従い値をダブルクォートで囲み、内部ダブルクォートを二重化する。 | CSV文字列が期待するescape済み文字列と一致する。 | `CsvExpectedDef` | カンマ・引用符・改行escapeパターン |
| 17 | `csv_export` | `csv_export_g004` | `state` | CSV文字列を生成した場合 | 列順と行順を入力順のまま維持する。 | ヘッダー列順およびデータ行順が入力順と一致する。 | `CsvExpectedDef` | 列順・行順維持パターン |
| 18 | `csv_export` | `csv_export_g005` | `rule` | include_bom=trueが指定された場合 | CSV文字列の先頭にUTF-8 BOMを付与する。 | has_bom=trueかつ先頭文字がBOMである。 | `CsvExpectedDef` | UTF-8 BOM付与パターン |
| 19 | `csv_export` | `csv_export_g006` | `rule` | lineBreakが未指定の場合 | CRLFを使用し、末尾にも改行を付ける。 | CSV文字列がCRLF区切りかつ末尾CRLFで終了する。 | `CsvExpectedDef` | 既定改行コードパターン |
| 20 | `grid_aggregate` | `grid_aggregate_g001` | `rule` | number型fieldにgrid.aggregate.operator=sumが宣言された場合 | 当該列の合計結果を生成する。 | items/byFieldに対象fieldのsum結果が存在する。 | `StateExpectedDef` | number列sum基本パターン |
| 21 | `grid_aggregate` | `grid_aggregate_g002` | `rule` | aggregate.scope=filteredが指定された場合 | filteredRowsだけを集計対象にする。 | source_countとvalueがfilteredRowsから算出した値に一致する。 | `RuleExpectedDef` | filteredスコープ集計パターン |
| 22 | `grid_aggregate` | `grid_aggregate_g003` | `rule` | aggregate.scope=allが指定された場合 | currentRows全体を集計対象にする。 | source_countとvalueがcurrentRows全体から算出した値に一致する。 | `RuleExpectedDef` | allスコープ集計パターン |
| 23 | `grid_aggregate` | `grid_aggregate_g004` | `rule` | 値が数値またはカンマ区切り数値文字列の場合 | 有限数へ解釈できる値を合計へ含める。 | 1,234.5が1234.5として集計される。 | `RuleExpectedDef` | カンマ区切り数値解釈パターン |
| 24 | `grid_aggregate` | `grid_aggregate_g005` | `state` | 空文字・非数値・非有限値が含まれる場合 | 当該値を合計から除外し、ignored_countへ計上する。 | value / valid_count / ignored_countが期待値と一致する。 | `StateExpectedDef` | 無効値除外と件数内訳パターン |
| 25 | `grid_aggregate` | `grid_aggregate_g006` | `rule` | 有効なaggregate宣言が存在しない場合 | 集計なしとしてhas_aggregates=falseを返す。 | itemsが空でhas_aggregates=falseである。 | `RuleExpectedDef` | 集計宣言なし互換パターン |

---

## 3. 初回横断観察 — 類似候補（未承認）

ここからは**ソース原文そのものではなく、横断比較から得た観察候補**である。まだBehavior Patternではない。

### 候補A — 「入力を変更しない」

- `grid_column_build_g005`: 入力されたfields定義を変更しない。
- `search_filter_g006`: 入力されたrowsを変更しない。

観察:

> 対象オブジェクトは異なるが、「処理対象として受け取った入力を副作用で変更しない」という意味はかなり近い。

確認したいこと:

- 同じBehaviorとして扱ってよいか。
- fields / rows以外にも同種保証が今後出てくるか。
- Expectedを「処理前後Diff 0件」のように共通生成できるか。

### 候補B — 「入力順を維持する」

- `grid_column_build_g002`: 返却列の順序はViewDef fieldsの順序を維持する。
- `csv_export_g004`: 列順と行順を入力順のまま維持する。

観察:

> 「順序を勝手に変えない」という意味は近い。ただし、Grid列だけの順序保持と、CSVの列順＋行順保持では対象範囲が異なる。

確認したいこと:

- 共通Behavior本体＋Option（列 / 行）の形にできるか。
- それとも別Behaviorに分けるべきか。

### 候補C — 「対象がない場合の安全な結果」

- `grid_column_build_g003`: fields未指定または空配列なら、例外停止せず空配列を返す。
- `grid_aggregate_g006`: 有効なaggregate宣言がなければ、items空・has_aggregates=falseを返す。

観察:

> どちらも「対象がないことを異常終了にせず、空・なしを表す正常結果へ落とす」構造に見える。ただし返却契約はかなり異なる。

確認したいこと:

- 同じBehaviorへ寄せる価値があるか。
- 「空入力」と「機能宣言なし」は意味を分けるべきではないか。

### 候補D — 「除外する」

- `grid_column_build_g001`: `grid.visible=false` の項目をGrid列へ含めない。
- `search_filter_g001`: 条件不一致行を結果へ含めない。
- `search_filter_g008`: キー名・number・booleanを全文検索対象へ含めない。
- `grid_aggregate_g005`: 空文字・非数値・非有限値を合計から除外する。

観察:

> 日本語ではすべて「除外」だが、対象・判定タイミング・出力契約が違う。**これは無理に共通化すると危険な候補**として扱う。

確認したいこと:

- 「除外」という動詞だけではBehavior Pattern化の根拠として弱いのではないか。
- Behaviorには対象・判定条件・結果契約まで必要ではないか。

---

## 4. このPilotで既に見えた重要点

### 4.1 Guaranteeの文言一致だけでは共通化できない

「除外」「維持」「変更しない」のような動詞は複数責務に現れる。

しかしBehavior Patternとして安全に扱うには、少なくとも次を一緒に見る必要がありそうである。

```text
対象
条件
保証
観測結果
Expected生成方法
```

### 4.2 共通化しやすそうな候補と、危険な候補がある

現時点では、

- 入力非破壊: 比較的近い
- 順序維持: 近いがOption化の検討が必要
- 空・なし安全: 一見近いが意味差が大きい
- 除外: 動詞だけの一致で、安易な共通化は危険

という差が見える。

これはまだ結論ではなく、**人間レビューへ出すための観察結果**とする。

---

## 5. 次の人間レビュー

Phase 2 Pilotの次の確認対象は、まず候補A・Bの2つに絞る。

```text
候補A: 入力を変更しない
候補B: 入力順を維持する
```

レビューで確認したい問い:

1. この2組は、本当に同じ意味のBehaviorとして承認できるか。
2. 共通Behaviorにした場合、責務ごとの差分はOptionとして表せるか。
3. 1 Behavior承認からTestPatternを何件生成できるか。
4. Expectedを機械生成するために不足している情報は何か。

候補C・Dは、A・Bで共通化の形を掴むまでは保留する。

---

## 6. Phase 2 Pilotの出口条件

- 少なくとも1つのBehavior Pattern候補について、人間が「同じ意味」と承認できる。
- そのBehavior Patternから生成できるTestPattern候補を列挙できる。
- Expected生成に必要な入力情報を特定できる。
- 共通化してはいけない類似Guaranteeの例を1つ以上残せる。
- Behavior名は、人間承認後に初めて確定する。

---

## Revision History

- 2026-08-22 / v0.1: Phase 2 Pilot開始。最新資材の4責務・25 Guaranteeを原文で横断配置し、Behavior名を付けずに類似候補A〜Dを観察。次レビュー対象を「入力非破壊」「順序維持」の2候補へ限定。
