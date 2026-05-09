# Changelog

All notable changes to the Artha AI project will be documented in this file.

## [1.3.0] - 2026-05-09

### Added
- **Material Design 3 Dark Mode:** Completely overhauled the platform's visual aesthetic by migrating all hardcoded color values to a dynamic CSS variable system (`index.css`). Implemented a premium, high-contrast Material 3 dark theme featuring deep slate backgrounds and vibrant lilac accents, with toggle buttons integrated natively into the mobile header and desktop sidebar.
- **Persistent Theme Preferences:** Updated the `SessionContext.jsx` to store and persist the user's `isDarkMode` preference via `localStorage`, ensuring a seamless experience across sessions.
- **Dedicated Fraud Detection Dashboard:** Developed a new, standalone frontend module (`FraudDetection.jsx`) to centralize account security.
- **Fraud Alerts History:** Upgraded the system's state management to track a comprehensive chronological `fraudHistory` array, allowing users to review all scam attempts intercepted by the AI during their session.
- **Risk Profiling & Community Reporting:** The new dashboard visualizes the user's specific fraud risk profile and provides an interactive form to report suspicious phone numbers or messages directly.

## [1.2.0] - 2026-05-09

### Added
- **Offline Scheme Recommender Engine:** Implemented a robust rule-based recommendation system (`schemes_scraper_and_recommender.py`) that matches users to optimal government schemes based on their profile attributes (occupation, income, etc.) without relying on external APIs.
- **Comprehensive Schemes Database:** Integrated a local offline database (`schemes_database.json`) containing detailed information on over 50 government schemes, ensuring the AI can provide immediate, offline assistance.
- **Enhanced SchemesAgent:** Upgraded the AI voice assistant's `SchemesAgent` to seamlessly query the new local database, allowing it to autonomously fetch scheme details and provide personalized recommendations during conversation.
- **Full-Stack Schemes Integration:** Connected the React frontend (`Schemes.jsx`) to new dedicated backend API routes (`/schemes/all`, `/schemes/recommend`), enabling users to browse, filter, and view detailed scheme information natively within the UI.
- **Interactive Financial Literacy Module:** Overhauled the `Education.jsx` page with a rich, categorized curriculum covering Security, Savings, and Government Schemes.
- **Native Text-to-Speech (TTS) Engine:** Built a powerful client-side reading feature directly into the Financial Literacy module. It utilizes the Web Speech API to read lessons aloud in English, Hindi, and Kannada. Features include seamless audio chunking (bypassing browser limits), intelligent currency pronunciation, and an animated progress tracker.

## [1.1.0] - 2026-05-08

### Added
- **React Frontend Implementation:** Developed a robust, mobile-first client application using Vite and React.
- **Stitch Design System Integration:** Strictly implemented the "Digital Soil" aesthetic using vanilla CSS (`index.css`), bringing Terracotta accents and proper typography (Playfair Display / Source Sans 3) to the UI.
- **Comprehensive Page Architecture:**
  - `Home`: Adaptive dashboard featuring a quick chat interface, insights, and quick actions.
  - `VoiceInteraction`: A dedicated, fullscreen recording interface utilizing the `MediaRecorder` API for real-time STT and TTS streaming.
  - `Transactions`: Organized ledger for checking account balance history.
  - `Schemes`: Dynamic tracker for enrolled and recommended government schemes.
  - `Education`: Financial literacy module featuring tabbed lessons aligned with the backend `LiteracySpecialistAgent`.
- **Global Context Management:** Added `SessionContext.jsx` to centrally manage the active user profile (`JD-0001`), conversation history, scheme eligibility, and fraud alert state.
- **Centralized API Client:** Created `api.js` to handle all Axios requests to the Flask backend, including multipart form data parsing for Whisper audio uploads and blob parsing for Google TTS responses.
- **Responsive Navigation:** Implemented dynamic layout components: `Sidebar` for desktop and `BottomNav` for mobile displays.
- **Fraud Alert UI:** Designed an `AlertBanner` component that triggers universally upon the backend returning a `fraud_triggered` flag.

## [1.0.0] - 2026-05-08

### Added
- **Backend Architecture & Folder Structure:** Completely reorganized the project into `backend/` and `frontend/` directories. Separated backend into `agents`, `banking`, and `core` modules for scalability.
- **Orchestrator Agent (`orchestrator_agent.py`):** Central brain for managing user profiles, conversation history, and routing user queries to specialist agents.
- **Specialist Agents (`specialist_agents.py`):**
  - `BankingAgent`: Integrates with the mock bank API to check balances and fetch transactions.
  - `SchemesAgent`: Helps users discover and enroll in government schemes.
  - `FraudGuardAgent`: Specialized local agent to warn users of scams.
  - `LiteracyAgent`: Educational agent for explaining financial terms.
- **LLM Router (`llm_router.py`):** A unified router supporting keyword-based intent classification (offline fallback) and Gemini (API-based) LLM generation.
- **Voice Layer (`voice_layer.py`):** Added `WhisperSTT` (OpenAI Whisper turbo) for high-accuracy localized speech-to-text and `ArthaTTS` (gTTS) for text-to-speech with automatic Hindi fallbacks.
- **Language Intelligence (`language_layer.py`):** Robust unicode script detection prioritizing Hindi and Kannada. Added fraud keyword dictionaries to intercept scam attempts pre-LLM.
- **Flask API (`main.py`):** Core API server on port 5000 exposing `/onboard`, `/chat`, `/stt`, `/tts`, `/reset`, and `/health`. Added comprehensive request logging.
- **Mock Banking Simulation (`banking/mock_bank.py` & `bank_api.py`):** Integrated a localized in-memory banking simulation running on port 5001. Features realistic user profiles, transaction histories, fund transfers, and bill payments.

### Fixed
- **API Rate Limiting & Fallbacks:** Designed the architecture to gracefully handle LLM rate limits. The fraud-screening engine and intent classifier now prioritize offline keyword heuristics before calling external LLM APIs to preserve quota.
- **Module Imports:** Fixed absolute paths across the backend following the folder restructuring. Ensure `PYTHONPATH` includes the backend directory during execution.
