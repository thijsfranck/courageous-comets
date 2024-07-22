import asyncio

import numpy as np
import torch
import torch.nn.functional as torch_nn_functional
from torch import Tensor
from transformers import AutoModel, AutoTokenizer

from courageous_comets import settings


class Vectorizer:
    """Convert a chunk of text to vector embedding.

    This class uses the Hugging Face sentence transformer to  create vector
    embeddings.

    Attributes
    ----------
    TRANSFORMER_MODEL: str
        The name of the model for training the transformer
    tokenizer: transformers.AutoTokenizer
        The Hugging Face sentence tokenizer
    model: transformers.AutoModel
        The sentence transformer
    """

    TRANSFORMER_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(self) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(
            Vectorizer.TRANSFORMER_MODEL_NAME,
            cache_dir=settings.HF_HOME,
        )
        self.model = AutoModel.from_pretrained(
            Vectorizer.TRANSFORMER_MODEL_NAME,
            cache_dir=settings.HF_HOME,
        )

    def encode(self, message: str) -> bytes:
        """
        Create vector embedding of a message.

        The encoder applies the follwowing steps:

        - Tokenize sentences
        - Compute token embeddings
        - Perform pooling taking into account the attention mask
        - Normalize embeddings using torch.nn.functional

        Adapted from: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2#usage-huggingface-transformers

        Parameters
        ----------
        message: str
            The message to generate vector embeddings

        Returns
        -------
        bytes
            The vector embeddings of the message
        """

        # Mean Pooling - Take attention mask into account for correct averaging
        def mean_pooling(model_output: list[Tensor], attention_mask: Tensor) -> Tensor:
            token_embeddings = model_output[
                0
            ]  # First element of model_output contains all token embeddings
            input_mask_expanded = (
                attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
            )
            return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
                input_mask_expanded.sum(1),
                min=1e-9,
            )

        # Tokenize sentences
        encoded_input = self.tokenizer(
            [message],
            padding=True,
            truncation=True,
            return_tensors="pt",
        )

        # Compute token embeddings
        with torch.no_grad():
            model_output = self.model(**encoded_input)

        # Perform pooling
        sentence_embeddings = mean_pooling(
            model_output,
            encoded_input["attention_mask"],
        )

        # Normalize embeddings
        return (
            torch_nn_functional.normalize(sentence_embeddings, p=2, dim=1)
            .numpy()
            .astype(np.float32)
            .tobytes()
        )

    async def aencode(self, message: str) -> bytes:
        """Create a vector embedding of message asynchronously."""
        return await asyncio.to_thread(self.encode, message)
