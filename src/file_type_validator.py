import csv
import json
import xml.etree.ElementTree as ET
from configparser import ConfigParser
from pathlib import Path
from typing import Union
from warnings import warn

import yaml
from PIL import Image
from PyPDF2 import PdfFileReader
from cv2 import VideoCapture
from soundfile import SoundFile

from src.enum_hatchery import FileCheckType, FileType
from src.file_utils import check_filepath


# =========================================================================== #

class FileTypeValidator:
    """
    This class provides methods for validating files against their expected types.

    Attributes:
        file_path (str): The path to the file that needs to be validated.
        file_type (FileType): The expected type of the file. This should be an
            enum or similar type.

    Methods:
        validate(): Validates the file against its expected type and returns a
            boolean indicating the validity.
    """

    def __init__(
        self,
        file_path: Union[str, Path],
        file_type: FileType
    ):
        self.file_path = str(file_path)
        self.file_type = file_type

    def validate(self) -> bool:
        """Validates a file against its expected file type."""
        type_validator_map = self._get_type_validator_map()
        check_filepath(self.file_path, FileCheckType.NOT_FOUND)
        if self.file_type not in type_validator_map:
            warn("File type not supported for validation.")
            return False
        try:
            return type_validator_map[self.file_type]()
        except Exception as e:
            warn(f"Unable to validate {self.file_path}: {str(e)}.")
            return False

    def _get_type_validator_map(self) -> dict:
        """Returns a dictionary mapping file types to validation functions."""
        return {
            FileType.JSON: self._validate_json,
            FileType.HTML: self._validate_html,
            FileType.SQL : self._validate_sql,
            FileType.XML : self._validate_xml,
            FileType.CSV : self._validate_csv,
            FileType.YAML: self._validate_yaml,
            FileType.TXT : self._validate_text,
            FileType.MD  : self._validate_text,
            FileType.INI : self._validate_ini,
            FileType.LOG : self._validate_text,
            FileType.CONF: self._validate_text,
            FileType.PY  : self._validate_text,
            FileType.JS  : self._validate_text,
            FileType.CSS : self._validate_text,
            FileType.JPG : self._validate_image,
            FileType.PNG : self._validate_image,
            FileType.GIF : self._validate_image,
            FileType.BMP : self._validate_image,
            FileType.TIFF: self._validate_image,
            FileType.PDF : self._validate_pdf,
            FileType.MP3 : self._validate_audio,
            FileType.WAV : self._validate_audio,
            FileType.FLAC: self._validate_audio,
            FileType.MP4 : self._validate_video,
            FileType.AVI : self._validate_video,
            FileType.MKV : self._validate_video,
            FileType.MOV : self._validate_video,
            FileType.WMV : self._validate_video
        }


    def _validate_image(self) -> bool:
        """Validates if a given file is a readable image."""
        try:
            with Image.open(self.file_path) as img:
                img.verify()
            return True
        except Exception as e:
            warn(f"Invalid Image file: {self.file_path}, Error: {e}")
            return False


    def _validate_audio(self) -> bool:
        """Validates if a given file is a readable audio file."""
        try:
            with SoundFile(self.file_path):
                pass
            return True
        except Exception as e:
            warn(f"Invalid Audio file: {self.file_path}, Error: {e}")
            return False

    def _validate_video(self) -> bool:
        """Validates if a given file is a readable video file."""
        try:
            video = VideoCapture(self.file_path)
            isOpened = video.isOpened()
            video.release()
            return isOpened
        except Exception as e:
            warn(f"Invalid Video file: {self.file_path}, Error: {e}")
            return False

    def _validate_pdf(self) -> bool:
        """Validates a PDF file."""
        try:
            with open(self.file_path, 'rb') as f:
                reader = PdfFileReader(f)
                if reader.isEncrypted:
                    warn("PDF file is encrypted, unable to validate.")
                    return False
            return True
        except Exception as e:
            warn(f"Invalid PDF file: {self.file_path}, Error: {e}")
            return False

    def _validate_json(self) -> bool:
        """Validates a JSON file."""
        try:
            with open(self.file_path, 'r') as f:
                json.load(f)
            return True
        except json.JSONDecodeError:
            warn(f"Invalid JSON file: {self.file_path}")
            return False

    def _validate_csv(self) -> bool:
        """Validates a CSV file."""
        try:
            with open(self.file_path, 'r') as f:
                reader = csv.reader(f)
                next(reader)
            return True
        except csv.Error:
            warn(f"Invalid CSV file: {self.file_path}")
            return False

    def _validate_html(self) -> bool:
        """Validates an HTML file."""
        try:
            with open(self.file_path, 'r') as f:
                return '<html>' in f.read().lower()
        except Exception as e:
            warn(f"Invalid HTML file: {self.file_path}, Error: {e}")
            return False

    def _validate_xml(self) -> bool:
        """Validates if the given file is a well-formed XML file."""
        try:
            ET.parse(self.file_path)
            return True
        except ET.ParseError:
            warn(f"Invalid XML file: {self.file_path}")
            return False

    def _validate_yaml(self) -> bool:
        """Validates if the given file is a well-formed YAML file."""
        try:
            with open(self.file_path, 'r') as f:
                yaml.safe_load(f)
            return True
        except yaml.YAMLError:
            warn(f"Invalid YAML file: {self.file_path}")
            return False

    def _validate_sql(self) -> bool:
        """Validates if the given file contains SQL keywords."""
        sql_keywords = [
            'select', 'from', 'where', 'insert', 'update',
            'delete', 'create', 'alter', 'drop'
        ]
        try:
            with open(self.file_path, 'r') as f:
                content = f.read().lower()
            return any(keyword in content for keyword in sql_keywords)
        except Exception as e:
            warn(f"Invalid SQL file: {self.file_path}, Error: {e}")
            return False

    def _validate_ini(self) -> bool:
        """Validates if the file object contains valid INI data."""
        try:
            config = ConfigParser()
            with open(self.file_path, 'r') as f:
                config.read_file(f)
            return True
        except Exception as e:
            warn(f"Invalid INI file: {self.file_path}, Error: {e}")
            return False

    def _validate_text(self) -> bool:
        """Validates if the file object contains readable text."""
        try:
            with open(self.file_path, 'r') as f:
                return bool(f.read())
        except Exception as e:
            warn(f"Invalid Text file: {self.file_path}, Error: {e}")
            return False
