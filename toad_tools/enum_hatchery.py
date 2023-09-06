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

class CurrencyType(Enum):
    USD = {'symbol': '$', 'placement': 'before', 'decimal_places': 2}
    EUR = {'symbol': '€', 'placement': 'before', 'decimal_places': 2}
    GBP = {'symbol': '£', 'placement': 'before', 'decimal_places': 2}
    JPY = {'symbol': '¥', 'placement': 'before', 'decimal_places': 0}
    INR = {'symbol': '₹', 'placement': 'before', 'decimal_places': 2}
    AUD = {'symbol': 'A$', 'placement': 'before', 'decimal_places': 2}
    CAD = {'symbol': 'C$', 'placement': 'before', 'decimal_places': 2}
    CHF = {'symbol': 'CHF', 'placement': 'after', 'decimal_places': 2}
    CNY = {'symbol': '¥', 'placement': 'before', 'decimal_places': 2}
    BRL = {'symbol': 'R$', 'placement': 'before', 'decimal_places': 2}
    MXN = {'symbol': 'MX$', 'placement': 'before', 'decimal_places': 2}
    NZD = {'symbol': 'NZ$', 'placement': 'before', 'decimal_places': 2}
    NOK = {'symbol': 'kr', 'placement': 'before', 'decimal_places': 2}
    RUB = {'symbol': '₽', 'placement': 'before', 'decimal_places': 2}
    ZAR = {'symbol': 'R', 'placement': 'before', 'decimal_places': 2}

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
