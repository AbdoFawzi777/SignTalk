# SignTalk Enterprise Platform - 10-Member Team Allocation & Work Breakdown Structure (WBS)

To maximize development velocity and prevent code overlap, the 10-developer team is divided into 3 specialized sub-teams with distinct responsibilities and API contracts.

---

## 👥 Sub-Team Allocations & Roles

### 1. 🤖 AI & Computer Vision Sub-Team (3 Developers)

| Developer ID | Role Title | Core Responsibilities & Deliverables |
|---|---|---|
| **AI-1 (Team Lead)** | Senior CV Engineer | MediaPipe Holistic 3D tracking pipeline (Hands + Face + Pose), 3D feature matrix normalizer $(30 \times 126+)$, and coordinate augmentation. |
| **AI-2** | Deep Learning Specialist | TFLite Model Architecture (BiLSTM / Lite Transformer), FP16/INT8 quantization, facial emotion classifier integration. |
| **AI-3** | NLP & AI Academy Engineer | HuggingFace Arabic LLM Contextual Grammar Corrector integration, AI Sign Academy gesture scoring evaluator script. |

---

### 2. 💻 Frontend & UI/UX Sub-Team (4 Developers)

| Developer ID | Role Title | Core Responsibilities & Deliverables |
|---|---|---|
| **FE-1 (Team Lead)** | Lead Mobile Architect | Flutter Mobile Engine architecture, camera stream controller, state management, and eye-friendly dark theme system. |
| **FE-2** | Mobile Feature Developer | Implementation of Mobile screens: Live Translation Camera View, Smart SOS GPS Dispatcher, AI Academy screen. |
| **FE-3** | Web Portal Developer | Institutional Enterprise Web Portal (React.js), real-time WebSockets UI counter display, employee control panel. |
| **FE-4** | 3D Graphics & Avatar Specialist | 3D Sign Avatar Visualizer component (Three.js / Web animation player) for Speech-to-Sign rendering. |

---

### 3. ⚙️ Backend, Cloud & QA Sub-Team (3 Developers)

| Developer ID | Role Title | Core Responsibilities & Deliverables |
|---|---|---|
| **BE-1 (Team Lead)** | Lead Backend Architect | FastAPI Microservices setup, high-concurrency WebSocket broadcast server (`/ws/translation`), API routing. |
| **BE-2** | Database & Cloud Engineer | Supabase (Free Tier PostgreSQL) schema design, authentication, and Render / HuggingFace Spaces cloud deployment pipelines. |
| **QA-1** | Test Automation & DevOps | End-to-end integration testing, WebSocket stress testing, latency profiling (< 15ms target), and CI/CD scripts. |

---

## 🔌 Inter-Team API Contracts

1. **AI <-> Mobile Engine:** TFLite model output tensor format `[1, num_classes]` with probability thresholding at `0.70`.
2. **Mobile/Web <-> Backend:** WebSocket JSON Payload format:
   ```json
   {
     "client_type": "web_portal",
     "session_id": "hosp_counter_01",
     "keypoint_vector": [0.12, 0.45, ...],
     "timestamp": 1724089200
   }
   ```
3. **Backend <-> Supabase DB:** PostgreSQL Async Engine via SQLAlchemy / Supabase Python SDK.
