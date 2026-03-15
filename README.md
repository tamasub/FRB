# FRB — Fishing Rod Benchmark

![status](https://img.shields.io/badge/status-research-blue)
![platform](https://img.shields.io/badge/platform-ESP32-green)
![analysis](https://img.shields.io/badge/analysis-FFT-orange)

**FRB (Fishing Rod Benchmark)** is a project to create a shared language for **fishing rod sensitivity**.

Fishing rod sensitivity has traditionally been subjective and difficult to describe.  
FRB aims to make it **observable, measurable, and shareable**.

The goal is **not replacing human feeling**.

The goal is making **human perception shareable**.

---

# FRB Concept

### What FRB Means

```mermaid
flowchart LR

A[Fishing Rod]

A --> B[Vibration Signals]

B --> C[Sensor System<br/>INMP441 + MPU6050]

C --> D[Signal Processing<br/>ESP32 FFT]

D --> E[FRB Metrics]

E --> F[Rod Benchmark]

F --> G[Shared Sensitivity Language]
```

### System Overview

```mermaid
flowchart LR

A[Fishing Rod] --> B[Vibration]
A --> C[Rod Motion]

B --> D[INMP441 Microphone]
C --> E[MPU-6050 IMU]

D --> F[ESP32]
E --> F

F --> G[FFT / Motion Analysis]

G --> H[FRB Metrics]

H --> I[Human Perception]

I --> J[Shared Sensitivity Culture]
```


FRB converts rod vibration into measurable data while keeping **human perception at the center**.

---

### Human + AI Analysis

```mermaid
flowchart LR

A[Fishing Rod Vibration] --> B[Sensor INMP441/MPU6050]
B --> C[ESP32 FFT Analysis]
C --> D[FRB Metrics]

D --> E[Human Perception]
D --> F[AI Analysis]

E --> G[Shared Sensitivity Culture]
F --> G
```

FRB uses both **human perception** and **AI-assisted analysis** to interpret rod vibration data.

---

### Traditional vs FRB

```mermaid
flowchart LR

subgraph Traditional Fishing
direction LR
A[Fishing Rod] --> B[Human Feeling] --> C[Personal Experience] --> D["'This rod feels sensitive'"]
end

subgraph FRB Approach
direction LR
E[Fishing Rod] --> F[Vibration Measurement] --> G[FFT Analysis] --> H[FRB Metrics] --> I[Human Perception] --> J[Shared Sensitivity Language]
end

D -.-> E
```

Traditional fishing relies on **individual feeling**.

FRB explores whether rod sensitivity can become **observable and comparable**.

---

# Current System

### FRB Architecture

```mermaid
flowchart TD
A[Fishing Rod] --> B[Vibration]
B --> C[INMP441 Microphone / MPU-6050 Rod Motion]

C --> D[ESP32]
D --> E[FFT Analysis]

E --> F[Feature Extraction]
F --> G[FRB Metrics]

G --> H[WebSocket Stream]
H --> I[Web UI Visualization]

I --> J[Human Perception]
```

The experimental setup currently includes:

- ESP32 microcontroller
- INMP441 digital microphone
- FFT-based vibration analysis
- Web-based visualization UI
- Rod comparison experiments


The current experimental setup captures rod vibration,
analyzes the signal using FFT, and visualizes the resulting metrics
through a web-based interface.


---

# Documents

Project documentation:

- [FRB Manifesto](FRB_MANIFESTO.md)
- [FRB Method](FRB_METHOD.md)
- [FRB Spec](FRB_SPEC.md)
- [FRB Terms](FRB_TERMS.md)
- [FRB Experiments](FRB_EXPERIMENTS.md)

---

# Story Behind FRB

The origin story of the project can be found here:

- [FRB Story](FRB_STORY.md)

Personal development notes and research logs:

- [mymemo.md](mymemo.md)

---

# Project Status

FRB is currently in an **experimental research phase**.

Current focus:

- vibration measurement
- signal processing
- perception correlation

---

# Philosophy

> Sensitivity becomes real when it can be shared.

---

FRB — Fishing Rod Benchmark

