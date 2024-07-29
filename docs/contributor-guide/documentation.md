# Documentation

Good code documentation aids understanding and speeds up the development process. Follow the guidelines below
to document your code effectively.

## What to Document

Always document the following elements of your code:

1. **Classes**, including their **attributes and public methods**
2. **Module-level functions and constants**

Prioritize documenting public methods and attributes (those not starting with an underscore). However, private
methods with complex logic should also be documented for clarity.

## Docstring Format

This project uses numpy-style docstrings. Refer to the [style guide](https://numpydoc.readthedocs.io/en/latest/format.html)
for the full specification and detailed examples.

Here are some examples of how to write good documentation for functions and classes:

??? EXAMPLE "Function Documentation"

    ```python
    def example_function(param1: int, param2: str):
        """
        One-line summary of the function.

        Detailed functional description of what the function does. Can span
        multiple lines.

        Parameters
        ----------
        param1 : int
            Description of the first parameter.
        param2 : str
            Description of the second parameter.

        Returns
        -------
        bool
            Description of the return value.

        Raises
        ------
        ValueError
            Description of the error.

        Examples
        --------
        >>> example_function(1, "test")
        True
        """
        ...
    ```

??? EXAMPLE "Class Documentation"

    ```python
    class Example:
        """
        Class-level docstring describing the class.

        Attributes
        ----------
        attribute : int
            Description of the attribute.
        """
        ...
    ```

## Type Annotations

Python type annotations are strongly encouraged to improve code readability and maintainability. Use type annotations
for all parameters and return values, as well as class attributes.

??? QUESTION "What are type annotations?"

    Type annotations are a way to specify the expected types of variables, function parameters, and return values
    in Python code. They are used to improve code readability and catch type-related errors early. Refer to the
    [official documentation](https://docs.python.org/3/library/typing.html) for more information.
