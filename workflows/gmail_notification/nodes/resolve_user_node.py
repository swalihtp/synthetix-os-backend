from workflows.gmail_notification.state import GmailNotificationState
from accounts.models import User

def resolve_user_node(state:GmailNotificationState)->GmailNotificationState:
    try:
        user = User.objects.get(email=state['email_address'])
        state['user_id'] = user.id

    except User.DoesNotExist:
        state['skip_workflow'] = True
        
    return state