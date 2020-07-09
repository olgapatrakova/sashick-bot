from asgiref.sync import sync_to_async
from botbuilder.core import MessageFactory
from botbuilder.dialogs import ComponentDialog, WaterfallDialog, \
    WaterfallStepContext, DialogTurnResult, PromptOptions, ChoicePrompt, Choice

from bot.models import Deck


class ChooseTopicDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(ChooseTopicDialog, self).__init__(dialog_id or ChooseTopicDialog.__name__)

        self.add_dialog(WaterfallDialog(WaterfallDialog.__name__, [self.give_choice_step,]))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))

        self.initial_dialog_id = WaterfallDialog.__name__

    async def give_choice_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        decks = await self.decks()

        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("I have these topics for you to learn. Please choose one."),
                choices=[Choice(x.title) for x in decks],
            ),
        )

    @sync_to_async
    def decks(self):
        return list(Deck.objects.all())