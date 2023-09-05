import base64
import string
from typing import List, Optional, Set

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


def word_count(input_str: str) -> int:

    if not isinstance(input_str, str):
        raise ValueError("Input must be a string.")

    return len(input_str.split())


def char_count(
    input_str: str,
    ignore_whitespace: bool = False
) -> int:

    if not isinstance(input_str, str):
        raise ValueError("Input must be a string.")

    if ignore_whitespace:
        return len(input_str.replace(" ", ""))

    return len(input_str)


def unique_words(input_str: str) -> Set[str]:

    if not isinstance(input_str, str):
        raise ValueError("Input must be a string.")
    words = input_str.split()
    return set(words)


def unique_chars(
    input_str: str,
    ignore_case: bool = False,
    ignore_whitespace: bool = False
) -> Set[str]:

    if not isinstance(input_str, str):
        raise ValueError("Input must be a string.")
    text = input_str
    if ignore_case:
        text = text.lower()
    if ignore_whitespace:
        text = text.replace(" ", "")
    return set(text)


def reverse_words(input_str: str) -> str:
    if input_str is None:
        raise ValueError("Input text cannot be None.")

    words = input_str.split()
    reversed_words = " ".join(reversed(words))
    return reversed_words


def reverse_characters(input_str: str) -> str:
    if input_str is None:
        raise ValueError("Input text cannot be None.")

    return input_str[::-1]


def reverse_string(input_str: str) -> str:

    return input_str[::-1]


def find_substrings(
    main_string: str,
    substr: str
) -> List[int]:
    if main_string is None or substr is None:
        raise ValueError("Main string and substring cannot be None.")

    if not substr:
        raise ValueError("Substring cannot be empty.")

    indices = []
    index = main_string.find(substr)
    while index != -1:
        indices.append(index)
        index = main_string.find(substr, index + 1)
    return indices


def replace_substrings(
    main_str: str,
    substr: str,
    replacement: str
) -> str:
    if main_str is None or substr is None or replacement is None:
        raise ValueError("Main string, substring, and replacement cannot be None.")

    if not substr:
        raise ValueError("Substring cannot be empty.")

    return main_str.replace(substr, replacement)


def is_palindrome(input_str: str) -> bool:
    sanitized_str = ''.join(c.lower() for c in input_str if c.isalnum())
    return sanitized_str == sanitized_str[::-1]


def encode_base64(input_str: str) -> Optional[str]:
    try:
        input_bytes = input_str.encode("utf-8")
        base64_bytes = base64.b64encode(input_bytes)
        base64_str = base64_bytes.decode("utf-8")
        return base64_str
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def decode_base64(base64_str: str) -> Optional[str]:
    try:
        base64_bytes = base64_str.encode("utf-8")
        decoded_bytes = base64.b64decode(base64_bytes)
        decoded_str = decoded_bytes.decode("utf-8")
        return decoded_str
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def is_base64(input_str: str) -> bool:
    try:
        decode_str = decode_base64(input_str)
        encode_str = encode_base64(decode_str)
        return encode_str == input_str
    except Exception:
        return False

