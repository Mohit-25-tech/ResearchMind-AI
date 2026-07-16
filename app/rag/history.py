def build_history(history):
    """
    Convert conversation history into a prompt string.
    """

    if not history:
        return ""

    conversation = []

    for row in history:

        conversation.append(
            f"""User: {row["question"]}

Assistant: {row["answer"]}"""
        )

    return "\n\n".join(conversation)