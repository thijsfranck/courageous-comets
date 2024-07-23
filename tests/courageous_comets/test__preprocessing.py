import pytest

from courageous_comets.preprocessing import (
    drop_extra_whitespace,
    drop_links,
    drop_punctuation,
    drop_very_long_words,
)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Hello, world!", "Hello, world!"),
        ("Hello,  world!", "Hello, world!"),
        ("Hello,   world!", "Hello, world!"),
        ("Hello, world! ", "Hello, world!"),
        (" Hello, world! ", "Hello, world!"),
        ("  Hello, world!  ", "Hello, world!"),
        ("   Hello, world!   ", "Hello, world!"),
    ],
)
def test__drop_extra_whitespace(text: str, expected: str) -> None:
    """
    Test whether `drop_extra_whitespace` removes extra whitespace from the given text.

    Asserts
    -------
    - Extra whitespace is removed from the given text.
    - Text without extra whitespace is not modified.
    """
    assert drop_extra_whitespace(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Hello, world!", "Hello, world!"),
        ("Hello, http://world.com!", "Hello, "),
        ("Hello, https://world.com! How are you?", "Hello,  How are you?"),
    ],
)
def test__drop_links(text: str, expected: str) -> None:
    """
    Test whether `drop_links` removes links from the given text.

    Asserts
    -------
    - Links are removed from the given text.
    - Text without links is not modified.
    """
    assert drop_links(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            "Hello, world!",
            "Hello world",
        ),
        (
            "Testing... 1, 2, 3.",
            "Testing 1 2 3",
        ),
        (
            "No punctuation here",
            "No punctuation here",
        ),
        (
            "Special characters: @#&*()",
            "Special characters ",
        ),
        (
            "Mixed punctuation! How's it going?",
            "Mixed punctuation Hows it going",
        ),
        (
            "End with punctuation.",
            "End with punctuation",
        ),
        (
            "Multiple spaces   and punctuation!!!",
            "Multiple spaces   and punctuation",
        ),
        (
            "Punctuation-in-the-middle.",
            "Punctuationinthemiddle",
        ),
        (
            "12345!@#$%",
            "12345",
        ),
        (
            "Quotes 'single' and \"double\"",
            "Quotes single and double",
        ),
    ],
)
def test__drop_punctuation(text: str, expected: str) -> None:
    """
    Test whether `drop_punctuation` removes punctuation from the given text.

    Asserts
    -------
    - Punctuation is removed from the given text.
    - Text without punctuation is not modified.
    """
    assert drop_punctuation(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Hello, world!", "Hello, world!"),
        ("Hello, verylongword!", "Hello, "),
        ("Hello, verylongword! How are you?", "Hello,  How are you?"),
    ],
)
def test__drop_very_long_word(text: str, expected: str) -> None:
    """
    Test whether `drop_very_long_words` removes very long words from the given text.

    Asserts
    -------
    - Very long words are removed from the given text.
    - Text without very long words is not modified.
    """
    assert drop_very_long_words(text, max_length=10) == expected
