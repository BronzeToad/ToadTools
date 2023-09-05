import string
from typing import Set


# =========================================================================== #

def remove_punctuation(input_str: str) -> str:

    if input_str is None:
        raise ValueError("Input string cannot be None.")

    translator = str.maketrans('', '', string.punctuation)
    return input_str.translate(translator)


def normalize_whitespace(input_str: str) -> str:

    if input_str is None:
        raise ValueError("Input string cannot be None.")

    return ' '.join(input_str.split())


def word_count(text: str) -> int:

    if not isinstance(text, str):
        raise ValueError("Input must be a string.")

    return len(text.split())


def char_count(
    text: str,
    ignore_whitespace: bool = False
) -> int:

    if not isinstance(text, str):
        raise ValueError("Input must be a string.")

    if ignore_whitespace:
        return len(text.replace(" ", ""))

    return len(text)


def unique_words(text: str) -> Set[str]:

    if not isinstance(text, str):
        raise ValueError("Input must be a string.")
    words = text.split()
    return set(words)


def unique_chars(
    text: str,
    ignore_case: bool = False,
    ignore_whitespace: bool = False
) -> Set[str]:

    if not isinstance(text, str):
        raise ValueError("Input must be a string.")
    if ignore_case:
        text = text.lower()
    if ignore_whitespace:
        text = text.replace(" ", "")
    return set(text)