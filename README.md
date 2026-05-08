# Artha AI

Artha AI is a multilingual, voice-first financial accessibility platform designed for rural and low-digital-literacy users in India. The system allows users to interact naturally in their native languages to perform tasks like checking bank balances, tracking transactions, discovering government schemes, and receiving fraud/scam protection.

Instead of a basic chatbot, Artha AI operates as an intelligent **AI Operating System**, coordinating multiple specialized AI agents to execute real financial workflows securely, paired with a beautiful, mobile-first responsive frontend built on the Stitch Design System.

---

## 🏗️ Architecture

The project is structured into a Python backend API and a React frontend client.

```text
Digi Seva/
├── backend/
│   ├── main.py                # Flask API Entry Point (Port 5000)
│   ├── agents/                # AI Agent Layer
│   │   ├── orchestrator_agent.py # Intent routing & context management
│   │   └── specialist_agents.py  # Domain agents (Banking, Schemes, Fraud, Literacy)
│   ├── banking/               # Mock Banking Simulator (Port 5001)
│   │   ├── bank_api.py        # Bank API endpoints
│   │   ├── mock_bank.py       # In-memory account & scheme DB
│   │   └── test_bank.py       # Simulator unit tests
│   └── core/                  # Intelligence & IO Foundations
│       ├── language_layer.py  # Script detection & fraud guardrails
│       ├── llm_router.py      # Keyword + LLM intent classification & routing
│       └── voice_layer.py     # Whisper STT & gTTS TTS engines
└── frontend/                  # React Vite Client Application
    ├── src/
    │   ├── api.js             # Centralized Axios API client communicating with backend
    │   ├── context/           # React Context (Session tracking, Profile, Chat History)
    │   ├── components/        # Reusable UI components (Buttons, Cards, Alert Banners)
    │   ├── pages/             # App Pages (Home, VoiceInteraction, Transactions, Schemes, Education)
    │   ├── index.css          # Core "Digital Soil" Design System CSS tokens
    │   └── App.jsx            # Application Router (react-router-dom)
    └── package.json           # Frontend dependencies
```

## 🚀 Features

### Frontend (Client Interface)
- **Stitch Design System:** Implements the "Digital Soil" aesthetic featuring terracotta actions, warm surface cards, and Playfair Display typography.
- **Responsive Mobile-First UI:** Adaptive layout with a bottom navigation bar on mobile and a persistent sidebar on desktop.
- **Voice Overlay Integration:** Direct access to a fullscreen voice interaction interface utilizing the `MediaRecorder` API to capture and stream speech natively.
- **Dedicated Application Modules:** 
  - *Home*: Dashboard with fallback text chat and dynamic insight snippets.
  - *Transactions*: Ledger of past debits/credits.
  - *Schemes*: Tracker for enrolled government benefits.
  - *Education*: Financial literacy module for learning safe digital banking.
- **Fraud Prevention Alerts:** High-visibility UI alerts triggered natively by backend security checks to halt scams immediately.

### Backend (Agentic Infrastructure)
- **Voice-First Interaction:** Built-in Speech-to-Text (OpenAI Whisper turbo) and Text-to-Speech (Google TTS) optimized for Indic languages.
- **Multilingual Intelligence:** Deep support for Hindi and Kannada, with script-based language detection.
- **Agentic Orchestration:** 
  - **Orchestrator Agent:** Intercepts messages, detects language, checks for fraud, and classifies user intent.
  - **Banking Agent:** Handles balances, transfers, and bill payments using financial context.
  - **Schemes Agent:** Recommends and enrolls users in government schemes (e.g., PM-KISAN, MGNREGA).
  - **FraudGuard Agent:** A deterministic, zero-latency safety layer that intercepts scams (e.g., OTP phishing).
  - **Literacy Agent:** Explains financial concepts simply in the user's native tongue.
- **Robust LLM Routing:** Uses local keyword-matching for ultra-fast intent classification, with a fallback to Google Gemini 2.0 Flash for complex queries.

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js (v16+) & npm
- `ffmpeg` (required for Whisper STT)
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt # (Ensure flask, flask-cors, python-dotenv, openai-whisper, gtts, google-generativeai, requests are installed)

# Configure Environment
echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env
```

### 2. Frontend Setup
```bash
cd frontend
npm install
```

## 🏃‍♂️ Running the Platform locally

To experience the full platform, you need to run three separate servers. Open three terminal tabs:

**Terminal 1: Mock Bank Server** (Simulates Core Banking System)
```bash
cd backend/banking
python bank_api.py
# Runs on http://localhost:5001
```

**Terminal 2: Artha AI Backend API** (The Agentic Brain)
```bash
cd backend
export PYTHONPATH=$(pwd):$PYTHONPATH
python main.py
# Runs on http://localhost:5000
```

**Terminal 3: React Frontend** (The Client App)
```bash
cd frontend
npm run dev
# Runs on http://localhost:5173
```

## 📡 API Endpoints (Artha AI - Port 5000)

- `POST /onboard`: Initialize a user session, fetch their bank profile and eligible schemes.
- `POST /chat`: Send a message to the orchestrator. Routes to the appropriate specialist agent.
- `POST /stt`: Upload a multipart audio file to transcribe to text (Whisper).
- `POST /tts`: Generate localized speech audio from text (gTTS).
- `POST /reset`: Clear conversation history.
- `GET /health`: System health and configuration check.
