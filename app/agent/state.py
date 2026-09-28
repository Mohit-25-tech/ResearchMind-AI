from typing import Any, Dict, List, Optional, Union
from typing_extensions import TypedDict
from langchain_core.documents import Document

class AgentState(TypedDict):
    """
    State definition for the LangGraph agentic research assistant.
    """
    question: str
    chat_history: List[Dict[str, str]]
    user_id: int
    document_ids: Optional[Union[List[str], str]]
    route: str  # "pdf_rag" | "arxiv" | "wikipedia" | "direct"
    sub_queries: List[str]
    current_query: str
    documents: List[Document]
    relevance: str  # "yes" | "no"
    rewrite_count: int
    answer: str
    grounded: bool
    regenerate_count: int
    sources: List[Dict[str, Any]]
    external_context: str
    trace: List[str]  # e.g. ["Routing query", "Decomposing query", "Retrieving documents", ...]
