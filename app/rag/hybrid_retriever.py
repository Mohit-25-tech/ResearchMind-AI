import logging
import re
from typing import Dict, List, Optional, Set, Tuple, Union
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi

from app.config.settings import settings
from app.rag.reranker import rerank_documents
from app.rag.vector_store import get_vector_store
from app.services.database import get_connection

logger = logging.getLogger(__name__)

# BM25 index cache: (user_id, tuple_of_doc_ids) -> (BM25Okapi, list[Document])
_bm25_cache: Dict[Tuple[int, Tuple[str, ...]], Tuple[BM25Okapi, List[Document]]] = {}


def invalidate_bm25_cache(user_id: Optional[int] = None) -> None:
    """
    Invalidate BM25 cache for a specific user or globally.
    Hooked into document upload/deletion in document_manager.
    """
    global _bm25_cache
    if user_id is None:
        _bm25_cache.clear()
        logger.info("Cleared entire BM25 cache.")
    else:
        keys_to_remove = [k for k in _bm25_cache if k[0] == user_id]
        for k in keys_to_remove:
            _bm25_cache.pop(k, None)
        logger.info("Cleared BM25 cache for user_id=%s.", user_id)


def tokenize(text: str) -> List[str]:
    """
    Simple word tokenizer for BM25.
    """
    return re.findall(r"\w+", text.lower())


