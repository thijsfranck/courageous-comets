from collections import defaultdict

from nltk.stem.snowball import SnowballStemmer, stopwords
from nltk.tokenize import word_tokenize

STOP_WORDS = set(stopwords.words("english"))


def tokenize_sentence(sentence: str) -> list[str]:
    """Split a sentence into tokens.

    The tokenizer applies stemming to the words that make up the sentence
    using the Snowball stemmer and removes stopwords.
    """
    stemmer = SnowballStemmer("english")
    stemmed_words = [stemmer.stem(token) for token in word_tokenize(sentence)]
    return [word for word in stemmed_words if len(word) > 1 and word not in STOP_WORDS]


def word_frequency(words: list[str]) -> dict[str, int]:
    """Count the number of times each word appears in words."""
    frequency: dict[str, int] = defaultdict(int)
    for word in words:
        frequency[word] += 1
    return frequency
