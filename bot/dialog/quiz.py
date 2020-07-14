from datetime import datetime, timedelta
from random import randint

from asgiref.sync import sync_to_async
from botbuilder.core import MessageFactory
from botbuilder.dialogs import ComponentDialog, WaterfallDialog, \
    WaterfallStepContext, DialogTurnResult, PromptOptions, ChoicePrompt, Choice

from bot.models import LearningMatrix

class QuizDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(QuizDialog, self).__init__(dialog_id or QuizDialog.__name__)

        self.add_dialog(WaterfallDialog(WaterfallDialog.__name__,
                                        [self.show_card_step,]))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.initial_dialog_id = WaterfallDialog.__name__

    async def show_card_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        user_id = step_context.context.activity.from_property.id
        new_card = await self.card_to_show(user_id)

        await step_context.context.send_activity(MessageFactory.text(f"{new_card.front}"))
        step_context.values['card'] = new_card
        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                choices=[Choice("Show answer")],
            ),
        )

    @sync_to_async
    def card_to_show(self, user):
        try:
            # TODO change show_after__gte back to lte
            lmx = LearningMatrix.objects.filter(user=user, show_after__gte=datetime.now().astimezone())
            count = len(lmx)
            random_index = randint(0, count - 1)
            return lmx[random_index].card
        except LearningMatrix.DoesNotExist:
            return None
