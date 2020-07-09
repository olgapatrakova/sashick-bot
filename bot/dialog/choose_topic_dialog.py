from botbuilder.core import MessageFactory
from botbuilder.dialogs import ComponentDialog, WaterfallDialog, NumberPrompt, PromptValidatorContext, WaterfallStepContext, DialogTurnResult, PromptOptions

class ChooseTopicDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(ChooseTopicDialog, self).__init__(dialog_id or ChooseTopicDialog.__name__)

        self.add_dialog(WaterfallDialog(WaterfallDialog.__name__, [self.selection_step,]))

    async def selection_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:

        await step_context.context.send_activity(MessageFactory.text("I have 5 topics for you to learn."))
        return await step_context.end_dialog()
