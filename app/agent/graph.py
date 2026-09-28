import logging
from typing import Any, Dict, Literal
from langgraph.graph import END, START, StateGraph

from app.agent.nodes import (
    arxiv_node,
    decompose_query_node,
    fallback_node,
    generate_direct_node,
    generate_node,
    grade_documents_node,
    grounding_check_node,
    regenerate_node,
    retrieve_node,
    rewrite_query_node,
    route_query_node,
    wikipedia_node,
)
from app.agent.state import AgentState

logger = logging.getLogger(__name__)


# ==========================================
# Conditional Routing Functions
# ==========================================

def route_branch(state: AgentState) -> Literal["generate_direct", "arxiv", "wikipedia", "decompose_query"]:
    """
    Branch from route_query based on state['route'].
    """
    route = state.get("route", "pdf_rag")
    if route == "direct":
        return "generate_direct"
    elif route == "arxiv":
        return "arxiv"
    elif route == "wikipedia":
        return "wikipedia"
    return "decompose_query"


def grade_branch(state: AgentState) -> Literal["generate", "rewrite_query", "fallback"]:
    """
    Branch from grade_documents:
    - If relevant -> generate
    - If not relevant and rewrite_count < 2 -> rewrite_query
    - If not relevant and rewrite_count >= 2 -> fallback
    """
    if state.get("relevance") == "yes":
        return "generate"
    if state.get("rewrite_count", 0) < 2:
        return "rewrite_query"
    return "fallback"


def fallback_branch(state: AgentState) -> Literal["arxiv", "wikipedia"]:
    """
    Branch from fallback node to either arXiv or Wikipedia.
    """
    if state.get("route") == "arxiv":
        return "arxiv"
    return "wikipedia"


def grounding_branch(state: AgentState) -> Literal["end", "regenerate", "caveat"]:
    """
    Branch from grounding_check:
    - If grounded -> END
    - If not grounded and regenerate_count < 1 -> regenerate
    - Otherwise -> append caveat -> END
    """
    if state.get("grounded", True):
        return "end"
    if state.get("regenerate_count", 0) < 1:
        return "regenerate"
    return "caveat"


def caveat_node(state: AgentState) -> Dict[str, Any]:
    """
    Append caveat when grounding cannot be fully verified after regeneration.
    """
    answer = state.get("answer", "")
    caveat = "\n\n*Note: Some parts of this answer may not be fully supported by the sources.*"
    if caveat not in answer:
        answer = answer + caveat
    return {
        "answer": answer,
        "trace": state.get("trace", []) + ["Appended ungrounded caveat"]
    }


# ==========================================
# Graph Construction
# ==========================================

