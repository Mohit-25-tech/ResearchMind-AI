def build_history(history, max_turns: int = 3) -> str:
    """
    Convert recent conversation history into a prompt string.
    Limits to the last `max_turns` turns to prevent prompt token blowout.
    """
    if not history:
        return ""

    recent_history = history[-max_turns:] if len(history) > max_turns else history
    conversation = []

    for row in recent_history:
        q = row.get("question", "")
        a = row.get("answer", "")
        # Truncate very long past answers to 600 characters to conserve context window
        if len(a) > 600:
            a = a[:600] + "... [truncated]"
        conversation.append(f"User: {q}\n\nAssistant: {a}")

    return "\n\n".join(conversation)