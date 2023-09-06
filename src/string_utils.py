import base64
import csv
import json
import re
import string
from typing import Dict, List, Optional, Set, Union

from src.enum_hatchery import CurrencyType

# =========================================================================== #

VOWELS = "aeiou"
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
URL_PATTERN = (r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),'
               r']|(?:%[0-9a-fA-F][0-9a-fA-F]))+')


def remove_punctuation(input_str: str) -> str:
    """
    Remove punctuation from a given string.

    Args:
        input_str (str): The string from which to remove punctuation.

    Raises:
        ValueError: If the input string is None.

    Returns:
        str: The input string with all punctuation characters removed.
    """
    if input_str is None:
        raise ValueError("Input string cannot be None.")

    translator = str.maketrans('', '', string.punctuation)
    return input_str.translate(translator)


def normalize_whitespace(input_str: str) -> str:
    """
    Normalize the whitespace in a given string.

    Args:
        input_str (str): The string in which to normalize whitespace.

    Raises:
        ValueError: If the input string is None.

    Returns:
        str: The input string with normalized whitespace.
    """
    if input_str is None:
        raise ValueError("Input string cannot be None.")

    return ' '.join(input_str.split())


def word_count(input_str: str) -> int:
    """
    Count the number of words in a given string.

    Args:
        input_str (str): The string in which to count words.

    Raises:
        ValueError: If the input is not a string.

    Returns:
        int: The number of words in the input string.
    """
    if not isinstance(input_str, str):
        raise ValueError("Input must be a string.")

    return len(input_str.split())


def char_count(
    input_str: str,
    ignore_whitespace: bool = False
) -> int:
    """
    Count the number of characters in a given string.

    Args:
        input_str (str): The string for which to count characters.
        ignore_whitespace (bool, optional): Whether to ignore whitespace
            characters. Defaults to False.

    Raises:
        ValueError: If the input is not a string.

    Returns:
        int: The number of characters in the input string, optionally
        excluding whitespace.
    """
    if not isinstance(input_str, str):
        raise ValueError("Input must be a string.")

    if ignore_whitespace:
        return len(input_str.replace(" ", ""))

    return len(input_str)


def unique_words(input_str: str) -> Set[str]:
    """
    Get the unique words in a given string.

    Args:
        input_str (str): The string from which to extract unique words.

    Raises:
        ValueError: If the input is not a string.

    Returns:
        Set[str]: A set containing the unique words in the input string.
    """
    if not isinstance(input_str, str):
        raise ValueError("Input must be a string.")

    words = input_str.split()
    return set(words)


def unique_chars(
    input_str: str,
    ignore_case: bool = False,
    ignore_whitespace: bool = False
) -> Set[str]:
    """
    Get the unique characters in a given string.

    Args:
        input_str (str): The string from which to extract unique characters.
        ignore_case (bool, optional): Whether to ignore case. Defaults to False.
        ignore_whitespace (bool, optional): Whether to ignore whitespace.
            Defaults to False.

    Raises:
        ValueError: If the input is not a string.

    Returns:
        Set[str]: A set containing the unique characters in the input string.
    """
    if not isinstance(input_str, str):
        raise ValueError("Input must be a string.")

    text = input_str
    if ignore_case:
        text = text.lower()
    if ignore_whitespace:
        text = text.replace(" ", "")
    return set(text)


def reverse_words(input_str: str) -> str:
    """
    Reverse the order of words in a given string.

    Args:
        input_str (str): The string in which to reverse the word order.

    Raises:
        ValueError: If the input string is None.

    Returns:
        str: The input string with the words reversed.
    """
    if input_str is None:
        raise ValueError("Input text cannot be None.")

    words = input_str.split()
    reversed_words = " ".join(reversed(words))
    return reversed_words


def reverse_chars(input_str: str) -> str:
    """
    Reverse the order of characters in a given string.

    Args:
        input_str (str): The string to reverse.

    Raises:
        ValueError: If the input string is None.

    Returns:
        str: The input string with the characters reversed.
    """
    if input_str is None:
        raise ValueError("Input text cannot be None.")

    return input_str[::-1]


