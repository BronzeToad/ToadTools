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
        self.__post_init__()

    def __post_init__(self):
        self.beginning_names = self.get_start_items()
        self.end_names = self.get_end_items()

    def get_start_items(self) -> List[str]:
        return Utils.combine_lists(
            GenNames.get_combined_items(self.item_list_keys, Position.START),
            GenNames.get_combined_items(self.item_list_keys, Position.START_END)
        )

    def get_end_items(self) -> List[str]:
        return Utils.combine_lists(
            GenNames.get_combined_items(self.item_list_keys, Position.END),
            GenNames.get_combined_items(self.item_list_keys, Position.START_END)
        )





# =========================================================================== #

if __name__ == '__main__':
    pass
