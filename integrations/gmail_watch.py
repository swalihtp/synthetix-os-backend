import os
from integrations.gmail import get_gmail_service


def register_gmail_watch(user):
    service = get_gmail_service(user)

    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT_ID')
    topic_name = f"projects/{project_id}/topics/gmail-events"

    result = service.users().watch(
        userId='me',
        body={
            'labelIds': ['INBOX'],
            'topicName': topic_name,
        }
    ).execute()

    print(f"Gmail watch registered: {result}")
    return result


def stop_gmail_watch(user):
    service = get_gmail_service(user)
    service.users().stop(userId='me').execute()
    print("Gmail watch stopped.")