from dataclasses import dataclass, field
from pathlib import Path
from typing import Union, Optional, List

from src.utils.toad_logger import ToadLogger, LogLevel

frog = ToadLogger("models.directory", level=LogLevel.DEBUG)

DISALLOWED_CHARS: List[str] = ["<", ">", ":", '"', "/", "\\", "|", "?", "*", "\0"]

RESERVED_NAMES: List[str] = [
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
]

# TODO: add method for deleting directory
# TODO: add method for renaming directory
#  will need to update dirname and path after renaming
#  dirname and path will need to be properties with setters
#  add a check for reserved names and disallowed chars before renaming
#  add a check for existing directory with new name before renaming


@dataclass
class Directory:
    """Represents a directory with validation and creation capabilities.

    Attributes:
        dirname (str): The name of the directory.
        parent (Union[str, Path]): The path to the parent directory.
        create_if_not_exists (bool): Whether to create the directory if it does not exist.
            Defaults to False.
        replacement_char (Optional[str]): Character to replace disallowed characters in dirname.
            Defaults to None.
        os_reserved_dirnames (List[str]): List of OS-reserved directory names.
            Defaults to RESERVED_NAMES.
        disallowed_chars (List[str]): List of characters not allowed in the dirname.
            Defaults to DISALLOWED_CHARS.
    """

    dirname: str
    parent: Union[str, Path]
    create_if_not_exists: bool = False
    replacement_char: Optional[str] = None
    os_reserved_dirnames: List[str] = field(
        repr=False, default_factory=lambda: RESERVED_NAMES
    )
    disallowed_chars: List[str] = field(
        repr=False, default_factory=lambda: DISALLOWED_CHARS
    )
    path: Optional[Path] = field(init=False, default=None)

    def __post_init__(self) -> None:
        """Post-initialization processing to validate and build the directory path.

        Raises:
            ValueError: If the directory name is reserved by the operating system.
            ValueError: If disallowed characters are present and no replacement char is provided.
        """
        frog.debug("Directory object created...")
        self.dirname = self.dirname.strip()
        self._validate_replacement_char()

        if self._check_dirname_for_reserved_names():
            raise ValueError("Directory name is reserved by the operating system.")

        if self._check_dirname_for_disallowed_chars():
            raise ValueError("Directory name contains disallowed character.")

        self.parent = Path(self.parent).resolve()
        self.path = self._build_full_path()

    def _validate_replacement_char(self) -> None:
        """Validates the replacement character for disallowed characters.

        Raises:
            ValueError: If the replacement character is invalid.
        """
        if self.replacement_char in self.disallowed_chars:
            frog.error(f"Replacement character '{self.replacement_char}' is not valid.")
            raise ValueError("Invalid replacement character.")
        if self.replacement_char and len(self.replacement_char) > 1:
            frog.error(
                f"Replacement character '{self.replacement_char}' is too long. "
                f"Must be a single character."
            )
            raise ValueError("Replacement character too long.")

    def _check_dirname_for_reserved_names(self, dirname: Optional[str] = None) -> bool:
        """Checks if the directory name is reserved by the operating system.

        Args:
            dirname (str): The directory name to check. Defaults to self.dirname.

        Returns:
            bool: True if the directory name is reserved, False otherwise.
        """
        dirname = dirname or self.dirname
        if dirname.upper() in self.os_reserved_dirnames:
            frog.error(f"Directory name '{dirname}' is reserved by OS.")
            return True
        return False

    def _check_dirname_for_disallowed_chars(
        self, dirname: Optional[str] = None
    ) -> bool:
        """Checks and handles disallowed characters in the directory name.

        Args:
            dirname (str): The directory name to check. Defaults to self.dirname.

        Returns:
            bool: True if disallowed characters are present and no replacement char is provided,
                False otherwise.
        """

        dirname = dirname or self.dirname

        def _strip_char(_dirname: str, _char: str) -> str:
            """Strips a disallowed character from the start or end of the directory name.

            Args:
                _dirname (str): The directory name.
                _char (str): The disallowed character to strip.

            Returns:
                str: The sanitized directory name.
            """
            if _dirname.startswith(_char):
                _dirname = _dirname[1:]
                frog.debug(
                    f"Removed disallowed character '{_char}' from start of directory name."
                )
            if _dirname.endswith(_char):
                _dirname = _dirname[:-1]
                frog.debug(
                    f"Removed disallowed character '{_char}' from end of directory name."
                )
            return _dirname

        for char in self.disallowed_chars:
            while dirname.startswith(char) or dirname.endswith(char):
                dirname = _strip_char(dirname, char)

        for char in self.disallowed_chars:
            if char in dirname:
                if self.replacement_char:
                    frog.debug(
                        f"Replacing disallowed character '{char}' in directory '{dirname}' "
                        f"with '{self.replacement_char}'."
                    )
                    dirname = dirname.replace(char, self.replacement_char)
                else:
                    frog.error(
                        f"Directory name '{dirname}' contains disallowed character '{char}'."
                    )
                    return True

        self.dirname = dirname
        return False

    def _build_full_path(self) -> Path:
        """Builds the full path for the directory.

        Returns:
            Path: The full directory path.

        Raises:
            ValueError: If the directory does not exist and creation is not enabled.
        """
        if self.dirname == self.parent.name:
            frog.info(
                f"Directory name '{self.dirname}' already included in parent path."
            )
            path = self.parent
        else:
            path = self.parent / self.dirname

        if self.create_if_not_exists:
            self.create_directory(path)

        if not path.exists():
            frog.error(f"Directory '{path}' does not exist.")
            raise ValueError("Directory does not exist.")

        return path

    @staticmethod
    def create_directory(path: Path) -> bool:
        """Creates the directory at the specified path if it does not exist.

        Args:
            path (Path): The path where the directory should be created.

        Returns:
            bool: True if the directory exists after the operation, False otherwise.
        """
        if not path.exists():
            frog.info(f"Creating directory '{path}'...")
            path.mkdir(parents=True, exist_ok=True)
        else:
            frog.info(f"Directory '{path}' already exists.")
        return path.exists()


if __name__ == "__main__":
    # Example usage
    test_dirnames: List[str] = [
        "<test>",
        "test",
        "test/",
        "test\\",
        "te/st//",
        "te\\st\\\\",
        "*t*e*st*",
    ]

    for dirname in test_dirnames:
        frog.error(f"\n\nTesting directory name: '{dirname}'")
        try:
            dir_instance = Directory(
                dirname=dirname,
                parent="B:/dolphin",
                create_if_not_exists=True,
                replacement_char="_",
            )
            frog.info(dir_instance)
        except ValueError as e:
            frog.error(f"Failed to create directory: {e}")
