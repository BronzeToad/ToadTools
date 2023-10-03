from typing import List, Optional, Union

import utilities as Utils
import godaddy as GoDaddy
import generate_names as GenNames

from generate_names import Position

# =========================================================================== #

class NameChecker:

    def __init__(
        self,
        env_type: Utils.EnvType,
        item_list_keys: Optional[Union[List[str], str]] = None,
        domain_endings: Optional[List[str]] = None,
    ):
        self.env_type = env_type
        self.item_list_keys = item_list_keys
        self.domain_endings = domain_endings
        self.__post_init__()


    def __post_init__(self):
        self.start_items = self.get_start_items()
        self.end_items = self.get_end_items()
        self.concat_items = self.get_concatenated_items()


    def get_start_items(self) -> List[str]:
        print("Fetching start items...")
        items = Utils.combine_lists(
            GenNames.get_combined_items(self.item_list_keys, Position.START),
            GenNames.get_combined_items(self.item_list_keys, Position.START_END)
        )
        print(f"Retrieved {len(items)} start items.")
        return items


    def get_end_items(self) -> List[str]:
        print("Fetching end items...")
        items = Utils.combine_lists(
            GenNames.get_combined_items(self.item_list_keys, Position.END),
            GenNames.get_combined_items(self.item_list_keys, Position.START_END)
        )
        print(f"Retrieved {len(items)} end items.")
        return items


    def get_concatenated_items(self) -> List[str]:
        print("Concatenating items...")
        items = GenNames.concatenate_item_lists(
            self.start_items,
            self.end_items
        )
        print(f"Generated {len(items)} concatenated items.")
        return items


    def check_domains(
        self,
        batch_size: Optional[int] = None,
        limit: Optional[int] = None
    ) -> None:
        GoDaddy.main(
            host_names=self.concat_items,
            env_type=self.env_type,
            domain_endings=self.domain_endings,
            batch_size=batch_size,
            limit=limit
        )


# =========================================================================== #

if __name__ == '__main__':

    item_lists = [
        'fantasy', 'mythical_creatures', 'science_fiction', 'birds', 'bugs',
        'mammals', 'other_animals', 'reptiles_and_amphibians',
        'underwater_animals', 'botanical', 'gemstones', 'materials',
        'musical_instruments', 'natural_things', 'tools_and_instruments',
        'architectural_terms', 'astronomy_and_space', 'colors',
        'geographical_landforms', 'math_and_science_terms', 'medieval_terms',
        'weather_phenomena'
    ]

    CheckItOut = NameChecker(
        env_type=Utils.EnvType.PRD
    )

    CheckItOut.check_domains()