def find_substrings(
    main_string: str,
    substr: str
) -> List[int]:
    """
    Find all occurrences of substring in given string and return their indices.

    Args:
        main_string (str): The string in which to find the substring.
        substr (str): The substring to find.

    Raises:
        ValueError: If main_string or substr is None.
        ValueError: If substr is empty.

    Returns:
        List[int]: A list of indices where the substring is found.
    """
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
    """
    Replace all occurrences of substring in a given string with another string.

    Args:
        main_str (str): The string in which to replace the substring.
        substr (str): The substring to replace.
        replacement (str): The string to replace substr with.

    Raises:
        ValueError: If main_str, substr, or replacement is None.
        ValueError: If substr is empty.

    Returns:
        str: The string with all occurrences of substr replaced.
    """
    if main_str is None or substr is None or replacement is None:
        raise ValueError("Main string, substring, and replacement "
                         "cannot be None.")

    if not substr:
        raise ValueError("Substring cannot be empty.")

    return main_str.replace(substr, replacement)


def encode_base64(input_str: str) -> Optional[str]:
    """
    Encode a given string in Base64.

    Args:
        input_str (str): The string to encode.

    Returns:
        Optional[str]: The Base64 encoded string, or None if an error occurs.
    """
    try:
        input_bytes = input_str.encode("utf-8")
        base64_bytes = base64.b64encode(input_bytes)
        base64_str = base64_bytes.decode("utf-8")
        return base64_str
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def decode_base64(input_str: str) -> Optional[str]:
    """
    Decode a given Base64 encoded string.

    Args:
        input_str (str): The Base64 encoded string to decode.

    Returns:
        Optional[str]: The decoded string, or None if an error occurs.
    """
    try:
        base64_bytes = input_str.encode("utf-8")
        decoded_bytes = base64.b64decode(base64_bytes)
        decoded_str = decoded_bytes.decode("utf-8")
        return decoded_str
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def is_base64(input_str: str) -> bool:
    """
    Check if a given string is a valid Base64 encoded string.

    Args:
        input_str (str): The string to check.

    Returns:
        bool: True if the string is a valid Base64 encoded string,
            False otherwise.
    """
    try:
        decode_str = decode_base64(input_str)
        encode_str = encode_base64(decode_str)
        return encode_str == input_str
    except Exception:
        return False


def format_phone_number(
    phone_number: Union[str, int],
    country_code: Optional[str] = None
) -> str:
    """
    Format a phone number into a standardized string representation.

    Args:
        phone_number (Union[str, int]): The phone number to format.
        country_code (Optional[str]): The country code to prepend.
            Defaults to '+1'.

    Raises:
        ValueError: If the phone number is empty, None, or not 10 digits.

    Returns:
        str: The formatted phone number.
    """
    if not phone_number:
        raise ValueError("Phone number cannot be empty or None.")

    digits = re.sub(r'\D', '', phone_number)

    if len(digits) != 10:
        raise ValueError("Invalid phone number. Must be 10 digits.")

    _country_code = (country_code or '+1').strip()
    formatted_number = f"{_country_code} ({digits[-10:-7]}) {digits[-7:-4]}-{digits[-4:]}"
    return formatted_number


def format_currency(
    amount: Union[int, float],
    currency_type: CurrencyType
) -> str:
    """
    Format a monetary amount into a standardized string representation.

    Args:
        amount (Union[int, float]): The monetary amount to format.
        currency_type (CurrencyType): The type of currency for formatting.

    Returns:
        str: The formatted currency amount.
    """
    if amount is None:
        return "Invalid amount"

    currency_info = currency_type.value
    symbol = currency_info['symbol']
    placement = currency_info['placement']
    decimal_places = currency_info['decimal_places']

    formatted_amount = f"{amount:.{decimal_places}f}"

    if placement == 'before':
        return f"{symbol}{formatted_amount}"
    else:
        return f"{formatted_amount}{symbol}"


