from datetime import datetime, timedelta

from asgiref.sync import sync_to_async
from botbuilder.core import MessageFactory
from botbuilder.dialogs import ComponentDialog, WaterfallDialog, \
    WaterfallStepContext, DialogTurnResult, PromptOptions, ChoicePrompt, Choice

from bot.dialog.quiz import QuizDialog
from bot.models import LearningMatrix


class InitialLearningDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(InitialLearningDialog, self).__init__(dialog_id or InitialLearningDialog.__name__)

        self.add_dialog(WaterfallDialog(WaterfallDialog.__name__,
                                        [self.show_card_step, self.show_answer_step, self.loop_step]))
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

    async def show_answer_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if step_context.result:
            card = step_context.values['card']
            user_id = step_context.context.activity.from_property.id
            await self.update_card_show_time(card, user_id)
            await step_context.context.send_activity(MessageFactory.text(f"{card.back}"))
            return await step_context.prompt(
                ChoicePrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("Please choose if this card was easy or hard."),
                    choices=[Choice("Easy"), Choice("Hard")],
                ),
            )


    async def loop_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        easiness = step_context.result.value
        user_id = step_context.context.activity.from_property.id
        await self.mark_easy_hard(step_context.values['card'], user_id, easiness)
        if await self.card_to_show(user_id) is None:
            await step_context.context.send_activity(MessageFactory.text("Yay! You have learned all cards in this topic."))
            await step_context.end_dialog(True)
            return await step_context.replace_dialog(QuizDialog.__name__)
        else:
            return await step_context.replace_dialog(InitialLearningDialog.__name__)

    @sync_to_async
    def card_to_show(self, user):
        try:
            lmx = LearningMatrix.objects.filter(user=user, show_after__lte=datetime.now().astimezone())
            return lmx.latest('last_shown', '-hard_count').card
        except LearningMatrix.DoesNotExist:
            return None

    @sync_to_async
    def mark_easy_hard(self, card, user, easiness):
        lmx = LearningMatrix.objects.get(user=user, card=card)
        if easiness == "Easy":
            lmx.easy_count += 1
        else:
            lmx.hard_count += 1
        lmx.save()

    @sync_to_async
    def update_card_show_time(self, card, user):
        lmx = LearningMatrix.objects.get(user=user, card=card)
        lmx.last_shown = datetime.now().astimezone()
        lmx.show_after = datetime.now().astimezone() + timedelta(days=1)
        lmx.show_count += 1
        lmx.save()

