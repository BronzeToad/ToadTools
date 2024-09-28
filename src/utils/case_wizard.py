import re
from enum import Enum, auto
from typing import Callable, Dict


class CaseType(Enum):
    """Enumeration of different case types supported by the CaseWizard."""

    CAMEL = auto()
    COBOL = auto()
    KEBAB = auto()
    PASCAL = auto()
    SCREAM = auto()
    SNAKE = auto()
    LOWER = auto()
    UPPER = auto()
    TITLE = auto()
    SPONGEBOB = auto()


def to_camel_case(input_string: str) -> str:
    """Converts a string to CamelCase format.

    Args:
        input_string (str): The string to convert.

    Returns:
        str: The converted CamelCase string.
    """
    words = re.findall(r"\w+", input_string.lower())
    return words[0] + "".join(word.capitalize() for word in words[1:])


def to_cobol_case(input_string: str) -> str:
    """Converts a string to COBOL-CASE format.

    Args:
        input_string (str): The string to convert.

    Returns:
        str: The converted COBOL-CASE string.
    """
    return "-".join(re.findall(r"\w+", input_string.upper()))


def to_kebab_case(input_string: str) -> str:
    """Converts a string to kebab-case format.

    Args:
        input_string (str): The string to convert.

    Returns:
        str: The converted kebab-case string.
    """
    return "-".join(re.findall(r"\w+", input_string.lower()))


def to_pascal_case(input_string: str) -> str:
    """Converts a string to PascalCase format.

    Args:
        input_string (str): The string to convert.

    Returns:
        str: The converted PascalCase string.
    """
    return "".join(
        word.capitalize() for word in re.findall(r"\w+", input_string.lower())
    )


def to_scream_case(input_string: str) -> str:
    """Converts a string to SCREAM_CASE format.

    Args:
        input_string (str): The string to convert.

    Returns:
        str: The converted SCREAM_CASE string.
    """
    return "_".join(re.findall(r"\w+", input_string.upper()))


def to_snake_case(input_string: str) -> str:
    """Converts a string to snake_case format.

    Args:
        input_string (str): The string to convert.

    Returns:
        str: The converted snake_case string.
    """
    return "_".join(re.findall(r"\w+", input_string.lower()))


def to_spongebob_case(input_string: str) -> str:
    """Converts a string to SpongeBobCase format.

    Alternates the casing of alphabetic characters, starting with lowercase.

    Args:
        input_string (str): The string to convert.

    Returns:
        str: The converted SpongeBobCase string.
    """
    return "".join(
        c.upper() if i % 2 else c.lower()
        for i, c in enumerate(input_string)
        if c.isalpha()
    )


class CaseWizard:
    """A class that provides methods to convert strings between different case types.

    Attributes:
        strategies (Dict[CaseType, Callable[[str], str]]): A mapping of case types to their
            corresponding conversion functions.
    """

    def __init__(self):
        """Initializes the CaseWizard with predefined conversion strategies."""

        self.strategies: Dict[CaseType, Callable[[str], str]] = {
            CaseType.CAMEL: to_camel_case,
            CaseType.COBOL: to_cobol_case,
            CaseType.KEBAB: to_kebab_case,
            CaseType.PASCAL: to_pascal_case,
            CaseType.SCREAM: to_scream_case,
            CaseType.SNAKE: to_snake_case,
            CaseType.LOWER: str.lower,
            CaseType.UPPER: str.upper,
            CaseType.TITLE: str.title,
            CaseType.SPONGEBOB: to_spongebob_case,
        }

    def convert(self, input_string: str, output_case: CaseType) -> str:
        """Converts an input string to the specified case format.

        Args:
            input_string (str): The string to convert.
            output_case (CaseType): The desired case format.

        Returns:
            str: The converted string in the specified case format.
        """
        strategy = self.strategies.get(output_case)
        return strategy(input_string) if strategy else input_string


if __name__ == "__main__":
    # Example usage
    wizard = CaseWizard()
    input_string = "Hello, World! This is a test string."

    for case in CaseType:
        print(f"{case.name.title()}: {wizard.convert(input_string, case)}")
