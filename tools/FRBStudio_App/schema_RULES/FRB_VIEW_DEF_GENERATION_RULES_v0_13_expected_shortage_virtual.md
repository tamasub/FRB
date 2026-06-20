# FRB ViewDef Generation Rules v0.13 — Expected Shortage VirtualData

## 目的

Expected / Check 定義から、テスト設計の不足や偏りを VirtualData として検出する。

## builder

```json
{
  "builder": "expected_check_shortage_findings",
  "targetPath": "$.expected_shortage_findings",
  "source": {
    "source": "$current",
    "path": "$.expected_checks"
  }
}
```

## 代表ルール

### axisRisk

品質観点 × リスク、チェック観点 × リスクなど、観点とリスクの組み合わせ不足を検出する。

```json
{
  "axisType": "quality_axis",
  "axisLabel": "品質観点",
  "field": "quality_axis_cd",
  "values": [
    { "cd": "display", "name": "表示" },
    { "cd": "evidence", "name": "証跡" }
  ],
  "risks": [
    { "cd": "high", "name": "高", "minCount": 1, "severity": "high" }
  ]
}
```

### constraintCoverage

制約IDごとの Expected 件数不足を検出する。

```json
{
  "enabled": true,
  "field": "constraint_ids",
  "minTotal": 2,
  "minHigh": 0
}
```

### testPatternCoverage

テストパターンごとの Expected 件数不足、高リスク不足を検出する。

```json
{
  "enabled": true,
  "source": {
    "source": "test_patterns",
    "path": "$.test_patterns"
  },
  "idField": "test_pattern_id",
  "titleField": "title",
  "minTotal": 5,
  "minHigh": 1
}
```

### requiredFields

Expected / Check の必須項目未設定を検出する。

```json
[
  { "field": "check_id", "caption": "チェックID", "severity": "high" },
  { "field": "risk_cd", "caption": "リスク", "severity": "high" }
]
```

## 方針

- 不足検出結果は保存対象 JSON に書き戻さない。
- ViewDef の `dataPath` は `targetPath` と一致させる。
- 検出結果には、必ず `check_ids` / `constraint_ids` / `test_pattern_ids` を持たせ、元の証拠候補へ戻れるようにする。

