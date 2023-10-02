import codecs
import csv
import hashlib
import json
import os
import pickle
import re
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple, Union

import chardet
import soundfile
import yaml
from PIL import Image
from cv2 import VideoCapture
from filelock import FileLock, Timeout

from src.enum_hatchery import ChecksumType, FileCheckType, FileType, OperationType, SerializationType
from src.file_type_validator import FileTypeValidator


# =========================================================================== #

def get_file_type_map() -> Dict[FileType, Tuple[str, Callable]]:
    """
    Returns a mapping of file types to read modes and read functions.

    This function returns a dictionary where the keys are FileType enums and
    the values are tuples containing the read mode ('r' or 'rb') and a callable
    read function to handle files of that type.

    Returns:
        Dict[FileType, Tuple[str, Callable]]: A dictionary mapping file types
        to read modes and read functions.
    """

    def _read_text_file(f):
        """Reads and returns the entire content of a text file."""
        return f.read()

    def _read_image(f):
        """Reads and returns an image file as a PIL Image object."""
        return Image.open(f)

    def _read_audio(f):
        """Reads and returns an audio file as a soundfile object."""
        return soundfile.read(f)

    def _read_video(f):
        """Reads and returns a video file as a cv2 VideoCapture object."""
        return VideoCapture(f)

    return {
        FileType.JSON: ('r', json.load),
        FileType.HTML: ('r', _read_text_file),
        FileType.SQL : ('r', _read_text_file),
        FileType.XML : ('r', _read_text_file),
        FileType.CSV: ('r', csv.reader),
        FileType.YAML: ('r', yaml.safe_load),
        FileType.TXT: ('r', _read_text_file),
        FileType.MD: ('r', _read_text_file),
        FileType.INI: ('r', _read_text_file),
        FileType.LOG: ('r', _read_text_file),
        FileType.CONF: ('r', _read_text_file),
        FileType.PY: ('r', _read_text_file),
        FileType.JS: ('r', _read_text_file),
        FileType.CSS: ('r', _read_text_file),
        FileType.JPG: ('rb', _read_image),
        FileType.PNG: ('rb', _read_image),
        FileType.GIF: ('rb', _read_image),
        FileType.BMP: ('rb', _read_image),
        FileType.TIFF: ('rb', _read_image),
        FileType.PDF: ('rb', _read_text_file),
        FileType.MP3: ('rb', _read_audio),
        FileType.WAV: ('rb', _read_audio),
        FileType.FLAC: ('rb', _read_audio),
        FileType.MP4: ('rb', _read_video),
        FileType.AVI: ('rb', _read_video),
        FileType.MKV: ('rb', _read_video),
        FileType.MOV: ('rb', _read_video),
        FileType.WMV: ('rb', _read_video)
    }


def check_filepath(
    filepath: Path,
    check_type: FileCheckType
) -> None:
    """
    Checks the existence or absence of a file and raises appropriate errors.

    This function performs checks on a file path based on the specified check
    type. It either checks if the file exists and raises a `FileExistsError`,
    or checks if the file is not found and raises a `FileNotFoundError`.

    Args:
        filepath (Path): The full path to the file that needs to be checked.
        check_type (FileCheckType): An enum indicating the type of check to
            perform. Use `FileCheckType.EXISTS` to check if the file exists,
            and `FileCheckType.NOT_FOUND` to check if the file is not found.

    Raises:
        FileExistsError: If the check type is `FileCheckType.EXISTS` and the
            file exists.
        FileNotFoundError: If the check type is `FileCheckType.NOT_FOUND` and
            the file is not found.
    """
    folder = os.path.dirname(filepath)
    filename = os.path.basename(filepath)

    if check_type == FileCheckType.EXISTS and filepath.is_file():
        raise FileExistsError(f"{filename} already exists in {folder}.")

    if check_type == FileCheckType.NOT_FOUND and not filepath.is_file():
        raise FileNotFoundError(f"{filename} not found in {folder}.")


def force_extension(
    filename: str,
    extension: str
) -> str:
    """
    Ensures that a filename has the specified extension.

    This function takes a filename and an extension, then returns the filename
    with the given extension. If the filename already has the correct
    extension, it is returned as-is. Otherwise, the correct extension is added.
    Extensions are case-insensitive and leading dots are optional.

    Args:
        filename (str): The name of the file, which can include an existing
            extension.
        extension (str): The desired file extension, with or without a leading
            dot.

    Returns:
        str: The filename with the specified extension.

    Raises:
        ValueError: If either the filename or extension is empty or None.
    """
    if not filename:
        raise ValueError("Filename cannot be empty or None.")

    if not extension:
        raise ValueError("Extension cannot be empty or None.")

    normalized_extension = extension.lstrip('.').lower()
    current_extension = Path(filename).suffix.lstrip('.').lower()

    if filename.endswith('.'):
        filename = filename.rstrip('.')

    if not current_extension or normalized_extension != current_extension:
        return f"{filename}.{normalized_extension}"

    return filename


