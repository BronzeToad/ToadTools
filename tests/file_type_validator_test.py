from unittest.mock import mock_open, patch

import pytest

from src.enum_hatchery import FileType
from src.file_type_validator import FileTypeValidator


# =========================================================================== #

file_type_to_method = {
    FileType.JSON: '_validate_json',
    FileType.HTML: '_validate_html',
    FileType.SQL : '_validate_sql',
    FileType.XML : '_validate_xml',
    FileType.CSV : '_validate_csv',
    FileType.YAML: '_validate_yaml',
    FileType.TXT : '_validate_text',
    FileType.MD  : '_validate_text',
    FileType.INI : '_validate_ini',
    FileType.LOG : '_validate_text',
    FileType.CONF: '_validate_text',
    FileType.PY  : '_validate_text',
    FileType.JS  : '_validate_text',
    FileType.CSS : '_validate_text',
    FileType.JPG : '_validate_image',
    FileType.PNG : '_validate_image',
    FileType.GIF : '_validate_image',
    FileType.BMP : '_validate_image',
    FileType.TIFF: '_validate_image',
    FileType.PDF : '_validate_pdf',
    FileType.MP3 : '_validate_audio',
    FileType.WAV : '_validate_audio',
    FileType.FLAC: '_validate_audio',
    FileType.MP4 : '_validate_video',
    FileType.AVI : '_validate_video',
    FileType.MKV : '_validate_video',
    FileType.MOV : '_validate_video',
    FileType.WMV : '_validate_video'
}


@pytest.mark.parametrize("file_type,method", file_type_to_method.items())
def test_validate_files(file_type, method):
    # Mock file open for text-based files
    m = mock_open(read_data='data') if file_type in [
        FileType.JSON, FileType.HTML, FileType.SQL,
        FileType.XML, FileType.CSV, FileType.TXT
    ] else mock_open(read_data=b'data')

    with patch('builtins.open', m):
        validator = FileTypeValidator("somepath", file_type)

        # Mock the specific validation method for this FileType
        with patch.object(validator, method, return_value=True):
            assert validator.validate() == True


def test_validate_unsupported_file_type():
    validator = FileTypeValidator("somepath", "unsupported_type")
    assert validator.validate() == False


def test_validate_exception_raised():
    with patch('builtins.open', mock_open(read_data='data')):
        validator = FileTypeValidator("somepath", FileType.JSON)

        # Mock _validate_json to raise an exception
        with patch.object(validator, '_validate_json', side_effect=Exception("Some Error")):
            assert validator.validate() == False
