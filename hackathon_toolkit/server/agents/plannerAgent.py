import json
from server.anthropicService import AnthropicService


class PlannerAgent:
    def __init__(self):
        self.ai = AnthropicService()

    def create_plan(self, user_message: str, conversation_history: list):
        history_text = ""

        for item in conversation_history[-8:]:
            history_text += f"{item.get('role')}: {item.get('message')}\n"

        prompt = f"""
You are the planner for A1 Financial Copilot.

The user talks to you like a chatbot.
Your job is to convert the user's message into a structured financial automation plan.

Available agents:
1. midnight_sweeper
2. lifestyle_arbitrage
3. tax_ledger
4. habit_enforcer
5. general_chat

Safety rules:
- Never execute banking actions directly from this plan.
- For payments, transfers, penalties, and rewards, set requiresConfirmation to true.
- For scheduled automations, set createsTask to true.
- For webhook-based transaction monitoring, set requiresWebhook to true.
- Use sandboxOnly true.

Return ONLY valid JSON.
No markdown.
No explanation.

JSON schema:
{{
  "intent": "midnight_sweeper | lifestyle_arbitrage | tax_ledger | habit_enforcer | general_chat",
  "reply": "short friendly reply to user",
  "createsTask": true,
  "requiresConfirmation": true,
  "requiresWebhook": false,
  "sandboxOnly": true,
  "task": {{
    "agentType": "string",
    "scheduleType": "none | once | daily | weekly | webhook",
    "runAt": "HH:MM or null",
    "trigger": "string or null",
    "config": {{}}
  }}
}}

Conversation history:
{history_text}

User message:
{user_message}
"""

        ai_response = self.ai.ask(prompt, max_tokens=700)

        try:
            return json.loads(ai_response)
        except json.JSONDecodeError:
            return {
                "intent": "general_chat",
                "reply": ai_response,
                "createsTask": False,
                "requiresConfirmation": False,
                "requiresWebhook": False,
                "sandboxOnly": True,
                "task": {
                    "agentType": "general_chat",
                    "scheduleType": "none",
                    "runAt": None,
                    "trigger": None,
                    "config": {}
                }
            }