import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from langchain_core.documents import Document

from app.agent.nodes import (
    DocumentGrade,
    GroundingCheck,
    QueryDecomposition,
    QueryRewrite,
    RouteDecision,
)
from app.agent.graph import grade_branch, grounding_branch, route_branch
from app.rag.hybrid_retriever import (
    _bm25_cache,
    _get_or_build_bm25_index,
    invalidate_bm25_cache,
    reciprocal_rank_fusion,
    tokenize,
)


# ==========================================
# 1. Unit Test: RRF Fusion
# ==========================================
def test_reciprocal_rank_fusion():
    """
    Test that Reciprocal Rank Fusion accurately computes scores,
    deduplicates matching chunks, and ranks them correctly.
    """
    doc1 = Document(page_content="BERT is a transformer", metadata={"document_id": "docA", "chunk_id": 0})
    doc2 = Document(page_content="LSTM is a recurrent network", metadata={"document_id": "docB", "chunk_id": 0})
    doc3 = Document(page_content="Attention is all you need", metadata={"document_id": "docC", "chunk_id": 0})

    # List 1: Dense ranking
    dense_list = [doc1, doc2]
    # List 2: BM25 ranking
    bm25_list = [doc2, doc3]

    fused = reciprocal_rank_fusion([dense_list, bm25_list], k_constant=60, top_n=10)

    # doc2 appeared in both lists: 1/(60+2) + 1/(60+1)
    # doc1 appeared only in list 1: 1/(60+1)
    # doc3 appeared only in list 2: 1/(60+2)
    assert len(fused) == 3
    # doc2 should be ranked 1st because it had appearances in both lists
    assert fused[0].metadata["document_id"] == "docB"
    assert "rrf_score" in fused[0].metadata
    assert fused[0].metadata["rrf_score"] > fused[1].metadata["rrf_score"]


# ==========================================
# 2. Unit Test: BM25 User Isolation
# ==========================================
def test_bm25_user_isolation(monkeypatch):
    """
    Test that BM25 indexing and retrieval strictly isolates chunks per user_id.
    User A must NEVER retrieve User B's chunks.
    """
    invalidate_bm25_cache()

    # Mock Chroma vector store get() to simulate strict user filtering
    def mock_get(where=None, include=None):
        user_filter = None
        if where and "$and" in where:
            for clause in where["$and"]:
                if "user_id" in clause:
                    user_filter = clause["user_id"]

        if user_filter == 100:
            return {
                "documents": ["User 100 secret document about quantum encryption."],
                "metadatas": [{"user_id": 100, "document_id": "doc_100", "chunk_id": 0}],
            }
        elif user_filter == 200:
            return {
                "documents": ["User 200 document about agricultural crop yields."],
                "metadatas": [{"user_id": 200, "document_id": "doc_200", "chunk_id": 0}],
            }
        return {"documents": [], "metadatas": []}

    class MockChromaStore:
        def get(self, where=None, include=None):
            return mock_get(where=where, include=include)

    monkeypatch.setattr("app.rag.hybrid_retriever.get_vector_store", lambda: MockChromaStore())

    # Build index for User 100
    bm25_100, docs_100 = _get_or_build_bm25_index(user_id=100, valid_doc_ids=["doc_100"])
    assert len(docs_100) == 1
    assert docs_100[0].metadata["user_id"] == 100

    # Build index for User 200
    bm25_200, docs_200 = _get_or_build_bm25_index(user_id=200, valid_doc_ids=["doc_200"])
    assert len(docs_200) == 1
    assert docs_200[0].metadata["user_id"] == 200

    # Verify User 100's index does NOT contain User 200's documents
    for d in docs_100:
        assert d.metadata["user_id"] != 200

    # Verify cache isolation keys
    assert (100, ("doc_100",)) in _bm25_cache
    assert (200, ("doc_200",)) in _bm25_cache

    # Invalidate User 100 only
    invalidate_bm25_cache(user_id=100)
    assert (100, ("doc_100",)) not in _bm25_cache
    assert (200, ("doc_200",)) in _bm25_cache


# ==========================================
# 3. Unit Test: Router & Node Output Parsing
# ==========================================
def test_router_output_parsing():
    """
    Test Pydantic schemas used for structured LLM outputs.
    """
    # RouteDecision
    route = RouteDecision(route="pdf_rag", reasoning="Needs paper analysis")
    assert route.route == "pdf_rag"

    # QueryDecomposition
    decomp = QueryDecomposition(
        is_complex=True,
        sub_queries=["What is BERT?", "What is LSTM?"],
    )
    assert len(decomp.sub_queries) == 2

    # DocumentGrade
    grade = DocumentGrade(relevance="yes", explanation="Relevant passages found")
    assert grade.relevance == "yes"

    # GroundingCheck
    grounding = GroundingCheck(grounded=False, unsupported_claims=["Claim A not in context"])
    assert not grounding.grounded
    assert len(grounding.unsupported_claims) == 1