def get_file(
    folder: str,
    filename: str,
    file_type: FileType,
    find_replace: Optional[Dict[str, str]] = None
) -> Union[Dict, str, bytes]:
    """
    Reads a file from a specified folder.

    This function reads a file based on its type and location. Additionally,
    it can perform find-replace operations on the file content if specified.

    Args:
        folder (str): The path to the folder containing the file.
        filename (str): The name of the file to read.
        file_type (FileType): Enum representing the file type.
        find_replace (Optional[Dict[str, str]]): A dictionary for find-replace
            operations to be performed on the file's content. Keys are the
            substrings to find, and values are the substrings to replace them
            with. Defaults to None.

    Returns:
        Union[Dict, str, bytes]: The content of the file. The type of the
            returned object depends on the file type:
            - For JSON files, a dictionary is returned.
            - For HTML and SQL files, a string is returned.
            - For other file types, bytes may be returned.

    Raises:
        ValueError: If the folder or filename is empty or None.
        FileNotFoundError: If the specified file is not found.
        ValueError: If an unsupported file type is specified.
    """
    if not folder or not filename:
        raise ValueError("Folder and filename cannot be empty or None.")

    standardized_filename = force_extension(filename, file_type.name.lower())
    filepath = Path(folder) / standardized_filename

    file_type_map = get_file_type_map()

    if file_type not in file_type_map:
        raise ValueError(f"Unsupported file type: {file_type.name}")

    read_mode, read_func = file_type_map[file_type]

    with open(filepath, read_mode) as file:
        obj = read_func(file)

    if find_replace and isinstance(obj, str):
        for key, val in find_replace.items():
            obj = obj.replace(key, str(val))

    return obj


def duplicate_file(
    source_folder: str,
    source_filename: str,
    dest_folder: str,
    file_type: FileType,
    dest_filename: Optional[str] = None
) -> str:
    """
    Duplicates a file from a source folder to a destination folder.

    This function duplicates a file by reading its content from the source
    folder and writing it to the destination folder. Optionally, the
    destination filename can be specified.

    Args:
        source_folder (str): The path to the folder containing the source file.
        source_filename (str): The name of the source file.
        dest_folder (str): The path to the destination folder.
        file_type (FileType): Enum representing the file type.
        dest_filename (Optional[str]): The name for the destination file.
            Defaults to `source_filename`.

    Returns:
        str: The full path to the duplicated file as a string.

    Raises:
        ValueError: If the source folder, source filename, or destination
            folder is empty or None.
        RuntimeError: If the file type is not supported for duplication.
        FileExistsError: If the destination file already exists.
    """
    if not source_folder or not source_filename or not dest_folder:
        raise ValueError("Source folder, source filename, and destination "
                         "folder cannot be empty or None.")

    source_content = get_file(source_folder, source_filename, file_type)

    if source_content is None:
        raise RuntimeError(f"File type {file_type.name} is not supported "
                           f"for duplication.")

    if dest_filename is None:
        dest_filename = source_filename

    dest_filename = force_extension(dest_filename, file_type.name.lower())
    Path(dest_folder).mkdir(parents=True, exist_ok=True)
    dest_filepath = Path(dest_folder) / dest_filename
    check_filepath(dest_filepath, FileCheckType.EXISTS)

    write_mode = 'wb' if isinstance(source_content, bytes) else 'w'
    with open(dest_filepath, write_mode) as dest_file:
        if isinstance(source_content, bytes):
            dest_file.write(source_content)
        elif isinstance(source_content, dict):
            json.dump(source_content, dest_file)
        else:
            dest_file.write(source_content)

    return str(dest_filepath)


