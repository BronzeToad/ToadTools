from enum import Enum, auto


# =========================================================================== #

class ChecksumType(Enum):
    SHA256 = auto()
    MD5 = auto()
    SHA1 = auto()

class OperationType(Enum):
    MOVE = auto()
    COPY = auto()

class SerializationType(Enum):
    JSON = auto()
    PICKLE = auto()

class FileCheckType(Enum):
    EXISTS = auto()
    NOT_FOUND = auto()

class FileType(Enum):
    JSON = "json"
    HTML = "html"
    SQL = "sql"
    XML = "xml"
    CSV = "csv"
    YAML = "yaml"
    TXT = "txt"
    MD = "md"
    INI = "ini"
    LOG = "log"
    CONF = "conf"
    PY = "py"
    JS = "js"
    CSS = "css"
    JPG = "jpg"
    PNG = "png"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"
    PDF = "pdf"
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    MP4 = "mp4"
    AVI = "avi"
    MKV = "mkv"
    MOV = "mov"
    WMV = "wmv"
