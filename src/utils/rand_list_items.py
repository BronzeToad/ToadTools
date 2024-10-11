from random import choice
from typing import List, Optional

from src.utils.toad_logger import ToadLogger, LogLevel

frog = ToadLogger("utils.rand_next_day", level=LogLevel.DEBUG)


def random_strings_from_lists_multiple(
        lists: List[List[str]],
        num: int,
        capitalize: bool = True,
        skip_items: Optional[List[str]] = None,
) -> List[str]:
    """Generate a list of random strings by combining strings from input lists.

    Args:
        lists (List[List[str]]): List of lists of strings.
        num (int): The number of strings to generate.
        capitalize (bool): Whether to capitalize the first letter of the string.
            Defaults to True.
        skip_items (Optional[List[str]]): A list of strings to skip. Defaults to None.

    Returns:
        List[str]: A list of strings that combines one item from each list.
    """
    skip_items = [item.lower() for item in (skip_items or [])]
    result = []
    loop_guard = 0

    while len(result) < num and loop_guard < 1000:
        new_item = random_strings_from_lists(lists, capitalize)
        new_item_lower = new_item.lower()

        if new_item_lower not in skip_items and new_item_lower not in [item.lower() for item in
                                                                       result]:
            result.append(new_item)

        loop_guard += 1

    return result

def random_strings_from_lists(
        lists: List[List[str]],
        capitalize: bool = True,
) -> str:
    """Generate a random string by combining strings from input lists.

    Args:
        lists (List[List[str]]): List of lists of strings.
        capitalize (bool): Whether to capitalize the first letter of the string.
            Defaults to True.

    Returns:
        str: A string that combines one item from each list.
    """
    combine = []

    for lst in lists:

        if not isinstance(lst, list):
            frog.error("All elements in the input list must be lists.")
            raise ValueError("Invalid input list.")

        if not lst:
            frog.error("All lists in the input list must be non-empty.")
            raise ValueError("Empty input list.")

        combine.append(str(choice(lst)))

    if capitalize:
        return "".join([x.capitalize() for x in combine])
    else:
        return "".join([x.lower() for x in combine])



# List A: Adjectives
adjectives = [
    "crimson",
    "amber",
    "scarlet",
    "cobalt",
    "charcoal",
    "ivory",
    "jade",
    "brass",
    "emerald",
    "garnet",
    "moss",
    "ruby",
    "sapphire",
    "steel",
    "amethyst",
    "copper",
]

# List B: Nouns
nouns = [
    "wizard",
    "giant",
    "phoenix",
    "werewolf",
    "kraken",
    "fox",
    "golem",
    "octopus",
]


if __name__ == "__main__":
    # Example usage

    skip_items = [
        "MossWizard", "IvoryFox", "MossKraken"
    ]

    combined_names = random_strings_from_lists_multiple(
        lists=[adjectives, nouns],
        num=10,
        skip_items=skip_items
    )

    for name in combined_names:
        print(f"{name} - {name.lower()}")


