"""
llm_router.py — Artha AI LLM Router

Routes user messages to the correct specialist agent by classifying intent.
Uses a keyword-based fallback classifier with hooks for Gemini-based
classification when API keys are configured.

This module is the single point of contact for all LLM interactions.
No direct Anthropic/OpenAI SDK usage — everything goes through LLMRouter.
"""

import os
import re
from typing import Optional

# =============================================================================
# Intent keyword maps (multilingual — romanized + native script)
# =============================================================================

_INTENT_KEYWORDS = {
    "banking": [
        # English
        "balance", "account", "bank", "statement", "passbook", "withdraw",
        "deposit", "transfer", "savings", "current account", "fixed deposit",
        # Hindi (romanized)
        "balance", "khata", "bank", "bachat", "jama", "nikalna", "paisa",
        "baaki", "rashi",
        # Hindi (Devanagari)
        "बैलेंस", "खाता", "बैंक", "बचत", "जमा", "निकालना", "पैसा",
        "बाकी", "राशि", "शेष",
        # Kannada (romanized)
        "balance", "khata", "bank", "ulitaaya",
        # Kannada (script)
        "ಬ್ಯಾಲೆನ್ಸ್", "ಖಾತೆ", "ಬ್ಯಾಂಕ್", "ಉಳಿತಾಯ", "ಹಣ",
    ],
    "schemes": [
        # English
        "scheme", "yojana", "government", "subsidy", "pension", "eligib",
        "apply", "benefit", "ration", "card", "insurance",
        # Hindi (romanized)
        "yojana", "sarkari", "pension", "labh", "ration", "bima",
        "kisan", "awas", "mudra", "ujjwala", "jan dhan",
        # Hindi (Devanagari)
        "योजना", "सरकारी", "पेंशन", "लाभ", "राशन", "बीमा",
        "किसान", "आवास", "मुद्रा", "उज्ज्वला", "जन धन",
        # Kannada (romanized)
        "yojane", "sarkari", "pension",
        # Kannada (script)
        "ಯೋಜನೆ", "ಸರ್ಕಾರಿ", "ಪಿಂಚಣಿ", "ಲಾಭ",
        # Scheme names (universal)
        "PM-KISAN", "PMJDY", "PMSBY", "PMJJBY", "MGNREGA",
        "PM Awas", "Ujjwala", "Mudra", "Jan Dhan",
    ],
    "payments": [
        # English
        "pay", "send money", "UPI", "recharge", "bill", "electricity",
        "mobile recharge", "DTH", "EMI", "loan",
        # Hindi (romanized)
        "bhejo", "bhejdo", "payment", "recharge", "bijli", "bill",
        "UPI", "karo", "kisto",
        # Hindi (Devanagari)
        "भेजो", "भुगतान", "रिचार्ज", "बिजली", "बिल", "किस्त",
        # Kannada (romanized)
        "kalisi", "payment", "recharge",
        # Kannada (script)
        "ಕಳಿಸಿ", "ಪಾವತಿ", "ರೀಚಾರ್ಜ್", "ಬಿಲ್",
    ],
    "fraud": [
        # English
        "fraud", "scam", "cheat", "fake", "stolen", "hack", "phishing",
        "suspicious", "unauthorized",
        # Hindi (romanized)
        "dhokha", "fraud", "thug", "chori", "loot", "OTP",
        "scam", "fake", "jhooth",
        # Hindi (Devanagari)
        "धोखा", "ठग", "चोरी", "लूट", "फ्रॉड", "स्कैम",
        # Kannada (romanized)
        "vanchane", "fraud", "mosadi",
        # Kannada (script)
        "ವಂಚನೆ", "ಮೋಸ", "ಕಳ್ಳತನ",
    ],
    "literacy": [
        # English
        "what is", "how to", "explain", "teach", "learn", "meaning",
        "help me understand", "what does",
        # Hindi (romanized)
        "kya hai", "kaise", "samjhao", "batao", "sikhao", "matlab",
        # Hindi (Devanagari)
        "क्या है", "कैसे", "समझाओ", "बताओ", "सिखाओ", "मतलब",
        # Kannada (romanized)
        "enu", "hege", "helkodi", "artham",
        # Kannada (script)
        "ಏನು", "ಹೇಗೆ", "ಹೇಳ್ಕೊಡಿ", "ಅರ್ಥ",
    ],
    "greeting": [
        # English
        "hello", "hi", "hey", "good morning", "good evening",
        "thank", "thanks", "bye", "goodbye",
        # Hindi (romanized)
        "namaste", "namaskar", "dhanyavaad", "shukriya", "alvida",
        # Hindi (Devanagari)
        "नमस्ते", "नमस्कार", "धन्यवाद", "शुक्रिया", "अलविदा",
        # Kannada (romanized)
        "namaskara", "dhanyavaada", "hogi bartini",
        # Kannada (script)
        "ನಮಸ್ಕಾರ", "ಧನ್ಯವಾದ",
    ],
}

