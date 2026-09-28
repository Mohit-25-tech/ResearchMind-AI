import logging
from typing import List, Optional
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder
from app.config.settings import settings

logger = logging.getLogger(__name__)

class CrossEncoderReranker:
    """
    Singleton cross-encoder reranker using sentence-transformers.
    Default model is configurable (default: BAAI/bge-reranker-base).
    """
    _instance: Optional["CrossEncoderReranker"] = None
    _model: Optional[CrossEncoder] = None
    _model_name: Optional[str] = None

    def __new__(cls) -> "CrossEncoderReranker":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_model(self, model_name: Optional[str] = None) -> CrossEncoder:
        target_name = model_name or settings.reranker_model
        if self._model is None or self._model_name != target_name:
            logger.info("Loading CrossEncoder model: %s", target_name)
            self._model = CrossEncoder(target_name)
            self._model_name = target_name
        return self._model

    def rerank(
        self,
        query: str,
        documents: List[Document],
        top_k: int = 5,
        model_name: Optional[str] = None,
    ) -> List[Document]:
        """
        Rerank a list of documents against a query using CrossEncoder.
        Attaches 'rerank_score' to document metadata and returns the top_k.
        """
        if not documents:
            return []

        try:
            model = self.get_model(model_name)
            pairs = [[query, doc.page_content] for doc in documents]
            scores = model.predict(pairs)

            for doc, score in zip(documents, scores):
                doc.metadata["rerank_score"] = float(score)

            ranked = sorted(
                documents,
                key=lambda d: d.metadata.get("rerank_score", float("-inf")),
                reverse=True,
            )
            return ranked[:top_k]
        except Exception as e:
            logger.error("Reranking failed with error: %s. Returning unranked documents.", e)
            for doc in documents:
                doc.metadata.setdefault("rerank_score", 0.0)
            return documents[:top_k]

reranker = CrossEncoderReranker()

def rerank_documents(
    query: str,
    documents: List[Document],
    top_k: int = 5,
    model_name: Optional[str] = None,
) -> List[Document]:
    """
    Convenience wrapper to rerank documents using the singleton reranker.
    """
    return reranker.rerank(query=query, documents=documents, top_k=top_k, model_name=model_name)
