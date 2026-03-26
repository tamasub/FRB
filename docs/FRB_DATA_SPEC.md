# FRB Data Specification (Draft)

Fishing Rod Benchmark (FRB) の測定結果を、
再現可能・比較可能・共有可能な形で記録するための
データ仕様（Draft）を定義する。

---

## Status

**Draft**

本仕様は初期ドラフトであり、
今後の実験・検証に応じて変更される可能性がある。

特に以下は将来的に変化しうる。

* Phase1 の代表素材および識別子
* Phase2 の指標名称
* 各 Phase の入力条件
* 補助メタデータ項目

FRBでは、
**意味のある比較構造を維持しながら、項目の進化を許容すること**
を重視する。

---

## 1. Purpose

FRB_DATA_SPEC は、
FRB測定結果を機械可読な形で記録・共有するための
共通フォーマットである。

目的は以下の通り。

* 測定結果を記録できること
* 入力条件と結果をセットで保持できること
* 比較・集計・可視化に利用できること
* 指標の追加・削除・名称変更に耐えられること

---

## 2. Design Principle

FRB_DATA_SPEC は、以下の設計思想に基づく。

### 2.1 固定するもの

以下は基本的に固定構造として扱う。

* schema_version
* frb_version
* phase
* test
* metrics
* notes

---

### 2.2 固定しないもの

以下は将来的な変更を許容する。

* 指標キー（例: J / F / S / Impulse / Suction / Weed）
* 素材名
* 入力方式
* 補助説明
* メタ情報の追加

---

### 2.3 基本方針

FRBでは、

**項目名を固定しない。枠だけを固定する。**

このため、
スコアは固定カラムではなく、
**可変指標の集合（metrics）** として保持する。

---

## 3. Top-Level Structure

FRBデータは、以下のトップレベル構造を持つ。

```json
{
  "schema_version": "0.1-draft",
  "frb_version": "draft",
  "phase": 1,
  "test": {},
  "metrics": [],
  "notes": []
}
```

---

## 4. Field Definitions

### 4.1 schema_version

このデータ仕様自体のバージョン。

```json
"schema_version": "0.1-draft"
```

---

### 4.2 frb_version

FRB規格・定義側のバージョン。

```json
"frb_version": "draft"
```

---

### 4.3 phase

測定対象のフェーズ番号。

```json
"phase": 1
```

---

### 4.4 test

入力条件・環境条件・試験条件を格納するオブジェクト。

```json
"test": {
  "type": "surface_response",
  "environment": "indoor",
  "angle_deg": 45
}
```

---

### 4.5 metrics

測定結果本体（可変指標）。

```json
"metrics": [
  {
    "key": "J",
    "label": "絨毯",
    "score": 99,
    "description": "low_band_response"
```



## Revision History

- 2026-03-26 : v0.1-draft 初版
