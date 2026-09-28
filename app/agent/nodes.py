import logging
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser

from app.agent.state import AgentState
from app.agent.tools import arxiv_tool, wikipedia_tool
from app.config.settings import settings
from app.models.llm import model
from app.prompts.prompts import rag_prompt
from app.rag.context import build_context
from app.rag.history import build_history
from app.rag.hybrid_retriever import retrieve
from app.rag.sources import extract_sources

logger = logging.getLogger(__name__)


# ==========================================
# Pydantic Schemas for Structured Outputs
# ==========================================
class RouteDecision(BaseModel):
    """Routing classification for user question."""
    route: Literal["pdf_rag", "arxiv", "wikipedia", "direct"] = Field(
        description=(
            "'pdf_rag' if the answer requires searching the user's uploaded research documents. "
            "'arxiv' if asking about recent scientific literature or papers not in local docs. "
            "'wikipedia' for general definitions, history, concepts, or encyclopedic knowledge. "
            "'direct' for greetings, conversational pleasantries, or queries answerable directly from chat history."
        )
    )
    reasoning: str = Field(description="Short rationale for the routing decision.")


class QueryDecomposition(BaseModel):
    """Decomposition of complex queries into focused sub-queries."""
    is_complex: bool = Field(description="True if the question is multi-part or a comparative question.")
    sub_queries: List[str] = Field(
        default_factory=list,
        description="Up to 3 focused search queries. If not complex, include just the original question."
    )


class DocumentGrade(BaseModel):
    """Grading retrieval relevance of documents."""
    relevance: Literal["yes", "no"] = Field(
        description="'yes' if retrieved context contains information relevant to the question, else 'no'."
    )
    explanation: str = Field(description="Brief explanation of why the documents are relevant or not.")


class QueryRewrite(BaseModel):
    """Rewritten search query for improved retrieval."""
    rewritten_query: str = Field(description="Rewritten query with acronyms expanded and synonyms added.")


class GroundingCheck(BaseModel):
    """Verification of factual grounding in provided context."""
    grounded: bool = Field(description="True if every claim in the answer is backed by context, False otherwise.")
    unsupported_claims: List[str] = Field(
        default_factory=list,
        description="List of specific claims in the answer that are NOT supported by the context."
    )


# ==========================================
# Node Implementations
# ==========================================

# ==========================================
# External Context Prompt Template
# ==========================================
from langchain_core.prompts import ChatPromptTemplate

external_rag_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are ResearchMind AI, an intelligent research assistant.
Answer the user's question clearly, concisely, and factually using ONLY the provided external context (from Wikipedia or arXiv) and conversation history.

