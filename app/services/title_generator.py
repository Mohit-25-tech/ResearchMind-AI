from app.models.llm import model

def generate_title_from_query(query: str) -> str:
    """
    Generate a concise title (3-6 words) based on the user's query.
    If the query is short, use it directly. Otherwise, use the LLM to summarize.
    """
    query = query.strip()
    words = query.split()
    if len(words) <= 4:
        return query

    try:
        prompt = (
            "You are a helpful assistant. Generate a short 3 to 6 word title summarizing the following user query. "
            "Do not include quotes, markdown formatting, prefixes like 'Title:', or punctuation. Just return the short title.\n\n"
            f"Query: {query}"
        )
        response = model.invoke(prompt)
        title = response.content.strip().strip('"').strip("'")
        if title:
            # Ensure it's not too long
            if len(title) > 50:
                title = title[:47] + "..."
            return title
    except Exception as e:
        print(f"LLM Title Generation failed: {e}")

    # Fallback: simple word truncation
    title = " ".join(words[:4])
    if len(title) > 30:
        title = title[:27] + "..."
    return title
