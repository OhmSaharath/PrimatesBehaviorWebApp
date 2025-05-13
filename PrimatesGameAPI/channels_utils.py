from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def broadcast_state(pi_state):
    channel_layer = get_channel_layer()
    group_name = f"rpi_{pi_state.rpiboard.pk}"
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'state_update',  # maps to consumer.state_update
            'data': pi_state.to_dict(),
        }
    )