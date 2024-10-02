from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List

from src.models.directory import Directory
from src.utils.toad_logger import ToadLogger, LogLevel

frog = ToadLogger("models.file", level=LogLevel.DEBUG)

DISALLOWED_CHARS: List[str] = ["<", ">", ":", '"', "/", "\\", "|", "?", "*", "\0"]


@dataclass
class File:
    """Represents a file with validation and path handling.

    Attributes:
        filename  (str): The name of the file.
        directory (Directory): The directory where the file resides.
        replacement_char (Optional[str]): Character to replace disallowed characters in filename.
            Defaults to None.
        disallowed_chars (List[str]): List of characters not allowed in the filename.
            Defaults to DISALLOWED_CHARS.
        filepath (Optional[Path]): The full path to the file.
    """

    filename: str
    directory: Directory
    replacement_char: Optional[str] = None
    disallowed_chars: List[str] = field(
        repr=False, default_factory=lambda: DISALLOWED_CHARS
    )
    filepath: Optional[Path] = field(init=False, default=None)

    def __post_init__(self):
        """Post-initialization processing to validate and build the filepath."""
        frog.debug("File object created...")
        self.filename = self.filename.strip()
        self._check_filename_for_disallowed_chars()
        self.filepath = self.directory.path / self.filename

    def _check_filename_for_disallowed_chars(self):
        """Checks and handles disallowed characters in the filename.

        Raises:
            ValueError: If disallowed characters are present and no replacement char is provided.
        """
        for char in self.disallowed_chars:
            if char in self.filename:
                if self.replacement_char:
                    frog.debug(
                        f"Replacing disallowed character '{char}' in filename '{self.filename}' "
                        f"with '{self.replacement_char}'."
                    )
                    self.filename = self.filename.replace(char, self.replacement_char)
                else:
                    frog.error(
                        f"Filename '{self.filename}' contains disallowed character '{char}'."
                    )
                    raise ValueError("Filename contains disallowed character.")


if __name__ == "__main__":
    # Example usage
    directory = Directory(
        dirname="tst", parent="B:/dolphin", create_if_not_exists=True
    )

    try:
        file_instance = File(
            filename="test:file.txt", directory=directory, replacement_char="_"
        )
        frog.info(file_instance)
    except ValueError as e:
        frog.error(e)
