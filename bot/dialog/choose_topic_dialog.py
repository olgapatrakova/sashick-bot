from botbuilder.core import MessageFactory
from botbuilder.dialogs import ComponentDialog, WaterfallDialog, NumberPrompt, PromptValidatorContext, WaterfallStepContext, DialogTurnResult, PromptOptions

class ChooseTopicDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(ChooseTopicDialog, self).__init__(dialog_id or ChooseTopicDialog.__name__)

        self.add_dialog(WaterfallDialog(WaterfallDialog.__name__, [self.selection_step,]))

    async def selection_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # WaterfallStep always finishes with the end of the Waterfall or with another dialog;
        # here it is a Prompt Dialog. Running a prompt here means the next WaterfallStep will
        # be run when the users response is received.

        # if step_context.options is None:
        #     raise Exception("internal error, number not passed in")

        # step_context.values["number"] = step_context.options

        await step_context.context.send_activity(MessageFactory.text("I have 5 topics for you to learn."))
        return await step_context.end_dialog()
