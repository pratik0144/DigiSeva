# Artha AI

Artha AI is a multilingual, voice-first financial accessibility platform designed for rural and low-digital-literacy users in India. The system allows users to interact naturally in their native languages to perform tasks like checking bank balances, tracking transactions, discovering government schemes, and receiving fraud/scam protection.

Instead of a basic chatbot, Artha AI operates as an intelligent **AI Operating System**, coordinating multiple specialized AI agents to execute real financial workflows securely.

---

## 🏗️ Architecture

The project is structured into a backend API and an upcoming frontend client.

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
│   │   ├── test_bank.py       # Simulator unit tests
│   │   └── index.html         # Simulator dashboard UI
│   └── core/                  # Intelligence & IO Foundations
│       ├── language_layer.py  # Script detection & fraud guardrails
│       ├── llm_router.py      # Keyword + LLM intent classification & routing
│       └── voice_layer.py     # Whisper STT & gTTS TTS engines
└── frontend/                  # (Upcoming) Mobile-first client application
```

## 🚀 Features

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
- `ffmpeg` (required for Whisper STT)
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt # (Ensure flask, flask-cors, python-dotenv, openai-whisper, gtts, google-generativeai, requests are installed)
```

### 2. Configure Environment
Create a `.env` file in the `backend/` directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Start the Mock Bank Server
The mock bank simulates the core banking system (CBS).
```bash
cd backend/banking
python bank_api.py
# Runs on http://localhost:5001
```

### 4. Start the Artha AI API
```bash
cd backend
export PYTHONPATH=$(pwd):$PYTHONPATH
python main.py
# Runs on http://localhost:5000
```

## 📡 API Endpoints (Artha AI - Port 5000)

- `POST /onboard`: Initialize a user session, fetch their bank profile and eligible schemes.
- `POST /chat`: Send a message to the orchestrator. Routes to the appropriate specialist agent.
- `POST /stt`: Upload a multipart audio file to transcribe to text (Whisper).
- `POST /tts`: Generate localized speech audio from text (gTTS).
- `POST /reset`: Clear conversation history.
- `GET /health`: System health and configuration check.