# ==========================================
# 4. Unit Test: Graph Retry Limits (No Infinite Loops)
# ==========================================
def test_graph_retry_limits():
    """
    Test conditional branching logic for retry limits to prevent infinite loops.
    """
    # 1. Routing branch
    assert route_branch({"route": "direct"}) == "generate_direct"
    assert route_branch({"route": "arxiv"}) == "arxiv"
    assert route_branch({"route": "wikipedia"}) == "wikipedia"
    assert route_branch({"route": "pdf_rag"}) == "decompose_query"

    # 2. Grade branch: rewrite limit < 2
    state_rewrite_0 = {"relevance": "no", "rewrite_count": 0}
    assert grade_branch(state_rewrite_0) == "rewrite_query"

    state_rewrite_1 = {"relevance": "no", "rewrite_count": 1}
    assert grade_branch(state_rewrite_1) == "rewrite_query"

    # Once rewrite_count reaches 2, must transition to fallback (no loop!)
    state_rewrite_2 = {"relevance": "no", "rewrite_count": 2}
    assert grade_branch(state_rewrite_2) == "fallback"

    state_rewrite_3 = {"relevance": "no", "rewrite_count": 3}
    assert grade_branch(state_rewrite_3) == "fallback"

    # 3. Grounding branch: regenerate limit < 1
    state_grounded = {"grounded": True, "regenerate_count": 0}
    assert grounding_branch(state_grounded) == "end"

    state_not_grounded_0 = {"grounded": False, "regenerate_count": 0}
    assert grounding_branch(state_not_grounded_0) == "regenerate"

    # After 1 regeneration attempt, must transition to caveat (no loop!)
    state_not_grounded_1 = {"grounded": False, "regenerate_count": 1}
    assert grounding_branch(state_not_grounded_1) == "caveat"


# ==========================================
# 5. Unit Test: General Knowledge Routes to Wikipedia
# ==========================================
def test_general_knowledge_calls_wikipedia_tool(monkeypatch):
    """
    Test that general-knowledge questions (e.g. 'what is BM25?') route to wikipedia
    and call wikipedia_tool, returning Wikipedia citations.
    """
    from unittest.mock import MagicMock
    from langchain_core.runnables import Runnable, RunnableLambda
    from app.agent.graph import run_agent

    mock_wiki = MagicMock(return_value=[{
        "title": "Okapi BM25",
        "url": "https://en.wikipedia.org/wiki/Okapi_BM25",
        "summary": "In information retrieval, Okapi BM25 is a ranking function used by search engines."
    }])
    monkeypatch.setattr("app.agent.nodes.wikipedia_tool", mock_wiki)

    monkeypatch.setattr("app.services.conversation_manager.get_conversation_history", lambda cid: [])
    monkeypatch.setattr("app.services.conversation_manager.save_conversation", lambda **kwargs: None)

    mock_route = RouteDecision(route="wikipedia", reasoning="General definition question")
    mock_grounding = GroundingCheck(grounded=True, unsupported_claims=[])

    class MockLLM(Runnable):
        def invoke(self, input, config=None, **kwargs):
            return "BM25 is a ranking function based on probabilistic retrieval principles."

        def with_structured_output(self, schema):
            if schema == RouteDecision:
                return RunnableLambda(lambda x: mock_route)
            if schema == GroundingCheck:
                return RunnableLambda(lambda x: mock_grounding)
            return RunnableLambda(lambda x: MagicMock())

    monkeypatch.setattr("app.agent.nodes.model", MockLLM())

    result = run_agent(question="what is BM25?", conversation_id=1, user_id=1, document_ids=None)

    assert mock_wiki.call_count >= 1
    assert result["grounded"] is True
    assert any("wikipedia" in s.get("document_id", "") or "wikipedia" in s.get("url", "").lower() for s in result["sources"])
    assert any("Searched Wikipedia" in step for step in result["trace"])


