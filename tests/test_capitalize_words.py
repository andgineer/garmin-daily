import pytest

from garmin_daily.snake_to_camel import capitalize_words


def test_capitalize_words_basic():
    assert capitalize_words("hello") == "Hello"


def test_capitalize_words_with_underscore():
    assert capitalize_words("hello_world") == "Hello World"


def test_capitalize_words_with_space():
    assert capitalize_words("hello world") == "Hello World"


def test_capitalize_words_mixed_separators():
    assert capitalize_words("hello_world test string") == "Hello World Test String"
    assert capitalize_words("hello world_test_string") == "Hello World Test String"


def test_capitalize_words_multiple_consecutive_separators():
    assert capitalize_words("hello__world") == "Hello World"
    assert capitalize_words("hello  world") == "Hello World"
    assert capitalize_words("hello _ world") == "Hello World"


def test_capitalize_words_empty_string():
    assert capitalize_words("") == ""


def test_capitalize_words_single_character():
    assert capitalize_words("a") == "A"


def test_capitalize_words_already_capitalized():
    assert capitalize_words("Hello_World") == "Hello World"


def test_capitalize_words_with_numbers():
    assert capitalize_words("hello_world_123") == "Hello World 123"
    assert capitalize_words("123_hello_world") == "123 Hello World"


def test_capitalize_words_with_special_characters():
    assert capitalize_words("hello!_world") == "Hello! World"
    assert capitalize_words("hello_@_world") == "Hello @ World"


def test_capitalize_words_leading_trailing_spaces():
    assert capitalize_words("  hello_world  ") == "Hello World"


def test_capitalize_words_non_string_input():
    with pytest.raises(AttributeError):
        capitalize_words(None)
    with pytest.raises(AttributeError):
        capitalize_words(123)
