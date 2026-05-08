"""
specialist_agents.py — Artha AI Specialist Agent Suite

Contains 4 specialist agents + AgentDispatcher, each handling a specific
domain of financial assistance for rural India users.

Agents:
  1. BankingAgent     — Balance, transactions, transfers, bill pay (Ministral 2.5)
  2. SchemesAgent     — Government scheme discovery & enrollment (Gemini)
  3. FraudGuardAgent  — Scam detection & user protection (Ministral 2.5)
  4. LiteracyAgent    — Financial literacy education (GLM via NVIDIA NIM)

All LLM calls go through LLMRouter.call() — NO direct SDK usage.
Banking API calls go to bank_api.py at localhost:5001.
"""

import json
import requests
from typing import Optional

from core import language_layer
from core.llm_router import LLMRouter


# =============================================================================
# AGENT 1 — BankingAgent
# =============================================================================

class BankingAgent:
    """
    Handles banking operations: balance checks, transaction history,
    money transfers, and bill payments.

    Routes through Ministral 2.5 via LLMRouter.
    Banking data fetched from bank_api.py (localhost:5001).
    """

    def __init__(self, orchestrator_context: dict):
        """
        Args:
            orchestrator_context: User context dict from orchestrator.build_context_block().
        """
        self.router = LLMRouter()
        self.context = orchestrator_context
        self.agent_name = "banking"
        self.base_url = "http://localhost:5001"

    # ---- Bank API Calls ----

    def _get_balance(self, account_id: str) -> str:
        """GET /account/{account_id}/balance — Fetch current balance."""
        try:
            resp = requests.get(
                f"{self.base_url}/account/{account_id}/balance",
                timeout=5,
            )
            resp.raise_for_status()
            return json.dumps(resp.json(), ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "error": "Balance unavailable",
                "detail": str(e),
            })

    def _get_transactions(self, account_id: str, last_n: int = 5) -> str:
        """GET /account/{account_id}/transactions?last_n={n} — Recent transactions."""
        try:
            resp = requests.get(
                f"{self.base_url}/account/{account_id}/transactions",
                params={"last_n": last_n},
                timeout=5,
            )
            resp.raise_for_status()
            return json.dumps(resp.json(), ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "error": "Transactions unavailable",
                "detail": str(e),
            })

    def _transfer(self, from_id: str, to_id: str, amount: float) -> str:
        """POST /transfer — Transfer money between accounts."""
        try:
            resp = requests.post(
                f"{self.base_url}/transfer",
                json={"from_id": from_id, "to_id": to_id, "amount": amount},
                timeout=5,
            )
            resp.raise_for_status()
            return json.dumps(resp.json(), ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "error": "Transfer failed",
                "detail": str(e),
            })

    def _pay_bill(self, account_id: str, bill_type: str, amount: float) -> str:
        """POST /bill/pay — Pay a utility bill."""
        try:
            resp = requests.post(
                f"{self.base_url}/bill/pay",
                json={
                    "account_id": account_id,
                    "bill_type": bill_type,
                    "amount": amount,
                },
                timeout=5,
            )
            resp.raise_for_status()
            return json.dumps(resp.json(), ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "error": "Bill payment failed",
                "detail": str(e),
            })

    # ---- Action Detection ----

    def _detect_banking_action(self, text: str) -> str:
        """Detect which banking action the user wants from their message."""
        text_lower = text.lower()

        balance_keywords = [
            "balance", "bakiye", "kitna paisa", "shesh", "baaki",
            "बैलेंस", "बाकी", "शेष", "पैसा कितना",
            "ಬ್ಯಾಲೆನ್ಸ್", "ಎಷ್ಟು ಹಣ",
        ]
        transaction_keywords = [
            "transaction", "history", "statement", "passbook", "lenden",
            "len den", "विवरण", "लेनदेन", "स्टेटमेंट",
            "ವಹಿವಾಟು", "ಹಿಸ್ಟರಿ",
        ]
        transfer_keywords = [
            "transfer", "bhejo", "send", "bhejdo", "paisa do",
            "भेजो", "ट्रांसफर",
            "ಕಳಿಸಿ", "ಟ್ರಾನ್ಸ್ಫರ್",
        ]
        bill_keywords = [
            "bill", "recharge", "bijli", "electricity", "mobile",
            "DTH", "gas", "pani", "water",
            "बिल", "बिजली", "रिचार्ज",
            "ಬಿಲ್", "ರೀಚಾರ್ಜ್",
        ]

        for kw in transfer_keywords:
            if kw in text_lower:
                return "transfer"
        for kw in bill_keywords:
            if kw in text_lower:
                return "bill"
        for kw in transaction_keywords:
            if kw in text_lower:
                return "transactions"
        for kw in balance_keywords:
            if kw in text_lower:
                return "balance"

        # Default for banking intent
        return "balance"

    # ---- Main Run ----

    def run(self, user_message: str, conversation_history: list) -> dict:
        """
        Process a banking request end-to-end.

        Steps:
          1. Detect banking sub-action (balance/transactions/transfer/bill)
          2. Call the relevant bank API
          3. Build system prompt with fetched data
          4. Generate natural language response via LLMRouter
        """
        account_id = self.context.get("account_id", "UNKNOWN")
        action = self._detect_banking_action(user_message)
        tool_called = action

        # Fetch data from bank API
        if action == "balance":
            tool_result = self._get_balance(account_id)
        elif action == "transactions":
            tool_result = self._get_transactions(account_id)
        elif action == "transfer":
            # For transfers, we'd parse recipient/amount from message
            # For now, provide what we have and let LLM ask for details
            tool_result = json.dumps({
                "status": "awaiting_details",
                "message": "Need recipient account and amount to proceed",
            })
        elif action == "bill":
            tool_result = json.dumps({
                "status": "awaiting_details",
                "message": "Need bill type and amount to proceed",
            })
        else:
            tool_result = self._get_balance(account_id)

        # Build language-aware system prompt
        lang = self.context.get("language", "hi")
        lang_instruction = language_layer.get_system_prompt_language_instruction(lang)

        system_prompt = f"""You are a banking assistant for rural India users.
{lang_instruction}

User context:
{json.dumps(self.context, ensure_ascii=False, indent=2)}

You have already fetched this data from the bank system:
BANK DATA: {tool_result}

Rules:
- Read numbers ONLY from BANK DATA above — never make up balances.
- Keep response under 3 sentences.
- Use simple words. No banking jargon.
- End with fraud reminder in user's language:
  Hindi: "Yaad rakhein: koi bhi aapka OTP ya PIN nahi maangta."
  Kannada: "Nenapirakoli: yaaru nimage OTP keḷabarudu."
"""

        # Generate response via LLMRouter
        messages = conversation_history + [{"role": "user", "content": user_message}]
        result = self.router.call(
            self.agent_name,
            system_prompt,
            messages,
            max_tokens=300,
        )

        return {
            "response": result["text"],
            "model_used": result["model_used"],
            "agent": self.agent_name,
            "tool_called": tool_called,
        }


