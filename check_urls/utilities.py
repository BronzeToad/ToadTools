import configparser
import json
import os
from enum import Enum, auto
from itertools import chain
from typing import Dict, List, Optional, Union


# =========================================================================== #

class EnvType(Enum):
    DEV = auto()
    TST = auto()
    PRD = auto()


class ConfigType(Enum):
    MAIN = 'config.ini'
    SECRETS = 'secrets.ini'


# =========================================================================== #

def get_config_val(
    section: str,
    key: str,
    config_type: Optional[ConfigType] = ConfigType.MAIN,
) -> Union[str, int, float]:
    """Retrieve and convert a value from .ini config file."""
    config_path = os.path.join('cfg', config_type.value)
    ConfigParser = configparser.ConfigParser()
    ConfigParser.read(config_path)
    val = ConfigParser.get(section, key)

    try:
        return int(val)
    except ValueError:
        pass

    try:
        return float(val)
    except ValueError:
        pass

    return val


def combine_lists(*lists: List[str]) -> List[str]:
    """Combine multiple lists into a single list with unique, sorted items."""
    unique_items = set(chain(*lists))
    return sorted(unique_items)


def load_json(file_path: str) -> List[Dict]:
    """Load JSON data from a given file path."""
    with open(file_path, 'r') as f:
        return json.load(f)


def save_results_to_json(
    data: List[Dict[str, Union[str, bool]]],
    file_path: str = None
) -> None:
    """Save or update domain availability results to a JSON file."""
    if file_path is None:
        file_path = get_config_val('Main', 'OUTPUT')

    try:
        with open(file_path, 'r') as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = []

    # Update or add new records
    for item in data:
        for existing_item in existing_data:
            if item['name'] == existing_item['name']:
                existing_item.update(item)
                break
        else:
            existing_data.append(item)

    with open(file_path, 'w') as f:
        json.dump(existing_data, f, indent=4)


# =========================================================================== #

if __name__ == '__main__':
    # Test get_config_val function
    print("Testing get_config_val:")
    print(get_config_val('Main', 'ROOT'))

    # Test combine_lists function
    print("\nTesting combine_lists:")
    print(combine_lists(['a', 'b'], ['c'], ['a', 'd']))

    # Test save_results_to_json function (assuming you have data to save)
    print("\nTesting save_results_to_json:")
    sample_data = [
        {'name': 'FakeNameAlpha', 'FakeNameAlpha.com': True},
        {'name': 'FakeNameBravo', 'FakeNameBravo.com': False}
    ]
    save_results_to_json(sample_data, 'test_output.json')
    print("Check 'test_output.json' to see if data is saved correctly.")
