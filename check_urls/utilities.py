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


def mash_list_strings(
    list_a: List[str],
    list_b: List[str]
) -> List[str]:
    """Combine strings from two lists into one list of concatenated strings."""
    return [a + b for a in list_a for b in list_b]


def combine_lists(*lists: List[str]) -> List[str]:
    """Combine multiple lists into a single list with unique, sorted items."""
    unique_items = set(chain(*lists))
    return sorted(unique_items)


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
            if item['host'] == existing_item['host']:
                existing_item.update(item)
                break
        else:
            existing_data.append(item)

    with open(file_path, 'w') as f:
        json.dump(existing_data, f, indent=4)


# =========================================================================== #

if __name__ == '__main__':
    pass