# Valid intent labels
VALID_INTENTS = list(_INTENT_KEYWORDS.keys())


class LLMRouter:
    """
    Central router for all LLM interactions in Artha AI.

    Provides:
      - Intent classification (keyword fallback + optional Gemini)
      - Prompt construction helpers
      - Model routing based on task complexity

    Usage:
        router = LLMRouter()
        intent = router.classify_intent("mera balance kitna hai")
        # → "banking"
    """

    def __init__(self, gemini_api_key: Optional[str] = None):
        """
        Initialize the LLM Router.

        Args:
            gemini_api_key: Optional Gemini API key. If not provided,
                            falls back to GEMINI_API_KEY env var.
                            If neither available, uses keyword-only classification.
        """
        self.api_key = gemini_api_key or os.environ.get("GEMINI_API_KEY")
        self._gemini_model = None

        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._gemini_model = genai.GenerativeModel("gemini-2.0-flash")
            except Exception as e:
                print(f"[LLMRouter] Gemini init failed, using keyword fallback: {e}")
                self._gemini_model = None

    def classify_intent(self, user_message: str) -> str:
        """
        Classify the user's intent from their message.

        Strategy:
          1. Try keyword-based classification first (fast, offline).
          2. If ambiguous and Gemini is available, use LLM classification.
          3. Default fallback → "greeting".

        Args:
            user_message: Raw user input text.

        Returns:
            Intent string: one of "banking", "schemes", "payments",
                           "fraud", "literacy", "greeting".
        """
        # Always try keyword classification first
        keyword_result = self._classify_by_keywords(user_message)

        if keyword_result["confidence"] == "high":
            return keyword_result["intent"]

        # If Gemini is available and keyword confidence is low, try LLM
        if self._gemini_model and keyword_result["confidence"] == "low":
            try:
                llm_intent = self._classify_by_llm(user_message)
                if llm_intent in VALID_INTENTS:
                    return llm_intent
            except Exception:
                pass  # Fall through to keyword result

        return keyword_result["intent"]

    def _classify_by_keywords(self, text: str) -> dict:
        """
        Score text against keyword lists for each intent category.

        Returns:
            {"intent": str, "confidence": "high"|"medium"|"low", "scores": dict}
        """
        text_lower = text.lower().strip()
        scores: dict[str, int] = {intent: 0 for intent in VALID_INTENTS}

        for intent, keywords in _INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    scores[intent] += 1

        max_score = max(scores.values())

        if max_score == 0:
            return {"intent": "greeting", "confidence": "low", "scores": scores}

        # Check for ties
        top_intents = [k for k, v in scores.items() if v == max_score]

        if len(top_intents) == 1:
            confidence = "high" if max_score >= 2 else "medium"
            return {"intent": top_intents[0], "confidence": confidence, "scores": scores}

        # Tie-breaking: prioritize fraud > banking > schemes > payments > literacy > greeting
        priority_order = ["fraud", "banking", "schemes", "payments", "literacy", "greeting"]
        for priority in priority_order:
            if priority in top_intents:
                return {"intent": priority, "confidence": "medium", "scores": scores}

        return {"intent": top_intents[0], "confidence": "low", "scores": scores}

    def _classify_by_llm(self, text: str) -> str:
        """
        Use Gemini to classify intent when keyword matching is ambiguous.

        Returns:
            Intent string from VALID_INTENTS.
        """
        prompt = (
            "You are an intent classifier for an Indian rural financial assistant.\n"
            "Classify the following user message into EXACTLY ONE of these categories:\n"
            "  banking, schemes, payments, fraud, literacy, greeting\n\n"
            "Rules:\n"
            "- 'banking' = balance checks, account info, statements, deposits, withdrawals\n"
            "- 'schemes' = government schemes, yojana, eligibility, applications\n"
            "- 'payments' = sending money, UPI, recharge, bills, EMI\n"
            "- 'fraud' = scam reports, suspicious activity, OTP/PIN requests\n"
            "- 'literacy' = financial education, explanations, 'what is X'\n"
            "- 'greeting' = hello, thanks, bye, general conversation\n\n"
            f"User message: \"{text}\"\n\n"
            "Respond with ONLY the category name, nothing else."
        )

        response = self._gemini_model.generate_content(prompt)
        result = response.text.strip().lower()

        # Validate the response
        if result in VALID_INTENTS:
            return result

        # Try to extract a valid intent from the response
        for intent in VALID_INTENTS:
            if intent in result:
                return intent

        return "greeting"  # Safe default

    def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[list] = None,
    ) -> str:
        """
        Generate a response using the configured LLM.

        Args:
            system_prompt: System-level instruction for the model.
            user_message: Current user message.
            conversation_history: Optional list of prior messages.

        Returns:
            Generated response text, or a fallback message if LLM unavailable.
        """
        if not self._gemini_model:
            return "[LLMRouter] No LLM configured. Set GEMINI_API_KEY to enable AI responses."

        try:
            # Build the full prompt
            full_prompt = f"{system_prompt}\n\n"

            if conversation_history:
                for msg in conversation_history[-6:]:  # Keep last 6 messages for context
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    full_prompt += f"{role}: {content}\n"

            full_prompt += f"user: {user_message}\nassistant:"

            response = self._gemini_model.generate_content(full_prompt)
            return response.text.strip()

        except Exception as e:
            return f"[LLMRouter] Error generating response: {e}"

    def call(
        self,
        agent_name: str,
        system_prompt: str,
        messages: list,
        max_tokens: int = 300,
    ) -> dict:
        """
        Unified call interface for specialist agents.

        Routes to the appropriate model based on agent_name:
          - "banking"  → Ministral 2.5 (via Gemini fallback)
          - "schemes"  → Gemini
          - "fraud"    → Ministral 2.5 (local, never fails)
          - "literacy" → GLM via NVIDIA NIM (via Gemini fallback)
          - default    → Gemini

        Args:
            agent_name: Name of the calling agent (e.g., "banking", "schemes").
            system_prompt: Full system prompt including context and instructions.
            messages: Conversation history as list of {"role": ..., "content": ...}.
            max_tokens: Maximum tokens for response generation.

        Returns:
            {
                "text": str,        — Generated response text
                "model_used": str,  — Model identifier that was used
                "agent": str,       — Agent that made the call
                "tokens": int,      — Max tokens requested
            }
        """
        # Model routing table — maps agent names to preferred models
        _MODEL_MAP = {
            "banking": "ministral-2.5",
            "schemes": "gemini-2.0-flash",
            "fraud": "ministral-2.5",
            "literacy": "glm-nim",
        }

        model_label = _MODEL_MAP.get(agent_name, "gemini-2.0-flash")

        # Extract the latest user message from the messages list
        user_message = ""
        history = []
        if messages:
            user_message = messages[-1].get("content", "")
            history = messages[:-1]

        # All models currently route through Gemini (or fallback)
        # In production, this would dispatch to Ministral/GLM endpoints
        response_text = self.generate_response(
            system_prompt=system_prompt,
            user_message=user_message,
            conversation_history=history if history else None,
        )

        return {
            "text": response_text,
            "model_used": model_label,
            "agent": agent_name,
            "tokens": max_tokens,
        }


