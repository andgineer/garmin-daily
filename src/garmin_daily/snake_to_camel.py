import re


def snake_to_camel(snake_case_name: str) -> str:
    """Convert snake_case_names to camelCase."""
    words = snake_case_name.split("_")
    return words[0].lower() + "".join(word.title() for word in words[1:])


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
