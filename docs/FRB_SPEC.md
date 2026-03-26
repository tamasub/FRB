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
* スコア項目の追加・削除

FRBでは、
**比較構造を維持しながら、スコアの進化を許容すること**
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
* スコア項目の変化に耐えられること

---

## 2. Design Principle

FRB_DATA_SPEC は、以下の設計思想に基づく。

### 2.1 固定するもの

* schema_version
* frb_version
* phase
* test
* scores
* notes

---

### 2.2 固定しないもの

* スコアキー（J / F / S / Impulse / Suction / Weed など）
* 素材名
* 入力方式
* スコア項目の構成

---

### 2.3 基本方針

FRBでは、

**スコア項目は固定しない。構造のみ固定する。**

このため、
スコアは固定カラムではなく、
**可変スコア集合（scores）** として保持する。

---

## 3. Top-Level Structure

```json
{
  "schema_version": "0.1-draft",
  "frb_version": "draft",
  "phase": 1,
  "test": {},
  "scores": [],
  "notes": []
}
```

---

## 4. Field Definitions

### 4.1 schema_version

データ仕様のバージョン。

```json
"schema_version": "0.1-draft"
```

---

### 4.2 frb_version

FRB規格側のバージョン。

```json
"frb_version": "draft"
```

---

### 4.3 phase

測定フェーズ。

```json
"phase": 1
```

---

### 4.4 test

入力条件・環境条件。

```json
"test": {
  "type": "surface_response",
  "environment": "indoor",
  "angle_deg": 45
}
```

---

### 4.5 scores

FRB Score を可変形式で保持する。

```json
"scores": [
  {
    "key": "J",
    "label": "絨毯",
    "score": 99,
    "description": "low_band_response"
  }
]
```

#### 各項目

* `key` : 識別子（変更可能）
* `label` : 表示名
* `score` : 数値
* `description` : 補足説明

---

### 4.6 notes

体感メモ。

```json
"notes": [
  "ジンジン感あり"
]
```

---

## 5. Phase-Specific Structure

### 5.1 Phase1（Surface Response）

```json
{
  "schema_version": "0.1-draft",
  "frb_version": "draft",
  "phase": 1,
  "test": {
    "type": "surface_response",
    "environment": "indoor",
    "surface_set": "default_v1",
    "angle_deg": 45,
    "operator": "manual"
  },
  "scores": [
    { "key": "J", "label": "絨毯", "score": 99 },
    { "key": "F", "label": "フローリング", "score": 85 },
    { "key": "S", "label": "ステンレス", "score": 72 }
  ],
  "notes": [
    "高域強め"
  ]
}
```

---

### 5.2 Phase2（Simulated Bite Response）

```json
{
  "schema_version": "0.1-draft",
  "frb_version": "draft",
  "phase": 2,
  "test": {
    "type": "bite_simulator",
    "environment": "indoor",
    "input_method": "rubber_impulse_3stage",
    "input_version": "draft_v1"
  },
  "scores": [
    { "key": "Impulse", "label": "コツン", "score": 92 },
    { "key": "Suction", "label": "ぬっ", "score": 78 },
    { "key": "Weed", "label": "モゾ", "score": 65 }
  ],
  "notes": [
    "コツン強い"
  ]
}
```

---

## 6. Why scores is Array

* スコアの追加・削除に強い
* 順序を保持できる
* UI / DB と相性が良い
* 将来の拡張に強い

---

## 7. Extension Policy

拡張可能：

* test項目追加
* scores属性追加
* top-level項目追加

---

## 8. Minimal Example

```json
{
  "schema_version": "0.1-draft",
  "frb_version": "draft",
  "phase": 1,
  "test": { "type": "surface_response" },
  "scores": [
    { "key": "J", "score": 99 }
  ],
  "notes": []
}
```

---

## 9. Summary

* 構造は固定
* スコアは可変
* scoresで表現
* Draft前提

---

**FRBは、体験から生まれ、スコアとして共有される。**


## Revision History

- 2026-03-14 : 初版
- 2026-03-26 : 概念整理更新