# =============================================================================
# AGENT 2 — SchemesAgent
# =============================================================================

class SchemesAgent:
    """
    Handles government scheme discovery and enrollment.
    Routes through Gemini via LLMRouter.
    """

    def __init__(self, orchestrator_context: dict):
        self.router = LLMRouter()
        self.context = orchestrator_context
        self.agent_name = "schemes"
        self.base_url = "http://localhost:5001"

    # ---- Scheme API Calls ----

    def _get_eligible_schemes(self, account_id: str) -> str:
        """GET /account/{account_id}/eligible_schemes — Fetch eligible schemes."""
        try:
            resp = requests.get(
                f"{self.base_url}/account/{account_id}/eligible_schemes",
                timeout=5,
            )
            resp.raise_for_status()
            return json.dumps(resp.json(), ensure_ascii=False)
        except Exception as e:
            # Fallback: return schemes from user profile if API is down
            fallback_schemes = self.context.get("eligible_schemes", [])
            return json.dumps({
                "schemes": fallback_schemes,
                "source": "profile_fallback",
                "note": f"Live API unavailable: {e}",
            }, ensure_ascii=False)

    def _enroll_scheme(self, account_id: str, scheme_name: str) -> str:
        """POST /scheme/enroll — Enroll user in a government scheme."""
        try:
            resp = requests.post(
                f"{self.base_url}/scheme/enroll",
                json={"account_id": account_id, "scheme_name": scheme_name},
                timeout=5,
            )
            resp.raise_for_status()
            return json.dumps(resp.json(), ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "status": "enrollment_pending",
                "scheme": scheme_name,
                "detail": str(e),
            })

    # ---- Enrollment Detection ----

    def _wants_enrollment(self, text: str) -> bool:
        """Check if the user wants to enroll in a scheme."""
        enroll_keywords = [
            "enroll", "register", "apply", "chahiye", "karna hai",
            "sign up", "join", "lagao",
            "नामांकन", "रजिस्टर", "लगाओ", "चाहिए", "करना है",
            "ನೋಂದಣಿ", "ಅಪ್ಲೈ", "ಮಾಡಿ", "ಬೇಕು",
        ]
        text_lower = text.lower()
        return any(kw in text_lower for kw in enroll_keywords)

    # ---- Main Run ----

    def run(self, user_message: str, conversation_history: list) -> dict:
        """
        Process a government schemes query.

        Steps:
          1. Always fetch eligible schemes first
          2. Check if user wants to enroll
          3. Build prompt with scheme data
          4. Generate response via LLMRouter
        """
        account_id = self.context.get("account_id", "UNKNOWN")

        # Always fetch fresh scheme data
        schemes_data = self._get_eligible_schemes(account_id)

        # Check for enrollment intent
        enrollment_result = None
        if self._wants_enrollment(user_message):
            # Try to extract scheme name from message (simple heuristic)
            scheme_names = ["PM-KISAN", "PMJDY", "Ujjwala", "PMSBY",
                            "PMJJBY", "MGNREGA", "PM Awas", "Mudra", "Jan Dhan"]
            for scheme in scheme_names:
                if scheme.lower() in user_message.lower():
                    enrollment_result = self._enroll_scheme(account_id, scheme)
                    break

        # Build language-aware system prompt
        lang = self.context.get("language", "hi")
        lang_instruction = language_layer.get_system_prompt_language_instruction(lang)

        enrollment_block = ""
        if enrollment_result:
            enrollment_block = f"\nEnrollment result: {enrollment_result}\n"

        system_prompt = f"""You are a government schemes advisor for rural India.
{lang_instruction}

User context:
{json.dumps(self.context, ensure_ascii=False, indent=2)}

Eligible schemes from database: {schemes_data}
{enrollment_block}
Rules:
- Only mention schemes from the data above — never invent schemes.
- Explain each scheme in 1 simple sentence. Always mention exact benefit amount.
- Prioritize: PM-KISAN for farmers, PMJDY for unbanked, Ujjwala for women.
- If user wants to enroll, confirm and call enrollment.
- Keep response under 4 sentences.
"""

        # Generate response via LLMRouter
        messages = conversation_history + [{"role": "user", "content": user_message}]
        result = self.router.call(
            self.agent_name,
            system_prompt,
            messages,
            max_tokens=400,
        )

        return {
            "response": result["text"],
            "model_used": result["model_used"],
            "agent": self.agent_name,
        }


