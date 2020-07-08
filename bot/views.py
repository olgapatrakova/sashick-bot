# Create your views here.
from botbuilder.schema import Activity
from django.http import HttpResponse, JsonResponse

from bot.bot import ADAPTER, BOT
from asgiref.sync import async_to_sync
import json


@async_to_sync
async def index(request):
    """
    Main bot message handler.
    """
    if "application/json" in request.content_type:
        body = json.loads(request.body)
    else:
        return HttpResponse(status=415)  # unsupported media type

    activity = Activity().deserialize(body)

    auth_header = request.headers.get("Authorization") or ""

    response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
    if response:
        return JsonResponse(response.body, safe=False, status=response.status)
    return HttpResponse(status=200)
