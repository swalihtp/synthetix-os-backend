import os
import json
import base64
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from integrations.models import Integration


SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
]


def get_gmail_service(user):
    """Build authenticated Gmail service for a user."""
    try:
        integration = Integration.objects.get(
            user=user,
            provider='gmail',
            is_active=True
        )
    except Integration.DoesNotExist:
        raise Exception("Gmail not connected. Please connect Gmail first.")

    creds = Credentials(
        token=integration.access_token,
        refresh_token=integration.refresh_token,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=os.environ.get('GOOGLE_CLIENT_ID'),
        client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
        scopes=SCOPES,
    )

    # Auto-refresh token if expired
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        integration.access_token = creds.token
        integration.save()

    return build('gmail', 'v1', credentials=creds)


def get_email_details(service, message_id: str) -> dict:
    """Fetch full email details by message ID."""
    message = service.users().messages().get(
        userId='me',
        id=message_id,
        format='full'
    ).execute()

    headers = message['payload'].get('headers', [])
    header_map = {h['name'].lower(): h['value'] for h in headers}

    # Extract body
    body = ''
    payload = message.get('payload', {})

    if 'parts' in payload:
        for part in payload['parts']:
            if part.get('mimeType') == 'text/plain':
                data = part.get('body', {}).get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    break
    else:
        data = payload.get('body', {}).get('data', '')
        if data:
            body = base64.urlsafe_b64decode(data).decode('utf-8')

    return {
        'message_id': message_id,
        'thread_id': message.get('threadId', ''),
        'subject': header_map.get('subject', '(no subject)'),
        'from': header_map.get('from', ''),
        'to': header_map.get('to', ''),
        'date': header_map.get('date', ''),
        'body': body,
        'snippet': message.get('snippet', ''),
    }


def send_reply(service, thread_id: str, to: str, subject: str, body: str):
    """Send an email reply in a thread."""
    import email.mime.text
    import email.mime.multipart

    message = email.mime.multipart.MIMEMultipart()
    message['to'] = to
    message['subject'] = f"Re: {subject}" if not subject.startswith('Re:') else subject

    msg = email.mime.text.MIMEText(body, 'plain')
    message.attach(msg)

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

    return service.users().messages().send(
        userId='me',
        body={
            'raw': raw,
            'threadId': thread_id,
        }
    ).execute()