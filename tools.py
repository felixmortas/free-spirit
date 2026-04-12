import os

from langchain.tools import tool

from ingestion.vectordb import RedisVectorDB
from ingestion.embedder import MistralEmbedder

# ==================== INITIALIZATION ====================

_embedder = MistralEmbedder(api_key=os.environ["MISTRAL_API_KEY"])
_vectordb = RedisVectorDB()

TOP_K = 3  # number of chunks retrieved

# ==================== RAG TOOL =====================

@tool
def search_knowledge_base(query: str) -> str:
    """
    Search for information in the hostel's knowledge base.
    Use this feature to answer questions about services,
    policies, amenities, rates, or any other internal information.

    Args:
        query: The question or topic to research.

    Returns:
        The most relevant excerpts found in the database.
    """
    # 1. Embedding de la requête
    query_vector = _embedder.embed([query])[0]

    # 2. Recherche vectorielle dans Redis
    results = _vectordb.search(query_vector=query_vector, top_k=TOP_K)

    # 3. Filtrage optionnel par score minimum
    MIN_SCORE = 0.5
    relevant = [r for r in results if r["score"] >= MIN_SCORE]

    if not relevant:
        return "No relevant information was found in the knowledge base."

    # 4. Construction du contexte pour le LLM
    chunks = "\n\n---\n\n".join(
        f"[Excerpt {i+1} — score: {r['score']}]\n{r['content']}"
        for i, r in enumerate(relevant)
    )

    return f"Information found in the knowledge base:\n\n{chunks}"


def get_tools() -> list:
    return [
        search_knowledge_base,
    ]