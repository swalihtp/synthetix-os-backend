from typing import TypedDict, List


class GmailNotificationState(TypedDict):
    payload: dict
    email_address: str
    history_id: str
    user_id: int
    message_ids: List[str]
    skip_workflow: bool
    pubsub_msg_id:str
    user: dict