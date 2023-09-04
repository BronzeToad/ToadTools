from enum import Enum


# =========================================================================== #

class FileType(Enum):
    # Text-based file types
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
    # Binary file types
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