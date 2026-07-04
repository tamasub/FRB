# Responsibility Expected Tests First Set / 責務単位Expectedテスト初期セット

## 基本情報

| 項目 | 値 |
|---|---|
| タイトル | Responsibility Expected Tests First Set / 責務単位Expectedテスト初期セット |
| Work Item | studio_work_0112 |
| Phase | v0.18.8-responsibility-expected-tests-first-set |
| Schema | responsibility_expected_tests_data_v0_1 |
| Document Type | responsibility_expected_tests |
| 対象責務 | grid_column_build / search_filter / csv_export |
| 方針 | v0.18.7で追加した責務Interfaceを対象に、まず小さく動くJSON駆動テストを作る。UI/DOM/VisualEvidence/studio_overlays直接テストは対象外とし、責務Interfaceの入力→出力だけを確認する。 |

## 責務Expectedテストパターン

件数: 6

### grid_column_build_visible_fields_basic / grid.visible=false のfieldをGrid列から除外する

| 項目 | 値 |
|---|---|
| Test Pattern ID | grid_column_build_visible_fields_basic |
| 責務CD | Grid列生成 |
| テスト名 | grid.visible=false のfieldをGrid列から除外する |
| Level | UT |
| ExpectedDef | RuleExpectedDef |
| 有効 | true |

#### Input: ViewDef Fields

件数: 3

| field | caption | type | grid | edit |
| --- | --- | --- | --- | --- |
| id | ID | text | {"visible":false} |  |
| title | タイトル | text | {"visible":true} |  |
| score | Score | number |  |  |

#### Expected: Field Names

- title zzz
- score

### grid_column_build_empty_fields_safe / fields未指定でも空配列を返し落ちない

| 項目 | 値 |
|---|---|
| Test Pattern ID | grid_column_build_empty_fields_safe |
| 責務CD | Grid列生成 |
| テスト名 | fields未指定でも空配列を返し落ちない |
| Level | UT |
| ExpectedDef | ErrorExpectedDef |
| 有効 | true |

### search_filter_contains_case_insensitive / 文字列contains検索は大文字小文字を無視して絞り込む

| 項目 | 値 |
|---|---|
| Test Pattern ID | search_filter_contains_case_insensitive |
| 責務CD | 検索条件評価 |
| テスト名 | 文字列contains検索は大文字小文字を無視して絞り込む |
| Level | UT |
| ExpectedDef | RuleExpectedDef |
| 有効 | true |

#### Input: Rows

件数: 3

| id | title | score |
| --- | --- | --- |
| a | Alpha | 3 |
| b | Beta | 10 |
| c | Gamma | 7 |

#### Input: Criteria

件数: 1

| field | raw | type | operator |
| --- | --- | --- | --- |
| title | GA | text | contains |

#### Expected: Row IDs

- c

#### Expected: Indexes

- 2

### search_filter_number_gte_preserves_indexes / 数値gte検索で条件一致行だけを返し元indexを保持する

| 項目 | 値 |
|---|---|
| Test Pattern ID | search_filter_number_gte_preserves_indexes |
| 責務CD | 検索条件評価 |
| テスト名 | 数値gte検索で条件一致行だけを返し元indexを保持する |
| Level | UT |
| ExpectedDef | StateExpectedDef |
| 有効 | true |

#### Input: Rows

件数: 3

| id | title | score |
| --- | --- | --- |
| a | Alpha | 3 |
| b | Beta | 10 |
| c | Gamma | 7 |

#### Input: Criteria

件数: 1

| field | raw | type | operator |
| --- | --- | --- | --- |
| score | 7 | number | gte |

#### Expected: Row IDs

- b
- c

#### Expected: Indexes

- 1
- 2

### csv_export_visible_fields_with_key_and_escape / 表示列にkey列を追加し、カンマとダブルクォートをCSV escapeする

| 項目 | 値 |
|---|---|
| Test Pattern ID | csv_export_visible_fields_with_key_and_escape |
| 責務CD | CSV出力 |
| テスト名 | 表示列にkey列を追加し、カンマとダブルクォートをCSV escapeする |
| Level | UT |
| ExpectedDef | RuleExpectedDef |
| 有効 | true |
| Input: Resolve Fields | true |
| Input: Key Field | id |
| Expected: Has BOM | false |
| Expected: CSV Text | id,title,score<br>a,"A, quote ""here""",3<br> |

#### Input: Rows

件数: 1

| row | index |
| --- | --- |
| {"id":"a","title":"A, quote \"here\"","score":3} | 0 |

#### Input: Base Fields

件数: 2

| field | caption | type |
| --- | --- | --- |
| title | title | text |
| score | score | number |

#### Input: All Fields

件数: 3

| field | caption | type |
| --- | --- | --- |
| id | id | text |
| title | title | text |
| score | score | number |

#### Expected: Field Names

- id
- title
- score

### csv_export_utf8_bom_option / includeBom=true の場合はUTF-8 BOM付きCSV文字列を返す

| 項目 | 値 |
|---|---|
| Test Pattern ID | csv_export_utf8_bom_option |
| 責務CD | CSV出力 |
| テスト名 | includeBom=true の場合はUTF-8 BOM付きCSV文字列を返す |
| Level | UT |
| ExpectedDef | RuleExpectedDef |
| 有効 | true |
| Input: Include BOM | true |
| Expected: Has BOM | true |
| Expected: CSV Preview | id a  |

#### Input: Rows

件数: 1

| row | index |
| --- | --- |
| {"id":"a"} | 0 |

#### Input: Fields

件数: 1

| field | caption | type |
| --- | --- | --- |
| id | id | text |
