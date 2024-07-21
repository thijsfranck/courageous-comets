import pytest

from courageous_comets.words import tokenize_sentence, word_frequency


@pytest.mark.parametrize(
    ("sentence", "expected"),
    [
        (
            "The quick brown fox jumps over the lazy dog",
            ["quick", "brown", "fox", "jump", "lazi", "dog"],
        ),
        (
            "Hello, world!",
            ["hello", "world"],
        ),
        (
            "I'm sorry, Dave. I'm afraid I can't do that.",
            ["sorri", "dave", "afraid"],
        ),
        (
            "I've been waiting for you, Obi-Wan. We meet again at last.",
            ["wait", "obi-wan", "meet", "last"],
        ),
        (
            "I don't like sand. It's coarse and rough and irritating and it gets everywhere.",
            ["like", "sand", "coars", "rough", "irrit", "get", "everywher"],
        ),
        (
            "You were the chosen one! It was said that you would destroy the Sith, not join them.",
            ["chosen", "one", "said", "would", "destroy", "sith", "join"],
        ),
        (
            "Bring balance to the Force, not leave it in darkness.",
            ["bring", "balanc", "forc", "leav", "dark"],
        ),
        (
            "I'm gonna wreck it!",
            ["go", "wreck"],
        ),
        (
            "I'm gonna wreck it! I'm gonna wreck it!",
            ["go", "wreck", "go", "wreck"],
        ),
        (
            "",  # Empty string
            [],
        ),
    ],
)
def test__tokenize_sentence(sentence: str, expected: list[str]) -> None:
    """
    Test whether a sentence is tokenized correctly.

    Asserts
    -------
    - Contractions are expanded.
    - The sentence is split into words.
    - Punctuation is removed.
    - The words are stemmed.
    - Stopwords and words with a length of 1 are removed.
    """
    result = tokenize_sentence(sentence)
    assert result == expected


@pytest.mark.parametrize(
    ("words", "expected"),
    [
        (
            ["go", "wreck"],
            {"go": 1, "wreck": 1},
        ),
        (
            ["go", "wreck", "go", "wreck"],
            {"go": 2, "wreck": 2},
        ),
        (
            [],
            {},
        ),
    ],
)
def test__word_frequency(words: list[str], expected: dict[str, int]) -> None:
    """
    Test whether the frequency of words is calculated correctly.

    Asserts
    -------
    - The frequency of each word is counted.
    """
    result = word_frequency(words)
    assert result == expected
