from datetime import datetime

from asgiref.sync import sync_to_async
from botbuilder.core import MessageFactory
from botbuilder.dialogs import ComponentDialog, WaterfallDialog, \
    WaterfallStepContext, DialogTurnResult, PromptOptions, ChoicePrompt, Choice, ConfirmPrompt
from django.db.models import Subquery

from bot.dialog.initial_learning import InitialLearningDialog
from bot.models import Deck, Card, LearningMatrix, User
from logging import getLogger

logger = getLogger(__name__)


class ChooseTopicDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(ChooseTopicDialog, self).__init__(dialog_id or ChooseTopicDialog.__name__)

        self.add_dialog(WaterfallDialog(WaterfallDialog.__name__,
                                        [self.give_choice_step, self.confirm_choice_step, self.choose_again_step, ]))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.initial_dialog_id = WaterfallDialog.__name__

    async def give_choice_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        user_id = step_context.context.activity.from_property.id
        decks = await self.not_learned_decks(user_id)
        if len(decks) > 0:
            return await step_context.prompt(
                ChoicePrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("Please choose one topic to learn."),
                    choices=[Choice(x.title, synonyms=[str(x.id)]) for x in decks],
                ),
            )
        else:
            await step_context.context.send_activity(MessageFactory.text("Sorry, no new topics for you to learn"))
            return await step_context.end_dialog(True)

    async def confirm_choice_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        step_context.values['deck'] = step_context.result
        deck = await self.deck_id(step_context.result.value)
        step_context.values['deck_id'] = deck
        cards_count = await self.cards_count(deck)
        # WaterfallStep always finishes with the end of the Waterfall or
        # with another dialog; here it is a Prompt Dialog.
        return await step_context.prompt(
            ConfirmPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text(f"You are going to learn {step_context.result.value} which contains {cards_count} cards. Please confirm.")),
        )

    async def choose_again_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if step_context.result:
            cards_list = await self.cards(step_context.values['deck_id'])
            user_id = step_context.context.activity.from_property.id
            deck_title = step_context.values['deck'].value
            # add all cards of a chosen deck to learning matrix
            await self.add_cards_to_learning_matrix(cards_list, user_id, deck_title)
            return await step_context.replace_dialog(InitialLearningDialog.__name__)
        else:
            return await step_context.replace_dialog(ChooseTopicDialog.__name__)

    @sync_to_async
    def not_learned_decks(self, user_id):
        # retrieve deck titles that are in the learning matrix for a certain user
        deck_in_progress = LearningMatrix.objects.filter(user=user_id).values("deck_title").distinct()
        # find all decks except those that are in progress
        not_yet_chosen_decks = Deck.objects.exclude(title__in=Subquery(deck_in_progress))
        return list(not_yet_chosen_decks)

    @sync_to_async
    def deck_id(self, deck_title):
        return Deck.objects.get(title=deck_title).id

    @sync_to_async
    def cards(self, deck_id):
        return list(Card.objects.filter(deck=deck_id))

    @sync_to_async
    def cards_count(self, deck_id):
        return len(list(Card.objects.filter(deck=deck_id)))

    @sync_to_async
    def add_cards_to_learning_matrix(self, cards_list, user_id, deck_title):
        user = User.objects.get(pk=user_id)
        for card in cards_list:
            LearningMatrix(
                user=user,
                card=card,
                deck_title=deck_title,
                last_shown=datetime.utcfromtimestamp(0),
                show_after=datetime.utcfromtimestamp(0),
                show_count=0,
                easy_count=0,
                hard_count=0
            ).save()
