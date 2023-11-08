import pytest
import src.string_utils as strutils


# =========================================================================== #

# test remove_punctuation
@pytest.mark.parametrize("input_str, expected", [
    ("Hello, World!", "Hello World"),
    ("No-change", "Nochange"),
    ("", ""),
])
def test_remove_punctuation(input_str, expected):
    assert strutils.remove_punctuation(input_str) == expected

def test_remove_punctuation_invalid_input():
    with pytest.raises(ValueError):
        strutils.remove_punctuation(None)

# test normalize_whitespace
@pytest.mark.parametrize("input_str, expected", [
    (" Hello  World ", "Hello World"),
    ("No change", "No change"),
    ("", ""),
])
def test_normalize_whitespace(input_str, expected):
    assert strutils.normalize_whitespace(input_str) == expected

def test_normalize_whitespace_invalid_input():
    with pytest.raises(ValueError):
        strutils.normalize_whitespace(None)

# test word_count
@pytest.mark.parametrize("input_str, expected", [
    ("Hello World", 2),
    ("One", 1),
    ("", 0),
])
def test_word_count(input_str, expected):
    assert strutils.word_count(input_str) == expected

def test_word_count_invalid_input():
    with pytest.raises(ValueError):
        strutils.word_count(None)

# test char_count
@pytest.mark.parametrize("input_str, ignore_whitespace, expected", [
    ("Hello World", False, 11),
    ("Hello World", True, 10),
    ("One", False, 3),
    ("", False, 0),
])
def test_char_count(input_str, ignore_whitespace, expected):
    assert strutils.char_count(input_str, ignore_whitespace) == expected

# test unique_words
@pytest.mark.parametrize("input_str, expected", [
    ("hello hello world", ["hello", "world"]),
    ("a a b b c c", ["a", "b", "c"]),
    ("", []),
])
def test_unique_words(input_str, expected):
    assert strutils.unique_words(input_str) == expected

# test unique_chars
@pytest.mark.parametrize("input_str, expected", [
    ("hello", ['h', 'e', 'l', 'o']),
    ("aabcc", ['a', 'b', 'c']),
    ("", []),
])
def test_unique_chars(input_str, expected):
    assert strutils.unique_chars(input_str) == expected

# test reverse_words
@pytest.mark.parametrize("input_str, expected", [
    ("hello world", "world hello"),
    ("a b c", "c b a"),
    ("", ""),
])
def test_reverse_words(input_str, expected):
    assert strutils.reverse_words(input_str) == expected

# test reverse_chars
@pytest.mark.parametrize("input_str, expected", [
    ("hello", "olleh"),
    ("abc", "cba"),
    ("", ""),
])
def test_reverse_chars(input_str, expected):
    assert strutils.reverse_chars(input_str) == expected

# test find_substrings
@pytest.mark.parametrize("input_str, substr, expected", [
    ("hello world hello", "hello", [0, 12]),
    ("aabcaabc", "abc", [1, 5]),
    ("", "abc", []),
])
def test_find_substrings(input_str, substr, expected):
    assert strutils.find_substrings(input_str, substr) == expected

# test replace_substrings
@pytest.mark.parametrize("input_str, substr, replacement, expected", [
    ("hello world hello", "hello", "hi", "hi world hi"),
    ("aabcaabc", "abc", "xyz", "axyzaxyz"),
    ("", "abc", "xyz", ""),
])
def test_replace_substrings(input_str, substr, replacement, expected):
    assert strutils.replace_substrings(input_str, substr, replacement) == expected

# test encode_base64
@pytest.mark.parametrize("input_str, expected", [
    ("Hello", "SGVsbG8="),
    ("", ""),
])
def test_encode_base64(input_str, expected):
    assert strutils.encode_base64(input_str) == expected

# test decode_base64
@pytest.mark.parametrize("input_str, expected", [
    ("SGVsbG8=", "Hello"),
    ("", ""),
])
def test_decode_base64(input_str, expected):
    assert strutils.decode_base64(input_str) == expected

# test is_base64
@pytest.mark.parametrize("input_str, expected", [
    ("SGVsbG8=", True),
    ("NotBase64", False),
    ("", False),
])
def test_is_base64(input_str, expected):
    assert strutils.is_base64(input_str) == expected