def delete_file(
    folder: str,
    filename: str,
    file_type: FileType,
    require_confirmation: Optional[bool] = False
) -> bool:
    """
    Deletes a file with optional confirmation steps.

    This function deletes a specified file and can also require a manual
    confirmation before proceeding with the deletion.

    Args:
        folder (str): The path to the folder containing the file to delete.
        filename (str): The name of the file to delete.
        file_type (FileType): Enum representing the file type.
        require_confirmation (Optional[bool]): Whether to require a
            confirmation before deletion. Defaults to False.

    Returns:
        bool: True if the file was deleted, False otherwise.

    Raises:
        ValueError: If either the folder or filename is empty or None.
        FileNotFoundError: If the specified file is not found in the folder.
    """
    if not folder or not filename:
        raise ValueError("Folder and filename cannot be empty or None.")

    standardized_filename = force_extension(filename, file_type.name.lower())
    filepath = Path(folder) / standardized_filename
    check_filepath(filepath, FileCheckType.EXISTS)

    if require_confirmation:
        confirm = input(f"Are you sure you want to delete "
                        f"'{standardized_filename}'? [y/N]: ")
        if confirm.lower() != 'y':
            print("File deletion cancelled.")
            return False

    filepath.unlink()
    print(f"'{standardized_filename}' has been deleted.")
    return True


def rename_file(
    src_folder: str,
    src_filename: str,
    src_file_type: FileType,
    dest_folder: Optional[str] = None,
    dest_filename: Optional[str] = None,
    dest_file_type: Optional[FileType] = None,
    overwrite: bool = False
) -> Union[str, None]:
    """
    Renames a file, with optional move, name change, and overwrite features.

    This function allows renaming a file and additionally offers the ability
    to move it to a different folder, change its name, or change its file
    type. If the destination file exists, it can optionally be overwritten.

    Args:
        src_folder (str): The path to the folder containing the source file.
        src_filename (str): The name of the source file.
        src_file_type (FileType): Enum representing the source file type.
        dest_folder (Optional[str]): The path to the destination folder.
            Defaults to `src_folder`.
        dest_filename (Optional[str]): The name for the destination file.
            Defaults to `src_filename`.
        dest_file_type (Optional[FileType]): Enum representing the destination
            file type. Defaults to `src_file_type`.
        overwrite (bool): Whether to overwrite the destination file if it
            exists. Defaults to False.

    Returns:
        Union[str, None]: The full path to the renamed file as a string, or
            None if the operation failed.

    Raises:
        ValueError: If either the source folder or source filename is empty
            or None.
        FileNotFoundError: If the source file is not found in the source
            folder.
        FileExistsError: If the destination file already exists and `overwrite`
            is False.
    """
    if not src_folder or not src_filename:
        raise ValueError("Source folder and source filename cannot be "
                         "empty or None.")

    src_filename = force_extension(src_filename, src_file_type.name.lower())
    src_full_path = Path(src_folder) / src_filename
    check_filepath(src_full_path, FileCheckType.EXISTS)

    dest_folder = dest_folder or src_folder
    dest_filename = dest_filename or src_filename
    dest_file_type = dest_file_type or src_file_type
    dest_filename = force_extension(dest_filename, dest_file_type.name.lower())
    dest_full_path = Path(dest_folder) / dest_filename

    if not overwrite:
        check_filepath(dest_full_path, FileCheckType.NOT_FOUND)

    src_full_path.rename(dest_full_path)

    return str(dest_full_path)


def ensure_directory_exists(
    folder: str,
    create_if_missing: bool = True
) -> Optional[str]:
    """
    Ensures a directory exists at the specified folder path.

    This function checks if a directory exists at the given path. If the
    directory does not exist, it can optionally create it. If the path exists
    but is not a directory, an error is raised.

    Args:
        folder (str): The path to the directory to ensure exists.
        create_if_missing (bool): Whether to create the directory if it does
            not exist. Defaults to True.

    Returns:
        Optional[str]: The path to the directory as a string if it exists or
            was created, or None if `create_if_missing` is False and the
            directory does not exist.

    Raises:
        ValueError: If the folder path is empty or None.
        FileExistsError: If the path exists but is not a directory.
        PermissionError: If there's no permission to create the directory.
    """
    if not folder:
        raise ValueError("Folder cannot be empty or None.")

    path = Path(folder)

    if path.is_dir():
        return str(path)

    if path.exists():
        raise FileExistsError(f"The path {folder} exists but is "
                              f"not a directory.")

    if create_if_missing:
        try:
            path.mkdir(parents=True, exist_ok=True)
            return str(path)
        except PermissionError:
            raise PermissionError(f"Do not have permission to create "
                                  f"directory at {folder}")

    return None


