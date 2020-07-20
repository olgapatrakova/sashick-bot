import logging
from datetime import datetime, timedelta

from asgiref.sync import sync_to_async
from botbuilder.core import MessageFactory, CardFactory
from botbuilder.dialogs import WaterfallDialog, \
    WaterfallStepContext, DialogTurnResult, PromptOptions, ChoicePrompt, Choice, DialogTurnStatus
from botbuilder.schema import Attachment, HeroCard, CardImage, CardAction, ActionTypes

from bot.state import CONVERSATION_STATE

from bot.dialog.cancel_and_help_dialog import CancelAndHelpDialog
from bot.dialog.quiz import QuizDialog
from bot.models import LearningMatrix, Card


class InitialLearningDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None):
        super(InitialLearningDialog, self).__init__(dialog_id or InitialLearningDialog.__name__)

        self.add_dialog(WaterfallDialog(WaterfallDialog.__name__,
                                        [self.show_card_step, self.show_answer_step, self.loop_step]))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.initial_dialog_id = WaterfallDialog.__name__
        self.current_card = CONVERSATION_STATE.create_property("CurrentCard")
        self.logger = logging.getLogger(self.__class__.__qualname__)

    async def show_card_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        self.logger.info('show_card_step')
        user_id = step_context.context.activity.from_property.id
        new_card = await self.card_to_show(user_id)
        if new_card is None:
            self.logger.info('no new card to show, replace current dialog with %s', 'ChooseTopicDialog')
            return await step_context.replace_dialog('ChooseTopicDialog')
        await self.current_card.set(step_context.context, new_card)
        await CONVERSATION_STATE.save_changes(step_context.context)
        step_context.values['card'] = new_card

        # a quiz question will be shown only if a card was already shown and learned, meaning that it's marked as easy
        if await self.get_easy_count(new_card, user_id) > 0:
            self.logger.info('begin dialog %s',QuizDialog.__name__)
            return await step_context.begin_dialog(QuizDialog.__name__, new_card)
        else:
            pic_url = await self.get_image(new_card.id)
            if pic_url:
                reply = MessageFactory.list([])
                reply.attachments.append(self.create_hero_card(pic_url, new_card))
                await step_context.context.send_activity(reply)
            else:
                # await step_context.context.send_activity(MessageFactory.text(f"{new_card.front}"))
                await step_context.prompt(
                    ChoicePrompt.__name__,
                    PromptOptions(
                        prompt=MessageFactory.text(f"{new_card.front}"),
                        choices=[Choice("Show answer")],
                    ),
                )

            return DialogTurnResult(DialogTurnStatus.Waiting)

    async def show_answer_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        self.logger.info('show_answer_step')
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
        return await step_context.next(False)

    async def loop_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        self.logger.info('loop_step')
        user_id = step_context.context.activity.from_property.id
        if step_context.result:
            easiness = step_context.result.value

            await self.mark_easy_hard(step_context.values['card'], user_id, easiness)
            if await self.card_to_show(user_id) is None:
                await step_context.context.send_activity(
                    MessageFactory.text("Yay! You have learned all cards in this topic."))
                self.logger.info('end current dialog')
                return await step_context.end_dialog(True)

        self.logger.info('replace current dialog with %s',InitialLearningDialog.__name__)
        return await step_context.replace_dialog(InitialLearningDialog.__name__)

    def create_hero_card(self, pic_url, new_card) -> Attachment:
        card = HeroCard(
            title=f"{new_card.front}",
            images=[
                CardImage(
                    url=f"{pic_url}"
                )
            ],
            buttons=[
                CardAction(
                    type=ActionTypes.message_back,
                    title="Show Answer",
                    text="Show Answer",
                    value="Action:Show answer",
                )
            ],
        )
        return CardFactory.hero_card(card)

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
