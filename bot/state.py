from botbuilder.core import ConversationState, UserState, MemoryStorage

MEMORY = MemoryStorage()
CONVERSATION_STATE = ConversationState(MEMORY)
USER_STATE = UserState(MEMORY)