def directory_cleanup(
    directory: str,
    older_than_days: Optional[int] = None,
    extensions: Optional[List[str]] = None
) -> int:
    """
    Cleans up a directory by deleting files based on age and file extensions.

    This function deletes files from the specified directory based on their
    age and/or file extensions. You can specify a time limit in days, and
    only files older than that will be deleted. Additionally, you can
    specify a list of file extensions to limit which files are deleted.

    Args:
        directory (str): The path to the directory to clean up.
        older_than_days (Optional[int]): The age limit for files to be
            deleted. Files older than this number of days will be deleted.
            Defaults to None, which means all files will be considered.
        extensions (Optional[List[str]]): A list of file extensions to
            consider for deletion. Defaults to None, which means all
            file types will be considered.

    Returns:
        int: The number of files that were deleted.

    Raises:
        ValueError: If the directory is empty or None.
        FileNotFoundError: If the specified directory does not exist.
    """
    if not directory:
        raise ValueError("Directory cannot be empty or None.")

    dir_path = Path(directory)
    if not dir_path.is_dir():
        raise FileNotFoundError(f"The specified directory {directory} "
                                f"does not exist.")

    deleted_files_count = 0
    current_time = time.time()

    for file_path in dir_path.iterdir():
        if not file_path.is_file():
            continue

        delete_file = True

        if older_than_days is not None:
            file_age_seconds = current_time - file_path.stat().st_mtime
            file_age_days = file_age_seconds / (24 * 60 * 60)
            if file_age_days <= older_than_days:
                delete_file = False

        if delete_file and extensions:
            file_extension = file_path.suffix.lower()
            if file_extension not in [ext.lower() for ext in extensions]:
                delete_file = False

        if delete_file:
            os.remove(file_path)
            deleted_files_count += 1

    return deleted_files_count


def get_file_size(
    folder: str,
    filename: str,
    file_type: Optional[FileType] = None
) -> int:
    """
    Gets the size of a file in bytes.

    This function retrieves the file size for a given file located in a
    specified folder. Optionally, the file type can be provided to ensure
    the filename has the correct extension.

    Args:
        folder (str): The path to the folder containing the file.
        filename (str): The name of the file.
        file_type (Optional[FileType]): Enum representing the file type.
            If provided, ensures the filename has the correct extension.
            Defaults to None.

    Returns:
        int: The file size in bytes.

    Raises:
        ValueError: If either the folder or filename is empty or None.
        FileNotFoundError: If the file is not found in the specified folder.
    """
    if not folder or not filename:
        raise ValueError("Folder and filename cannot be empty or None.")

    if file_type:
        filename = force_extension(filename, file_type.name.lower())

    filepath = Path(folder) / filename
    check_filepath(filepath, FileCheckType.NOT_FOUND)

    return os.path.getsize(filepath)


def get_last_modified(
    folder: str,
    filename: str,
    file_type: Optional[FileType] = None
) -> Union[datetime, None]:
    """
    Retrieves the last modified timestamp of a file.

    This function gets the last modified timestamp for a file located in a
    specified folder. Optionally, a file type can be specified to ensure
    that the filename has the correct extension.

    Args:
        folder (str): The path to the folder containing the file.
        filename (str): The name of the file.
        file_type (Optional[FileType]): Enum representing the file type.
            If provided, ensures the filename has the correct extension.
            Defaults to None.

    Returns:
        Union[datetime, None]: The last modified timestamp as a datetime
            object, or None if the file does not exist.

    Raises:
        ValueError: If either the folder or filename is empty or None.
    """
    if not folder or not filename:
        raise ValueError("Folder and filename cannot be empty or None.")

    if file_type:
        filename = force_extension(filename, file_type.name.lower())

    filepath = Path(folder) / filename

    if not filepath.is_file():
        return None

    timestamp = os.path.getmtime(filepath)
    return datetime.fromtimestamp(timestamp)


def validate_file_type(
    folder: str,
    filename: str,
    expected_type: FileType
) -> Optional[str]:
    """
    Validates a file's type against an expected file type.

    This function reads a file and validates its type using pre-defined
    type validation functions. If the file does not match the expected type,
    a message indicating the discrepancy is returned.

    Args:
        folder (str): The path to the folder containing the file.
        filename (str): The name of the file to validate.
        expected_type (FileType): Enum representing the expected file type.

    Returns:
        Optional[str]: A message indicating the result of the validation.
            Returns None if the file type is valid.

    Raises:
        ValueError: If either the folder or filename is empty or None.
    """
    if not folder or not filename:
        raise ValueError("Folder and filename cannot be empty or None.")

    std_filename = force_extension(filename, expected_type.name.lower())
    filepath = Path(folder) / std_filename
    return FileTypeValidator(filepath, expected_type).validate()


