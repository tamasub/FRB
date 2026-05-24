# FRB — Fishing Rod Benchmark

*Sensitivity becomes real when it can be shared.*

～　[感覚は分かち合って初めて本物になる](https://qiita.com/tamasub364/items/2b6649748e1772b7eec1)　～

*Turning fishing rod vibration into shareable sensitivity metrics.*

![status](https://img.shields.io/badge/status-research-blue)
![platform](https://img.shields.io/badge/platform-ESP32-green)
![analysis](https://img.shields.io/badge/analysis-FFT-orange)

---

## 🎯 Overview

**FRB (Fishing Rod Benchmark)** is a project to create a shared language for **fishing rod sensitivity**.

Fishing rod sensitivity has traditionally been subjective and difficult to describe.  
FRB aims to make it **observable, measurable, and shareable**.

The goal is **not replacing human feeling**.  
The goal is making **human perception shareable**.

---

## 🔍 Concept

FRB transforms:

- human experience  
→ into  
- measurable and comparable data  

This allows rod performance to be discussed in a structured way.

> **Sensitivity = characteristics of vibration**

---

## 🧱 Architecture

FRB is composed of two main phases:

### Phase 1 — Surface Response

- Measures vibration characteristics (magnitude + frequency)  
- Input: continuous contact (rubbing test)  
- Purpose: understand frequency response  

👉 Comparable to **Sequential Read/Write** in SSD benchmarks

---

### Phase 2 — Simulated Bite Response

- Measures response to load changes (tension variation)  
- Input: simulated bite (controlled impulse / pull)  
- Purpose: evaluate transmission characteristics  

👉 Comparable to **IOPS (random access)** in SSD benchmarks

---

## 📊 Structure

| Category | FRB | SSD Benchmark |
|--------|-----|--------------|
| Phase 1 | Surface Response | Sequential |
| Phase 2 | Bite Response | IOPS |

---

## 🧪 Example Scores

### Phase 1

:::note info
Phase1 Score (Surface Response)

J: 99 (Carpet / Low frequency)  
F: 85 (Flooring / Mid frequency)  
S: 72 (Stainless / High frequency)
:::

---

### Phase 2

:::note info
FRB Phase2 Score (Simulated Bite Response)

Impulse: 92   (impact response)  
Suction: 78   (pull response)  
Weed: 65      (interference response)
:::

---

## 🧠 Key Idea

Fish bites are not “mysterious signals.”

They are:

> **changes in force (tension variation)**

FRB treats all bite sensations as:

- Impulse (impact)  
- Suction (pull)  
- Weed (interference)  

→ All observable as **load changes on the line**

---

## 🎯 Design Philosophy

### 1. Reproducibility

- Indoor testing possible  
- No special equipment required  
- Comparable under consistent conditions  

---

### 2. Simplicity

- Max 3 metrics per phase  
- Expandable via additional phases  

---

### 3. Purpose

FRB is not designed for evaluation.

> **FRB is a metric for selection.**

---

## 🌍 Vision

Instead of:

> “This rod is sensitive”

We aim for:

> “This rod has these vibration characteristics”

---

## 📚 Repository Structure

This repository contains the following core documents:

* **FRB Method** — measurement framework
  → [FRB Method](./docs/FRB_METHOD.md)

* **FRB Spec** — formal definitions
  → [FRB Spec](./docs/FRB_SPEC.md)

* **FRB Data Spec** — data structure (Draft)
  → [FRB Data Spec](./docs/FRB_DATA_SPEC.md)

* **FRB Versioning** — versioning rules
  → [FRB Versioning](./docs/FRB_VERSIONING.md)

* **FRB Terms** — terminology
  → [FRB Terms](./docs/FRB_TERMS.md)

* **FRB Experiments** — experimental logs
  → [FRB Experiments](./docs/FRB_EXPERIMENTS.md)

* **FRB Story** — origin and background
  → [FRB Story](./docs/FRB_STORY.md)

* **FRB Blog** — origin and background
  → [FRB Blog](./FRB_Blog/README.md)

* **FRB Tools** — origin and background
  → [FRB Tools](./tools/README.md)


---


## 🧭 Where to Start

👉 If you're new:

- Read: `FRB_METHOD.md`

👉 If you're technical:

- Check: `FRB_EXPERIMENTS.md`

👉 If you're curious about the origin:

- Read: `FRB_STORY.md`

---

## ⚠️ Status

FRB is currently in:

> **Draft / Experimental phase**

The methodology is under continuous validation.

---

## ✨ Final Note

FRB does not measure:

- catch rate  
- fishing skill  

FRB measures:

> **the structure of what you feel**

---

## 🚀 Future

- Standardization of input methods  
- Sensor-based validation (ESP32 / FFT)  
- Open benchmark dataset  

---

## 🧩 Philosophy

> Sensitivity becomes real only when it can be shared.


## Revision History

- 2026-03-14 : 初版
- 2026-03-26 : ファイル構造見直し
