import logging
from typing import Any, Dict, List
import arxiv
import wikipedia

logger = logging.getLogger(__name__)


def arxiv_tool(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """
    Search arXiv for research papers.
    Returns list of dicts with title, authors, summary, url.
    Wrapped in try/except; returns [] on failure.
    """
    try:
        logger.info("Searching arXiv for query: %s", query)
        client = arxiv.Client(page_size=max_results, delay_seconds=1.0, num_retries=2)
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
        )
        papers: List[Dict[str, Any]] = []
        for result in client.results(search):
            papers.append({
                "title": result.title,
                "authors": [a.name for a in result.authors],
                "summary": result.summary.replace("\n", " "),
                "url": result.entry_id,
            })
        return papers
    except Exception as e:
        logger.error("arXiv tool failed: %s", e)
        return []


def wikipedia_tool(query: str, max_results: int = 2) -> List[Dict[str, Any]]:
    """
    Search Wikipedia for background/definition pages.
    Returns list of dicts with title, summary, url.
    Wrapped in try/except; returns [] on failure.
    """
    try:
        logger.info("Searching Wikipedia for query: %s", query)
        wikipedia.set_lang("en")
        wikipedia.set_user_agent("ResearchMindAI/1.0 (https://github.com/Mohit-25-tech/ResearchMind-AI; researchmind@example.com)")
        search_titles = wikipedia.search(query, results=max_results)
        articles: List[Dict[str, Any]] = []
        for title in search_titles:
            try:
                page = wikipedia.page(title, auto_suggest=False)
                articles.append({
                    "title": page.title,
                    "summary": page.summary[:1500].replace("\n", " "),
                    "url": page.url,
                })
            except wikipedia.exceptions.DisambiguationError as dis_err:
                # Pick the first option from disambiguation
                if dis_err.options:
                    try:
                        first_opt = dis_err.options[0]
                        page = wikipedia.page(first_opt, auto_suggest=False)
                        articles.append({
                            "title": page.title,
                            "summary": page.summary[:1500].replace("\n", " "),
                            "url": page.url,
                        })
                    except Exception:
                        continue
            except Exception as page_err:
                logger.warning("Failed to fetch Wikipedia page '%s': %s", title, page_err)
                continue
        return articles
    except Exception as e:
        logger.error("Wikipedia tool failed: %s", e)
        return []