def concatenate_files(
    folder: str,
    filenames: List[str],
    file_type: FileType,
    output_filename: str,
    delimiter: Optional[str] = None
) -> None:
    """
    Concatenates multiple files of the same type into a single file.

    This function reads the content of each file in the `filenames` list,
    concatenates them, and writes the result to `output_filename`. An optional
    delimiter can be specified to separate the contents of each file.

    Args:
        folder (str): The path to the folder containing the files to concatenate.
        filenames (List[str]): A list of filenames to concatenate.
        file_type (FileType): Enum representing the file type.
        output_filename (str): The name for the output file.
        delimiter (Optional[str]): A string to insert between each file's
            content. Defaults to None, meaning files are concatenated directly.

    Raises:
        ValueError: If `folder`, `filenames`, or `output_filename` are empty
            or None.
        FileNotFoundError: If one or more files are not found in the folder.
    """
    if not folder or not filenames or not output_filename:
        raise ValueError("Folder, filenames, and output filename cannot be "
                         "empty or None.")

    try:
        contents = [
            get_file(folder, filename, file_type)
            for filename in filenames
        ]
    except FileNotFoundError as e:
        raise FileNotFoundError(f"One or more files not found. {str(e)}")

    combined = delimiter.join(contents) if delimiter else ''.join(contents)
    output_filepath = (
        Path(folder) / force_extension(output_filename, file_type.name.lower())
    )

    with open(output_filepath, 'w') as file:
        file.write(combined)


def count_lines(
    folder: str,
    filename: str,
    file_type: FileType
) -> Union[int, str]:
    """
    Counts the number of lines in a file.

    This function reads the content of a file and returns the number of lines
    it contains. For binary files where line count is not applicable, a
    specific message is returned.

    Args:
        folder (str): The path to the folder containing the file.
        filename (str): The name of the file.
        file_type (FileType): Enum representing the file type.

    Returns:
        Union[int, str]: The number of lines in the file if it is a text-based
            file. A message indicating that line count is not applicable for
            binary files.

    Raises:
        ValueError: If either the folder or filename is empty or None.
    """
    if not folder or not filename:
        raise ValueError("Folder and filename cannot be empty or None.")

    file_content = get_file(folder, filename, file_type)

    if isinstance(file_content, str):
        return len(file_content.splitlines())
    else:
        return "Line count is not applicable for binary files."


def convert_file_encoding(
    folder: str,
    filename: str,
    file_type: FileType,
    target_encoding: str,
    source_encoding: Optional[str] = None
) -> None:
    """
    Converts the encoding of a file to a target encoding.

    This function reads a file and converts its encoding to the specified
    target encoding. If the source encoding is not provided, it will be
    automatically detected.

    Args:
        folder (str): The path to the folder containing the file.
        filename (str): The name of the file to be converted.
        file_type (FileType): Enum representing the file type.
        target_encoding (str): The target encoding to convert the file to.
        source_encoding (Optional[str]): The source encoding of the file.
            If not provided, it will be automatically detected. Defaults to None.

    Returns:
        None: This function performs the conversion in-place and does not
            return any value.

    Raises:
        ValueError: If either the folder or filename is empty or None.
    """
    if not folder or not filename:
        raise ValueError("Folder and filename cannot be empty or None.")

    content = get_file(folder, filename, file_type)

    if source_encoding is None:
        detection_result = chardet.detect(content.encode())
        source_encoding = detection_result['encoding']

    converted = content.encode(source_encoding).decode(target_encoding)
    output_filepath = (
        Path(folder) / force_extension(filename, file_type.name.lower())
    )

    with codecs.open(output_filepath,
                     mode='w',
                     encoding=target_encoding) as file:
        file.write(converted)


def search_text_in_file(
    folder: str,
    filename: str,
    query: str,
    is_regex: bool = False,
    case_sensitive: bool = False,
    file_type: Optional[FileType] = None
) -> List[str]:
    """
    Searches text within a file and returns lines where the query is found.

    This function reads the file line-by-line and checks for the presence of a
    query string or regular expression. Matching lines are returned in a list.

    Args:
        folder (str): The path to the folder containing the file to search in.
        filename (str): The name of the file to search in.
        query (str): The text or regular expression to search for.
        is_regex (bool): Whether the query is a regular expression. Defaults
            to False.
        case_sensitive (bool): Whether the search should be case-sensitive.
            Defaults to False.
        file_type (Optional[FileType]): Enum representing the file type. If
            provided, filename is forced to this extension. Defaults to None.

    Returns:
        List[str]: A list of lines from the file where the query was found.

    Raises:
        ValueError: If the folder, filename, or query is empty or None.
        FileNotFoundError: If specified file is not found in the given folder.
    """

    if not folder or not filename or not query:
        raise ValueError("Folder, filename, and query cannot be empty or None.")

    if file_type:
        filename = force_extension(filename, file_type.name.lower())

    filepath = Path(folder) / filename
    check_filepath(filepath, FileCheckType.NOT_FOUND)

    found_lines = []

    def text_search(query, line):
        return query in line

    with open(filepath, 'r') as file:
        for line in file:
            search_func = re.search if is_regex else text_search
            target_line = line if case_sensitive else line.lower()
            target_query = query if case_sensitive else query.lower()

            if search_func(target_query, target_line):
                found_lines.append(line.strip())

    return found_lines


