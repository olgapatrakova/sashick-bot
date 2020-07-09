# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import MessageFactory, UserState, ConversationState
from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import (
    ConfirmPrompt,
    PromptOptions,
    PromptValidatorContext,
)

from bot.dialog.choose_topic_dialog import ChooseTopicDialog


class MainDialog(ComponentDialog):
    def __init__(self, conversation_state: ConversationState, user_state: UserState):
        # call parent constructor to activate its functionality with name Main dialog
        super(MainDialog, self).__init__(MainDialog.__name__)

        # create a new WaterFall dialog with name WD and add it to a dialog set
        self.add_dialog(WaterfallDialog(WaterfallDialog.__name__))

        self.add_dialog(ChooseTopicDialog(ChooseTopicDialog.__name__))

        # launch the first dialog
        self.initial_dialog_id = ChooseTopicDialog.__name__

    # async def choose_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
    #
    #     # number = randrange(0, 11)
    #
    #     # step_context.values["number"] = number
    #     return await step_context.begin_dialog(ChooseTopicDialog.__name__)

    # async def acknoweledge(self, step_context: WaterfallStepContext) -> DialogTurnResult:
    #
    #     await step_context.context.send_activity(MessageFactory.text(f"Congratulations! You won. The number was {step_context.values['number']}"))
    #
    #     return await step_context.prompt(ConfirmPrompt.__name__, PromptOptions(prompt=MessageFactory.text("Would you like to play again?")))
    #
    # async def play_again(self, step_context: WaterfallStepContext) -> DialogTurnResult:
    #     if step_context.result:
    #         return await step_context.replace_dialog(MainDialog.__name__)
    #     else:
    #         await step_context.context.send_activity(MessageFactory.text("Thank you for playing!!!"))
    #         return await step_context.end_dialog(True)
    #
    # @staticmethod
    # def number_validator(prompt_context: PromptValidatorContext) -> bool:
    #     return prompt_context.recognized.succeeded and 0 <= prompt_context.recognized.value <= 10
