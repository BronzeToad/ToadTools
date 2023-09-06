from src.enum_hatchery import StringCase

# =========================================================================== #

class CaseWizard:
    """
    CaseWizard is a utility class for converting strings into various cases.

    Attributes:
        input_string (str): The input string to be converted.
        output_case (StringCase): The desired output case defined in StringCase enum.

    Methods:
        convert(): Convert the input string to the specified output case and return it.
    """

    def __init__(
        self,
        input_string: str,
        output_case: StringCase
    ):
        self.input_string = input_string
        self.output_case = output_case

    def convert(self) -> str:
        """Convert the string to the specified case."""
        case_map = self._get_case_map()
        return case_map[self.output_case]()

    def _get_case_map(self) -> dict:
        """Get the mapping of StringCase to conversion methods."""
        return {
            StringCase.CAMEL: self._to_camel_case,
            StringCase.COBOL: self._to_cobol_case,
            StringCase.KEBAB: self._to_kebab_case,
            StringCase.PASCAL: self._to_pascal_case,
            StringCase.SCREAM: self._to_scream_case,
            StringCase.SNAKE: self._to_snake_case,
            StringCase.LOWER: self._to_lower_case,
            StringCase.UPPER: self._to_upper_case,
            StringCase.TITLE: self._to_title_case,
            StringCase.SPONGEBOB: self._to_spongebob_case
        }

    def _to_camel_case(self) -> str:
        """Convert to camel case."""
        words = self.input_string.lower().split()
        return words[0] + ''.join(word.capitalize() for word in words[1:])

    def _to_cobol_case(self) -> str:
        """Convert to COBOL case."""
        return self.input_string.upper().replace(' ', '-')

    def _to_kebab_case(self) -> str:
        """Convert to kebab case."""
        return self.input_string.lower().replace(' ', '-')

    def _to_pascal_case(self) -> str:
        """Convert to Pascal case."""
        words = self.input_string.lower().split()
        return ''.join(word.capitalize() for word in words)

    def _to_scream_case(self) -> str:
        """Convert to scream case."""
        return self.input_string.upper().replace(' ', '_')

    def _to_snake_case(self) -> str:
        """Convert to snake case."""
        return self.input_string.lower().replace(' ', '_')

    def _to_lower_case(self) -> str:
        """Convert to lowercase."""
        return self.input_string.lower()

    def _to_upper_case(self):
        """Convert to uppercase."""
        return self.input_string.upper()

    def _to_title_case(self) -> str:
        """Convert to title case."""
        return self.input_string.title()

    def _to_spongebob_case(self) -> str:
        """Convert to Spongebob case.

        Notes:
            Who lives in a pineapple under the sea?
            SpongeBob SquarePants!
            Absorbent and yellow and porous is he
            SpongeBob SquarePants!
            If nautical nonsense be something you wish
            SpongeBob SquarePants!
            Then drop on the deck and flop like a fish!
            SpongeBob SquarePants! (Ready?!)
            SpongeBob SquarePants!
            SpongeBob SquarePants!
            SpongeBob SquarePants!
        """
        s = ''
        toggle = True
        for char in self.input_string:
            if char.isalpha():
                s += char.upper() if toggle else char.lower()
                toggle = not toggle
            else:
                s += char
        return s