# =============================================================================
# AGENT 3 — FraudGuardAgent
# =============================================================================

class FraudGuardAgent:
    """
    Fraud detection and user protection specialist.
    Routes through Ministral 2.5 via LLMRouter — local, never fails.
    """

    def __init__(self, orchestrator_context: dict):
        self.router = LLMRouter()
        self.context = orchestrator_context
        self.agent_name = "fraud"
        self.base_url = "http://localhost:5001"

    # ---- Fraud API Call ----

    def _check_fraud_api(self, text: str) -> dict:
        """POST /fraud/check — Check text against bank's fraud detection."""
        try:
            resp = requests.post(
                f"{self.base_url}/fraud/check",
                json={"text": text},
                timeout=5,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception:
            # Fallback to local language_layer fraud check
            lang = self.context.get("language", "hi")
            local_check = language_layer.check_fraud_language(text, lang)
            return {
                "is_suspicious": local_check["is_fraud"],
                "matched_patterns": local_check["matched"],
                "warning": local_check["warning"],
                "source": "local_fallback",
            }

    # ---- Main Run ----

    def run(self, user_message: str, conversation_history: list) -> dict:
        """
        Process a fraud/scam query.

        Steps:
          1. Always run fraud check via bank API (with local fallback)
          2. Build prompt with fraud scan results
          3. Generate protective response via LLMRouter
        """
        # Always check for fraud first
        fraud_result = self._check_fraud_api(user_message)

        # Build language-aware system prompt
        lang = self.context.get("language", "hi")
        lang_instruction = language_layer.get_system_prompt_language_instruction(lang)

        system_prompt = f"""You are a fraud protection specialist for rural India users.
{lang_instruction}

User context:
{json.dumps(self.context, ensure_ascii=False, indent=2)}

Fraud scan result: {json.dumps(fraud_result, ensure_ascii=False)}

Rules:
- If fraud detected: clearly say SCAM/DHOKA in bold. Explain in 2 simple sentences
  what the scammer wants and why it's a scam.
- Tell user exactly what to do: hang up / block number / tell family.
- Real banks NEVER ask for OTP, PIN, or Aadhaar on phone. Ever.
- Tone: calm and reassuring, like a trusted elder in the family.
- If not fraud: reassure the user briefly in 1 sentence.
"""

        # Generate response via LLMRouter
        messages = conversation_history + [{"role": "user", "content": user_message}]
        result = self.router.call(
            self.agent_name,
            system_prompt,
            messages,
            max_tokens=300,
        )

        return {
            "response": result["text"],
            "model_used": result["model_used"],
            "agent": self.agent_name,
            "fraud_detected": fraud_result.get("is_suspicious", False),
        }


# =============================================================================
# AGENT 4 — LiteracyAgent
# =============================================================================

class LiteracyAgent:
    """
    Financial literacy teacher for first-time banking users.
    Routes through GLM via NVIDIA NIM (via LLMRouter).
    """

    def __init__(self, orchestrator_context: dict):
        self.router = LLMRouter()
        self.context = orchestrator_context
        self.agent_name = "literacy"

    # ---- Main Run ----

    def run(self, user_message: str, conversation_history: list) -> dict:
        """
        Process a financial literacy question.

        Steps:
          1. Build literacy-focused system prompt
          2. Generate educational response with rural analogies via LLMRouter
        """
        lang = self.context.get("language", "hi")
        lang_instruction = language_layer.get_system_prompt_language_instruction(lang)

        system_prompt = f"""You are a financial literacy teacher for first-time banking users in rural India.
{lang_instruction}

User context:
{json.dumps(self.context, ensure_ascii=False, indent=2)}

Rules:
- Teach one concept per response. Max 4 sentences.
- Use rural analogies:
    Interest = "Paisa uthane ka kiraya" (rent for using money)
    EMI = "Mahine ka hissa" (monthly share)
    Savings = "Kal ke liye aaj ka paisa" (today's money for tomorrow)
    Collateral = "Girvee" (pledge)
    Credit Score = "Bharosa ki rating" (trust rating)
    Insurance = "Suraksha kavach" (safety shield)
- Never use English jargon without explaining it immediately after.
- End with one simple action the user can take today.
"""

        # Generate response via LLMRouter
        messages = conversation_history + [{"role": "user", "content": user_message}]
        result = self.router.call(
            self.agent_name,
            system_prompt,
            messages,
            max_tokens=350,
        )

        return {
            "response": result["text"],
            "model_used": result["model_used"],
            "agent": self.agent_name,
        }


# =============================================================================
# AGENT DISPATCHER — Routes orchestrator results to the correct agent
# =============================================================================

class AgentDispatcher:
    """
    Dispatcher that routes orchestrator results to the correct specialist agent.

    Creates fresh agent instances per request to inject the latest context.
    """

    # Map route names to agent classes
    _AGENT_MAP = {
        "banking": BankingAgent,
        "payments": BankingAgent,  # Payments route to BankingAgent
        "schemes": SchemesAgent,
        "fraud": FraudGuardAgent,
        "literacy": LiteracyAgent,
    }

    def __init__(self):
        """No agents initialized here — create fresh per request."""
        pass

    def dispatch(
        self,
        route_result: dict,
        user_message: str,
        history: list,
        orchestrator_context: str,
    ) -> dict:
        """
        Route a classified message to the correct specialist agent.

        Args:
            route_result: Dict from orchestrator.run() with "route_to" key.
            user_message: Original user message.
            history: Conversation history list.
            orchestrator_context: Context string from orchestrator.build_context_block().

        Returns:
            Agent's full response dict, or a greeting/fallback response.
        """
        route_to = route_result.get("route_to", "greeting")

        # Handle greetings directly — no specialist agent needed
        if route_to == "greeting":
            lang = route_result.get("language", "hi")
            return {
                "response": language_layer.get_greeting(lang),
                "model_used": "none",
                "agent": "greeting",
            }

        # Build context dict from the orchestrator context string
        context = self._parse_context(orchestrator_context, route_result)

        # Get the correct agent class
        agent_class = self._AGENT_MAP.get(route_to)
        if not agent_class:
            return {
                "response": language_layer.get_greeting(
                    route_result.get("language", "hi")
                ),
                "model_used": "none",
                "agent": "fallback",
                "note": f"No agent for route: {route_to}",
            }

        # Instantiate and run the agent
        agent = agent_class(context)
        return agent.run(user_message, history)

    def _parse_context(self, context_string: str, route_result: dict) -> dict:
        """
        Parse the orchestrator context string into a dict for agent consumption.

        Falls back to extracting data from route_result if parsing fails.
        """
        context = {
            "language": route_result.get("language", "hi"),
        }

        # Try to parse structured data from the context string
        lines = context_string.strip().split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("User:"):
                parts = line.replace("User:", "").strip().split(",")
                if len(parts) >= 3:
                    context["name"] = parts[0].strip()
                    context["occupation"] = parts[1].strip()
                    context["location"] = parts[2].strip().rstrip(".")
            elif line.startswith("Language:"):
                parts = line.split(".")
                for part in parts:
                    part = part.strip()
                    if part.startswith("Language:"):
                        context["language"] = part.replace("Language:", "").strip()
                    elif part.startswith("Account:"):
                        context["account_id"] = part.replace("Account:", "").strip()
            elif line.startswith("Fraud risk:"):
                parts = line.split(".")
                for part in parts:
                    part = part.strip()
                    if part.startswith("Fraud risk:"):
                        context["fraud_risk"] = part.replace("Fraud risk:", "").strip()
                    elif part.startswith("Enrolled schemes:"):
                        schemes_str = part.replace("Enrolled schemes:", "").strip()
                        context["eligible_schemes"] = [
                            s.strip() for s in schemes_str.split(",") if s.strip() and s.strip() != "None"
                        ]
            elif line.startswith("Income:"):
                context["income_bracket"] = line.replace("Income:", "").strip().rstrip(".")

        return context


# =============================================================================
# Self-test
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  Artha AI — Specialist Agents Self-Test")
    print("=" * 60)

    ctx = {
        "language": "kn",
        "account_id": "JD-0002",
        "name": "Savitha",
        "occupation": "farmer",
        "location": "village",
        "fraud_risk": "low",
        "income_bracket": "low",
        "eligible_schemes": ["PM-KISAN", "Ujjwala"],
    }

    # --- Test SchemesAgent ---
    print("\n🏛️  Testing SchemesAgent...")
    print("─" * 40)
    agent = SchemesAgent(ctx)
    r = agent.run("Yaava scheme sigatte naage?", [])
    print(f"  Agent:    {r['agent']}")
    print(f"  Model:    {r['model_used']}")
    print(f"  Response: {r['response'][:120]}...")

    # --- Test FraudGuardAgent ---
    print("\n🛡️  Testing FraudGuardAgent...")
    print("─" * 40)
    agent = FraudGuardAgent(ctx)
    r = agent.run("Yaaru oo OTP keḷtaidaare, account close aagatte antaare", [])
    print(f"  Agent:          {r['agent']}")
    print(f"  Model:          {r['model_used']}")
    print(f"  Fraud detected: {r['fraud_detected']}")
    print(f"  Response:       {r['response'][:120]}...")

    # --- Test BankingAgent ---
    print("\n🏦 Testing BankingAgent...")
    print("─" * 40)
    ctx_hi = {**ctx, "language": "hi", "account_id": "JD-0001", "name": "Ramesh"}
    agent = BankingAgent(ctx_hi)
    r = agent.run("Mera balance kitna hai?", [])
    print(f"  Agent:       {r['agent']}")
    print(f"  Model:       {r['model_used']}")
    print(f"  Tool called: {r['tool_called']}")
    print(f"  Response:    {r['response'][:120]}...")

    # --- Test LiteracyAgent ---
    print("\n📚 Testing LiteracyAgent...")
    print("─" * 40)
    agent = LiteracyAgent(ctx_hi)
    r = agent.run("EMI kya hota hai?", [])
    print(f"  Agent:    {r['agent']}")
    print(f"  Model:    {r['model_used']}")
    print(f"  Response: {r['response'][:120]}...")

    # --- Test AgentDispatcher ---
    print("\n🔀 Testing AgentDispatcher...")
    print("─" * 40)
    dispatcher = AgentDispatcher()

    test_routes = [
        {"route_to": "greeting", "language": "kn"},
        {"route_to": "banking", "language": "hi"},
        {"route_to": "fraud", "language": "kn"},
    ]

    context_string = (
        "User: Savitha, farmer, village.\n"
        "Language: kn. Account: JD-0002.\n"
        "Fraud risk: low. Enrolled schemes: PM-KISAN, Ujjwala.\n"
        "Income: low."
    )

    for route in test_routes:
        r = dispatcher.dispatch(route, "test message", [], context_string)
        print(f"  Route: {route['route_to']:10s} → Agent: {r['agent']:10s} | Model: {r['model_used']}")

    print(f"\n{'=' * 60}")
    print(f"  All specialist agent tests complete!")
    print(f"{'=' * 60}")
