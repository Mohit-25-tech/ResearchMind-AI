def extract_sources(documents):
    """
    Extract source metadata from retrieved documents.
    """

    sources = []

    seen = set()

    for document in documents:

        metadata = document.metadata

        source = {
            "document_id": metadata.get("document_id"),
            "filename": metadata.get("source"),
            "page": metadata.get("page"),
            "chunk_id": metadata.get("chunk_id"),
        }

        key = (
            source["document_id"],
            source["page"],
            source["chunk_id"],
        )

        if key not in seen:
            seen.add(key)
            sources.append(source)

    return sources