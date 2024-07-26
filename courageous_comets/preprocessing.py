import re
import string
from collections.abc import Callable
from functools import partial

import contractions
from unidecode import unidecode

from courageous_comets import settings

Processor = Callable[[str], str]


def drop_code_blocks(text: str) -> str:
    """
    Remove code blocks from the given text.

    Parameters
    ----------
    text : str
        The text to process.

    Returns
    -------
    str
        The text with code blocks removed.
    """
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def drop_extra_whitespace(text: str) -> str:
    """
    Remove extra whitespace from the given text.

    Parameters
    ----------
    text : str
        The text to process.

    Returns
    -------
    str
        The text with extra whitespace removed.
    """
    return re.sub(r"\s+", " ", text.strip())


def drop_links(text: str) -> str:
    """
    Remove links from the given text.

    Parameters
    ----------
    text : str
        The text to process.

    Returns
    -------
    str
        The text with links removed.
    """
    return re.sub(r"http\S+", "", text)


def drop_punctuation(text: str) -> str:
    """
    Remove punctuation from the given text.

    Parameters
    ----------
    text : str
        The text to process.

    Returns
    -------
    str
        The text without punctuation.
    """
    return text.translate(str.maketrans("", "", string.punctuation))


def drop_very_long_words(text: str, max_length: int) -> str:
    """
    Remove very long words from the given text.

    Parameters
    ----------
    text : str
        The text to process.
    max_length : int
        The maximum length of a word to keep.

    Returns
    -------
    str
        The text with very long words removed.
    """
    return re.sub(r"\S{%d,}" % max_length, "", text)


def truncate(text: str, max_length: int) -> str:
    """
    Truncate the given text to the specified length.

    Parameters
    ----------
    text : str
        The text to truncate.
    max_length : int
        The maximum length of the text.

    Returns
    -------
    str
        The truncated text.
    """
    return text[:max_length]


# Steps are executed in order
PROCESSORS: list[Processor] = [
    drop_code_blocks,
    drop_links,
    unidecode,
    contractions.fix,  # type: ignore
    drop_punctuation,
    partial(drop_very_long_words, max_length=settings.PREPROCESSING_MAX_WORD_LENGTH),
    drop_extra_whitespace,
    partial(truncate, max_length=settings.PREPROCESSING_MESSAGE_TRUNCATE_LENGTH),
]


def process(text: str, processors: list[Processor] = PROCESSORS) -> str:
    """
    Process the text using all available processors.

    Parameters
    ----------
    text : str
        The text to process.
    processors : list[Processor], optional
        The processors to use, by default uses a predefined set of processors.

    Returns
    -------
    str
        The processed text.
    """
    result = text

    for processor in processors:
        text = processor(result)

    return result
