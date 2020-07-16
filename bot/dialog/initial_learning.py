from datetime import datetime, timedelta

from asgiref.sync import sync_to_async
from botbuilder.core import MessageFactory
from botbuilder.dialogs import ComponentDialog, WaterfallDialog, \
    WaterfallStepContext, DialogTurnResult, PromptOptions, ChoicePrompt, Choice
from botbuilder.schema import Attachment, Activity, ActivityTypes

from bot.dialog.quiz import QuizDialog
from bot.models import LearningMatrix, Card


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

        pic_url = await self.get_image(new_card.id)
        if pic_url:
            att = Attachment(
                name="architecture-resize.png",
                content_type="image/png",
                content_url=pic_url,
            )
            reply = Activity(type=ActivityTypes.message)
            reply.attachments = [att]
            await step_context.context.send_activity(reply)

        # a quiz question will be shown only if a card was already shown and learned, meaning that it's marked as easy
        if await self.get_easy_count(new_card, user_id) > 0:
            return await step_context.begin_dialog(QuizDialog.__name__, new_card)

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
                    prompt=MessageFactory.text("Please choose if this card was easy or hard for you."),
                    choices=[Choice("Easy"), Choice("Hard")],
                ),
            )


    async def loop_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        easiness = step_context.result.value
        user_id = step_context.context.activity.from_property.id
        await self.mark_easy_hard(step_context.values['card'], user_id, easiness)
        if await self.card_to_show(user_id) is None:
            await step_context.context.send_activity(MessageFactory.text("Yay! You have learned all cards in this topic."))
            return await step_context.end_dialog(True)
        else:
            return await step_context.replace_dialog(InitialLearningDialog.__name__)

    @sync_to_async
    def card_to_show(self, user):
        lmx = LearningMatrix.objects.filter(user=user, show_after__lte=datetime.now().astimezone())
        card_obj = lmx.order_by('last_shown', '-hard_count').first()
        if card_obj:
            return card_obj.card

    @sync_to_async
    def get_image(self, card):
        return Card.objects.get(pk=card).url

    @sync_to_async
    def get_easy_count(self, card, user):
        return LearningMatrix.objects.get(user=user, card=card).easy_count

    @sync_to_async
    def mark_easy_hard(self, card, user, easiness):
        spaced_repetition = {1: 1, 2: 6, 3: 9, 4: 19}
        lmx = LearningMatrix.objects.get(user=user, card=card)
        if easiness == "Easy":
            lmx.easy_count += 1
            repeat_after_days = spaced_repetition.get(lmx.easy_count, 19)
            lmx.show_after = datetime.now().astimezone() + timedelta(days=repeat_after_days)
        else:
            lmx.hard_count += 1
        lmx.save()

    @sync_to_async
    def update_card_show_time(self, card, user):
        lmx = LearningMatrix.objects.get(user=user, card=card)
        lmx.last_shown = datetime.now().astimezone()
        lmx.show_count += 1
        lmx.save()

