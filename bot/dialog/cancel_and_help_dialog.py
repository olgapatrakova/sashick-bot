from asgiref.sync import sync_to_async
from botbuilder.dialogs import (
    ComponentDialog,
    DialogContext,
    DialogTurnResult,
    DialogTurnStatus, WaterfallDialog, WaterfallStepContext, ChoicePrompt, ConfirmPrompt, PromptOptions
)
from botbuilder.schema import ActivityTypes, InputHints, HeroCard, CardAction, ActionTypes, Activity
from botbuilder.core import MessageFactory, CardFactory

from bot.models import Card, LearningMatrix
import logging


class CancelAndHelpDialog(ComponentDialog):
    def __init__(self, dialog_id: str):
        super(CancelAndHelpDialog, self).__init__(dialog_id)
        self.add_dialog(WaterfallDialog('InterruptionMenuDialog',
                                        [self.show_help, self.process_interruption_choice]))
        self.add_dialog(ChoicePrompt('InterruptionChoice'))
        self.logger = logging.getLogger(self.__class__.__qualname__)
        self.add_dialog(WaterfallDialog('DropDialog',
                                        [self.confirmation_step, self.drop_step]))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))

    async def on_continue_dialog(self, inner_dc: DialogContext) -> DialogTurnResult:
        result = await self.interrupt(inner_dc)
        if result is not None:
            return result

        return await super().on_continue_dialog(inner_dc)

    async def show_help(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        self.logger.info("show_help")
        help_message_text = "Here is what you can do with topics:\n" \
                            "1. Drop the topic means you don't want to learn this topic anymore.\n" \
                            "2. Switch the topic means you want to start learning a new topic and keep progress of the current topic as well.\n" \
                            "3. Back to topic means you want to proceed learning the current topic."

        help_message = MessageFactory.text(
            help_message_text, help_message_text, InputHints.expecting_input
        )
        await step_context.context.send_activity(help_message)

        msg = self.interruption_menu()
        await step_context.context.send_activity(msg)
        return DialogTurnResult(DialogTurnStatus.Waiting)

    async def process_interruption_choice(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        self.logger.info("process_interruption_choice")
        current_card = step_context.options['current_card']
        current_deck = await self.find_deck(current_card)
        user_id = step_context.context.activity.from_property.id
        if step_context.result == "Drop the topic":
            await self.drop_topic(user_id, current_card)
            await step_context.context.send_activity(
                MessageFactory.text(f"You have just dropped the topic {current_deck}"))
            self.logger.info("end current dialog")
            return await step_context.cancel_all_dialogs()
        if step_context.result == "<< Back to topic":
            await step_context.end_dialog(True)
            return DialogTurnResult(DialogTurnStatus.Waiting)

    async def interrupt(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if step_context.context.activity.type == ActivityTypes.message:
            text = step_context.context.activity.text.lower()

            if text in ("help", "?"):
                self.logger.info("interrupt help")

                # inner_dc.context.turn_state['ConversationState']
                current_card = None
                if hasattr(self, 'current_card'):
                    current_card = await self.current_card.get(step_context.context, None)
                    self.logger.info('current card %s', current_card)

                self.logger.info('replace current dialog with %s', 'InterruptionMenuDialog')
                return await step_context.begin_dialog('InterruptionMenuDialog', {'current_card': current_card})

            elif text in ("cancel", "quit", "drop"):
                current_card = None
                if hasattr(self, 'current_card'):
                    current_card = await self.current_card.get(step_context.context, None)
                    self.logger.info('current card %s', current_card)
                return await step_context.begin_dialog('DropDialog', {'current_card': current_card})

    async def confirmation_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        current_card = step_context.options['current_card']
        current_deck = await self.find_deck(current_card)
        step_context.values['card'] = current_card
        step_context.values['deck'] = current_deck
        return await step_context.prompt(
            ConfirmPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text(f"You are going to drop {current_deck} topic. Are you sure?")),
        )

    async def drop_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if step_context.result:
            user_id = step_context.context.activity.from_property.id
            await self.drop_topic(user_id, step_context.values['card'])
            await step_context.context.send_activity(
                MessageFactory.text(f"You have just dropped the topic {step_context.values['deck']}"))
            self.logger.info("end current dialog")
            return await step_context.cancel_all_dialogs()
        return await step_context.next(None)

    def interruption_menu(self) -> Activity:
        reply = MessageFactory.list([])
        card = HeroCard(
            title="Please choose one option:",
            buttons=[
                CardAction(
                    type=ActionTypes.message_back,
                    title="Drop the topic",
                    text="Drop the topic",
                    display_text="Drop the topic",
                    value="Drop the topic",
                ),
                CardAction(
                    type=ActionTypes.message_back,
                    title="<< Back to topic",
                    text="<< Back to topic",
                    display_text="<< Back to topic",
                    value="Action:<< Back to topic",
                ),
            ],
        )
        reply.attachments.append(CardFactory.hero_card(card))

        return reply

    @sync_to_async
    def find_deck(self, card):
        return card.deck.title

    @sync_to_async
    def drop_topic(self, user_id: str, current_card: Card) -> bool:
        self.logger.info("drop_topic")
        if not current_card: return
        if not current_card.deck: return
        topic = current_card.deck.title
        deleted, rows_count = LearningMatrix.objects.filter(user_id=user_id, deck_title=topic).delete()
        self.logger.info('deleted %d learning matrix cards for user=%s topic=%s', deleted, user_id, topic)
        return deleted
