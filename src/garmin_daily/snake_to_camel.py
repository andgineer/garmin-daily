"""Convert names from Python (snake-name) to Java (camelName) name convention and vice-versa."""

import re


def snake_to_camel(snake_case_name: str) -> str:
    """Convert snake_case_names to camelCase."""
    words = snake_case_name.split("_")
    return words[0].lower() + "".join(word.title() for word in words[1:])


def capitalize_words(name: str) -> str:
    """Capitalize words in a string.

    Replace underscores with spaces and capitalize each word.
    Split on both spaces and underscores.

    name: Input string with words separated by spaces and/or underscores

    Returns: String with capitalized words separated by spaces

    >>> capitalize_words("hello_world")
    'Hello World'
    >>> capitalize_words("hello world")
    'Hello World'
    >>> capitalize_words("hello_world example_string")
    'Hello World Example String'
    """
    # First replace underscores with spaces, then split on spaces
    words = name.replace("_", " ").split()
    return " ".join(word.capitalize() for word in words)


def camel_to_upper_snake(name: str) -> str:
    """Convert camelCase to UPPER_SNAKE_CASE.

    >>> camel_to_upper_snake('camel2_camel2_case')
    'CAMEL2_CAMEL2_CASE'

    >>> camel_to_upper_snake('getHTTPResponseCode')
    'GET_HTTP_RESPONSE_CODE'

    >>> camel_to_upper_snake('HTTPResponseCodeXYZ')
    'HTTP_RESPONSE_CODE_XYZ'

    """
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).upper()


if __name__ == "__main__":  # pragma: no cover
    import doctest

    doctest.testmod()
