import shutil
from pathlib import Path
from typing import Union, Optional, List

from src.utils.toad_logger import ToadLogger, LogLevel

frog = ToadLogger("models.directory", level=LogLevel.DEBUG)

DISALLOWED_CHARS: List[str] = ["<", ">", ":", '"', "/", "\\", "|", "?", "*", "\0"]


class Directory:
    """Represents a directory with validation, creation, deletion, and renaming capabilities.

    Attributes:
        name (str): The name of the directory.
        parent (Union[str, Path]): The path to the parent directory.
        replacement_char (Optional[str]): Character to replace disallowed characters in name.
            Defaults to None.
        disallowed_chars (List[str]): List of characters not allowed in the directory name.
            Defaults to DISALLOWED_CHARS.
    """

    def __init__(
        self,
        name: str,
        parent: Union[str, Path],
        replacement_char: Optional[str] = None,
    ):
        self._name = name
        self._parent = parent
        self._replacement_char = replacement_char
        self.disallowed_chars = DISALLOWED_CHARS
        self.__post_init__()

    def __post_init__(self):
        """Post-initialization processing to validate and set attribute values."""
        frog.debug("Directory object created...")
        self.name = self._name
        self.parent = self._parent
        self.replacement_char = self._replacement_char

    def __repr__(self):
        """Overloaded method to return a string representation of the Directory object."""
        return (
            f"Directory("
            f"name: {self.name}, "
            f"parent: {self.parent}, "
            f"path: {self.path}, "
            f"exists: {self.exists}"
            f")"
        )

    @property
    def name(self) -> str:
        """Gets the directory name.

        Returns:
            str: The directory name.
        """
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Sets the directory name.

        Args:
            value (str): The directory name.
        """
        v = value.strip()

        if Path(v).is_reserved():
            frog.error(f"Directory name '{v}' is reserved by the operating system.")
            return

        for char in self.disallowed_chars:
            while v.startswith(char) or v.endswith(char):
                v = self._strip_char(v, char)

        for char in self.disallowed_chars:
            if char in v and self.replacement_char:
                frog.debug(
                    f"Replacing disallowed character '{char}' in directory name '{v}' "
                    f"with '{self.replacement_char}'."
                )
                v = v.replace(char, self.replacement_char)
            elif char in v and not self.replacement_char:
                frog.error(
                    f"Directory name '{v}' contains disallowed character '{char}'. Unable to set new name."
                )
                return

        frog.debug(f"Setting dirname to '{v}'")
        self._name = v

    @property
    def parent(self) -> Union[str, Path]:
        """Gets the parent directory path.

        Returns:
            Union[str, Path]: The parent directory path.
        """
        return self._parent

    @parent.setter
    def parent(self, value: Union[str, Path]) -> None:
        """Sets the parent directory path.

        Args:
            value (Union[str, Path]): The parent directory path.
        """
        if isinstance(value, str):
            v = Path(value.strip()).resolve()
        else:
            v = value.resolve()

        if not v.is_dir():
            frog.error(f"Parent directory '{v}' does not exist.")
            return

        frog.debug(f"Setting parent to '{v}'")
        self._parent = v

    @property
    def replacement_char(self) -> Optional[str]:
        """Gets the replacement character for disallowed characters in the directory name.

        Returns:
            Optional[str]: The replacement character.
        """
        return self._replacement_char

    @replacement_char.setter
    def replacement_char(self, value: Optional[str]) -> None:
        """Sets the replacement character for disallowed characters in the directory name.

        Args:
            value (Optional[str]): The replacement character.
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

        frog.debug(f"Setting replacement_char to '{v}'")
        self._replacement_char = v

    @property
    def path(self) -> Optional[Path]:
        """Gets the full path to the directory.

        Returns:
            Optional[Path]: The full path to the directory, or None if the directory does not exist.
        """
        if self.name == self.parent.name:
            frog.info(f"Directory name '{self.name}' already included in parent path.")
            return self.parent
        else:
            return self.parent / self.name

    @property
    def exists(self) -> bool:
        """Checks if the directory exists.

        Returns:
            bool: True if the directory exists, False otherwise.
        """
        return self.path.is_dir()

    @staticmethod
    def _strip_char(name: str, char: str) -> str:
        """Strips a disallowed character from the start or end of the directory name.

        Args:
            name (str): The directory name.
            char (str): The disallowed character to strip.

        Returns:
            str: The sanitized directory name.
        """
        if name.startswith(char):
            name = name[1:]
            frog.debug(
                f"Removed disallowed character '{char}' from start of directory name."
            )
        if name.endswith(char):
            name = name[:-1]
            frog.debug(
                f"Removed disallowed character '{char}' from end of directory name."
            )
        return name

    def create(self) -> bool:
        """Creates Directory.path if it does not exist.

        Returns:
            bool: True if the directory exists after the operation, False otherwise.
        """
        try:
            if self.path.exists():
                frog.info(f"Directory '{self.path}' already exists.")
            else:
                frog.info(f"Creating directory '{self.path}'...")
                self.path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            frog.error(f"Failed to create directory '{self.path}': {e}")
            return False

    def delete(self) -> bool:
        """Deletes Directory.path if it exists.

        Returns:
            bool: True if the directory does not exist after the operation, False otherwise.
        """
        if self.path.exists():
            try:
                frog.info(f"Deleting directory '{self.path}'...")
                shutil.rmtree(self.path)
            except Exception as e:
                frog.error(f"Failed to delete directory '{self.path}': {e}")
                return False
        else:
            frog.info(f"Directory '{self.path}' does not exist.")
        return not self.path.exists()

    def rename(self, new_name: str) -> bool:
        """Renames the directory to the specified name.

        Args:
            new_name (str): The new directory name.

        Returns:
            bool: True if the directory was successfully renamed, False otherwise.
        """
        if self.name == new_name:
            frog.info(f"Directory name '{new_name}' is the same as the current name.")
            return True

        if not self.exists:
            frog.error(f"Directory '{self.path}' does not exist. Unable to rename.")
            return False

        new_path = self.path.with_name(new_name)

        if new_path.exists():
            frog.error(f"Directory '{new_path}' already exists. Unable to rename.")
            return False

        try:
            frog.info(f"Renaming directory '{self.name}' to '{new_name}'...")
            self.path.rename(new_path)
            self.name = new_name
            return True
        except Exception as e:
            frog.error(f"Failed to rename directory '{self.path}' to '{new_name}': {e}")
            return False

    def copy(self, target: Union[str, Path]) -> bool:
        """Copies the directory to the specified target destination.

        Args:
            target (Union[str, Path]): The target directory.

        Returns:
            bool: True if the directory was successfully copied, False otherwise.
        """
        if not self.exists:
            frog.error(f"Directory '{self.path}' does not exist. Unable to copy.")
            return False

        target = Path(target).resolve()
        if not target.is_dir():
            frog.error(f"Target directory '{target}' does not exist. Unable to copy.")
            return False

        new_path = target / self.name

        if new_path.exists():
            frog.error(f"Directory '{new_path}' already exists. Unable to copy.")
            return False

        try:
            frog.info(f"Copying directory '{self.path}' to '{new_path}'...")
            shutil.copytree(self.path, new_path)
            return True
        except Exception as e:
            frog.error(f"Failed to copy directory '{self.path}' to '{new_path}': {e}")
            return False

    def move(self, target: Union[str, Path]) -> bool:
        """Moves the directory to the specified target destination.

        Args:
            target (Union[str, Path]): The target directory.

        Returns:
            bool: True if the directory was successfully moved, False otherwise.
        """
        if not self.exists:
            frog.error(f"Directory '{self.path}' does not exist. Unable to move.")
            return False

        target = Path(target).resolve()
        if not target.is_dir():
            frog.error(f"Target directory '{target}' does not exist. Unable to move.")
            return False

        new_path = target / self.name

        if new_path.exists():
            frog.error(f"Directory '{new_path}' already exists. Unable to move.")
            return False

        try:
            frog.info(f"Moving directory '{self.path}' to '{new_path}'...")
            shutil.move(str(self.path), str(new_path))
            self.parent = target
            return True
        except Exception as e:
            frog.error(f"Failed to move directory '{self.path}' to '{new_path}': {e}")
            return False


if __name__ == "__main__":
    # Example usage
    try:
        dir_instance = Directory(name="test", parent="B:/dolphin", replacement_char="_")
        frog.info(dir_instance)
        dir_instance.create()
        dir_instance.rename("test1234")
        frog.info(dir_instance)
    except ValueError as e:
        frog.error(f"Failed to create directory: {e}")
