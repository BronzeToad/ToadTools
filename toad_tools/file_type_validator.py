from configparser import ConfigParser
from csv import reader as csv_reader
from json import load as json_load
from pathlib import Path
from typing import Union
from warnings import warn
from xml.etree.ElementTree import parse as et_parse

from PIL import Image
from PyPDF2 import PdfFileReader
from cv2 import VideoCapture
from soundfile import SoundFile
from yaml import safe_load as yaml_safe_load

from toad_tools.enum_hatchery import FileCheckType, FileType
from toad_tools.file_utils import check_filepath


# =========================================================================== #

def validate_file_type(
    file_path: Union[str, Path],
    file_type: FileType
) -> bool:
    """
    Validates a file against its expected file type.

    This function checks if a given file matches its expected file type by
    invoking the corresponding validation function from a pre-defined map of
    type validators.

    Args:
        file_path (Union[str, Path]): Path to file that needs to be validated.
        file_type (FileType): An enum representing the expected file type.

    Returns:
        bool: True if the file is a valid instance of the expected file type,
            False otherwise.

    Raises:
        Warning: If the file type is not supported for validation, or if
            the validation fails, or if an error occurs during validation.
    """
    type_validator_map = get_type_validator_map()

    if file_type not in type_validator_map:
        return "File type not supported for validation."

    check_filepath(file_path, FileCheckType.NOT_FOUND)

    try:
        with open(file_path, 'r') as file:
            if not type_validator_map[file_type](file):
                warn(f"Invalid {file_type.name} file.")
                return False
    except Exception as e:
        warn(f"Unable to validate {file_path}: {str(e)}.")
        return False

    return True


def get_type_validator_map():
    """
    Returns a dictionary mapping file types to validation functions.

    This function provides a map of FileType enums to validation functions,
    which can be used to check if a given file adheres to the expected format
    or structure for its type. The validation functions should accept a file
    object and return a boolean indicating the validity of the file.

    Returns:
        dict: A dictionary where the keys are FileType enums and the values are
            functions that take a file object and return a boolean.
    """

    return {
        FileType.JSON: _validate_json,
        FileType.HTML: _validate_html,
        FileType.SQL : _validate_sql,
        FileType.XML : _validate_xml,
        FileType.CSV : _validate_csv,
        FileType.YAML: _validate_yaml,
        FileType.TXT : _validate_text,
        FileType.MD  : _validate_text,
        FileType.INI : _validate_ini,
        FileType.LOG : _validate_text,
        FileType.CONF: _validate_text,
        FileType.PY  : _validate_text,
        FileType.JS  : _validate_text,
        FileType.CSS : _validate_text,
        FileType.JPG : _validate_image,
        FileType.PNG : _validate_image,
        FileType.GIF : _validate_image,
        FileType.BMP : _validate_image,
        FileType.TIFF: _validate_image,
        FileType.PDF : _validate_pdf,
        FileType.MP3 : _validate_audio,
        FileType.WAV : _validate_audio,
        FileType.FLAC: _validate_audio,
        FileType.MP4 : _validate_video,
        FileType.AVI : _validate_video,
        FileType.MKV : _validate_video,
        FileType.MOV : _validate_video,
        FileType.WMV : _validate_video
    }

def _validate_image(f):
    """
    Validates if a given file is a readable image.

    This function uses the PIL library to attempt to open and verify the image.

    Args:
        f (file): The file object to be validated.

    Returns:
        bool: True if the file is a valid image, False otherwise.
    """
    try:
        with Image.open(f) as img:
            img.verify()
        return True
    except:
        return False

def _validate_audio(f):
    """
    Validates if a given file is a readable audio file.

    This function uses the SoundFile library to attempt to open the audio file.

    Args:
        f (file): The file object to be validated.

    Returns:
        bool: True if the file is a valid audio file, False otherwise.
    """
    try:
        SoundFile(f)
        return True
    except:
        return False

def _validate_video(f):
    """
    Validates if a given file is a readable video file.

    This function uses the OpenCV library to attempt to open and
    verify the video file.

    Args:
        f (file): The file object to be validated.

    Returns:
        bool: True if the file is a valid video file, False otherwise.
    """
    try:
        video = VideoCapture(f)
        return video.isOpened()
    except:
        return False

def _validate_pdf(f):
    """
    Validates a PDF file.

    This function checks if a given PDF file is readable and not encrypted.

    Args:
        f (file): A file object opened in read mode.

    Returns:
        bool: True if the file is a valid PDF, False otherwise.

    Raises:
        Warning: If the PDF is encrypted.
    """
    try:
        reader = PdfFileReader(f)
        if reader.isEncrypted:
            warn("PDF file is encrypted, unable to validate...")
            return False
        return True
    except:
        return False

def _validate_json(f):
    """
    Validates a JSON file.

    This function checks if a given JSON file is properly formatted.

    Args:
        f (file): A file object opened in read mode.

    Returns:
        bool: True if the file is a valid JSON, False otherwise.
    """
    try:
        json_load(f)
        return True
    except:
        return False

def _validate_html(f):
    """
    Validates an HTML file.

    This function checks if a given HTML file contains the '<html>' tag,
    a basic indicator of an HTML file.

    Args:
        f (file): A file object opened in read mode.

    Returns:
        bool: True if the file is a valid HTML, False otherwise.
    """
    try:
        return '<html>' in f.read().lower()
    except:
        return False

def _validate_xml(f):
    """
    Validates if the given file is a well-formed XML file.

    Args:
        f (file object): A file object representing the XML file.

    Returns:
        bool: True if the file is a well-formed XML, False otherwise.
    """
    try:
        et_parse(f)
        return True
    except:
        return False

def _validate_yaml(f):
    """
    Validates if the given file is a well-formed YAML file.

    Args:
        f (file object): A file object representing the YAML file.

    Returns:
        bool: True if the file is a well-formed YAML, False otherwise.
    """
    try:
        yaml_safe_load(f)
        return True
    except:
        return False

def _validate_sql(f):
    """
    Validates if the given file is a SQL file containing SQL keywords.

    Args:
        f (file object): A file object representing the SQL file.

    Returns:
        bool: True if the file contains SQL keywords, False otherwise.
    """
    sql_keywords = [
        'select', 'from', 'where', 'insert', 'update',
        'delete', 'create', 'alter', 'drop'
    ]
    try:
        content = f.read().lower()
        return any(keyword in content for keyword in sql_keywords)
    except:
        return False

def _validate_csv(f):
    """
    Validates if the file object contains valid CSV data.

    This function reads the file object to see if it conforms to the CSV
    (Comma Separated Values) format. It uses Python's built-in `csv.reader`.

    Args:
        f (file object): A file object opened in read mode.

    Returns:
        bool: True if the file is a valid CSV file, False otherwise.
    """
    try:
        reader = csv_reader(f)
        next(reader)
        return True
    except:
        return False

def _validate_ini(f):
    """
    Validates if the file object contains valid INI data.

    This function reads the file object to see if it conforms to the INI
    format. It uses Python's built-in `ConfigParser`.

    Args:
        f (file object): A file object opened in read mode.

    Returns:
        bool: True if the file is a valid INI file, False otherwise.
    """
    try:
        config = ConfigParser()
        config.read_file(f)
        return True
    except:
        return False

def _validate_text(f):
    """
    Validates if the file object contains readable text.

    This function reads the file object to check if it contains any text.
    It returns True if the file is not empty.

    Args:
        f (file object): A file object opened in read mode.

    Returns:
        bool: True if the file is not empty, False otherwise.
    """
    try:
        return bool(f.read())
    except:
        return False
