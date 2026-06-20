# FRB Studio 027 — Expected 不足検出 VirtualData

## 目的

観点分類入り Expected 定義から、テスト設計上の不足・偏りを VirtualData として検出する。

ポイントは、テストパターンを増やす前に、Expected / Check の不足を見える化すること。

## 追加ファイル

```text
defs/qa_shortage_expected_findings_view_def_v0_1.json
```

## 追加 builder

```text
expected_check_shortage_findings
```

別名互換:

```text
expected_checks_shortage_findings
qa_expected_shortage_findings
expected_check_gap_findings
```

## 使い方

```text
データJSON:
  qa_expected_checks_classified_v0_1.json

画面定義JSON:
  qa_shortage_expected_findings_view_def_v0_1.json
```

## 検出するもの

### 1. 観点 × リスク不足

例:

```text
品質観点「表示」× リスク「高」が0件
チェック観点「エラー確認」× リスク「高」が0件
```

### 2. 制約IDごとのExpected薄さ

既定では、制約IDごとの Expected が2件未満なら警告する。

### 3. テストパターンごとのExpected薄さ

既定では、テストパターンごとの Expected が5件未満、または高リスクExpectedが0件なら警告する。

### 4. 必須項目未設定

check_id / test_pattern_id / quality_axis_cd / check_axis_cd / risk_cd / constraint_ids などが未設定なら警告する。

## 出力例

```text
finding_id
severity_cd
finding_type_name
target_type_name
target_cd
target_name
risk_name
check_count
risk_summary
threshold_summary
message
suggested_action
check_ids
constraint_ids
test_pattern_ids
```

## 設計メモ

保存対象 JSON には不足検出結果を書き戻さない。
表示時だけ `$.expected_shortage_findings` に VirtualData として生成する。

