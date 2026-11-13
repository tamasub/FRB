# Grid数値列集計 / v0.18.20 実装レポート

- phase: `v0.18.20-grid-numeric-aggregate-header-row`
- incident: `studio_work_0137`
- 実施日: 2026-07-16
- 正本ソース: ローカル `F:\FRB`

## 結論

ViewDefで宣言した数値列の合計を、Studio Core標準機能として通常Gridの列ヘッダー直下へ表示できるようにした。FX固有のField名や損益計算はCoreへ持ち込まず、GPT FX Lab側は`realized_profit_jpy`列の利用宣言だけを持つ。

## ViewDef契約

```json
{
  "type": "number",
  "grid": {
    "aggregate": {
      "operator": "sum",
      "scope": "filtered",
      "label": "表示合計"
    }
  }
}
```

- MVP演算子は`sum`。
- `scope: filtered`は検索・Plugin Filter後の表示行を対象とする。省略時も`filtered`。
- `scope: all`は`currentRows`全件を対象とする。
- `label`は集計の意味を示す任意ラベル。視覚表示は省スペースな`Σ`に統一し、labelはTooltip / aria-labelの意味補足へ使う。
- `type: number`以外のaggregate宣言は計算対象にしない。

## 責務境界

- `GridAggregator`: Field宣言の解決、対象行の選択、元値の数値化、合計、採用・除外件数を返す純粋責務。
- `grid_detail.js`: `visibleFields`に合わせた`thead`二段目のDOM生成と既存formatによる表示。
- `styles.css`: 二段sticky headerと数値配置。
- ViewDef Schema / 生成ルール: 宣言契約とAI生成時の注意を保持。
- FX ViewDef: 利用宣言だけを保持。

集計値は表示時の派生値であり、Data JSONへの保存、CSV Data行への混入、Document Cardへの表示は行わない。

## 数値の扱い

- 有限のnumberを採用する。
- カンマを含む数値文字列はカンマを除去して採用する。
- `null`、空文字、非数値、`NaN`、`Infinity`は合計から除外する。
- 表示には対象Fieldの既存formatを再利用する。

## 検証結果

### 自動確認

- `node --check`で`grid_aggregator.js`、`grid_detail.js`、責務Smokeテストの構文を確認。
- `responsibility_refactor_first_step_smoke.mjs`: OK。
- aggregate未宣言、number以外、filtered/all、負数、カンマ文字列、空値、非有限値を確認。
- Schema、生成ルール、FX ViewDef、Incident JSONをNode標準`JSON.parse`で確認。

### Studio実画面

対象: `simulattion_集計/batch_20260714_224839_entry_results.json`

| 条件 | 表示行数 | 表示合計 |
|---|---:|---:|
| 全件 | 36 | 3854 |
| Lane = NORMAL | 13 | 5370 |
| Lane = EXPANSION_LITE | 23 | -1516 |

- 集計セルと`損益（円）`列ヘッダーのX座標差・幅差: ともに0px。
- 一段目ヘッダーは`top: 0px`、集計行は`top: 30px`のsticky表示。
- 集計セルは薄い`Σ`と数値だけを表示し、Tooltipで`表示中N件の合計`または`全N件の合計`を補足する。
- ブラウザコンソールエラー: 0件。

## 今後の拡張候補

`count`、`average`、`min`、`max`、group by、小計は今回の範囲外。必要時に`field.grid.aggregate`契約を後方互換で拡張する。