def calculate_checksum(
    folder: str,
    filename: str,
    checksum_type: ChecksumType = ChecksumType.SHA256,
    buffer_size: int = 65536
) -> Optional[str]:
    """
    Calculates the checksum of a file using a specified algorithm.

    This function computes the checksum of a file located in a given folder,
    using the specified checksum algorithm (e.g., SHA256, MD5). The function
    reads the file in chunks to efficiently handle large files.

    Args:
        folder (str): The path to the folder containing the file.
        filename (str): The name of the file for which to calculate checksum.
        checksum_type (ChecksumType): Enum representing the checksum algorithm.
            Defaults to ChecksumType.SHA256.
        buffer_size (int): The size of each read from the file to compute the
            checksum. Defaults to 65536.

    Returns:
        Optional[str]: The computed checksum as a hexadecimal string, or None
            if the computation failed.

    Raises:
        ValueError: If either the folder or filename is empty or None.
        FileNotFoundError: If the file is not found in the specified folder.
    """
    if not folder or not filename:
        raise ValueError("Folder and filename cannot be empty or None.")

    filepath = Path(folder) / filename
    check_filepath(filepath, FileCheckType.NOT_FOUND)
    hash_obj = hashlib.new(checksum_type.value)

    with open(filepath, 'rb') as f:
        while chunk := f.read(buffer_size):
            hash_obj.update(chunk)

    return hash_obj.hexdigest()


def bulk_rename(
    folder: str,
    rename_func: Callable[[str], str]
) -> None:
    """
    Renames files in bulk within a given folder based on a renaming function.

    This function iterates through each file in a specified folder and renames
    it using a provided rename function. The rename function takes the stem of
    the old filename as an argument and returns the new name.

    Args:
        folder (str): The path to the folder containing the files to be renamed.
        rename_func (Callable[[str], str]): A function that takes the old
            filename (without extension) and returns the new filename.

    Returns:
        None

    Raises:
        ValueError: If either the folder or rename function is empty or None.
        NotADirectoryError: If the specified folder is not a directory.
        FileExistsError: If a renamed file would overwrite an existing file.
    """
    if not folder or not rename_func:
        raise ValueError("Folder and rename function cannot be empty or None.")

    folder_path = Path(folder)

    if not folder_path.is_dir():
        raise NotADirectoryError(f"{folder} is not a directory.")

    for file_path in folder_path.iterdir():
        if file_path.is_file():
            old_name = file_path.stem
            old_extension = file_path.suffix
            new_name = rename_func(old_name)
            new_file_path = folder_path / f"{new_name}{old_extension}"

            if new_file_path.exists():
                raise FileExistsError(f"File {new_file_path} already exists.")

            os.rename(file_path, new_file_path)


def bulk_move_copy(
    src_folder: str,
    dest_folder: str,
    filenames: List[str],
    operation: OperationType,
    std_extensions: Optional[str] = None
) -> None:
    """
    Moves or copies multiple files from a source folder to a destination folder.

    This function performs either a bulk move or copy operation of files from
    a source folder to a destination folder. Optionally, it can standardize
    the file extensions of the destination files.

    Args:
        src_folder (str): The path to the source folder.
        dest_folder (str): The path to the destination folder.
        filenames (List[str]): List of filenames to move or copy.
        operation (OperationType): Enum representing either 'MOVE' or 'COPY'.
        std_extensions (Optional[str]): If provided, standardizes file
            extensions of destination files to this value. Defaults to None.

    Raises:
        ValueError: If either source folder, destination folder, or filenames
            list is empty or None.
        FileNotFoundError: If a source file is not found in the source folder.
        FileExistsError: If a destination file already exists in destination
            folder.
    """
    if not src_folder or not dest_folder or not filenames:
        raise ValueError("Source folder, destination folder, and filenames "
                         "cannot be empty or None.")

    src_folder_path = Path(src_folder)
    dest_folder_path = Path(dest_folder)
    dest_folder_path.mkdir(parents=True, exist_ok=True)

    for filename in filenames:
        src_filepath = src_folder_path / filename
        dest_filepath = dest_folder_path / filename

        if std_extensions:
            dest_filepath = (
                dest_folder_path / force_extension(filename, std_extensions)
            )

        check_filepath(src_filepath, FileCheckType.NOT_FOUND)
        check_filepath(dest_filepath, FileCheckType.EXISTS)

        if operation == OperationType.MOVE:
            shutil.move(str(src_filepath), str(dest_filepath))
        elif operation == OperationType.COPY:
            shutil.copy(str(src_filepath), str(dest_filepath))


