from src.client import openrouter_client

def generate_embedding(text: str) -> list[float]:
    """Generates embeddings for a given text using OpenRouter API."""
    try:
        embedding = openrouter_client.embeddings.create(
            input=text,
            model="text-embedding-3-small",
            dimensions=1536,
        )
        return embedding.data[0].embedding
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return []