# test format_phone_number
@pytest.mark.parametrize("input_str, expected", [
    ("1234567890", "(123) 456-7890"),
    ("", ""),
])
def test_format_phone_number(input_str, expected):
    assert strutils.format_phone_number(input_str) == expected

# test format_currency
@pytest.mark.parametrize("amount, currency, expected", [
    (1234.56, "USD", "$1,234.56"),
    (1234, "JPY", "¥1,234"),
])
def test_format_currency(amount, currency, expected):
    assert strutils.format_currency(amount, currency) == expected

# test levenshtein_distance
@pytest.mark.parametrize("str1, str2, expected", [
    ("kitten", "sitting", 3),
    ("flaw", "lawn", 2),
    ("", "", 0),
])
def test_levenshtein_distance(str1, str2, expected):
    assert strutils.levenshtein_distance(str1, str2) == expected

# test jaccard_similarity
@pytest.mark.parametrize("str1, str2, expected", [
    ("apple", "pleas", 0.3),
    ("", "", 1.0),
])
def test_jaccard_similarity(str1, str2, expected):
    assert strutils.jaccard_similarity(str1, str2) == pytest.approx(expected, 0.1)

# test is_palindrome
@pytest.mark.parametrize("input_str, expected", [
    ("racecar", True),
    ("hello", False),
    ("", True),  # Empty string is a palindrome
])
def test_is_palindrome(input_str, expected):
    assert strutils.is_palindrome(input_str) == expected

# test generate_anagrams
@pytest.mark.parametrize("input_str, expected", [
    ("abc", ["abc", "acb", "bac", "bca", "cab", "cba"]),
    ("aab", ["aab", "aba", "aab", "aba", "baa", "baa"]),  # Duplicates are possible
    ("", [""]),  # Single empty string as the anagram
])
def test_generate_anagrams(input_str, expected):
    assert set(strutils.generate_anagrams(input_str)) == set(expected)

# test parse_json_string
@pytest.mark.parametrize("input_str, expected", [
    ('{"key": "value"}', {"key": "value"}),
    ('{"boolean": true}', {"boolean": True}),
    ('[]', []),
])
def test_parse_json_string(input_str, expected):
    assert strutils.parse_json_string(input_str) == expected

# test parse_csv_string
@pytest.mark.parametrize("input_str, expected", [
    ("a,b,c\n1,2,3", [["a", "b", "c"], ["1", "2", "3"]]),
    ("name,age\nAlice,30", [["name", "age"], ["Alice", "30"]]),
    ("", []),
])
def test_parse_csv_string(input_str, expected):
    assert strutils.parse_csv_string(input_str) == expected

def test_parse_csv_string_invalid_input():
    with pytest.raises(ValueError):
        strutils.parse_csv_string(None)

# test reverse_string
@pytest.mark.parametrize("input_str, expected", [
    ("Hello", "olleH"),
    ("World", "dlroW"),
    ("", ""),
])
def test_reverse_string(input_str, expected):
    assert strutils.reverse_string(input_str) == expected

# test count_vowels
@pytest.mark.parametrize("input_str, expected", [
    ("Hello", 2),
    ("World", 1),
    ("", 0),
])
def test_count_vowels(input_str, expected):
    assert strutils.count_vowels(input_str) == expected

# test count_consonants
@pytest.mark.parametrize("input_str, expected", [
    ("Hello", 3),
    ("World", 3),
    ("", 0),
])
def test_count_consonants(input_str, expected):
    assert strutils.count_consonants(input_str) == expected

# test extract_urls
@pytest.mark.parametrize("input_str, expected", [
    ("Visit https://example.com", ["https://example.com"]),
    ("No URL here", []),
    ("", []),
])
def test_extract_urls(input_str, expected):
    assert strutils.extract_urls(input_str) == expected

# test extract_emails
@pytest.mark.parametrize("input_str, expected", [
    ("Email me at email@example.com", ["email@example.com"]),
    ("No email here", []),
    ("", []),
])
def test_extract_emails(input_str, expected):
    assert strutils.extract_emails(input_str) == expected
