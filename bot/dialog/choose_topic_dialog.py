from asgiref.sync import sync_to_async
from botbuilder.core import MessageFactory
from botbuilder.dialogs import ComponentDialog, WaterfallDialog, \
    WaterfallStepContext, DialogTurnResult, PromptOptions, ChoicePrompt, Choice, ConfirmPrompt

from bot.models import Deck


class ChooseTopicDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(ChooseTopicDialog, self).__init__(dialog_id or ChooseTopicDialog.__name__)

        self.add_dialog(WaterfallDialog(WaterfallDialog.__name__, [self.give_choice_step, self.confirm_choice_step, self.choose_again_step,]))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.initial_dialog_id = WaterfallDialog.__name__

    async def give_choice_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        decks = await self.decks()

        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Please choose one topic to learn."),
                choices=[Choice(x.title) for x in decks],
            ),
        )

    async def confirm_choice_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        step_context.values['deck'] = step_context.result

        # WaterfallStep always finishes with the end of the Waterfall or
        # with another dialog; here it is a Prompt Dialog.
        return await step_context.prompt(
            ConfirmPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text(f"You are going to learn {step_context.result.value}. Right?")),
        )

    async def choose_again_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if step_context.result:
            return await step_context.end_dialog(True)
        else:
            return await step_context.replace_dialog(ChooseTopicDialog.__name__)

    @sync_to_async
    def decks(self):
        return list(Deck.objects.all())