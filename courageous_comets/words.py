from collections import Counter

import contractions
from nltk.stem.snowball import SnowballStemmer, stopwords
from nltk.tokenize import word_tokenize


def tokenize_sentence(sentence: str) -> list[str]:
    """
    Split a sentence into tokens.

    The tokenizer applies the following steps:

    - Expand contractions.
    - Break the sentence into words.
    - Stem the words.
    - Remove stopwords and words with a length of 1.

    Parameters
    ----------
    sentence : str
        The sentence to tokenize.

    Returns
    -------
    list[str]
        The tokens derived from the sentence.

    Notes
    -----
    The tokenizer is intended to be used with English text.
    """
    # Expand contractions
    expanded = contractions.fix(sentence)

    # Break the sentence into words
    words = word_tokenize(expanded)

    # Stem the words
    stemmer = SnowballStemmer("english")
    stemmed_words = [stemmer.stem(word) for word in words]

    # Remove stopwords and words with a length of 1
    stop_words = set(stopwords.words("english"))

    return [word for word in stemmed_words if len(word) > 1 and word not in stop_words]


def word_frequency(words: list[str]) -> dict[str, int]:
    """
    Count the number of times each word appears in the given list of words.

    Parameters
    ----------
    words : list[str]
        The list of words to count the frequency of.

    Returns
    -------
    dict[str, int]
        The frequency of each word in words.
    """
    return Counter(words)
