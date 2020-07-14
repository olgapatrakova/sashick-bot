from datetime import datetime, timedelta
from random import randint

from asgiref.sync import sync_to_async
from botbuilder.core import MessageFactory
from botbuilder.dialogs import ComponentDialog, WaterfallDialog, \
    WaterfallStepContext, DialogTurnResult, PromptOptions, ChoicePrompt, Choice

from bot.models import LearningMatrix, ShownQuestion, Question


class QuizDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(QuizDialog, self).__init__(dialog_id or QuizDialog.__name__)

        self.add_dialog(WaterfallDialog(WaterfallDialog.__name__,
                                        [self.show_question_step,]))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.initial_dialog_id = WaterfallDialog.__name__

    async def show_question_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        user_id = step_context.context.activity.from_property.id
        if step_context.options is None:
            raise Exception("internal error, card not passed in")
        new_card = step_context.options
        await self.find_question(new_card, user_id)

        # step_context.values['card'] = new_card
        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                choices=[Choice("Show answer")],
            ),
        )

    @sync_to_async
    def find_question(self, card, user):
        questions = Question.objects.filter(card=card)
        if not questions:
            return None
        else:
            for question in questions:
                try:
                    ShownQuestion.objects.get(user=user, question=question)
                except ShownQuestion.DoesNotExist:
                    return question
