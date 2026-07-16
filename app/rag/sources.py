def extract_sources(documents):
    """
    Extract unique document sources.
    """

    grouped = {}

    for document in documents:

        metadata = document.metadata

        filename = metadata.get("source")
        document_id = metadata.get("document_id")
        page = metadata.get("page")

        if document_id not in grouped:

            grouped[document_id] = {
                "document_id": document_id,
                "filename": filename,
                "pages": set(),
            }

        grouped[document_id]["pages"].add(page)

    sources = []

    for source in grouped.values():

        source["pages"] = sorted(list(source["pages"]))

        sources.append(source)

    return sources