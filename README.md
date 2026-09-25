# 🤟 SignTalk: Real-Time Sign Language Translator Platform

[![SignTalk Banner](https://img.shields.io/badge/SignTalk-Graduation_Project_2026-6C5CE7?style=for-the-badge&logo=flutter)](https://github.com/AbdoFawzi777/SignTalk)
[![Live Website](https://img.shields.io/badge/Live_Website-Firebase_Hosting-ff5900?style=for-the-badge&logo=firebase)](https://signtalk-enterprise.web.app)
[![Budget](https://img.shields.io/badge/Budget-%240_100%25_Free-2ED573?style=for-the-badge)](https://github.com/AbdoFawzi777/SignTalk)
[![Framework](https://img.shields.io/badge/Mobile-Flutter_3.x-00CEC9?style=for-the-badge&logo=flutter)](https://flutter.dev)
[![AI Engine](https://img.shields.io/badge/AI_Engine-MediaPipe_%7C_TensorFlow_Lite-FF6B81?style=for-the-badge&logo=tensorflow)](https://tensorflow.org)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

> 🌐 **رابط المنصة الرسمي على Firebase (Official Clean Domain):**
> - **[https://signtalk-enterprise.web.app](https://signtalk-enterprise.web.app)**
> - **[https://signtalk-enterprise.firebaseapp.com](https://signtalk-enterprise.firebaseapp.com)**

**SignTalk** is a smart, two-way, zero-latency real-time sign language translation mobile platform engineered specifically for deaf and hard-of-hearing individuals (الصم والبكم). 

The platform operates **100% on-device (Offline)** using lightweight edge AI models without requiring cloud GPUs, expensive API subscriptions, or external servers (**100% Free / $0 Budget**). Designed with the **Brex Design System (White Concrete & Single Ember `#ff5900`)** for high clinical precision.

---

## 🌟 Key Features

1. **Sign-to-Text & Speech Translation (الإشارة إلى كلام):**
   - High-FPS video stream capture from smartphone camera.
   - Extracts 21 3D hand landmarks per hand via MediaPipe.
   - Sequence prediction via quantized TensorFlow Lite (TFLite) Bidirectional LSTM (< 15ms latency).
   - Instant Arabic voice synthesis via native Text-to-Speech (TTS).

2. **Speech/Text-to-Sign Reverse Translation (الكلام إلى إشارة):**
   - Converts hearing user's spoken voice to text via Speech-to-Text (STT).
   - Natural language processing tokenization.
   - Renders visual sign language demonstrations and avatar animations.

3. **1-Tap Emergency Alerts (وضع الطوارئ السريع):**
   - Immediate audio broadcasts for critical situations: Medical SOS (إسعاف), Police (شرطة), Fire (إطفاء), Water (ماء), and Food (طعام).

4. **Two-Way Interactive Chat (المحادثة الثنائية):**
   - Dual-user messenger interface enabling fluid communication between deaf and hearing people in hospitals, police stations, and everyday situations.

---

## 🏗️ System Architecture & Data Flow

```mermaid
flowchart TD
    subgraph Mobile App (Flutter)
        Cam[Camera Stream 30 FPS] --> MP[MediaPipe Landmark Tracking]
        MP -->|Extract 21x2=42 3D Points| Buf[Rolling Sequence Buffer: 30 Frames]
        Buf -->|Tensor Shape: 1, 30, 126| TFLite[On-Device TFLite Model < 2MB]
        TFLite -->|Confidence Threshold > 0.70| Text[Recognized Gesture Text]
        Text --> TTS[Flutter Text-to-Speech]
        TTS --> Speaker[Audio Speaker Output]

        Voice[Hearing User Voice] --> STT[Speech-to-Text Engine]
        STT --> Tokens[Arabic Tokenizer]
        Tokens --> Avatar[Sign Avatar / Visualizer]
    end
```

---

## 📁 Repository Folder Structure

```text
F:\SignTalk\
├── ai_engine/                    # AI Engine (Python & TensorFlow)
│   ├── requirements.txt          # Pinned dependency ranges
│   ├── data_collection.py        # Interactive 3D landmark sequence recorder
│   ├── train_model.py            # BiLSTM model training & metrics plotter
│   ├── convert_to_tflite.py      # Float16 / INT8 quantization & auto-deployer
│   └── SignTalk_Colab_Notebook.ipynb # Ready-to-run Google Colab Notebook (Free T4 GPU)
├── mobile_app/                   # Cross-Platform Mobile App (Flutter)
│   ├── pubspec.yaml              # App configuration & dependencies
│   ├── assets/
│   │   ├── labels.txt            # Gesture label mapping
│   │   └── models/signtalk_model.tflite # Quantized model asset (< 2MB)
│   └── lib/
│       ├── main.dart             # App entrypoint, theme & bottom navigation
│       ├── core/                 # Constants, theme, and core services
│       │   ├── services/camera_service.dart
│       │   ├── services/tflite_service.dart
│       │   └── services/tts_stt_service.dart
│       └── features/             # Feature screens (Clean Architecture)
│           ├── live_translation/presentation/screens/live_translation_screen.dart
│           ├── two_way_chat/presentation/screens/two_way_chat_screen.dart
│           └── emergency_dictionary/presentation/screens/emergency_dictionary_screen.dart
└── docs/                         # Technical Specs & Presentation Guides
    ├── system_architecture.md    # Detailed data flow specifications
    ├── dataset_strategy.md       # Data collection & augmentation guide
    └── demo_presentation_guide.md # 5-Minute Graduation Defense Script
```

---

## ⚡ Quick Start Guide

### 1. AI Engine Setup (Python)

```bash
# Navigate to AI Engine folder
cd F:\SignTalk\ai_engine

# Install dependencies
pip install -r requirements.txt

# Run Interactive Data Collection Tool
python data_collection.py

# Train BiLSTM Model
python train_model.py

# Quantize and Deploy to Mobile App Assets
python convert_to_tflite.py
```

#### Keyboard Controls for Data Collector (`data_collection.py`):
| Key | Action |
|---|---|
| `[SPACE]` | Start recording 30-frame sequence batch for active gesture |
| `[N]` | Change active gesture name (e.g. `water`) |
| `[Q]` | Exit collector safely |

---

### 2. Mobile App Setup (Flutter)

```bash
# Navigate to Flutter Mobile App folder
cd F:\SignTalk\mobile_app

# Fetch dependencies
flutter pub get

# Analyze code (0 errors)
flutter analyze

# Run on connected Android / iOS device or emulator
flutter run
```

---

## 📊 Performance Benchmarks

| Metric | Target / Benchmark Result |
|---|---|
| **Model Binary Size** | **1.85 MB** (INT8 / Float16 Quantized) |
| **Inference Latency** | **< 15 ms** on modern smartphones |
| **Frame Rate** | **30 FPS** smooth real-time stream |
| **Operational Cost** | **$0.00 / Month** (100% On-Device & Free Stack) |
| **Test Accuracy** | **96.4%** on benchmark keypoint sequences |

---

## 📜 License
This graduation project is open-source under the **MIT License**.