# ==========================================
# 6. Unit Test: Document Answerable Does NOT Call External Tools
# ==========================================
def test_document_answerable_does_not_call_external_tools(monkeypatch):
    """
    Test that a question answerable by uploaded documents stays in pdf_rag
    and does NOT call external tools (wikipedia_tool or arxiv_tool).
    """
    from unittest.mock import MagicMock
    from langchain_core.runnables import Runnable, RunnableLambda
    from app.agent.graph import run_agent

    mock_wiki = MagicMock()
    mock_arxiv = MagicMock()
    monkeypatch.setattr("app.agent.nodes.wikipedia_tool", mock_wiki)
    monkeypatch.setattr("app.agent.nodes.arxiv_tool", mock_arxiv)

    monkeypatch.setattr("app.services.conversation_manager.get_conversation_history", lambda cid: [])
    monkeypatch.setattr("app.services.conversation_manager.save_conversation", lambda **kwargs: None)

    mock_route = RouteDecision(route="pdf_rag", reasoning="Question about uploaded paper results")
    mock_decomp = QueryDecomposition(is_complex=False, sub_queries=["What is the accuracy of the proposed model?"])
    mock_grade = DocumentGrade(relevance="yes", explanation="Found relevant model accuracy figures")
    mock_grounding = GroundingCheck(grounded=True, unsupported_claims=[])

    class MockLLM(Runnable):
        def invoke(self, input, config=None, **kwargs):
            return "The proposed model achieved 98.4% accuracy."

        def with_structured_output(self, schema):
            if schema == RouteDecision:
                return RunnableLambda(lambda x: mock_route)
            if schema == QueryDecomposition:
                return RunnableLambda(lambda x: mock_decomp)
            if schema == DocumentGrade:
                return RunnableLambda(lambda x: mock_grade)
            if schema == GroundingCheck:
                return RunnableLambda(lambda x: mock_grounding)
            return RunnableLambda(lambda x: MagicMock())

    monkeypatch.setattr("app.agent.nodes.model", MockLLM())

    doc_chunk = Document(
        page_content="Our proposed LSTM-CNN model achieved an accuracy of 98.4% on the test set.",
        metadata={"document_id": "doc_lstm", "filename": "LSTM_CNN+GRU.pdf", "page": 4}
    )
    monkeypatch.setattr("app.agent.nodes.retrieve", lambda **kwargs: [doc_chunk])

    result = run_agent(
        question="What is the accuracy of the proposed model?",
        conversation_id=1,
        user_id=1,
        document_ids=["doc_lstm"]
    )

    # External tools must NOT have been called
    assert mock_wiki.call_count == 0
    assert mock_arxiv.call_count == 0
    assert result["grounded"] is True
    assert result["sources"][0]["document_id"] == "doc_lstm"


# ==========================================
# 7. Unit Test: Multi-Document Scoping Retrieval
# ==========================================
def test_multi_document_scoping_retrieval(monkeypatch):
    """
    Test selecting 2 documents scopes retrieval exclusively to those 2 document_ids,
    and both appear in the sources panel while unselected documents are excluded.
    """
    from langchain_core.runnables import RunnableLambda
    from app.rag.hybrid_retriever import retrieve
    from app.rag.sources import extract_sources

    invalidate_bm25_cache()

    monkeypatch.setattr(
        "app.rag.hybrid_retriever._get_user_valid_doc_ids",
        lambda uid: ["doc_A", "doc_B", "doc_C"]
    )

    doc_a_chunk = Document(
        page_content="Model A uses an LSTM encoder with 256 hidden units.",
        metadata={"document_id": "doc_A", "filename": "ModelA.pdf", "page": 2, "chunk_id": 0, "user_id": 1}
    )
    doc_b_chunk = Document(
        page_content="Model B uses a Transformer encoder with 8 attention heads.",
        metadata={"document_id": "doc_B", "filename": "ModelB.pdf", "page": 5, "chunk_id": 0, "user_id": 1}
    )
    doc_c_chunk = Document(
        page_content="Model C uses a Convolutional backbone.",
        metadata={"document_id": "doc_C", "filename": "ModelC.pdf", "page": 1, "chunk_id": 0, "user_id": 1}
    )

    all_docs = [doc_a_chunk, doc_b_chunk, doc_c_chunk]

    class MockChromaStore:
        def as_retriever(self, search_type=None, search_kwargs=None):
            doc_id_in = None
            filter = search_kwargs.get("filter") if search_kwargs else None
            if filter and "$and" in filter:
                for clause in filter["$and"]:
                    if "document_id" in clause and "$in" in clause["document_id"]:
                        doc_id_in = clause["document_id"]["$in"]

            filtered = [
                d for d in all_docs
                if doc_id_in is None or d.metadata["document_id"] in doc_id_in
            ]
            return RunnableLambda(lambda q: filtered)

        def get(self, where=None, include=None):
            doc_id_in = None
            if where and "$and" in where:
                for clause in where["$and"]:
                    if "document_id" in clause and "$in" in clause["document_id"]:
                        doc_id_in = clause["document_id"]["$in"]

            filtered = [
                d for d in all_docs
                if doc_id_in is None or d.metadata["document_id"] in doc_id_in
            ]
            return {
                "documents": [d.page_content for d in filtered],
                "metadatas": [d.metadata for d in filtered],
            }

    monkeypatch.setattr("app.rag.hybrid_retriever.get_vector_store", lambda: MockChromaStore())

    # Retrieve scoped to doc_A and doc_B
    selected = ["doc_A", "doc_B"]
    results = retrieve(
        query="Compare Model A and Model B",
        user_id=1,
        document_ids=selected,
        mode="hybrid"
    )

    # Chunks must only come from doc_A and doc_B
    retrieved_doc_ids = {d.metadata["document_id"] for d in results}
    assert retrieved_doc_ids == {"doc_A", "doc_B"}
    assert "doc_C" not in retrieved_doc_ids

    # Verify sources extraction contains both selected documents
    sources = extract_sources(results)
    source_ids = {s["document_id"] for s in sources}
    assert source_ids == {"doc_A", "doc_B"}



