import shutil
from pathlib import Path
from typing import Optional, List

from src.models.directory import Directory
from src.utils.toad_logger import ToadLogger, LogLevel

frog = ToadLogger("models.file", level=LogLevel.DEBUG)

DISALLOWED_CHARS: List[str] = ["<", ">", ":", '"', "/", "\\", "|", "?", "*", "\0"]


class FileError(Exception):
    """Custom exception for File-related errors."""

    def __init__(self, message, *args):
        super().__init__(message, *args)
        frog.critical(f"File-related error occurred: {message}")


class File:
    """Represents a file with validation and path handling.

    Attributes:
        name (str): The name of the file.
        directory (Directory): The directory where the file resides.
        replacement_char (Optional[str]): Character to replace disallowed characters in filename.
            Defaults to None.
        disallowed_chars (List[str]): List of characters not allowed in the filename.
            Defaults to DISALLOWED_CHARS.
    """

    def __init__(
        self,
        name: str,
        directory: Directory,
        replacement_char: Optional[str] = None,
    ):
        """Initializes the File object with the given name, directory, and replacement character.

        Args:
            name (str): The name of the file.
            directory (Directory): The directory where the file resides.
            replacement_char (Optional[str]): Character to replace disallowed characters in filename.
                Defaults to None.
        """
        self._name = name
        self._directory = directory
        self._replacement_char = replacement_char
        self.disallowed_chars = DISALLOWED_CHARS
        self.__post_init__()

    def __post_init__(self):
        """Post-initialization processing to validate and set attribute values."""
        frog.debug(f"File object created: {self}")
        self.name = self._name
        self.directory = self._directory
        self.replacement_char = self._replacement_char

    def __repr__(self):
        """Returns a string representation of the File object."""
        return (
            f"File("
            f"name: {self.name}, "
            f"directory: {self.directory}, "
            f"path: {self.path}, "
            f"exists: {self.exists}"
            f")"
        )

    @property
    def name(self) -> str:
        """Gets the name of the file.

        Returns:
            str: The name of the file.
        """
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Sets and sanitizes the name of the file.

        Args:
            value (str): The new filename.

        Raises:
            FileError: If the filename contains disallowed characters and no replacement character is set,
                or if the filename is reserved by the operating system.
        """
        v = value.strip()

        if Path(v).is_reserved():
            raise FileError(f"Filename '{v}' is reserved by the operating system.")

        for char in self.disallowed_chars:
            if char in v and self.replacement_char:
                frog.debug(
                    f"Replacing disallowed character '{char}' in filename '{v}' "
                    f"with '{self.replacement_char}'."
                )
                v = v.replace(char, self.replacement_char)
            elif char in v and not self.replacement_char:
                raise FileError(
                    f"Filename '{v}' contains disallowed character '{char}'. Unable to set new name."
                )

        self._name = v

    @property
    def directory(self) -> Directory:
        """Gets the directory object where the file resides.

        Returns:
            Directory: The directory object.
        """
        return self._directory

    @directory.setter
    def directory(self, value: Directory) -> None:
        """Sets the directory object where the file resides.

        Args:
            value (Directory): The new directory object.
        """
        self._directory = value

    @property
    def replacement_char(self) -> Optional[str]:
        """Gets the replacement character for disallowed characters in the filename.

        Returns:
            Optional[str]: The replacement character.
        """
        return self._replacement_char

    @replacement_char.setter
    def replacement_char(self, value: Optional[str]) -> None:
        """Sets the replacement character for disallowed characters in the filename.

        Args:
            value (Optional[str]): The replacement character.

        Note:
            If the provided replacement character is invalid or disallowed, it will be set to None.
        """
        v = value.strip() if value else value
        if v in self.disallowed_chars:
            frog.error(f"Replacement character '{v}' is not valid.")
            v = None
        elif v and len(v) > 1:
            frog.error(
                f"Replacement character '{v}' is too long. Must be a single character."
            )
            v = None

        self._replacement_char = v

    @property
    def path(self) -> Path:
        """Gets the full path of the file.

        Returns:
            Path: The full path of the file.
        """
        return Path(self.directory.path) / self.name

    @property
    def exists(self) -> bool:
        """Checks if the file exists.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        return self.path.is_file()

    def create(self, content: str = "") -> bool:
        """Creates the file if it doesn't exist.

        Args:
            content (str, optional): Initial content to write to the file. Defaults to empty string.

        Returns:
            bool: True if the file exists after the operation, False otherwise.

        Raises:
            FileError: If an error occurs during the create operation.
        """
        try:
            if self.exists:
                frog.debug(f"File '{self.path}' already exists.")
            else:
                frog.info(f"Creating file '{self.path}'...")
                self.path.write_text(content)
            return True
        except Exception as e:
            raise FileError(f"Failed to create file '{self.path}': {e}")

    def delete(self) -> bool:
        """Deletes the file if it exists.

        Returns:
            bool: True if the file does not exist after the operation, False otherwise.

        Raises:
            FileError: If an error occurs during the delete operation.
        """
        if self.exists:
            try:
                frog.info(f"Deleting file '{self.path}'...")
                self.path.unlink()
            except Exception as e:
                raise FileError(f"Failed to delete file '{self.path}': {e}")
        else:
            frog.info(f"File '{self.path}' does not exist.")
        return not self.exists

    def rename(self, new_name: str) -> bool:
        """Renames the file to the specified name.

        Args:
            new_name (str): The new filename.

        Returns:
            bool: True if the file was successfully renamed, False otherwise.

        Raises:
            FileError: If an error occurs during the rename operation.
        """
        if self.name == new_name:
            frog.debug(f"Filename '{new_name}' is the same as the current name.")
            return True

        if not self.exists:
            frog.error(f"File '{self.path}' does not exist. Unable to rename.")
            return False

        new_path = self.path.with_name(new_name)

        if new_path.exists():
            frog.error(f"File '{new_path}' already exists. Unable to rename.")
            return False

        try:
            frog.info(f"Renaming file '{self.name}' to '{new_name}'...")
            self.path.rename(new_path)
            self.name = new_name
            return True
        except Exception as e:
            raise FileError(f"Failed to rename file '{self.path}' to '{new_name}': {e}")

    def copy(self, destination: Directory) -> bool:
        """Copies the file to the specified destination directory.

        Args:
            destination (Directory): The destination directory.

        Returns:
            bool: True if the file was successfully copied, False otherwise.

        Raises:
            FileError: If an error occurs during the copy operation.
        """
        if not self.exists:
            frog.error(f"File '{self.path}' does not exist. Unable to copy.")
            return False

        if not destination.exists:
            frog.error(
                f"Destination directory '{destination.path}' does not exist. Unable to copy."
            )
            return False

        new_path = Path(destination.path) / self.name

        if new_path.exists():
            frog.error(
                f"File '{new_path}' already exists in the destination. Unable to copy."
            )
            return False

        try:
            frog.info(f"Copying file '{self.path}' to '{new_path}'...")
            shutil.copy2(self.path, new_path)
            return True
        except Exception as e:
            raise FileError(f"Failed to copy file '{self.path}' to '{new_path}': {e}")

    def move(self, destination: Directory) -> bool:
        """Moves the file to the specified destination directory.

        Args:
            destination (Directory): The destination directory.

        Returns:
            bool: True if the file was successfully moved, False otherwise.

        Raises:
            FileError: If an error occurs during the move operation.
        """
        if not self.exists:
            frog.error(f"File '{self.path}' does not exist. Unable to move.")
            return False

        if not destination.exists:
            frog.error(
                f"Destination directory '{destination.path}' does not exist. Unable to move."
            )
            return False

        new_path = Path(destination.path) / self.name

        if new_path.exists():
            frog.error(
                f"File '{new_path}' already exists in the destination. Unable to move."
            )
            return False

        try:
            frog.info(f"Moving file '{self.path}' to '{new_path}'...")
            shutil.move(str(self.path), str(new_path))
            self.directory = destination
            return True
        except Exception as e:
            raise FileError(f"Failed to move file '{self.path}' to '{new_path}': {e}")
