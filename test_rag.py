from app.services.conversation_manager import (
    save_conversation,
    get_conversation_history,
)

session = "demo"

save_conversation(
    session,
    "What is BERT?",
    "BERT is a transformer model."
)

save_conversation(
    session,
    "Explain LSTM.",
    "LSTM is a recurrent neural network."
)

history = get_conversation_history(session)

for row in history:
    print(dict(row))