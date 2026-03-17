import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz


SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
]


def get_calendar_service(user):
    """Build authenticated Google Calendar service for a user."""
    from integrations.models import Integration

    try:
        integration = Integration.objects.get(
            user=user,
            provider='google_calendar',
            is_active=True
        )
    except Integration.DoesNotExist:
        raise Exception("Google Calendar not connected. Please connect Calendar first.")

    creds = Credentials(
        token=integration.access_token,
        refresh_token=integration.refresh_token,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=os.environ.get('GOOGLE_CLIENT_ID'),
        client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
        scopes=SCOPES,
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        integration.access_token = creds.token
        integration.save()

    return build('calendar', 'v3', credentials=creds)


def get_available_slots(service, days_ahead: int = 7) -> list:
    """Check calendar and return available 30-min slots in next N days."""
    now = datetime.utcnow().isoformat() + 'Z'
    end = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'

    # Get busy times
    body = {
        "timeMin": now,
        "timeMax": end,
        "items": [{"id": "primary"}]
    }

    freebusy = service.freebusy().query(body=body).execute()
    busy_times = freebusy.get('calendars', {}).get('primary', {}).get('busy', [])

    # Generate available slots (9am-5pm, Mon-Fri)
    available_slots = []
    current = datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0)

    for day in range(days_ahead):
        day_date = current + timedelta(days=day)

        # Skip weekends
        if day_date.weekday() >= 5:
            continue

        for hour in range(9, 17):
            slot_start = day_date.replace(hour=hour, minute=0)
            slot_end = slot_start + timedelta(minutes=30)

            slot_start_str = slot_start.isoformat() + 'Z'
            slot_end_str = slot_end.isoformat() + 'Z'

            # Check if slot conflicts with busy times
            is_busy = False
            for busy in busy_times:
                busy_start = busy['start']
                busy_end = busy['end']
                if slot_start_str < busy_end and slot_end_str > busy_start:
                    is_busy = True
                    break

            if not is_busy:
                available_slots.append({
                    "start": slot_start_str,
                    "end": slot_end_str,
                    "display": slot_start.strftime("%A %B %d at %I:%M %p UTC"),
                })

            if len(available_slots) >= 5:
                break

        if len(available_slots) >= 5:
            break

    return available_slots


def create_calendar_event(
    service,
    title: str,
    start_time: str,
    end_time: str,
    attendee_email: str,
    description: str = ""
) -> dict:
    """Create a Google Calendar event and send invite to attendee."""
    event = {
        'summary': title,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'UTC',
        },
        'attendees': [
            {'email': attendee_email},
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
        'conferenceData': {
            'createRequest': {
                'requestId': f"synthetix-{start_time}",
                'conferenceSolutionKey': {'type': 'hangoutsMeet'},
            }
        },
    }

    event = service.events().insert(
        calendarId='primary',
        body=event,
        conferenceDataVersion=1,
        sendUpdates='all',
    ).execute()

    return {
        'event_id': event.get('id'),
        'event_link': event.get('htmlLink'),
        'meet_link': event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri', ''),
        'start': start_time,
        'end': end_time,
    }