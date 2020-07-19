from botbuilder.core import UserState, ConversationState
from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
)

from bot.dialog.choose_topic_dialog import ChooseTopicDialog
from bot.dialog.initial_learning import InitialLearningDialog
from bot.dialog.quiz import QuizDialog


class MainDialog(ComponentDialog):
    def __init__(self, conversation_state: ConversationState, user_state: UserState):
        # call parent constructor to activate its functionality with name Main dialog
        super(MainDialog, self).__init__(MainDialog.__name__)

        # create a new WaterFall dialog with name WD and add it to a dialog set
        self.add_dialog(WaterfallDialog(WaterfallDialog.__name__))

        self.add_dialog(ChooseTopicDialog(ChooseTopicDialog.__name__))
        self.add_dialog(InitialLearningDialog(InitialLearningDialog.__name__))
        self.add_dialog(QuizDialog(QuizDialog.__name__))
        # launch the first dialog
        self.initial_dialog_id = ChooseTopicDialog.__name__
