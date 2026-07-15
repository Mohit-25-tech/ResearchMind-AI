from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_documents(documents,chunk_size=1000,chun_overlap=150):
    """Breaks long document into overlapping chunks so retriveval is practise."""

    splitter = RecursiveCharacterTextSplitter(
        chunk_size= chunk_size,
        chunk_overlap = chun_overlap
    )

    split_docs = splitter.split_documents(documents)
    return split_docs
    