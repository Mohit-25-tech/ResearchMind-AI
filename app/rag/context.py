def build_context(documents):

    context = []

    for document in documents:

        metadata = document.metadata

        context.append(
            f"""
========================
Document: {metadata.get("source")}
Page: {metadata.get("page")}
========================

{document.page_content}
"""
        )

    return "\n\n".join(context)