Guidelines:
- Explain the concept thoroughly in your own words.
- Explicitly cite the source article or paper title and its URL.
- Do NOT fabricate details or claim this information is from the user's uploaded documents.
- If the external context does not contain sufficient details to answer, state: "This isn't covered in your documents or external literature."
"""
    ),
    (
        "human",
        "Conversation History:\n{history}\n\nExternal Context:\n{context}\n\nQuestion: {question}"
    )
])


# ==========================================
# Node Implementations
# ==========================================

def route_query_node(state: AgentState) -> Dict[str, Any]:
    """
    LLM classifies the question into one of four routes:
    'pdf_rag', 'arxiv', 'wikipedia', 'direct'.
    """
    question = state["question"]
    logger.info("Node: route_query for question: %s", question)
    system_prompt = (
        "You are an expert intent router for an AI research assistant workspace.\n"
        "Analyze the user's question and conversation history to select the single best route:\n\n"
        "- 'wikipedia': For general definitions, conceptual explanations, algorithms, history, or encyclopedic knowledge.\n"
        "  Examples:\n"
        "  * 'what is BM25?' -> wikipedia\n"
        "  * 'what is a transformer model' -> wikipedia\n"
        "  * 'explain RAG' -> wikipedia\n"
        "  * 'who invented BM25' -> wikipedia\n"
        "  * 'define gradient descent' -> wikipedia\n\n"
        "- 'arxiv': For discovering research papers, broad scientific literature, recent publications, or academic trends.\n"
        "  Examples:\n"
        "  * 'find recent papers on LoRA fine-tuning' -> arxiv\n"
        "  * 'what are recent publications on multi-modal agents?' -> arxiv\n"
        "  * 'papers on deep learning for protein folding' -> arxiv\n\n"
        "- 'pdf_rag': For questions about the user's uploaded document(s), findings, specific data, sections, or comparative analysis of files.\n"
        "  Examples:\n"
        "  * 'what is the main conclusion of the paper?' -> pdf_rag\n"
        "  * 'summarize the results table in my uploaded document' -> pdf_rag\n"
        "  * 'how does document A compare to document B?' -> pdf_rag\n"
        "  * 'what dataset was used in this study?' -> pdf_rag\n\n"
        "- 'direct': For greetings, conversational remarks, chit-chat, or questions answerable purely from prior conversation history.\n"
        "  Examples:\n"
        "  * 'hello', 'hi there' -> direct\n"
        "  * 'thank you so much' -> direct\n"
        "  * 'what was the second point you just mentioned?' -> direct"
    )
    router_llm = model.with_structured_output(RouteDecision)
    try:
        decision = router_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Question: {question}\nHistory:\n{build_history(state.get('chat_history', []))}")
        ])
        route = decision.route
        raw_output = decision.model_dump()
        reasoning = decision.reasoning
    except Exception as e:
        logger.error("Routing failed: %s. Defaulting to 'pdf_rag'.", e)
        route = "pdf_rag"
        raw_output = {"error": str(e)}
        reasoning = "Fallback default on exception"

    logger.info(
        "[AGENT_DEBUG] route_query: chosen_route='%s' | raw_decision=%s | reasoning='%s'",
        route, raw_output, reasoning
    )

    return {
        "route": route,
        "current_query": question,
        "trace": state.get("trace", []) + [f"Routed to: {route.upper()} (Reason: {reasoning})"]
    }


def generate_direct_node(state: AgentState) -> Dict[str, Any]:
    """
    Generate direct conversational response without document retrieval.
    """
    logger.info("Node: generate_direct")
    history_text = build_history(state.get("chat_history", []))
    prompt = (
        "You are ResearchMind AI, a helpful research assistant. Answer the user conversationally and concisely.\n"
        f"Conversation History:\n{history_text}\n\n"
        f"User: {state['question']}"
    )
    response = model.invoke(prompt)
    answer = response.content if hasattr(response, "content") else str(response)

    logger.info("[AGENT_DEBUG] generate_direct executed: answer_length=%d", len(answer))
    return {
        "answer": answer,
        "sources": [],
        "grounded": True,
        "trace": state.get("trace", []) + ["Direct answer generated"]
    }


def arxiv_node(state: AgentState) -> Dict[str, Any]:
    """
    Query arXiv literature and prepare external context.
    """
    query = state.get("current_query") or state["question"]
    logger.info("Node: arxiv_node for query: %s", query)
    papers = arxiv_tool(query, max_results=3)

    logger.info("[AGENT_DEBUG] tool_executed: arXiv | query='%s' | papers_found=%d", query, len(papers))

    if not papers:
        context = ""
        sources = []
    else:
        context_parts = []
        sources = []
        for p in papers:
            context_parts.append(
                f"Paper: {p['title']}\nAuthors: {', '.join(p['authors'])}\nURL: {p['url']}\nSummary: {p['summary']}\n"
            )
            sources.append({
                "document_id": "arxiv",
                "filename": p["title"],
                "url": p["url"],
                "pages": []
            })
        context = "\n---\n".join(context_parts)

    return {
        "external_context": context,
        "sources": sources,
        "documents": [],
        "trace": state.get("trace", []) + [f"Searched arXiv ({len(papers)} papers found)"]
    }


def wikipedia_node(state: AgentState) -> Dict[str, Any]:
    """
    Query Wikipedia and prepare external context.
    """
    query = state.get("current_query") or state["question"]
    logger.info("Node: wikipedia_node for query: %s", query)
    pages = wikipedia_tool(query, max_results=2)

    logger.info("[AGENT_DEBUG] tool_executed: Wikipedia | query='%s' | articles_found=%d", query, len(pages))

    if not pages:
        context = ""
        sources = []
    else:
        context_parts = []
        sources = []
        for p in pages:
            context_parts.append(
                f"Article: {p['title']}\nURL: {p['url']}\nContent: {p['summary']}\n"
            )
            sources.append({
                "document_id": "wikipedia",
                "filename": p["title"],
                "url": p["url"],
                "pages": []
            })
        context = "\n---\n".join(context_parts)

    return {
        "external_context": context,
        "sources": sources,
        "documents": [],
        "trace": state.get("trace", []) + [f"Searched Wikipedia ({len(pages)} articles found)"]
    }


def decompose_query_node(state: AgentState) -> Dict[str, Any]:
    """
    Analyze if the question is multi-part or comparison; produce up to 3 sub-queries.
    """
    question = state["question"]
    doc_ids = state.get("document_ids")
    logger.info("Node: decompose_query for question: %s (scoped doc_ids: %s)", question, doc_ids)
    
    system_prompt = (
        "You are an expert query decomposer for an AI research workspace.\n"
        "If the user's question compares two concepts or documents (e.g., 'compare X in doc A vs doc B', "
        "or 'how does method 1 compare to method 2'), or contains distinct multi-part sub-questions, "
        "break it down into up to 3 focused sub-queries so retrieval covers each aspect.\n"
        "If it is a single focused inquiry, return just the original question in sub_queries."
    )
    decomposer_llm = model.with_structured_output(QueryDecomposition)
    try:
        context_msg = f"Question: {question}"
        if doc_ids:
            context_msg += f"\nActive scoped document IDs: {doc_ids}"
        decomp = decomposer_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=context_msg)
        ])
        sub_queries = decomp.sub_queries if decomp.sub_queries else [question]
    except Exception as e:
        logger.error("Decomposition failed: %s. Using original question.", e)
        sub_queries = [question]

    sub_queries = sub_queries[:3]
    logger.info("[AGENT_DEBUG] decompose_query: is_complex=%s | sub_queries=%s", len(sub_queries) > 1, sub_queries)
    return {
        "sub_queries": sub_queries,
        "trace": state.get("trace", []) + [f"Decomposed into {len(sub_queries)} queries: {sub_queries}"]
    }


def retrieve_node(state: AgentState) -> Dict[str, Any]:
    """
    Retrieve documents for each sub-query using hybrid search / reranker,
    merge and deduplicate, keeping top 6 by rerank_score.
    """
    sub_queries = state.get("sub_queries") or [state["question"]]
    user_id = state["user_id"]
    document_ids = state.get("document_ids")

    logger.info("Node: retrieve for sub_queries: %s | user_id: %s | doc_ids: %s", sub_queries, user_id, document_ids)
    mode = "hybrid_rerank" if settings.use_reranker else ("hybrid" if settings.use_hybrid else "mmr")

    all_docs: List[Document] = []
    seen_keys = set()

    for q in sub_queries:
        docs = retrieve(query=q, user_id=user_id, document_ids=document_ids, mode=mode)
        for doc in docs:
            doc_id = doc.metadata.get("document_id", "")
            chunk_id = doc.metadata.get("chunk_id", "")
            key = f"{doc_id}_{chunk_id}" if doc_id and chunk_id != "" else hash(doc.page_content)
            if key not in seen_keys:
                seen_keys.add(key)
                all_docs.append(doc)

    all_docs.sort(
        key=lambda d: d.metadata.get("rerank_score", d.metadata.get("rrf_score", 0.0)),
        reverse=True
    )
    top_docs = all_docs[:6]
    logger.info("[AGENT_DEBUG] retrieve_node: retrieved %d chunks (top 6 kept)", len(top_docs))

    return {
        "documents": top_docs,
        "sources": extract_sources(top_docs),
        "trace": state.get("trace", []) + [f"Retrieved {len(top_docs)} document chunks"]
    }


def grade_documents_node(state: AgentState) -> Dict[str, Any]:
    """
    LLM strictly evaluates whether retrieved chunks contain relevant information to answer the question.
    """
    logger.info("Node: grade_documents")
    docs = state.get("documents", [])
    if not docs:
        logger.info("[AGENT_DEBUG] grade_documents: No documents retrieved -> NO")
        return {
            "relevance": "no",
            "trace": state.get("trace", []) + ["Grading: No documents found (NO)"]
        }

    context = build_context(docs)
    grader_llm = model.with_structured_output(DocumentGrade)
    system_prompt = (
        "You are a strict, objective document relevance grader.\n"
        "Assess whether the retrieved document context contains substantive, factual information that directly answers or helps answer the user's question.\n\n"
        "Grading Rubric:\n"
        "- Grade 'yes' ONLY if the context explicitly mentions or explains the specific concept, entity, or topic queried.\n"
        "- Grade 'no' if the context is unrelated, or if it merely shares generic terminology without addressing the user's inquiry.\n"
        "- For example, if the question asks 'what is BM25?' and the context discusses LSTM or CNN models without explaining or defining BM25, you MUST grade 'no'."
    )
    try:
        grade = grader_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Question: {state['question']}\n\nContext:\n{context}")
        ])
        relevance = grade.relevance
        explanation = grade.explanation
    except Exception as e:
        logger.error("Grading failed: %s. Defaulting to 'no'.", e)
        relevance = "no"
        explanation = "Grading failed, defaulting to 'no' for safety"

    logger.info(
        "[AGENT_DEBUG] grade_documents: relevance='%s' | explanation='%s' | chunks_count=%d",
        relevance, explanation, len(docs)
    )

    return {
        "relevance": relevance,
        "trace": state.get("trace", []) + [f"Grading: Relevant = {relevance.upper()} ({explanation})"]
    }


def rewrite_query_node(state: AgentState) -> Dict[str, Any]:
    """
    Rewrite the query to improve retrieval, expanding acronyms and synonyms.
    """
    count = state.get("rewrite_count", 0) + 1
    current_q = state.get("current_query") or state["question"]
    logger.info("Node: rewrite_query (attempt %s)", count)

    rewrite_llm = model.with_structured_output(QueryRewrite)
    system_prompt = (
        "You are an expert search query optimizer. The previous query failed to retrieve relevant documents.\n"
        "Rewrite the query to be clearer, expand acronyms, add domain synonyms, and remove conversational phrasing."
    )
    try:
        res = rewrite_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Original Question: {state['question']}\nFailed Query: {current_q}")
        ])
        rewritten = res.rewritten_query
    except Exception as e:
        logger.error("Rewriting failed: %s", e)
        rewritten = current_q

    logger.info(
        "[AGENT_DEBUG] rewrite_query: attempt=%d | original='%s' | rewritten='%s'",
        count, state["question"], rewritten
    )

    return {
        "current_query": rewritten,
        "sub_queries": [rewritten],
        "rewrite_count": count,
        "trace": state.get("trace", []) + [f"Rewritten query (Attempt {count}): '{rewritten}'"]
    }


def generate_node(state: AgentState) -> Dict[str, Any]:
    """
    Generate answer using RAG prompt for uploaded documents, or external RAG prompt for arXiv/Wikipedia.
    If no information was found in documents or external tools, return strict refusal without hallucination.
    """
    logger.info("Node: generate")
    docs = state.get("documents", [])
    ext_context = (state.get("external_context") or "").strip()
    history_text = build_history(state.get("chat_history", []))

    # Case 1: Answering from uploaded documents
    if docs:
        context_str = build_context(docs)
        sources = extract_sources(docs)
        rag_chain = rag_prompt | model | StrOutputParser()
        try:
            answer = rag_chain.invoke({
                "history": history_text,
                "context": context_str,
                "question": state["question"],
            })
        except Exception as e:
            logger.error("Generation failed: %s", e)
            answer = "I encountered an error generating the answer. Please try again."

    # Case 2: Answering from external context (Wikipedia / arXiv)
    elif ext_context and not ext_context.startswith("No relevant"):
        context_str = ext_context
        sources = state.get("sources", [])
        ext_chain = external_rag_prompt | model | StrOutputParser()
        try:
            answer = ext_chain.invoke({
                "history": history_text,
                "context": context_str,
                "question": state["question"],
            })
        except Exception as e:
            logger.error("External generation failed: %s", e)
            answer = "I encountered an error generating the external answer. Please try again."

    # Case 3: Both document retrieval and external tools found nothing
    else:
        logger.info("[AGENT_DEBUG] generate_node: No information available from documents or external tools -> strict refusal.")
        answer = "This isn't covered in your documents."
        sources = []

    logger.info("[AGENT_DEBUG] generate_node completed: answer_length=%d | sources_count=%d", len(answer), len(sources))

    return {
        "answer": answer,
        "sources": sources,
        "trace": state.get("trace", []) + ["Generated initial answer"]
    }


def grounding_check_node(state: AgentState) -> Dict[str, Any]:
    """
    Verify whether every claim in the answer is supported by the context.
    """
    logger.info("Node: grounding_check")
    docs = state.get("documents", [])
    context_str = build_context(docs) if docs else (state.get("external_context") or "").strip()
    answer_text = state.get("answer", "")

    # Skip grounding check for refusals or empty contexts
    if not context_str or "isn't covered in your documents" in answer_text.lower() or "couldn't find that information" in answer_text.lower():
        logger.info("[AGENT_DEBUG] grounding_check: Skipped for refusal/empty context")
        return {
            "grounded": True,
            "trace": state.get("trace", []) + ["Grounding check passed (Refusal or no context)"]
        }

    checker_llm = model.with_structured_output(GroundingCheck)
    system_prompt = (
        "You are an auditor verifying factual consistency.\n"
        "Check if every statement in the generated answer is supported by the context.\n"
        "If there are hallucinated facts or ungrounded assertions, set grounded=False and list the unsupported claims."
    )
    try:
        check = checker_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Context:\n{context_str}\n\nAnswer:\n{answer_text}")
        ])
        is_grounded = check.grounded
        claims = check.unsupported_claims
    except Exception as e:
        logger.error("Grounding check failed: %s. Assuming grounded.", e)
        is_grounded = True
        claims = []

    logger.info(
        "[AGENT_DEBUG] grounding_check: is_grounded=%s | unsupported_claims=%s",
        is_grounded, claims
    )

    trace_msg = "Grounding check: PASSED" if is_grounded else f"Grounding check: FAILED ({len(claims)} unsupported claims)"
    return {
        "grounded": is_grounded,
        "trace": state.get("trace", []) + [trace_msg]
    }


def regenerate_node(state: AgentState) -> Dict[str, Any]:
    """
    Regenerate answer with strict instructions to remove unsupported claims.
    """
    logger.info("Node: regenerate")
    docs = state.get("documents", [])
    context_str = build_context(docs) if docs else (state.get("external_context") or "").strip()
    history_text = build_history(state.get("chat_history", []))

    stricter_prompt = (
        "You are ResearchMind AI. A previous attempt contained ungrounded claims. "
        "Strictly answer the question using ONLY the provided context below. "
        "Do NOT invent details. Do not include claims not directly verifiable in the context.\n\n"
        f"Context:\n{context_str}\n\n"
        f"History:\n{history_text}\n\n"
        f"Question: {state['question']}\n\n"
        "Provide a concise, factual, grounded answer:"
    )

    try:
        response = model.invoke(stricter_prompt)
        answer = response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        logger.error("Regeneration failed: %s", e)
        answer = state.get("answer", "")

    count = state.get("regenerate_count", 0) + 1
    logger.info("[AGENT_DEBUG] regenerate_node completed: attempt=%d", count)

    return {
        "answer": answer,
        "regenerate_count": count,
        "grounded": True,
        "trace": state.get("trace", []) + ["Regenerated grounded answer"]
    }


def fallback_node(state: AgentState) -> Dict[str, Any]:
    """
    Fallback after query rewrites are exhausted:
    Route to arXiv if question is research/academic-paper-seeking, otherwise Wikipedia.
    """
    logger.info("Node: fallback_node")
    q = state["question"].lower()
    is_research = any(w in q for w in ["paper", "study", "arxiv", "literature", "publication", "proceedings", "conference", "journal"])

    route = "arxiv" if is_research else "wikipedia"
    logger.info(
        "[AGENT_DEBUG] fallback_node: routing to %s for question '%s' (rewrite_count=%d)",
        route, state["question"], state.get("rewrite_count", 0)
    )
    return {
        "route": route,
        "trace": state.get("trace", []) + [f"Fallback: Routing to {route.upper()} (document search exhausted)"]
    }
