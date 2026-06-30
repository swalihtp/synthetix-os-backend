import os
import json
import base64
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from integrations.models import Integration
import email.mime.text
import email.mime.multipart
import logging
from integrations.models import GmailSync
import os
import base64
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from django.db import transaction

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]


def get_gmail_service(user):
    """Build authenticated Gmail service for a user."""

    integration = Integration.objects.get(user=user, provider="gmail", is_active=True)

    creds = Credentials(
        token=integration.access_token,
        refresh_token=integration.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ.get("GOOGLE_CLIENT_ID"),
        client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
        scopes=SCOPES,
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        integration.access_token = creds.token
        integration.save(update_fields=["access_token"])

    return build("gmail", "v1", credentials=creds)


def extract_email_body(payload):
    """Extract plain text body recursively."""

    body = ""

    if payload.get("mimeType") == "text/plain":
        data = payload.get("body", {}).get("data")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8")

    for part in payload.get("parts", []):
        body = extract_email_body(part)
        if body:
            return body

    return body


def extract_attachments(service, message_id, payload):
    """Extract attachment metadata + content."""

    attachments = []

    parts = payload.get("parts", [])

    for part in parts:
        filename = part.get("filename")

        if filename:
            body = part.get("body", {})
            attachment_id = body.get("attachmentId")

            if attachment_id:
                attachment = (
                    service.users()
                    .messages()
                    .attachments()
                    .get(userId="me", messageId=message_id, id=attachment_id)
                    .execute()
                )

                data = attachment.get("data")

                file_data = base64.urlsafe_b64decode(data)

                attachments.append(
                    {
                        "filename": filename,
                        "mime_type": part.get("mimeType"),
                        "size": body.get("size"),
                        "data": file_data,
                    }
                )

        # Recursive check for nested parts
        if part.get("parts"):
            attachments.extend(extract_attachments(service, message_id, part))

    return attachments


def get_email_details(service, message_id: str) -> dict:
    """Fetch full email details including attachments."""

    message = (
        service.users()
        .messages()
        .get(userId="me", id=message_id, format="full")
        .execute()
    )

    payload = message.get("payload", {})
    headers = payload.get("headers", [])

    header_map = {h["name"].lower(): h["value"] for h in headers}

    body = extract_email_body(payload)

    attachments = extract_attachments(service, message_id, payload)

    return {
        "message_id": message_id,
        "thread_id": message.get("threadId", ""),
        "subject": header_map.get("subject", "(no subject)"),
        "from": header_map.get("from", ""),
        "to": header_map.get("to", ""),
        "date": header_map.get("date", ""),
        "body": body,
        "snippet": message.get("snippet", ""),
        "attachments": attachments,
    }


def send_reply(
    user, to: str, subject: str, body: str, thread_id: str, in_reply_to: str = None
):
    """Send an email reply in a thread with proper threading headers."""

    # Get Gmail service for the user
    service = get_gmail_service(user)

    # Create message
    message = email.mime.multipart.MIMEMultipart()
    message["to"] = to
    message["subject"] = subject  # Subject already has "Re:" from tasks.py

    # CRITICAL: Add threading headers
    if in_reply_to:
        message["In-Reply-To"] = in_reply_to
        message["References"] = (
            in_reply_to  # For simple replies, References = In-Reply-To
        )

    # Attach body
    msg = email.mime.text.MIMEText(body, "plain")
    message.attach(msg)

    # Encode and send
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

    return (
        service.users()
        .messages()
        .send(
            userId="me",
            body={
                "raw": raw,
                "threadId": thread_id,
            },
        )
        .execute()
    )


def get_email_ids(service, user, new_history_id):

    # Read current history id under lock
    with transaction.atomic():
        gmail_sync = GmailSync.objects.select_for_update().get(user=user)

        if not gmail_sync.last_history_id:
            return []

        start_history_id = gmail_sync.last_history_id

    message_ids = set()
    next_page_token = None

    # Gmail API calls OUTSIDE the transaction
    while True:

        response = (
            service.users()
            .history()
            .list(
                userId="me",
                startHistoryId=start_history_id,
                historyTypes=["messageAdded"],
                pageToken=next_page_token,
            )
            .execute()
        )

        history_records = response.get("history", [])

        for record in history_records:

            for msg in record.get("messagesAdded", []):
                message = msg.get("message", {})
                message_id = message.get("id")
                labels = message.get("labelIds", [])

                # Skip sent emails
                if "SENT" in labels:
                    continue

                # Skip drafts
                if "DRAFT" in labels:
                    continue

                # Only process inbox emails
                if "INBOX" not in labels:
                    continue

                if message_id:
                    message_ids.add(message_id)

        next_page_token = response.get("nextPageToken")

        if not next_page_token:
            break

    # Update history id under lock
    with transaction.atomic():
        gmail_sync = GmailSync.objects.select_for_update().get(user=user)

        if gmail_sync.last_history_id and int(new_history_id) > int(
            gmail_sync.last_history_id
        ):
            gmail_sync.last_history_id = str(new_history_id)
            gmail_sync.save(update_fields=["last_history_id"])

    return list(message_ids)
