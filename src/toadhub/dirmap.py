from dataclasses import dataclass, field

from src.models.directory import Directory
from src.utils.toad_logger import ToadLogger, LogLevel

frog = ToadLogger("toadhub.dirmap", level=LogLevel.DEBUG)

ROOT_DRIVE = "T:/"


@dataclass
class DirMap:
    """Represents a directory map structure for ToadHub.

    Attributes:
        root (str): The root directory path.
        data (Directory): The 'data' subdirectory.
        encode (Directory): The 'encode' subdirectory within 'data'.
        media (Directory): The 'media' subdirectory within 'data'.
        torrents (Directory): The 'torrents' subdirectory within 'data'.
    """

    root: str = ROOT_DRIVE
    data: Directory = field(init=False)
    encode: Directory = field(init=False)
    media: Directory = field(init=False)
    torrents: Directory = field(init=False)

    def __post_init__(self):
        """Post-initialization processing to create the directory structure."""
        self.data = Directory(dirname="data", parent=self.root)
        self.encode = Directory(dirname="encode", parent=self.data.path)
        self.media = Directory(dirname="media", parent=self.data.path)
        self.torrents = Directory(dirname="torrents", parent=self.data.path)


if __name__ == "__main__":
    # Example usage
    try:
        dirmap_instance = DirMap()
        frog.info(dirmap_instance)
    except ValueError as e:
        frog.error(e)
