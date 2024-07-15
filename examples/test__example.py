"""
The `test__example` module contains example tests for a Python project.

For guidelines on writing good tests, see the contributor guide.
"""

import pytest


@pytest.fixture()
def example_data() -> list[int]:
    """
    Fixture that returns a list of integers for testing.

    Returns
    -------
    list[int]
        A list of integers.
    """
    return [1, 2, 3, 4, 5]


def test__addition() -> None:
    """
    Example of a basic test case.

    Asserts
    -------
    - 1 + 1 is equal to 2.
    """
    assert 1 + 1 == 2


def test__sum_with_fixture(example_data: list[int]) -> None:
    """
    Example of a test case that uses a fixture.

    Parameters
    ----------
    example_data: list[int]
        A list of integers.

    Asserts
    -------
    - The sum of the example data is 15.
    """
    assert sum(example_data) == 15


@pytest.mark.parametrize(
    ("input_data", "expected_output"),
    [
        ([1, 2, 3], 6),
        ([4, 5, 6], 15),
        ([], 0),
    ],
)
def test__sum_with_parameterization(
    input_data: list[int],
    expected_output: int,
) -> None:
    """
    Example of a parameterized test case.

    Parameters
    ----------
    input_data: list[int]
        A list of integers to sum.
    expected_output: int
        The expected sum of the input list.

    Asserts
    -------
    - The sum of the input data is equal to the expected output.
    """
    assert sum(input_data) == expected_output