def build_agent_graph():
    """
    Assemble and compile the LangGraph agent state graph.
    """
    workflow = StateGraph(AgentState)

    # 1. Add Nodes
    workflow.add_node("route_query", route_query_node)
    workflow.add_node("generate_direct", generate_direct_node)
    workflow.add_node("arxiv", arxiv_node)
    workflow.add_node("wikipedia", wikipedia_node)
    workflow.add_node("decompose_query", decompose_query_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("grade_documents", grade_documents_node)
    workflow.add_node("rewrite_query", rewrite_query_node)
    workflow.add_node("fallback", fallback_node)
    workflow.add_node("generate", generate_node)
    workflow.add_node("grounding_check", grounding_check_node)
    workflow.add_node("regenerate", regenerate_node)
    workflow.add_node("caveat", caveat_node)

    # 2. Add Edges
    workflow.add_edge(START, "route_query")

    # Routing conditional edge
    workflow.add_conditional_edges(
        "route_query",
        route_branch,
        {
            "generate_direct": "generate_direct",
            "arxiv": "arxiv",
            "wikipedia": "wikipedia",
            "decompose_query": "decompose_query",
        }
    )

    workflow.add_edge("generate_direct", END)
    workflow.add_edge("arxiv", "generate")
    workflow.add_edge("wikipedia", "generate")

    workflow.add_edge("decompose_query", "retrieve")
    workflow.add_edge("retrieve", "grade_documents")

    # Grade conditional edge
    workflow.add_conditional_edges(
        "grade_documents",
        grade_branch,
        {
            "generate": "generate",
            "rewrite_query": "rewrite_query",
            "fallback": "fallback",
        }
    )

    workflow.add_edge("rewrite_query", "retrieve")

    # Fallback conditional edge
    workflow.add_conditional_edges(
        "fallback",
        fallback_branch,
        {
            "arxiv": "arxiv",
            "wikipedia": "wikipedia",
        }
    )

    # Generate -> Grounding Check
    workflow.add_edge("generate", "grounding_check")

    # Grounding check conditional edge
    workflow.add_conditional_edges(
        "grounding_check",
        grounding_branch,
        {
            "end": END,
            "regenerate": "regenerate",
            "caveat": "caveat",
        }
    )

    workflow.add_edge("regenerate", END)
    workflow.add_edge("caveat", END)

    return workflow.compile()


# Singleton compiled graph
agent_graph = build_agent_graph()

NODE_STATUS_MAP = {
    "route_query": "Routing query",
    "generate_direct": "Generating direct response",
    "decompose_query": "Decomposing query",
    "retrieve": "Retrieving documents",
    "grade_documents": "Grading documents",
    "rewrite_query": "Rewriting query",
    "arxiv": "Searching arXiv literature",
    "wikipedia": "Searching Wikipedia",
    "fallback": "Applying fallback search",
    "generate": "Generating answer",
    "grounding_check": "Verifying factual grounding",
    "regenerate": "Refining answer with strict grounding",
    "caveat": "Finalizing response",
}


def run_agent(
    question: str,
    conversation_id: int,
    user_id: int,
    document_ids: list[str] | str | None = None,
    document_id: str | None = None,
) -> Dict[str, Any]:
    """
    Execute the agent graph synchronously, save conversation, and return answer + sources + trace.
    """
    from app.services.conversation_manager import get_conversation_history, save_conversation

    target_docs = document_ids if document_ids is not None else document_id
    if isinstance(target_docs, str):
        target_docs = [x.strip() for x in target_docs.split(",") if x.strip()]

    history = get_conversation_history(conversation_id)
    state: AgentState = {
        "question": question,
        "chat_history": history,
        "user_id": user_id,
        "document_ids": target_docs,
        "route": "",
        "sub_queries": [],
        "current_query": question,
        "documents": [],
        "relevance": "",
        "rewrite_count": 0,
        "answer": "",
        "grounded": False,
        "regenerate_count": 0,
        "sources": [],
        "external_context": "",
        "trace": [],
    }

    result = agent_graph.invoke(state)
    answer = result.get("answer", "")
    sources = result.get("sources", [])
    trace = result.get("trace", [])

    save_conversation(
        conversation_id=conversation_id,
        question=question,
        answer=answer,
    )

    return {
        "answer": answer,
        "sources": sources,
        "trace": trace,
        "grounded": result.get("grounded", True),
    }


async def stream_agent(
    question: str,
    conversation_id: int,
    user_id: int,
    document_ids: list[str] | str | None = None,
    document_id: str | None = None,
):
    """
    Execute the agent graph as an async stream:
    (1) Emits status events as nodes begin.
    (2) Streams tokens from the final generation node.
    (3) Emits final sources and trace event.
    Saves the completed conversation turn to SQLite.
    """
    import json
    from app.services.conversation_manager import get_conversation_history, save_conversation

    target_docs = document_ids if document_ids is not None else document_id
    if isinstance(target_docs, str):
        target_docs = [x.strip() for x in target_docs.split(",") if x.strip()]

    history = get_conversation_history(conversation_id)
    state: AgentState = {
        "question": question,
        "chat_history": history,
        "user_id": user_id,
        "document_ids": target_docs,
        "route": "",
        "sub_queries": [],
        "current_query": question,
        "documents": [],
        "relevance": "",
        "rewrite_count": 0,
        "answer": "",
        "grounded": False,
        "regenerate_count": 0,
        "sources": [],
        "external_context": "",
        "trace": [],
    }

    seen_nodes = set()
    complete_answer = ""
    sources = []
    trace = []

    try:
        async for event in agent_graph.astream_events(state, version="v2"):
            kind = event.get("event")
            node = event.get("metadata", {}).get("langgraph_node")

            # 1. Node start -> emit status event
            if kind == "on_chain_start" and node and node not in seen_nodes:
                seen_nodes.add(node)
                status_text = NODE_STATUS_MAP.get(node, node.replace("_", " ").title())
                yield json.dumps({"type": "status", "step": status_text}) + "\n"

            # 2. Token from generation nodes
            elif kind == "on_chat_model_stream" and node in ("generate", "generate_direct", "regenerate"):
                chunk_obj = event.get("data", {}).get("chunk")
                chunk_content = getattr(chunk_obj, "content", "")
                if chunk_content:
                    complete_answer += chunk_content
                    yield json.dumps({"type": "token", "content": chunk_content}) + "\n"

            # On chain end, extract final answer, sources, and trace
            elif kind == "on_chain_end" and event.get("name") == "LangGraph":
                final_output = event.get("data", {}).get("output", {})
                if isinstance(final_output, dict):
                    if not complete_answer and final_output.get("answer"):
                        complete_answer = final_output.get("answer")
                    sources = final_output.get("sources", [])
                    trace = final_output.get("trace", [])

    except Exception as e:
        logger.error("Error in stream_agent: %s", e)
        complete_answer = f"Error during agent execution: {e}"
        yield json.dumps({"type": "token", "content": complete_answer}) + "\n"

    # 3. Sources and trace event
    yield json.dumps({"type": "sources", "sources": sources, "trace": trace}) + "\n"

    # Save to SQLite
    try:
        save_conversation(
            conversation_id=conversation_id,
            question=question,
            answer=complete_answer,
        )
    except Exception as db_err:
        logger.error("Failed to save streamed conversation: %s", db_err)