def lock_file(
    folder: str,
    filename: str,
    file_type: FileType,
    timeout: int = 10,
    find_replace: Optional[Dict[str, str]] = None
) -> Union[Dict, str, bytes]:
    """
    Acquires a lock on a file and reads its content.

    This function attempts to acquire a lock on the specified file within
    a given timeout. If the lock is successfully acquired, the file's content
    is read and returned.

    Args:
        folder (str): The path to the folder containing the file.
        filename (str): The name of the file to lock and read.
        file_type (FileType): Enum representing the file type.
        timeout (int): The maximum time in seconds to wait for the lock.
            Defaults to 10.
        find_replace (Optional[Dict[str, str]]): A dictionary for find-replace
            operations on the file's content. Keys are the substrings to find,
            and values are the substrings to replace them with.
            Defaults to None.

    Returns:
        Union[Dict, str, bytes]: The content of the file, depending on its type.

    Raises:
        ValueError: If either the folder or filename is empty or None.
        Timeout: If the lock could not be acquired within the specified timeout.
    """
    if not folder or not filename:
        raise ValueError("Folder and filename cannot be empty or None.")

    lock_path = f"{folder}/{filename}.lock"
    lock = FileLock(lock_path, timeout=timeout)

    try:
        with lock.acquire():
            content = get_file(folder, filename, file_type, find_replace)
            return content
    except Timeout:
        raise Timeout(f"Could not acquire lock on {filename} "
                      f"within {timeout} seconds.")


def save_versioned_file(
    folder: str,
    filename: str,
    file_type: FileType,
    content: str,
    timestamp_format: str = "%Y%m%d%H%M%S",
    max_versions: int = 5
) -> str:
    """
    Saves a versioned copy of a file with a timestamp suffix.

    This function saves the content to a file with a timestamp suffix added
    to the filename. It also limits the number of versioned files based on
    the `max_versions` parameter. If the number of versioned files exceeds
    `max_versions`, the oldest file will be deleted.

    Args:
        folder (str): The path to the folder where the file will be saved.
        filename (str): The name of the file to be saved.
        file_type (FileType): Enum representing the file type.
        content (str): The content to be written to the file.
        timestamp_format (str, optional): The format of the timestamp to be
            appended to the filename. Defaults to "%Y%m%d%H%M%S".
        max_versions (int, optional): The maximum number of versioned files
            to keep in the folder. Defaults to 5.

    Returns:
        str: The full path of the saved file.

    Raises:
        ValueError: If the folder, filename, or content is empty or None.
    """
    if not folder or not filename or content is None:
        raise ValueError("Folder, filename, and content cannot be empty "
                         "or None.")

    standardized_filename = force_extension(filename, file_type.name.lower())
    timestamp = datetime.now().strftime(timestamp_format)
    versioned_filename = f"{standardized_filename}_{timestamp}"
    versioned_filepath = Path(folder) / versioned_filename

    with open(versioned_filepath, 'w') as file:
        file.write(content)

    base_name = Path(standardized_filename).stem
    version_files = sorted(
        Path(folder).glob(f"{base_name}_*.{file_type.name.lower()}"),
        key=os.path.getmtime
    )

    while len(version_files) > max_versions:
        oldest_file = version_files.pop(0)
        oldest_file.unlink()

    return str(versioned_filepath)


def _serialize(
    data: Any,
    filepath: str,
    serialization_type: SerializationType
) -> None:
    """
    Serializes and saves Python data to a file using either JSON or Pickle.

    This is an internal helper function that handles the actual serialization
    process based on the given serialization type.

    Args:
        data (Any): The Python data to serialize.
        filepath (str): The path where the serialized data will be saved.
        serialization_type (SerializationType): Enum specifying whether to use
            JSON or Pickle for serialization.

    Raises:
        OSError: If the file could not be written.
    """
    write_mode = 'w' if serialization_type == SerializationType.JSON else 'wb'
    with open(filepath, write_mode) as file:
        if serialization_type == SerializationType.JSON:
            json.dump(data, file)
        else:
            pickle.dump(data, file)


