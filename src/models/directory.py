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


@dataclass
class Directory:
    """Represents a directory with validation and creation capabilities.

    Attributes:
        dirname (str): The name of the directory.
        parent_path (Union[str, Path]): The path to the parent directory.
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
    parent_path: Union[str, Path]
    create_if_not_exists: bool = False
    replacement_char: Optional[str] = None
    os_reserved_dirnames: List[str] = field(repr=False, default_factory=lambda: RESERVED_NAMES)
    disallowed_chars: List[str] = field(repr=False, default_factory=lambda: DISALLOWED_CHARS)
    full_path: Optional[Path] = field(init=False, default=None)

    def __post_init__(self) -> None:
        """Post-initialization processing to validate and build the directory path."""
        frog.debug("Directory object created...")
        self.dirname = self.dirname.strip()
        self._validate_replacement_char()
        self._check_dirname_for_reserved_names()
        self._check_dirname_for_disallowed_chars()
        self.parent_path = Path(self.parent_path).resolve()
        self.full_path = self._build_full_path()

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

    def _check_dirname_for_reserved_names(self) -> None:
        """Checks if the directory name is reserved by the operating system.

        Raises:
            ValueError: If the directory name is reserved.
        """
        if self.dirname.upper() in self.os_reserved_dirnames:
            frog.error(f"Directory name '{self.dirname}' is reserved by OS.")
            raise ValueError("Directory name is reserved by the operating system.")

    def _check_dirname_for_disallowed_chars(self) -> None:
        """Checks and handles disallowed characters in the directory name.

        Raises:
            ValueError: If disallowed characters are present and no replacement char is provided.
        """

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
            while self.dirname.startswith(char) or self.dirname.endswith(char):
                self.dirname = _strip_char(self.dirname, char)

        for char in self.disallowed_chars:
            if char in self.dirname:
                if self.replacement_char:
                    frog.debug(
                        f"Replacing disallowed character '{char}' in directory '{self.dirname}' "
                        f"with '{self.replacement_char}'."
                    )
                    self.dirname = self.dirname.replace(char, self.replacement_char)
                else:
                    frog.error(
                        f"Directory name '{self.dirname}' contains disallowed character '{char}'."
                    )
                    raise ValueError("Directory name contains disallowed character.")

    def _build_full_path(self) -> Path:
        """Builds the full path for the directory.

        Returns:
            Path: The full directory path.

        Raises:
            ValueError: If the directory does not exist and creation is not enabled.
        """
        if self.dirname == self.parent_path.name:
            frog.info(
                f"Directory name '{self.dirname}' already included in parent path."
            )
            path = self.parent_path
        else:
            path = self.parent_path / self.dirname

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
                parent_path="B:/dolphin",
                create_if_not_exists=True,
                replacement_char="_",
            )
            frog.info(dir_instance)
        except ValueError as e:
            frog.error(f"Failed to create directory: {e}")
