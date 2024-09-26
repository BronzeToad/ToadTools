from pathlib import Path
from typing import Union

from pydantic import BaseModel

from src.toad_logger import ToadLogger, LogLevel

logging = ToadLogger("dolphin.drvr.directory", level=LogLevel.DEBUG)

class Directory(BaseModel):
    name: str

    parent_path: Union[str, Path]


if __name__ == '__main__':
    pass

