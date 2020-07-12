from datetime import datetime, timedelta

from asgiref.sync import sync_to_async
from botbuilder.core import MessageFactory
from botbuilder.dialogs import ComponentDialog, WaterfallDialog, \
    WaterfallStepContext, DialogTurnResult, PromptOptions, ChoicePrompt, Choice, ConfirmPrompt
from django.db.models import Subquery

from bot.models import Deck, Card, LearningMatrix, User
from logging import getLogger

class InitialLearningDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(InitialLearningDialog, self).__init__(dialog_id or InitialLearningDialog.__name__)

        self.add_dialog(WaterfallDialog(WaterfallDialog.__name__,
                                        [self.show_card_step, self.show_answer_step,]))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.initial_dialog_id = WaterfallDialog.__name__

    async def show_card_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if step_context.options is None:
            raise Exception("internal error, cards list was not passed in")

        cards_list = step_context.options
        for card in cards_list:
            await step_context.context.send_activity(MessageFactory.text(f"{card.front}"))
            await step_context.prompt(
                ChoicePrompt.__name__,
                PromptOptions(
                    choices=[Choice("Show answer")],
                ),
            )
            step_context.values['card'] = step_context.result
        return await step_context.end_dialog(True)

    async def show_answer_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if step_context.result:
            await step_context.context.send_activity(MessageFactory.text(f"{step_context.values['card'].back}"))

    @sync_to_async
    def cards(self, deck_id):
        return list(Card.objects.filter(deck=deck_id))
