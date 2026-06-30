from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def send_workflow_update(agent_id, data):
    print("SENDING WEBSOCKET EVENT::")

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"agent_{agent_id}",
        {
            "type": "workflow_update",
            "data": data
        }
    )