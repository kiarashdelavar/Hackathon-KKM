from server.agents.plannerAgent import PlannerAgent
from server.chat.conversationStore import save_message, get_conversation
from server.automation.taskStore import save_task, update_task_status, get_tasks_for_user


class ChatOrchestrator:
    def __init__(self):
        self.planner = PlannerAgent()

    def handle_message(self, user_id: str, message: str):
        save_message(user_id, "user", message)

        conversation = get_conversation(user_id)

        lowered = message.lower().strip()
        if lowered in ["yes", "yes activate it", "activate it", "confirm", "ok activate"]:
            tasks = get_tasks_for_user(user_id)
            draft_tasks = [task for task in tasks if task["status"] == "draft"]

            if not draft_tasks:
                reply = "I could not find a draft automation to activate."
                save_message(user_id, "assistant", reply)
                return {
                    "reply": reply,
                    "activatedTask": None,
                }

            latest_draft = draft_tasks[-1]
            activated = update_task_status(latest_draft["id"], "active")

            reply = "Done. I activated your automation task."
            save_message(user_id, "assistant", reply)

            return {
                "reply": reply,
                "activatedTask": activated,
            }

        plan = self.planner.create_plan(
            user_message=message,
            conversation_history=conversation,
        )

        draft_task = None

        if plan.get("createsTask"):
            draft_task = save_task(
                user_id=user_id,
                task_data=plan.get("task", {}),
                status="draft" if plan.get("requiresConfirmation") else "active",
            )

        reply = plan.get("reply", "I understood your request.")
        save_message(user_id, "assistant", reply)

        return {
            "reply": reply,
            "plan": plan,
            "draftTask": draft_task,
        }