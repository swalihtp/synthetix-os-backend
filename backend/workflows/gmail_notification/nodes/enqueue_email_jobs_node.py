from workflows.gmail_notification.state import GmailNotificationState

def enqueue_email_jobs_node(state:GmailNotificationState)->GmailNotificationState:
    from workflows.tasks import process_email_task
    for message_id in state['message_ids']:
        process_email_task.delay(message_id, state['user_id'])
    return state