from datetime import datetime
from asgiref.sync import sync_to_async
from botbuilder.core import ActivityHandler, ConversationState, TurnContext, UserState, MessageFactory, CardFactory
from botbuilder.dialogs import Dialog
from botbuilder.schema import Attachment, Activity, ActivityTypes, ConversationReference, AnimationCard, MediaUrl

from bot.dialog.helper import DialogHelper
from bot.models import User
from logging import getLogger
from typing import Dict
logger = getLogger(__name__)


class DialogBot(ActivityHandler):
    """
    This Bot implementation can run any type of Dialog. The use of type parameterization is to allows multiple
    different bots to be run at different endpoints within the same project. This can be achieved by defining distinct
    Controller types each with dependency on distinct Bot types. The ConversationState is used by the Dialog system. The
    UserState isn't, however, it might have been used in a Dialog implementation, and the requirement is that all
    BotState objects are saved at the end of a turn.
    """

    def __init__(
            self, conversation_state: ConversationState, user_state: UserState, dialog: Dialog, conversation_references: Dict[str, ConversationReference]
    ):
        if conversation_state is None:
            raise TypeError("[DialogBot]: Missing parameter. conversation_state is required but None was given")
        if user_state is None:
            raise TypeError("[DialogBot]: Missing parameter. user_state is required but None was given")
        if dialog is None:
            raise Exception("[DialogBot]: Missing parameter. dialog is required")

        self.conversation_state = conversation_state
        self.welcomed = conversation_state.create_property("welcomed")
        self.user_state = user_state
        self.dialog = dialog
        self.conversation_references = conversation_references

    async def on_turn(self, turn_context: TurnContext):
        await super().on_turn(turn_context)
        user_id = turn_context.activity.from_property.id
        await self.get_or_create_user(user_id)
        # Save any state changes that might have ocurred during the turn.
        await self.conversation_state.save_changes(turn_context)
        await self.user_state.save_changes(turn_context)

    async def on_conversation_update_activity(self, turn_context: TurnContext):
        self._add_conversation_reference(turn_context.activity)
        user_id = turn_context.activity.members_added[1].id
        await self.get_or_create_user(user_id)
        already_welcomed = await self.welcomed.get(turn_context, default_value_or_factory=lambda: False)
        if not already_welcomed:
            await turn_context.send_activity(MessageFactory.text(
                "Hello, I'm Sashick. I will help you learn new things using spaced repetition technique."))
            await self.welcomed.set(turn_context, True)
            await self.conversation_state.save_changes(turn_context)
            reply = MessageFactory.list([])
            reply.attachments.append(self.create_animation_card())
            await turn_context.send_activity(reply)

            await turn_context.send_activity(MessageFactory.text(
                "You can control me by sending these commands:\n\n" \
                "<br/>" \
                ":white_check_mark: **drop** - to drop a topic at any time of your learning\n\n" \
                "<br/>" \
                ":white_check_mark: **?** or **help** - to see your statistics, start new topic or drop the current topic"))

        await super(self.__class__, self).on_conversation_update_activity(turn_context)
        await DialogHelper.run_dialog(
            self.dialog, turn_context, self.conversation_state.create_property("DialogState"),
        )

    async def on_message_activity(self, turn_context: TurnContext):
        self._add_conversation_reference(turn_context.activity)
        already_welcomed = await self.welcomed.get(turn_context, default_value_or_factory=lambda: False)

        if not already_welcomed or turn_context.activity.text == '/start':
            await turn_context.send_activity(MessageFactory.text(
                "Hello, I'm Sashick. I will help you learn new things using spaced repetition technique."))
            await self.welcomed.set(turn_context, True)
            await self.conversation_state.save_changes(turn_context)
            reply = MessageFactory.list([])
            reply.attachments.append(self.create_animation_card())
            await turn_context.send_activity(reply)
            await turn_context.send_activity(MessageFactory.text(
                "You can control me by sending these commands:\n\n" \
                "<br/>" \
                ":white_check_mark: **drop** - to drop a topic at any time of your learning\n\n" \
                "<br/>" \
                ":white_check_mark: **?** or **help** - to see your statistics, start new topic or drop the current topic"))
        await DialogHelper.run_dialog(
            self.dialog, turn_context, self.conversation_state.create_property("DialogState"),
        )

    def _add_conversation_reference(self, activity: Activity):
        """
        This populates the shared Dictionary that holds conversation references. In this sample,
        this dictionary is used to send a message to members when /api/notify is hit.
        :param activity:
        :return:
        """
        conversation_reference = TurnContext.get_conversation_reference(activity)
        self.conversation_references[
            conversation_reference.user.id
        ] = conversation_reference

    def create_animation_card(self) -> Attachment:
        card = AnimationCard(
            media=[MediaUrl(url="https://i.imgur.com/A6zuLf4.gif")],
        )
        return CardFactory.animation_card(card)

    @sync_to_async
    def get_or_create_user(self, user_id):
        try:
            obj = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            obj = User(user_id=user_id)
        finally:
            obj.last_interaction_time = datetime.now()
            obj.save()
        return obj
