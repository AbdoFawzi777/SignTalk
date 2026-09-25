# SignTalk Enterprise Platform - Architecture & Data Specification

## 1. System Vision
SignTalk Enterprise expands SignTalk into an all-inclusive institutional digital accessibility ecosystem. It enables hospitals, banks, and government agencies to communicate seamlessly with deaf citizens via web counters, smartphone camera tracking, contextual Arabic LLM grammar reconstruction, interactive AI sign academy, and smart GPS emergency dispatchers — all running on a **100% Free / $0 Cost Budget**.

---

## 2. Platform Architecture Diagram

```mermaid
flowchart TD
    subgraph Mobile Engine (Flutter)
        Cam[Mobile Camera] --> Holistic[MediaPipe Holistic: Hands + Face + Pose]
        Holistic --> LocalTFLite[TFLite Model Engine]
        LocalTFLite --> RawTokens[Extracted Keywords]
        RawTokens --> LLMService[Contextual Arabic LLM Grammar Corrector]
        LLMService --> ArabicSentence[Fluent Arabic Sentence]
        ArabicSentence --> TTS[Native Device TTS]
        GPS[GPS Dispatcher] --> SOS[Smart Emergency Dispatcher]
    end

    subgraph Backend Microservices (FastAPI & WebSockets - Free Cloud)
        WS[WebSocket /ws/translation Router] <--> Sync[Real-Time Sync Engine]
        REST[REST API /api/v1 Router] <--> DB[(Supabase Free PostgreSQL)]
        LLM_API[HuggingFace Free Inference API] <--> REST
    end

    subgraph Enterprise Web Portal (React / Web)
        WebCam[Institutional Counter WebCam] --> WebTracking[Web MediaPipe Engine]
        WebTracking --> WS
        WS --> EmployeeDisplay[Employee Screen Banner]
        EmployeeVoice[Employee Voice] --> STT[Web Speech Recognition]
        STT --> Avatar3D[3D Sign Avatar Visualizer]
    end

    subgraph AI Sign Academy
        UserMotion[User Camera Motion] --> Assessor[Gesture Precision Evaluator]
        Assessor --> ScoreFeedback[Instant Score & Accuracy Gauge]
    end

    Mobile Engine <--> WS
    Enterprise Web Portal <--> REST
```

---

## 3. Tech Stack Matrix ($0 Budget)

| Layer | Component | Free Tech Stack | Purpose |
|---|---|---|---|
| **Mobile App** | Flutter 3.x | MediaPipe Holistic, TFLite, Provider | Cross-platform offline translation & SOS |
| **Web Portal** | React.js / Vite | WebSockets, Lucide Icons | Institutional counter translation dashboard |
| **AI Vision** | MediaPipe Holistic | Python & JS MediaPipe | 3D Hand + Facial Expression + Pose Tracking |
| **LLM Engine** | HuggingFace Inference API | `Qwen/Qwen2.5-7B-Instruct` (Free Tier) | Converts keywords to fluent Arabic sentences |
| **Backend API** | FastAPI + WebSockets | Python 3.10+ | High-concurrency real-time WebSocket broker |
| **Database** | Supabase (Free Tier) | PostgreSQL + Row Level Security | User profiles, audit logs, and dictionary DB |
| **Cloud Host** | Render / HuggingFace Spaces | Free Tier Hosting | $0 backend microservice hosting |
