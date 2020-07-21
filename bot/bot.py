import os
import sys
import traceback
from datetime import datetime
from typing import Dict
from http import HTTPStatus

from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.schema import Activity, ActivityTypes, ConversationReference

from bot.activity_handler import DialogBot
from bot.dialog.main_dialog import MainDialog
from dotenv import load_dotenv
from aiohttp import web
from aiohttp.web import Request, Response, json_response

from bot.state import CONVERSATION_STATE, USER_STATE

load_dotenv(verbose=True)

from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    ConversationState,
    MemoryStorage,
    TurnContext,
    UserState,
)


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.getenv("APP_ID")
    APP_PASSWORD = os.getenv("APP_PASSWORD")


CONFIG = DefaultConfig()

# Create adapter.
# See https://aka.ms/about-bot-adapter to learn more about how bots work.
SETTINGS = BotFrameworkAdapterSettings(CONFIG.APP_ID, CONFIG.APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)


# Catch-all for errors.
async def on_error(context: TurnContext, error: Exception):
    # This check writes out errors to console log
    # NOTE: In production environment, you should consider logging this to Azure
    #       application insights.
    print(f"\n [on_turn_error]: {error}", file=sys.stderr)
    traceback.print_exc()

    # Send a message to the user
    await context.send_activity("The bot encountered an error or bug.")
    await context.send_activity("To continue to run this bot, please fix the bot source code.")
    # Send a trace activity if we're talking to the Bot Framework Emulator
    if context.activity.channel_id == "emulator":
        # Create a trace activity that contains the error object
        trace_activity = Activity(
            label="TurnError",
            name="on_turn_error Trace",
            timestamp=datetime.utcnow(),
            type=ActivityTypes.trace,
            value=f"{error}",
            value_type="https://www.botframework.com/schemas/error",
        )

        # Send a trace activity, which will be displayed in Bot Framework Emulator
        await context.send_activity(trace_activity)

    # Clear out state
    await CONVERSATION_STATE.delete(context)


# Set the error handler on the Adapter.
# In this case, we want an unbound method, so MethodType is not needed.
ADAPTER.on_turn_error = on_error

# Create a shared dictionary.  The Bot will add conversation references when users
# join the conversation and send messages.
CONVERSATION_REFERENCES: Dict[str, ConversationReference] = dict()

# create main dialog and bot
DIALOG = MainDialog(CONVERSATION_STATE, USER_STATE)
APP_ID = os.getenv("APP_ID")
BOT = DialogBot(CONVERSATION_STATE, USER_STATE, DIALOG, CONVERSATION_REFERENCES)


