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
    """
    Convert the input string to camel case.

    Args:
        input_string (str): The input string to convert.

    Returns:
        str: The input string converted to camel case.
    """
    words = re.findall(r"\w+", input_string.lower())
    return words[0] + "".join(word.capitalize() for word in words[1:])


def to_cobol_case(input_string: str) -> str:
    """
    Convert the input string to COBOL case.

    Args:
        input_string (str): The input string to convert.

    Returns:
        str: The input string converted to COBOL case.
    """
    return "-".join(re.findall(r"\w+", input_string.upper()))


def to_kebab_case(input_string: str) -> str:
    """
    Convert the input string to kebab case.

    Args:
        input_string (str): The input string to convert.

    Returns:
        str: The input string converted to kebab case.
    """
    return "-".join(re.findall(r"\w+", input_string.lower()))


def to_pascal_case(input_string: str) -> str:
    """
    Convert the input string to Pascal case.

    Args:
        input_string (str): The input string to convert.

    Returns:
        str: The input string converted to Pascal case.
    """
    return "".join(
        word.capitalize() for word in re.findall(r"\w+", input_string.lower())
    )


def to_scream_case(input_string: str) -> str:
    """
    Convert the input string to SCREAM case.

    Args:
        input_string (str): The input string to convert.

    Returns:
        str: The input string converted to SCREAM case.
    """
    return "_".join(re.findall(r"\w+", input_string.upper()))


def to_snake_case(input_string: str) -> str:
    """
    Convert the input string to snake case.

    Args:
        input_string (str): The input string to convert.

    Returns:
        str: The input string converted to snake case.
    """
    return "_".join(re.findall(r"\w+", input_string.lower()))


def to_spongebob_case(input_string: str) -> str:
    """
    Convert the input string to SpOnGeBoB case.

    Args:
        input_string (str): The input string to convert.

    Returns:
        str: The input string converted to SpOnGeBoB case.
    """
    return "".join(
        c.upper() if i % 2 else c.lower()
        for i, c in enumerate(input_string)
        if c.isalpha()
    )


class CaseWizard:
    """
    A class that provides methods to convert strings between different case types.
    """

    def __init__(self):
        """
        Initialize the CaseWizard with a dictionary of conversion strategies.
        """
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
        """
        Convert the input string to the specified case type.

        Args:
            input_string (str): The input string to convert.
            output_case (CaseType): The desired output case type.

        Returns:
            str: The input string converted to the specified case type.
                 If the case type is not supported, returns the original string.
        """
        strategy = self.strategies.get(output_case)
        return strategy(input_string) if strategy else input_string


if __name__ == "__main__":
    # Example usage
    wizard = CaseWizard()
    input_string = "Hello, World! This is a test string."

    for case in CaseType:
        print(f"{case.name.title()}: {wizard.convert(input_string, case)}")
