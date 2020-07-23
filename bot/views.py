# Create your views here.
from botbuilder.core import TurnContext
from botbuilder.schema import Activity
from django.http import HttpResponse, JsonResponse

from bot.bot import ADAPTER, BOT, CONVERSATION_REFERENCES, DefaultConfig
from asgiref.sync import async_to_sync
import json


def index(request):
    """
    Main bot message handler.
    """
    if "application/json" in request.content_type:
        body = json.loads(request.body)
    else:
        return HttpResponse(status=415)  # unsupported media type

    activity = Activity().deserialize(body)

    auth_header = request.META['HTTP_AUTHORIZATION'] if 'HTTP_AUTHORIZATION' in request.META else ""

    response = get_bot_response(activity, auth_header)
    if response:
        return JsonResponse(response.body, safe=False, status=response.status)
    return HttpResponse(status=200)

@async_to_sync
async def get_bot_response(activity, auth_header):
    return await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)

@async_to_sync
async def notify(request):
    await _send_proactive_message()
    return HttpResponse(status=200)


# Send a message to all conversation members.
# This uses the shared Dictionary that the Bot adds conversation references to.
async def _send_proactive_message():
    for conversation_reference in CONVERSATION_REFERENCES.values():
        user_id = conversation_reference.user.id
        await ADAPTER.continue_conversation(
            conversation_reference,
            lambda turn_context: notify_user(user_id, turn_context),
            DefaultConfig.APP_ID
        )


async def notify_user(user_id, turn_context: TurnContext):
    return await turn_context.send_activity(f"proactive hello user {user_id}")
