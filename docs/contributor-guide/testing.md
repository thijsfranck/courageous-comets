# Testing

Automated tests are key to our success, since they allow us to catch bugs early, run sections of code in isolation,
and accelerate our development pace.

## Structure

Test modules should be located in the `tests` directory at the root of the project. The `tests` directory is further
divided into subdirectories for unit tests and integration tests. Each unit tests module should have a corresponding
module in the `courageous_comets` package.

??? EXAMPLE "Test Module Structure"

    ```plaintext
    project_root/
    ├── courageous_comets/
    │   ├── __init__.py
    │   └── example.py
    ├── tests/
    |   ├── conftest.py
    │   ├── courageous_comets/
    │   │   ├── __init__.py
    │   │   └── test__example.py
    │   └── integrations/
    │       ├── __init__.py
    │       └── test__integration.py
    └── ...
    ```

## Running Tests

We use the [`pytest`](https://docs.pytest.org) framework for writing and running our tests. To run the tests,
use the following command from the root of the project:

```bash
poetry run pytest
```

This command will discover and run all the tests modules that match the pattern `test__*.py`.

??? TIP "Running Tests in your IDE"

    Most modern IDEs have built-in support for running tests. You can run tests directly from your IDE, which
    can be more convenient than running them from the command line.

    - [Visual Studio Code](https://code.visualstudio.com/docs/python/testing)
    - [PyCharm](https://www.jetbrains.com/help/pycharm/pytest.html)

    The development container is pre-configured for using `pytest` in Visual Studio Code.

## What to Test

Unit tests should cover the following aspects of your code:

- Input validation
- Correctness of output (or outcome) given a valid input
- Error handling

??? TIP "Consider Edge Cases"

    When writing tests, consider edge cases such as invalid inputs and unexpected behavior. These are often the
    areas where bugs are most likely to occur.

Some parts of the code may be more critical than others. Focus on writing tests for the most critical parts of
the codebase, such as complex algorithms, core functionality or user-facing features.

## Writing Tests

Each test case should be self-contained and independent of other tests. This means that each test should set up
its own data and clean up after itself. Avoid relying on the state of other tests or the order in which tests
are run.

When writing tests, follow these guidelines:

- Use descriptive test names that clearly indicate what is being tested.
- Limit each test to a single logical concept.
- Use the `assert` statement to check the expected outcome of the test.
- Aim for one `assert` statement per test.
- Use [fixtures](https://docs.pytest.org/en/latest/explanation/fixtures.html) to set up common data or resources.

??? EXAMPLE "Example Tests"

    The `examples` folder includes sample tests that you can use as a base for your own test.

## Unit Testing and Type Annotations

You can reduce the need for unit tests by indicating the expected types of input arguments and return values as
type annotations. While they don't replace unit tests, type annotations can reduce the number of tests you might
need to write, particularly those related to input validation.

For instance, consider the following function without type annotations:

???+ EXAMPLE "Function Without Type Annotations"

    ```python
    def add(a, b):
        return a + b
    ```

Without type annotations, you might write multiple tests to ensure that the function behaves correctly with different
types of input, like strings, integers, or floats. But with type annotations:

???+ EXAMPLE "Function With Type Annotations"

    ```python
    def add(a: int, b: int) -> int:
        return a + b
    ```

The function's expected behavior is clearer. You know that both `a` and `b` should be integers, and the return
value will also be an integer. With these type annotations in place, there's less need to write unit tests checking
for behaviors with non-integer inputs since the static type checker can catch those mistakes for you.
