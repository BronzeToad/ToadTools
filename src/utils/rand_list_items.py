from random import choice
from typing import List

from src.utils.toad_logger import ToadLogger, LogLevel

frog = ToadLogger("utils.rand_next_day", level=LogLevel.DEBUG)


def random_adjective_noun(lists: List[List[str]], capitalize: bool = True) -> str:
    """Generate a random string by combining a random adjective and a random noun.

    Args:
        lists (List[List[str]]): List of lists of strings.
        capitalize (bool): Whether to capitalize the first letter of the string.
            Defaults to True.

    Returns:
        str: A string that combines one item from each list.
    """
    output_str = ""

    for lst in lists:

        if not isinstance(lst, list):
            frog.error("All elements in the input list must be lists.")
            raise ValueError("Invalid input list.")

        if not lst:
            frog.error("All lists in the input list must be non-empty.")
            raise ValueError("Empty input list.")

        next_item = str(choice(lst))

        if capitalize:
            next_item = next_item.capitalize()

        output_str += next_item

    return output_str


# List A: Adjectives
adjectives = [
    "brave",
    "sly",
    "witty",
    "calm",
    "fierce",
    "gentle",
    "wise",
    "bold",
    "shy",
    "clever",
    "swift",
    "proud",
    "kind",
    "stern",
    "merry",
    "crafty",
    "loyal",
    "grumpy",
    "sleek",
    "humble",
    "jolly",
    "quirky",
    "nimble",
    "eager",
    "solemn",
    "keen",
    "deft",
    "spry",
    "brash",
    "coy",
    "plucky",
    "meek",
    "wry",
    "prim",
    "brisk",
    "burly",
    "droll",
    "lithe",
    "zesty",
    "sage",
    "posh",
    "blunt",
    "snug",
    "wily",
    "terse",
    "glib",
    "suave",
    "quaint",
]

# List B: Nouns
nouns = [
    "elf",
    "dragon",
    "wizard",
    "fairy",
    "troll",
    "mermaid",
    "unicorn",
    "gnome",
    "giant",
    "phoenix",
    "centaur",
    "werewolf",
    "vampire",
    "siren",
    "gorgon",
    "basilisk",
    "chimera",
    "kraken",
    "sphinx",
    "pegasus",
    "minotaur",
    "cyclops",
    "griffon",
    "imp",
    "ogre",
    "harpy",
    "nymph",
    "satyr",
    "wraith",
    "goblin",
    "dryad",
    "fox",
    "djinni",
    "valkyrie",
    "golem",
    "hydra",
    "ghoul",
    "elemental",
    "druid",
    "changeling",
    "manticore",
    "gargoyle",
    "elephant",
    "penguin",
    "octopus",
    "chimpanzee",
    "dolphin",
    "kangaroo",
    "platypus",
    "raccoon",
    "lemur",
    "koala",
    "sloth",
    "panda",
    "giraffe",
    "ostrich",
    "flamingo",
    "wombat",
    "hedgehog",
    "orangutan",
    "gorilla",
    "leopard",
    "jaguar",
    "lynx",
    "squirrel",
    "beaver",
    "otter",
    "walrus",
    "seal",
    "pelican",
    "toucan",
    "macaw",
    "cockatoo",
    "chameleon",
    "iguana",
    "gecko",
    "armadillo",
    "anteater",
    "porcupine",
    "badger",
    "meerkat",
    "mongoose",
    "weasel",
    "tapir",
    "capybara",
    "opossum",
    "pangolin",
    "aardvark",
    "okapi",
    "ibex",
    "gazelle",
    "bison",
]


if __name__ == "__main__":
    # Example usage

    for _ in range(25):
        print(random_adjective_noun([adjectives, nouns]))
