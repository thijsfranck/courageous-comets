import asyncio

import numpy as np
from sentence_transformers import SentenceTransformer


class Vectorizer:
    """Convert a chunk of text to vector embedding.

    This class uses the Hugging Face sentence transformer to  create vector
    embeddings.

    Attributes
    ----------
    transformer: sentence_transformers.SentenceTransformer
        The sentence transformer
    """

    def __init__(self) -> None:
        self.transformer = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2",
        )

    async def embed(self, message: str) -> bytes:
        """Create a vector embedding of message."""
        embedding = await asyncio.to_thread(
            self.transformer.encode,
            message,
        )
        return embedding.astype(  # pyright: ignore[reportGeneralTypeIssues]
            np.float32,
        ).tobytes()
