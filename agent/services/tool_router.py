# agents/services/tool_router.py

class ToolRouter:

    def execute_action(self, action_config, context):
        tool = action_config["tool"]

        if tool == "telegram":
            return self._send_telegram(action_config, context)

        if tool == "google_calendar":
            return self._create_calendar_event(action_config, context)

        if tool == "google_sheets":
            return self._append_sheet(action_config, context)

        if tool == "gmail":
            return self._send_email(action_config, context)

        raise ValueError("Unsupported tool")

    def _send_telegram(self, config, context):
        # Implement Telegram API call
        return {"status": "sent"}

    def _create_calendar_event(self, config, context):
        return {"status": "event_created"}

    def _append_sheet(self, config, context):
        return {"status": "row_added"}

    def _send_email(self, config, context):
        return {"status": "email_sent"}