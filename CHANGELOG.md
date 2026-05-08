# Changelog

All notable changes to the Artha AI project will be documented in this file.

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