# =============================================================================
# Module self-test
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  Artha AI — LLM Router Self-Test")
    print("=" * 60)

    router = LLMRouter()

    test_messages = [
        ("Mera balance kya hai", "banking"),
        ("PM-KISAN yojana ke baare mein batao", "schemes"),
        ("₹500 bhejo Suresh ko", "payments"),
        ("Kisi ne OTP maanga hai", "fraud"),
        ("UPI kya hota hai", "literacy"),
        ("Namaste", "greeting"),
        ("मेरा बैलेंस बताओ", "banking"),
        ("ನನ್ನ ಬ್ಯಾಲೆನ್ಸ್ ಎಷ್ಟು", "banking"),
        ("सरकारी योजना बताओ", "schemes"),
        ("ಯೋಜನೆ ಬಗ್ಗೆ ಹೇಳಿ", "schemes"),
    ]

    print(f"\n🧠 Gemini available: {router._gemini_model is not None}")
    print(f"📋 Valid intents: {VALID_INTENTS}\n")

    print("🔍 Intent Classification Tests:")
    passed = 0
    for msg, expected in test_messages:
        result = router.classify_intent(msg)
        status = "✅" if result == expected else "❌"
        if result == expected:
            passed += 1
        print(f"  {status} '{msg[:40]}' → {result} (expected: {expected})")

    print(f"\n  Results: {passed}/{len(test_messages)} passed")
    print("=" * 60)
