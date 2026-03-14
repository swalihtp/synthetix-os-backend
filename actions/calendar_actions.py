from .base import BaseAction


class CalendarCheckAvailabilityAction(BaseAction):
    def execute(self, config: dict, context: dict) -> dict:
        # Stub — will call Google Calendar API
        print("[STUB] Checking calendar availability...")
        return {
            "available_slots": ["2026-03-15 10:00", "2026-03-15 14:00"],
            "calendar_checked": True,
        }


class CalendarCreateEventAction(BaseAction):
    def execute(self, config: dict, context: dict) -> dict:
        # Stub — will call Google Calendar API
        print("[STUB] Creating calendar event...")
        return {
            "event_created": True,
            "event_id": "stub-event-id-123",
        }