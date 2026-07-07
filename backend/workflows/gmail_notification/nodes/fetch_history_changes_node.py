from workflows.gmail_notification.state import GmailNotificationState
from integrations.gmail import get_email_ids,get_gmail_service
from accounts.models import User

def fetch_history_changes_node(state:GmailNotificationState)-> GmailNotificationState:
    user=User.objects.get(email=state['email_address'])
    state['user'] = user
    service=get_gmail_service(user)
    message_ids = get_email_ids(service,user,state['history_id'])
    state['message_ids']=message_ids
    return state
    
