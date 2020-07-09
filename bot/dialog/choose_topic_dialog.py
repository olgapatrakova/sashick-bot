from asgiref.sync import sync_to_async
from botbuilder.core import MessageFactory
from botbuilder.dialogs import ComponentDialog, WaterfallDialog, NumberPrompt, PromptValidatorContext, WaterfallStepContext, DialogTurnResult, PromptOptions

from bot.models import Deck


class ChooseTopicDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(ChooseTopicDialog, self).__init__(dialog_id or ChooseTopicDialog.__name__)

        self.add_dialog(WaterfallDialog(WaterfallDialog.__name__, [self.selection_step,]))

    async def selection_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        decks = await self.decks()
        await step_context.context.send_activity(MessageFactory.text(f"I have these topics for you to learn: {decks}."))
        return await step_context.end_dialog()

    @sync_to_async
    def decks(self):
        return list(Deck.objects.all())