def levenshtein_distance(
    string1: str,
    string2: str
) -> int:
    """
    Calculate the Levenshtein distance between two strings.

    The Levenshtein distance is a measure of the similarity between two strings.
    The distance is calculated as the number of deletions, insertions, or
    substitutions required to transform string1 into string2.

    Args:
        string1 (str): The first string to compare.
        string2 (str): The second string to compare.

    Raises:
        ValueError: If either of the input strings is None.

    Returns:
        int: The Levenshtein distance between string1 and string2.
    """
    if string1 is None or string2 is None:
        raise ValueError("Input strings cannot be None.")

    m, n = len(string1), len(string2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0:
                dp[i][j] = j
            elif j == 0:
                dp[i][j] = i
            else:
                dp[i][j] = min(
                    dp[i - 1][j] + 1,
                    dp[i][j - 1] + 1,
                    dp[i - 1][j - 1] + (0 if string1[i - 1] == string2[j - 1] else 1)
                )

    return dp[m][n]


def jaccard_similarity(
    string1: Union[str, set],
    string2: Union[str, set]
) -> float:
    """
    Compute the Jaccard similarity between two strings or sets.

    Args:
        string1 (Union[str, set]): The first string or set to compare.
        string2 (Union[str, set]): The second string or set to compare.

    Raises:
        ValueError: If either of the input strings or sets is None.

    Returns:
        float: The Jaccard similarity index between the two strings or sets.
    """
    if string1 is None or string2 is None:
        raise ValueError("Input strings or sets cannot be None.")

    if isinstance(string1, str):
        set1 = set(string1)
    else:
        set1 = string1

    if isinstance(string2, str):
        set2 = set(string2)
    else:
        set2 = string2

    intersection_len = len(set1.intersection(set2))
    union_len = len(set1.union(set2))

    if union_len == 0:
        return 0.0

    return intersection_len / union_len


def is_palindrome(input_str: str) -> bool:
    """
    Check if a given string is a palindrome.

    Args:
        input_str (str): The string to check for palindrome properties.

    Raises:
        ValueError: If the input string is None.

    Returns:
        bool: True if the input string is a palindrome, False otherwise.
    """
    if input_str is None:
        raise ValueError("Input string cannot be None.")

    cleaned_s = ''.join(input_str.split()).lower()
    return cleaned_s == cleaned_s[::-1]


def generate_anagrams(input_str: str) -> List[str]:
    """
    Generate all unique anagrams of a given string.

    Args:
        input_str (str): The string for which to generate anagrams.

    Raises:
        ValueError: If the input string is None.

    Returns:
        List[str]: A list of unique anagrams of the input string.
    """
    from itertools import permutations

    if input_str is None:
        raise ValueError("Input string cannot be None.")

    unique_anagrams = set(permutations(input_str))
    return [''.join(p) for p in unique_anagrams]


def parse_json_string(json_str: str) -> Union[Dict, List]:
    """
    Parse a JSON-formatted string and return a Python object.

    Args:
        json_str (str): The JSON-formatted string to parse.

    Raises:
        ValueError: If the input string is not valid JSON.

    Returns:
        Union[Dict, List]: A Python object representing the parsed JSON.
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON string: {e}")


def parse_csv_string(
    csv_str: str,
    delimiter: str = ','
) -> List[List[str]]:
    """
    Parse a CSV-formatted string and return a list of lists.

    Args:
        csv_str (str): The CSV-formatted string to parse.
        delimiter (str, optional): The delimiter used in the CSV string.
            Defaults to ','.

    Raises:
        ValueError: If the input string is not valid CSV.

    Returns:
        List[List[str]]: A list of lists representing the parsed CSV rows.
    """
    try:
        return list(csv.reader(csv_str.splitlines(), delimiter=delimiter))
    except csv.Error as e:
        raise ValueError(f"Invalid CSV string: {e}")


def reverse_string(input_str: str) -> str:
    """
    Reverse a given string.

    Args:
        input_str (str): The string to reverse.

    Raises:
        ValueError: If the input string is None.

    Returns:
        str: The reversed string.
    """
    if input_str is None:
        raise ValueError("Input string cannot be None.")
    return input_str[::-1]


def count_vowels(input_str: str) -> int:
    """
    Count the number of vowels in a given string.

    Args:
        input_str (str): The string in which to count vowels.

    Raises:
        ValueError: If the input string is None.

    Returns:
        int: The number of vowels in the input string.
    """
    if input_str is None:
        raise ValueError("Input string cannot be None.")
    return sum(1 for char in input_str.lower() if char in VOWELS)


def count_consonants(input_str: str) -> int:
    """
    Count the number of consonants in a given string.

    Args:
        input_str (str): The string in which to count consonants.

    Raises:
        ValueError: If the input string is None.

    Returns:
        int: The number of consonants in the input string.
    """
    if input_str is None:
        raise ValueError("Input string cannot be None.")
    return sum(1 for char in input_str.lower() if char.isalpha() and char not in VOWELS)


def extract_urls(input_str: str) -> List[str]:
    """
    Extract all URLs from a given string using a predefined URL pattern.

    Args:
        input_str (str): The string from which to extract URLs.

    Returns:
        List[str]: A list of URLs found in the input string. Returns an empty list if the input is empty.
    """
    if not input_str:
        return []

    urls = re.findall(URL_PATTERN, input_str)
    return urls


def extract_emails(input_str: str) -> List[str]:
    """
    Extract all email addresses from a given string using a predefined email pattern.

    Args:
        input_str (str): The string from which to extract email addresses.

    Returns:
        List[str]: A list of email addresses found in the input string. Returns an empty list if the input is empty.
    """
    if not input_str:
        return []

    emails = re.findall(EMAIL_PATTERN, input_str)
    return emails
