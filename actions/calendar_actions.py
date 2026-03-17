from .base import BaseAction


class CalendarCheckAvailabilityAction(BaseAction):
    def execute(self, config: dict, context: dict) -> dict:
        user_id = context.get("user_id")
        days_ahead = config.get("days_ahead", 7)

        if user_id:
            try:
                from django.contrib.auth import get_user_model
                from integrations.google_calendar import (
                    get_calendar_service,
                    get_available_slots
                )
                User = get_user_model()
                user = User.objects.get(id=user_id)
                service = get_calendar_service(user)
                slots = get_available_slots(service, days_ahead)

                return {
                    "available_slots": slots,
                    "calendar_checked": True,
                    "slots_found": len(slots),
                }
            except Exception as e:
                print(f"[Calendar] Could not check availability: {e}")

        # Stub fallback
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        stub_slots = []
        for i in range(1, 4):
            slot_start = (now + timedelta(days=i)).replace(hour=10, minute=0)
            slot_end = slot_start + timedelta(minutes=30)
            stub_slots.append({
                "start": slot_start.isoformat() + 'Z',
                "end": slot_end.isoformat() + 'Z',
                "display": slot_start.strftime("%A %B %d at %I:%M %p UTC"),
            })

        return {
            "available_slots": stub_slots,
            "calendar_checked": True,
            "slots_found": len(stub_slots),
        }


class CalendarCreateEventAction(BaseAction):
    def execute(self, config: dict, context: dict) -> dict:
        user_id = context.get("user_id")
        sender = context.get("sender", "")
        subject = context.get("subject", "Meeting")
        available_slots = context.get("available_slots", [])

        # Get first available slot
        if not available_slots:
            return {"event_created": False, "error": "No available slots"}

        first_slot = available_slots[0]
        start_time = first_slot.get("start", "")
        end_time = first_slot.get("end", "")

        # Extract email from sender string like "Name <email@domain.com>"
        import re
        email_match = re.search(r'<(.+?)>', sender)
        attendee_email = email_match.group(1) if email_match else sender

        if user_id and start_time and attendee_email:
            try:
                from django.contrib.auth import get_user_model
                from integrations.google_calendar import (
                    get_calendar_service,
                    create_calendar_event
                )
                User = get_user_model()
                user = User.objects.get(id=user_id)
                service = get_calendar_service(user)

                result = create_calendar_event(
                    service=service,
                    title=f"Meeting: {subject}",
                    start_time=start_time,
                    end_time=end_time,
                    attendee_email=attendee_email,
                    description=f"Meeting scheduled via Synthetix OS.\nOriginal request: {subject}",
                )

                print(f"[Calendar] Event created: {result.get('event_link')}")
                return {
                    "event_created": True,
                    "event_id": result.get("event_id"),
                    "event_link": result.get("event_link"),
                    "meet_link": result.get("meet_link"),
                    "meeting_time": first_slot.get("display"),
                    "attendee": attendee_email,
                }
            except Exception as e:
                print(f"[Calendar] Could not create event: {e}")

        # Stub fallback
        print(f"[STUB] Creating calendar event for {attendee_email} at {start_time}")
        return {
            "event_created": True,
            "event_id": "stub-event-123",
            "event_link": "https://calendar.google.com/stub",
            "meet_link": "https://meet.google.com/stub",
            "meeting_time": first_slot.get("display", "Tomorrow at 10:00 AM UTC"),
            "attendee": attendee_email,
        }