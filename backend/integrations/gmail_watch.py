import os
from integrations.gmail import get_gmail_service
from integrations.models import Integration
from integrations.models import GmailSync


def register_gmail_watch(user):
    service = get_gmail_service(user)

    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT_ID")
    topic_name = f"projects/{project_id}/topics/gmail-events"

    result = (
        service.users()
        .watch(
            userId="me",
            body={
                "labelIds": ["INBOX"],
                "topicName": topic_name,
            },
        )
        .execute()
    )

    history_id = str(result.get("historyId", "")) or None

    Integration.objects.filter(user=user, provider="gmail").update(
        last_gmail_history_id=history_id
    )

    GmailSync.objects.update_or_create(
        user=user, defaults={"last_history_id": history_id}
    )

    print(f"Gmail watch registered: {result}")

    return result


def stop_gmail_watch(user):
    service = get_gmail_service(user)
    service.users().stop(userId="me").execute()
    print("Gmail watch stopped.")
