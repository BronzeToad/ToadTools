from typing import Dict, List, Optional, Union
from enum import Enum

import utilities as Utils


# =========================================================================== #

class Position(Enum):
    START = 'start'
    END = 'end'
    START_END = 'start_end'


# =========================================================================== #

def get_name_seeds() -> List[Dict]:
    """Retrieve name seed data from a configured JSON file."""
    filepath = Utils.get_config_val('Main', 'NAME_SEEDS')
    return Utils.load_json(filepath)


def get_names() -> List[str]:
    """Get all unique list names from the name seed data."""
    name_seeds = get_name_seeds()
    return [item['key'] for item in name_seeds]


def get_positions() -> List[Position]:
    """Get all unique list placements from the Position enum."""
    return [pos.value for pos in Position]


def get_combined_items(
    keys: Optional[Union[List[str], str]] = None,
    positions: Optional[Union[List[Position], Position]] = None
) -> List[str]:
    """Combine lists by names and positions, return unique, sorted list."""

    if keys is None:
        _keys = get_names()
    elif isinstance(keys, str):
        _keys = [keys]
    else:
        _keys = keys

    if positions is None:
        _positions = get_positions()
    elif isinstance(positions, Position):
        _positions = [positions.value]
    else:
        _positions = [pos.value for pos in positions]

    lists_to_combine = []
    for item in get_name_seeds():
        for pos in _positions:
            if item['key'] in _keys and item['position'] == pos:
                lists_to_combine.append(item['items'])

    return Utils.combine_lists(*lists_to_combine)


def concatenate_item_lists(
    list_a: List[str],
    list_b: List[str]
) -> List[str]:
    """Combine strings from two lists into one list of concatenated strings."""
    concatenated = []
    for a in list_a:
        for b in list_b:
            if a != b:  # Check to prevent items like "AlphaAlpha"
                concatenated.append(a + b)
    return concatenated

# =========================================================================== #

if __name__ == '__main__':
    # Test get_name_seeds
    print("Testing get_name_seeds:")
    print(get_name_seeds())
    print()

    # Test get_list_names
    print("Testing get_list_names:")
    print(get_names())
    print()

    # Test get_list_placements
    print("Testing get_list_placements:")
    print(get_positions())
    print()

    # Test get_combined_list with default values (None)
    print("Testing get_combined_list with default values:")
    print(get_combined_items())
    print()

    # Test get_combined_list with a specific list_name
    print("Testing get_combined_list with a specific list_name:")
    print(get_combined_items(keys='botanical'))
    print()

    # Test get_combined_list with multiple list_names
    print("Testing get_combined_list with multiple list_names:")
    print(get_combined_items(keys=['birds', 'gemstones']))
    print()

    # Test get_combined_list with a specific placement
    print("Testing get_combined_list with a specific placement:")
    print(get_combined_items(positions=Position.START))
    print()

    # Test get_combined_list with multiple placements
    print("Testing get_combined_list with multiple placements:")
    print(get_combined_items(positions=[Position.END, Position.START_END]))
    print()

    # Test concatenate_string_lists
    print("Testing concatenate_string_lists:")
    print(concatenate_item_lists(['A', 'B'], ['C', 'D']))