def _get_user_valid_doc_ids(user_id: int) -> List[str]:
    """
    Fetch all active document IDs owned by the user from SQLite.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT document_id FROM documents WHERE user_id = ?", (user_id,))
    valid_doc_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return valid_doc_ids


def _build_chroma_filter(user_id: int, valid_doc_ids: List[str]) -> Optional[dict]:
    """
    Build ChromaDB metadata filter for user_id and valid document IDs.
    Guarantees user isolation.
    """
    if not valid_doc_ids:
        return None

    if len(valid_doc_ids) == 1:
        return {
            "$and": [
                {"user_id": user_id},
                {"document_id": valid_doc_ids[0]},
            ]
        }
    return {
        "$and": [
            {"user_id": user_id},
            {"document_id": {"$in": valid_doc_ids}},
        ]
    }


def _dense_retrieval(
    query: str,
    user_id: int,
    valid_doc_ids: List[str],
    k: int = 20,
    search_type: str = "mmr",
) -> List[Document]:
    """
    Perform dense vector retrieval via ChromaDB with MMR or similarity search.
    """
    filters = _build_chroma_filter(user_id, valid_doc_ids)
    if not filters:
        return []

    vector_store = get_vector_store()
    search_kwargs = {
        "k": k,
        "filter": filters,
    }
    if search_type == "mmr":
        search_kwargs["fetch_k"] = max(k * 2, 20)
        search_kwargs["lambda_mult"] = 0.5
        retriever = vector_store.as_retriever(
            search_type="mmr",
            search_kwargs=search_kwargs,
        )
    else:
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs=search_kwargs,
        )

    try:
        return retriever.invoke(query)
    except Exception as e:
        logger.error("Dense retrieval error: %s", e)
        return []


def _get_or_build_bm25_index(
    user_id: int,
    valid_doc_ids: List[str],
) -> Tuple[Optional[BM25Okapi], List[Document]]:
    """
    Get cached BM25 index or build one from Chroma chunks belonging to user_id and valid_doc_ids.
    """
    cache_key = (user_id, tuple(sorted(valid_doc_ids)))
    if cache_key in _bm25_cache:
        return _bm25_cache[cache_key]

    filters = _build_chroma_filter(user_id, valid_doc_ids)
    if not filters:
        return None, []

    vector_store = get_vector_store()
    try:
        data = vector_store.get(where=filters, include=["documents", "metadatas"])
    except Exception as e:
        logger.error("Failed to fetch documents from Chroma for BM25: %s", e)
        return None, []

    docs: List[Document] = []
    text_contents = data.get("documents") or []
    metadatas = data.get("metadatas") or []

    for text, meta in zip(text_contents, metadatas):
        if text:
            docs.append(Document(page_content=text, metadata=meta or {}))

    if not docs:
        return None, []

    tokenized_corpus = [tokenize(doc.page_content) for doc in docs]
    bm25 = BM25Okapi(tokenized_corpus)
    _bm25_cache[cache_key] = (bm25, docs)
    return bm25, docs


def _sparse_retrieval(
    query: str,
    user_id: int,
    valid_doc_ids: List[str],
    k: int = 20,
) -> List[Document]:
    """
    Perform sparse BM25 retrieval over user's cached chunks.
    """
    bm25, docs = _get_or_build_bm25_index(user_id, valid_doc_ids)
    if not bm25 or not docs:
        return []

    tokenized_query = tokenize(query)
    if not tokenized_query:
        return docs[:k]

    scores = bm25.get_scores(tokenized_query)
    # Sort docs by BM25 score descending
    doc_scores = list(zip(docs, scores))
    doc_scores.sort(key=lambda x: x[1], reverse=True)

    results: List[Document] = []
    for doc, score in doc_scores[:k]:
        # Create a copy so we don't mutate cached document
        d = Document(page_content=doc.page_content, metadata=dict(doc.metadata))
        d.metadata["bm25_score"] = float(score)
        results.append(d)

    return results


def reciprocal_rank_fusion(
    ranked_lists: List[List[Document]],
    k_constant: int = 60,
    top_n: int = 20,
) -> List[Document]:
    """
    Apply Reciprocal Rank Fusion (RRF) across multiple ranked document lists.
    RRF score: sum(1.0 / (k_constant + rank)) where rank is 1-indexed.
    Deduplicates documents by unique chunk identifier (doc_id + chunk_id) or content hash.
    """
    rrf_scores: Dict[str, float] = {}
    doc_map: Dict[str, Document] = {}

    for doc_list in ranked_lists:
        for rank, doc in enumerate(doc_list, start=1):
            doc_id = doc.metadata.get("document_id", "")
            chunk_id = doc.metadata.get("chunk_id", "")
            if doc_id and chunk_id != "":
                unique_key = f"{doc_id}_{chunk_id}"
            else:
                unique_key = hash(doc.page_content)

            score = 1.0 / (k_constant + rank)
            rrf_scores[unique_key] = rrf_scores.get(unique_key, 0.0) + score
            if unique_key not in doc_map:
                doc_map[unique_key] = Document(
                    page_content=doc.page_content,
                    metadata=dict(doc.metadata),
                )

    # Sort by accumulated RRF score descending
    sorted_keys = sorted(rrf_scores.keys(), key=lambda k: rrf_scores[k], reverse=True)

    results: List[Document] = []
    for key in sorted_keys[:top_n]:
        d = doc_map[key]
        d.metadata["rrf_score"] = rrf_scores[key]
        results.append(d)

    return results


def retrieve(
    query: str,
    user_id: int,
    document_ids: Optional[Union[List[str], str]] = None,
    mode: str = "hybrid_rerank",
) -> List[Document]:
    """
    Main retrieval entrypoint.
    Modes:
      - 'mmr': Dense MMR search only (top 5).
      - 'hybrid': Dense (top 20) + BM25 (top 20) fused via RRF (top 20).
      - 'hybrid_rerank': Dense + BM25 -> RRF top 20 -> CrossEncoder rerank -> top 5.
    """
    all_user_doc_ids = _get_user_valid_doc_ids(user_id)
    if not all_user_doc_ids:
        return []

    # Normalize document_ids: if empty or None, default to querying across ALL user documents
    if document_ids:
        if isinstance(document_ids, str):
            requested = [d.strip() for d in document_ids.split(",") if d.strip()]
        else:
            requested = [str(d).strip() for d in document_ids if str(d).strip()]
        target_doc_ids = [d for d in requested if d in all_user_doc_ids]
        if not target_doc_ids:
            return []
    else:
        target_doc_ids = all_user_doc_ids

    # 1. MMR mode
    if mode == "mmr":
        return _dense_retrieval(query, user_id, target_doc_ids, k=5, search_type="mmr")

    # 2. Dense + Sparse retrieval for hybrid
    dense_docs = _dense_retrieval(query, user_id, target_doc_ids, k=20, search_type="mmr")
    bm25_docs = _sparse_retrieval(query, user_id, target_doc_ids, k=20)

    fused_docs = reciprocal_rank_fusion([dense_docs, bm25_docs], k_constant=60, top_n=20)

    # 3. Hybrid only (no cross-encoder rerank)
    if mode == "hybrid":
        return fused_docs[:5]

    # 4. Hybrid + Cross-Encoder Rerank
    if mode == "hybrid_rerank":
        if settings.use_reranker:
            return rerank_documents(query=query, documents=fused_docs, top_k=5)
        return fused_docs[:5]

    # Default fallback
    return fused_docs[:5]
