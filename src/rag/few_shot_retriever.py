from src.database import get_session, GoldenExample
from src.rag.embeddings import generate_embedding


def retrieve_similar_examples(query: str, top_k: int = 3) -> list[dict]:
    """
    Embeds the input query and retrieves the top_k most similar 
    golden examples from PostgreSQL using pgvector cosine distance.
    """
    query_embedding = generate_embedding(query)
    if not query_embedding:
        return []

    session = get_session()
    try:
        # pgvector provides .cosine_distance() on Vector columns
        results = (
            session.query(GoldenExample)
            .order_by(GoldenExample.embedding.cosine_distance(query_embedding))
            .limit(top_k)
            .all()
        )
        
        return [
            {
                "user_query": ex.user_query,
                "perfect_response": ex.perfect_response,
                "category": ex.category,
            }
            for ex in results
        ]
    finally:
        session.close()


def format_few_shot_examples(examples: list[dict]) -> str:
    """Formats retrieved golden examples into a clean string for prompt injection."""
    if not examples:
        return ""
    
    formatted = ["\n[Reference Examples from Past Perfect Interactions]:"]
    for i, ex in enumerate(examples, 1):
        formatted.append(
            f"Example {i} (Category: {ex['category']}):\n"
            f"Customer: \"{ex['user_query']}\"\n"
            f"Agent Response: \"{ex['perfect_response']}\""
        )
    return "\n\n".join(formatted)


if __name__ == "__main__":
    test_query = "Why did you charge my credit card $50 extra?"
    print(f"Testing retrieval for: '{test_query}'\n")
    similar = retrieve_similar_examples(test_query, top_k=3)
    print(format_few_shot_examples(similar))
