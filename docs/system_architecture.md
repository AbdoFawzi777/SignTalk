# SignTalk - Technical System Architecture & Specification

## 1. Architectural Blueprint & Philosophy

SignTalk is engineered with an **Edge-First, Zero-Cloud-Cost ($0 Budget)** architectural design. Rather than sending heavy raw video frames over high-latency network APIs (which incur high cloud server costs and network lag), SignTalk processes all computer vision feature extractions and neural network inferences **100% locally on the user's mobile device**.

---

## 2. End-to-End Data Flow Specification

### A. Sign Language to Speech Pipeline (Sign-to-Speech)

```mermaid
flowchart TD
    subgraph Client Hardware
        Cam[Device Camera 30 FPS] --> FrameProc[YUV to RGB Image Processor]
        FrameProc --> MP[MediaPipe Hands 3D Detector]
    end

    subgraph Feature Extraction & Normalization
        MP -->|21 Left Hand 3D Points| LH[Left Vector: 63 Floats]
        MP -->|21 Right Hand 3D Points| RH[Right Vector: 63 Floats]
        LH & RH --> Concat[Concatenate Feature Vector: 126 Floats]
    end

    subgraph Temporal Engine
        Concat --> Buffer[Rolling Window Buffer: 30 Frames]
        Buffer -->|Tensor Shape: 1, 30, 126| TFLite[TensorFlow Lite BiLSTM Engine]
    end

    subgraph Post-Processing & Output
        TFLite --> Softmax[Softmax Argmax Probabilities]
        Softmax -->|Confidence > 0.70| Label[Gesture Label Lookup]
        Label --> UI[Flutter Screen Text Banner]
        Label --> TTS[Flutter Text-to-Speech Engine]
        TTS --> AudioOut[Device Speaker Audio]
    end
```

---

### B. Speech to Sign Language Pipeline (Speech-to-Sign)

```mermaid
flowchart TD
    subgraph Audio Capture & STT
        HearingUser[Hearing Person Voice] --> Mic[Device Microphone]
        Mic --> STT[Native Speech-to-Text Engine]
        STT --> RawText[Recognized Arabic Text String]
    end

    subgraph NLP & Tokenization
        RawText --> Clean[Text Normalizer & Stopword Filter]
        Clean --> Tokenizer[Key Token Extractor]
        Tokenizer --> Dictionary[ArSL Dictionary Resolver]
    end

    subgraph Rendering Output
        Dictionary --> AvatarEngine[Sign Avatar / GIF Visualizer]
        AvatarEngine --> Screen[Deaf User Screen Render]
    end
```

---

## 3. Key Technical Specifications

### Feature Vector Formulation
For each camera frame $t$, MediaPipe extracts $K = 21$ keypoints for both hands:
$$\mathbf{v}_t = [x_{L,1}, y_{L,1}, z_{L,1}, \dots, x_{L,21}, y_{L,21}, z_{L,21}, x_{R,1}, y_{R,1}, z_{R,1}, \dots, x_{R,21}, y_{R,21}, z_{R,21}]^T \in \mathbb{R}^{126}$$

A sequence window of length $T = 30$ frames (1 second motion) forms input tensor:
$$\mathbf{X} \in \mathbb{R}^{1 \times 30 \times 126}$$

---

## 4. Latency Budget Analysis

| Pipeline Stage | Processing Unit | Latency |
|---|---|---|
| Frame Acquisition (30 FPS) | Camera Service | ~ 33 ms |
| Landmark Extraction | MediaPipe | ~ 10 ms |
| Sequence Accumulation | Circular Buffer | ~ 0 ms |
| TFLite Model Inference | Edge TFLite CPU/NNAPI | **8 - 12 ms** |
| TTS Audio Generation | Native OS Engine | ~ 5 ms |
| **Total System Delay** | **On-Device** | **< 20 ms** |
