from typing import Dict, List, Optional, Union
from enum import Enum

import utilities as Utils


# =========================================================================== #

class ListPlacement(Enum):
    BEGINNING = 'beginning'
    END = 'end'
    BOTH = 'both'


# =========================================================================== #

def get_name_seeds() -> List[Dict]:
    """Retrieve name seed data from a configured JSON file."""
    filepath = Utils.get_config_val('Main', 'NAME_SEEDS')
    return Utils.load_json(filepath)


def get_list_names() -> List[str]:
    """Get all unique list names from the name seed data."""
    name_seeds = get_name_seeds()
    return [item['listName'] for item in name_seeds]


def get_list_placements() -> List[ListPlacement]:
    """Get all unique list placements from the ListPlacement enum."""
    return [placement.value for placement in ListPlacement]


def get_combined_list(
    list_names: Optional[Union[List[str], str]] = None,
    list_placements: Optional[Union[List[ListPlacement], ListPlacement]] = None
) -> List[str]:
    """Combine lists by names and placements, return unique, sorted list."""

    if list_names is None:
        names = get_list_names()
    elif isinstance(list_names, str):
        names = [list_names]
    else:
        names = list_names

    if list_placements is None:
        placements = get_list_placements()
    elif isinstance(list_placements, ListPlacement):
        placements = [list_placements.value]
    else:
        placements = [p.value for p in list_placements]

    lists_to_combine = []
    for item in get_name_seeds():
        for placement in placements:
            if item['listName'] in names and item['listPlacement'] == placement:
                lists_to_combine.append(item['listItems'])

    return Utils.combine_lists(*lists_to_combine)


def concatenate_string_lists(
    list_a: List[str],
    list_b: List[str]
) -> List[str]:
    """Combine strings from two lists into one list of concatenated strings."""
    return [a + b for a in list_a for b in list_b]

# =========================================================================== #

if __name__ == '__main__':
    # Test get_name_seeds
    print("Testing get_name_seeds:")
    print(get_name_seeds())
    print()

    # Test get_list_names
    print("Testing get_list_names:")
    print(get_list_names())
    print()

    # Test get_list_placements
    print("Testing get_list_placements:")
    print(get_list_placements())
    print()

    # Test get_combined_list with default values (None)
    print("Testing get_combined_list with default values:")
    print(get_combined_list())
    print()

    # Test get_combined_list with a specific list_name
    print("Testing get_combined_list with a specific list_name:")
    print(get_combined_list(list_names='botanical'))
    print()

    # Test get_combined_list with multiple list_names
    print("Testing get_combined_list with multiple list_names:")
    print(get_combined_list(list_names=['birds', 'gemstones']))
    print()

    # Test get_combined_list with a specific placement
    print("Testing get_combined_list with a specific placement:")
    print(get_combined_list(list_placements=ListPlacement.BEGINNING))
    print()

    # Test get_combined_list with multiple placements
    print("Testing get_combined_list with multiple placements:")
    print(get_combined_list(list_placements=[ListPlacement.BEGINNING, ListPlacement.BOTH]))
    print()

    # Test concatenate_string_lists
    print("Testing concatenate_string_lists:")
    print(concatenate_string_lists(['A', 'B'], ['C', 'D']))
