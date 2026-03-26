# FRB Versioning Policy (Draft)

FRB（Fishing Rod Benchmark）の仕様・データ定義のバージョン管理ルールを定義する。

---

## 1. Purpose

FRBは進化する規格である。

そのため、

* どの定義に基づくものか
* どの時点の仕様か

を明確にする必要がある。

本ポリシーは、
FRBの進化を整理し、
比較可能性と拡張性を両立することを目的とする。

---

## 2. Version Structure

FRBでは以下の形式でバージョンを表現する。

```
<major>.<minor>-<status>
```

例：

* 0.1-draft
* 0.2-beta
* 1.0
* 1.1

---

## 3. Status Definition

### 3.1 draft

* 検証段階
* 仕様が頻繁に変わる
* 後方互換性は保証しない

例：

```
0.1-draft
```

---

### 3.2 beta

* 基本構造が安定
* 実用テスト段階
* 大きな変更は減るが、まだ調整あり

例：

```
0.5-beta
```

---

### 3.3 stable（表記なし）

* 安定版
* 比較基準として使用可能
* 後方互換性を意識

例：

```
1.0
```

---

## 4. Version Increment Rules

### 4.1 major（X.0）

以下の場合に変更する。

* スコア構造の根本変更
* Phase構造の変更
* 比較互換性が失われる変更

例：

```
0.x → 1.0
```

---

### 4.2 minor（0.X）

以下の場合に変更する。

* スコア項目の追加・削除
* test条件の拡張
* descriptionの強化

例：

```
0.1 → 0.2
```

---

### 4.3 status変更

* draft → beta → stable

例：

```
0.2-draft → 0.2-beta → 1.0
```

---

## 5. Scope of Versioning

FRBでは以下を個別に管理する。

### 5.1 FRB Specification

* FRB_SPEC.md
* 概念・定義

例：

```
frb_version: 0.1-draft
```

---

### 5.2 Data Specification

* FRB_DATA_SPEC.md
* データ構造

例：

```
schema_version: 0.1-draft
```

---

### 5.3 Measurement Data

実験データは、
どのバージョンの仕様に基づくかを明示する。

```json
{
  "schema_version": "0.1-draft",
  "frb_version": "0.1-draft"
}
```

---

## 6. Compatibility Policy

### 6.1 draft

* 互換性を保証しない
* 自由に変更可能

---

### 6.2 beta

* できるだけ互換性を維持
* 破壊的変更は最小限

---

### 6.3 stable

* 後方互換性を重視
* 破壊的変更はmajor更新のみ

---

## 7. Tagging (Git)

FRBではGitタグを使用して
バージョンを固定する。

例：

```
v0.1-draft
v0.2-beta
v1.0
```

---

## 8. Practical Rule

FRBの現時点の運用ルール：

* 今はすべて **draft**
* 気にせず変更してよい
* ただしバージョンは必ず上げる

---

## 9. Summary

* FRBは進化する規格である
* バージョンで状態を表す
* draft → beta → stable の流れを持つ
* 互換性は段階的に強化する

---

**FRBは完成するものではなく、更新され続けるものである。**


## Revision History

- 2026-03-26 : 初版