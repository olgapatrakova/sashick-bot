from asgiref.sync import sync_to_async
from botbuilder.core import MessageFactory
from botbuilder.dialogs import ComponentDialog, WaterfallDialog, \
    WaterfallStepContext, DialogTurnResult, PromptOptions, TextPrompt
from django.db.models import Subquery

from bot.models import ShownQuestion, Question, User, Card


class QuizDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(QuizDialog, self).__init__(dialog_id or QuizDialog.__name__)

        self.add_dialog(WaterfallDialog(WaterfallDialog.__name__,
                                        [self.show_question_step, self.check_answer_step,]))
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.initial_dialog_id = WaterfallDialog.__name__

    async def show_question_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        user_id = step_context.context.activity.from_property.id
        if step_context.options is None:
            raise Exception("internal error, card not passed in")
        new_card = step_context.options

        if await self.has_card_question(new_card):
            question_to_ask = await self.get_question(new_card, user_id)
            step_context.values['question'] = question_to_ask
            # add this question to ShownQuestions
            user_id = step_context.context.activity.from_property.id
            await self.mark_question_as_shown(question_to_ask, user_id)
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(prompt=MessageFactory.text(f"{question_to_ask}")),
            )

    async def check_answer_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        user_answer = step_context.result
        is_correct = await self.check_answer(user_answer, step_context.values['question'])
        if is_correct:
            await step_context.context.send_activity(MessageFactory.text("Correct!"))
            return await step_context.end_dialog(True)
        else:
            await step_context.context.send_activity(MessageFactory.text("Not correct."))
            # show one of the correct answers if the back of the card is different. Else show the back of the card only
            question = step_context.values['question']
            if await self.correct_answer_is_different(question):
                correct_answer = await self.correct_answer(step_context.values['question'])
                await step_context.context.send_activity(MessageFactory.text(f"Correct answer is: {correct_answer}"))
            return await step_context.end_dialog(True)

    @sync_to_async
    def correct_answer(self, question):
        return question.answers.first()

    @sync_to_async
    def correct_answer_is_different(self, question):
        card_back = Card.objects.get(pk=question.card_id).back
        return not question.answers.filter(text__iexact=card_back).exists()

    @sync_to_async
    def check_answer(self, user_answer, question):
        return question.answers.filter(text__iexact=user_answer).exists()

    @sync_to_async
    def has_card_question(self, card):
        return Question.objects.filter(card=card).count() > 0

    @sync_to_async
    def mark_question_as_shown(self, question, user_id):
        user = User.objects.get(pk=user_id)
        card = Card.objects.get(pk=question.card_id)
        ShownQuestion(user=user, card=card, question=question).save()

    @sync_to_async
    def get_question(self, card, user):
        shown_questions = ShownQuestion.objects.filter(user=user, card=card).values("question_id")
        questions = Question.objects.filter(card=card).exclude(id__in=Subquery(shown_questions))
        if not questions.count():
            ShownQuestion.objects.filter(user=user, card=card).delete()
            questions = Question.objects.filter(card=card)
        return questions.first()

