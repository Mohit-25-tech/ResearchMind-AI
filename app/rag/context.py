def build_context(documents):
    """
    Converts retrieved documents into one context string.
    """

    return "\n\n".join(
        document.page_content
        for document in documents
    )