def _deserialize(
    filepath: str,
    serialization_type: SerializationType
) -> Any:
    """
    Deserializes Python data from a file using either JSON or Pickle.

    This is an internal helper function that handles the actual deserialization
    process based on the given serialization type.

    Args:
        filepath (str): The path to the file containing the serialized data.
        serialization_type (SerializationType): Enum specifying whether to use
            JSON or Pickle for deserialization.

    Returns:
        Any: The deserialized Python data.

    Raises:
        FileNotFoundError: If the file is not found.
        OSError: If the file could not be read.
    """
    read_mode = 'r' if serialization_type == SerializationType.JSON else 'rb'
    with open(filepath, read_mode) as file:
        if serialization_type == SerializationType.JSON:
            return json.load(file)
        else:
            return pickle.load(file)


def serialize_deserialize(
    operation: str,
    filepath: str,
    data: Optional[Any] = None,
    serialization_type: SerializationType = SerializationType.JSON
) -> Any:
    """
    Serializes or deserializes data to/from a file.

    This function either serializes a Python object to a file or deserializes
    an object from a file based on the given operation type ('serialize' or
    'deserialize'). The serialization format can be specified (e.g., JSON,
    Pickle).

    Args:
        operation (str): The operation to perform. Either 'serialize' or
            'deserialize'.
        filepath (str): The path to the file for serialization or
            deserialization.
        data (Optional[Any]): The data to serialize. Required if the operation
            is 'serialize'.
        serialization_type (SerializationType): The serialization format.
            Defaults to JSON.

    Returns:
        Any: If the operation is 'deserialize', returns the deserialized
            object. Otherwise, returns None.

    Raises:
        ValueError: If the filepath is empty or None.
        ValueError: If data is None when the operation is 'serialize'.
        FileNotFoundError: If the file for deserialization is not found.
        ValueError: If an invalid operation type is specified.
    """
    if not filepath:
        raise ValueError("Filepath cannot be empty or None.")

    standardized_filepath = force_extension(filepath, serialization_type.value)

    if operation == 'serialize':
        if data is None:
            raise ValueError("Data cannot be None when serializing.")
        _serialize(data, standardized_filepath, serialization_type)

    elif operation == 'deserialize':
        if not Path(standardized_filepath).is_file():
            raise FileNotFoundError(f"{standardized_filepath} not found.")
        return _deserialize(standardized_filepath, serialization_type)

    else:
        raise ValueError("Invalid operation specified. Use 'serialize' "
                         "or 'deserialize'.")


def read_large_file_in_chunks(
    folder: str,
    filename: str,
    file_type: FileType,
    chunk_size: int = 1024
) -> Generator[str, None, None]:
    """
    Reads a large file in chunks and yields each chunk as a string.

    This function reads a file in chunks to handle large files without
    loading the entire file into memory. The chunk size can be specified.

    Args:
        folder (str): The path to the folder where the file is located.
        filename (str): The name of the file to read.
        file_type (FileType): An enum representing the file type.
        chunk_size (int): The size of each chunk in bytes. Defaults to 1024.

    Yields:
        str: Each chunk of the file as a string.

    Raises:
        ValueError: If the folder, filename, or chunk size is empty, None,
            or non-positive.
        FileNotFoundError: If the specified file is not found in the given
            folder.
    """
    if not folder or not filename or chunk_size <= 0:
        raise ValueError("Folder, filename, and chunk size cannot be empty, "
                         "None, or non-positive.")

    standardized_filename = force_extension(filename, file_type.name.lower())
    filepath = Path(folder) / standardized_filename
    check_filepath(filepath, FileCheckType.EXISTS)

    with open(filepath, 'r') as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            yield chunk


def write_large_string_in_chunks(
    folder: str,
    filename: str,
    file_type: FileType,
    large_string: str,
    chunk_size: int = 1024
) -> None:
    """
    Writes a large string to a file in chunks.

    This function allows writing a large string to a file by breaking it
    into smaller chunks, which can be especially useful for very large files.
    The size of each chunk is configurable.

    Args:
        folder (str): The path to the folder where the file will be saved.
        filename (str): The name of the file to be created.
        file_type (FileType): Enum representing the type of the file.
        large_string (str): The large string to be written to the file.
        chunk_size (int, optional): The size of each chunk in bytes.
            Defaults to 1024 (1KB).

    Raises:
        ValueError: If the folder, filename, large_string are empty or None,
            or if chunk_size is non-positive.
    """
    if not folder or not filename or large_string is None or chunk_size <= 0:
        raise ValueError("Folder, filename, large string, and chunk size "
                         "cannot be empty, None, or non-positive.")

    standardized_filename = force_extension(filename, file_type.name.lower())
    filepath = Path(folder) / standardized_filename

    with open(filepath, 'w') as file:
        for i in range(0, len(large_string), chunk_size):
            file.write(large_string[i:i + chunk_size])
