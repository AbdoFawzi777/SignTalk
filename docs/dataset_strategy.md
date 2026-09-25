# SignTalk - Datasets Strategy & Expansion Guide

## 1. Executive Strategy

To ensure high accuracy while maintaining zero cost, SignTalk uses a **3D Landmark Keypoint Vector Representation** instead of storing or training on heavy raw video files. Storing 3D coordinates reduces dataset disk footprint by over **99%** (1 sequence file is ~15 KB instead of 10 MB video), enabling rapid model training in minutes on Google Colab's free GPU tier.

---

## 2. Hybrid Data Sourcing Plan

```
SignTalk Dataset
├── Source A: Self-Collected Data (data_collection.py)
│   ├── Egyptian Sign Language (LSO) Gestures
│   └── Emergency Phrases (Help, Doctor, Police, Fire, Water, Food)
└── Source B: Public Arabic Sign Language (ArSL) Open Datasets
    ├── ArSL21 Dataset (21 Common Words)
    ├── KACST ArSL Dataset (Alphabets & Numbers)
    └── Kaggle Arabic Sign Language Datasets
```

---

## 3. Recommended Gesture Action Classes

| ID | Class Label (Arabic) | Gesture Description | Priority |
|---|---|---|---|
| 0 | **مرحباً** | Hand wave greeting | High |
| 1 | **شكراً** | Hand touching chin moving outward | High |
| 2 | **مساعدة** | Open palm lifted by fist | Critical (Emergency) |
| 3 | **طبيب** | Two fingers on wrist pulse point | Critical (Emergency) |
| 4 | **ماء** | Three fingers touching mouth | High |
| 5 | **طعام** | Pinch fingers to mouth | High |
| 6 | **شرطة** | C-shape hand near shoulder/chest | Critical (Emergency) |
| 7 | **نعم** | Nodding fist sign | Medium |
| 8 | **لا** | Index finger side-to-side move | Medium |
| 9 | **طوارئ** | Rapid SOS waving palm | Critical (Emergency) |

---

## 4. Landmark Data Augmentation Techniques

To prevent model overfitting and increase real-world generalization across different users and camera angles, data augmentation is performed directly on the keypoint matrices:

1. **Spatial Translation (Jittering):**
   $$\mathbf{x}_{aug} = \mathbf{x} + \Delta x, \quad \Delta x \sim \mathcal{N}(0, 0.01)$$
2. **Coordinate Scaling:**
   Simulating different hand-to-camera distances by scaling $(x, y)$ values by factor $s \in [0.9, 1.1]$.
3. **Temporal Interpolation:**
   Subsampling or upsampling sequence frames to simulate faster or slower gesture speeds.
