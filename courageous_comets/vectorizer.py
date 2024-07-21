import asyncio

from redisvl.utils.vectorize.text.huggingface import HFTextVectorizer


class Vectorizer:
    """Convert a chunk of text to vector embedding.

    This class uses the Hugging Face sentence transformer to  create vector
    embeddings.

    Attributes
    ----------
    transformer: huggingface.HFTextVectorizer
        The Hugging Face sentence transformer
    """

    def __init__(self) -> None:
        self.transformer = HFTextVectorizer(
            model="sentence-transformers/all-MiniLM-L6-v2",
        )

    async def embed(self, message: str) -> bytes:
        """Create a vector embedding of message."""
        return await asyncio.to_thread(
            self.transformer.embed,  # pyright: ignore
            message,
            as_buffer=True,
        )
