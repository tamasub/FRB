# FRB Architecture (Draft)

FRB（Fishing Rod Benchmark）の全体構造を定義する。

---

## Overview

FRBは、
感度（振動体験）を

**構造化・再現・共有するためのシステム**

である。

---

## Structure

FRBは以下の層で構成される。

### 1. Experience Layer

人間が感じる感度。

* コツン
* ぬぅ
* モゾ

👉 すべての出発点

---

### 2. Input Layer

再現可能な入力。

* 床擦り（Phase1）
* 擬似バイト（Phase2）

👉 感度を発生させる条件

---

### 3. Measurement Layer

振動の観測。

* 加速度
* 音
* FFT解析

👉 振動を可視化

---

### 4. Data Layer

測定結果の構造化。

* FRB Score
* JSONフォーマット

👉 データとして記録

---

### 5. Specification Layer

定義とルール。

* FRB_SPEC.md
* FRB_DATA_SPEC.md
* FRB_VERSIONING.md

👉 比較可能性を担保

---

### 6. Application Layer

活用。

* ロッド比較
* 選択支援
* データ共有

👉 FRBの目的

---

## Flow

```mermaid
flowchart TD

A[Experience]
→ B[Input]
→ C[Measurement]
→ D[Data]
→ E[Specification]
→ F[Application]
```

---

## Key Concept

FRBは、

**体験 → 構造 → データ**

へと変換する仕組みである。

---

## Position

FRBは、

単なる測定手法ではない。

**文化と規格を接続する構造である。**

---

## Status

Draft / evolving

---

## Summary

* 感度は体験から始まる
* 入力で再現する
* 測定で観測する
* データで記録する
* 規格で共有する

---

**FRBは、体験を構造に変えるアーキテクチャである。**



## Revision History

- 2026-03-26 : v0.1-draft 初版