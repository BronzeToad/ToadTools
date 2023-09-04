import codecs
import hashlib
import json
import os
import pickle
import re
import shutil
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, Optional, Union

import chardet
from PIL import Image
from filelock import FileLock, Timeout

from toad_tools.enum_hatchery import ChecksumType, FileType, OperationType, SerializationType


# TODO: add function to take filepath and check if it exists
# =========================================================================== #

def force_extension(
    filename: str,
    extension: str
) -> str:
    """
    Standardizes the file extension of a given filename.

    This function takes a filename and ensures that it ends with the specified extension.
    The comparison is case-insensitive. If the filename has no extension or has a different
    extension, the specified extension is appended.

    :param filename: The original filename.
    :type filename: str
    :param extension: The extension to force on the filename.
    :type extension: str
    :return: The filename with the standardized extension.
    :rtype: str

    :Example:

    >>> force_extension("file", "json")
    "file.json"

    >>> force_extension("file.JSON", "json")
    "file.JSON"

    >>> force_extension("file.", "json")
    "file.json"
    """

    # remove leading dot and make extension lowercase for internal comparison
    normalized_extension = extension.lstrip('.').lower()
    current_extension = Path(filename).suffix.lstrip('.').lower()

    # handle the case where filename ends with a dot
    if filename.endswith('.'):
        filename = filename.rstrip('.')

    # if the filename has no extension or has a different extension, append the given one
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
    Retrieve and optionally modify the contents of a file.

    This function takes a folder path, filename, and FileType enum to read the file.
    Optionally, it also accepts a find-replace dictionary to modify the contents of text-based files.

    :param folder: The folder where the file is located.
    :type folder: str
    :param filename: The name of the file.
    :type filename: str
    :param file_type: The type of the file, specified as an enum (FileType).
    :type file_type: FileType
    :param find_replace: Optional dictionary containing find-replace pairs for text-based files.
    :type find_replace: dict, optional
    :return: The file contents. For text-based files, this could be a string or a dictionary (for JSON).
             For binary files, this will be a bytes object.
    :rtype: Union[dict, str, bytes]

    :raises FileNotFoundError: If the specified file is not found in the given folder.
    :raises RuntimeError: If find_replace is used on a binary file type.

    :Example:

    >>> get_file("/path/to/folder", "file", FileType.JSON)
    {"key": "value"}  # Assuming the JSON file contains this data

    >>> get_file("/path/to/folder", "file", FileType.TXT, {"old": "new"})
    "new text"  # Assuming the TXT file contains "old text"

    >>> get_file("/path/to/folder", "image", FileType.JPG)
    b'\xff\xd8\xff\xe0\x00\x10JFIF...'  # Returns bytes object for binary files
    """

    # standardize the file extension
    standardized_filename = force_extension(filename, file_type.name.lower())
    filepath = Path(folder) / standardized_filename

    # check if the file exists
    if not filepath.is_file():
        raise FileNotFoundError(f"{standardized_filename} not found in {folder}.")

    # read the file based on its type
    if file_type in [FileType.JPG, FileType.PNG, FileType.GIF, FileType.BMP, FileType.TIFF,
                     FileType.PDF, FileType.MP3, FileType.WAV, FileType.FLAC,
                     FileType.MP4, FileType.AVI, FileType.MKV, FileType.MOV, FileType.WMV]:
        # binary file types
        with open(filepath, 'rb') as file:
            obj = file.read()
    else:
        # text-based file types
        with open(filepath, 'r') as file:
            if file_type == FileType.JSON:
                obj = json.load(file)
            elif file_type in [FileType.HTML, FileType.SQL, FileType.XML, FileType.CSV,
                               FileType.YAML, FileType.TXT, FileType.MD, FileType.INI,
                               FileType.LOG, FileType.CONF, FileType.PY, FileType.JS, FileType.CSS]:
                obj = file.read()
            else:
                obj = None

    # optional find-and-replace operation
    if find_replace is not None:
        if isinstance(obj, str):  # only apply find/replace on text-based content
            for key, val in find_replace.items():
                obj = obj.replace(key, str(val))
        else:
            raise RuntimeError(f"Find/Replace not supported for {file_type.name}")

    return obj


def duplicate_file(
    source_folder: str,
    source_filename: str,
    dest_folder: str,
    file_type: FileType,
    dest_filename: Optional[str] = None
) -> str:
    """
    Duplicates a file from a source folder to a destination folder with an optional new filename.

    :param source_folder: The folder where the source file is located.
    :type source_folder: str
    :param source_filename: The name of the source file.
    :type source_filename: str
    :param dest_folder: The folder where the destination file will be located.
    :type dest_folder: str
    :param dest_filename: The name of the destination file. If None, source_filename is used.
    :type dest_filename: str, optional
    :param file_type: The type of the file, specified as an enum (FileType).
    :type file_type: FileType
    :return: The path of the duplicated file.
    :rtype: str

    :raises FileNotFoundError: If the source file is not found.
    :raises FileExistsError: If the destination file already exists.
    :raises RuntimeError: If the file type is not supported for duplication.

    :Example:

    >>> duplicate_file("/source/folder", "file.txt", "/dest/folder", "new_file.txt", FileType.TXT)
    "/dest/folder/new_file.txt"
    """

    # read the source file content
    source_content = get_file(source_folder, source_filename, file_type)
    if source_content is None:
        raise RuntimeError(f"File type {file_type.name} is not supported for duplication.")

    # determine the destination filename
    if dest_filename is None:
        dest_filename = source_filename
    dest_filename = force_extension(dest_filename, file_type.name.lower())

    # check if destination folder exists, if not create it
    Path(dest_folder).mkdir(parents=True, exist_ok=True)

    # create the destination file path
    dest_filepath = Path(dest_folder) / dest_filename

    # check if destination file already exists
    if dest_filepath.is_file():
        raise FileExistsError(f"{dest_filepath} already exists.")

    # write content to the destination file
    mode = 'wb' if isinstance(source_content, bytes) else 'w'
    with open(dest_filepath, mode) as dest_file:
        if file_type == FileType.JSON:
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
    Delete a file from a specified folder.

    This function takes a folder path, filename, and FileType enum to delete the file.
    Optionally, it also accepts a flag to require confirmation before deletion.

    :param folder: The folder where the file is located.
    :type folder: str
    :param filename: The name of the file to delete.
    :type filename: str
    :param file_type: The type of the file, specified as an enum (FileType).
    :type file_type: FileType
    :param require_confirmation: Flag indicating whether to require confirmation before deleting.
    :type require_confirmation: bool, optional
    :return: True if the file was successfully deleted, False otherwise.
    :rtype: bool

    :raises FileNotFoundError: If the specified file is not found in the given folder.

    :Example:

    >>> delete_file("/path/to/folder", "file", FileType.JSON)
    True  # Returns True if the file was successfully deleted

    >>> delete_file("/path/to/folder", "file", FileType.JSON, True)
    Are you sure you want to delete 'file.json'? [y/N]: y
    True  # Returns True if the file was successfully deleted after confirmation
    """

    # use force_extension to standardize the file extension
    standardized_filename = force_extension(filename, file_type.name.lower())
    filepath = Path(folder) / standardized_filename

    # check if the file exists
    if not filepath.is_file():
        raise FileNotFoundError(f"{standardized_filename} not found in {folder}.")

    # require confirmation if specified
    if require_confirmation:
        confirm = input(f"Are you sure you want to delete '{standardized_filename}'? [y/N]: ")
        if confirm.lower() != 'y':
            print("File deletion cancelled.")
            return False

    # delete the file
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
    Rename a file and optionally move it to a different folder.

    :param src_folder: The source folder where the file is currently located.
    :type src_folder: str
    :param src_filename: The source filename to be renamed.
    :type src_filename: str
    :param src_file_type: The type of the source file, specified as an enum (FileType).
    :type src_file_type: FileType
    :param dest_folder: The destination folder where the file should be moved, optional.
    :type dest_folder: str, optional
    :param dest_filename: The new filename, optional.
    :type dest_filename: str, optional
    :param dest_file_type: The type of the destination file, specified as an enum (FileType), optional.
    :type dest_file_type: FileType, optional
    :param overwrite: Whether to overwrite the destination file if it exists.
    :type overwrite: bool
    :return: The new filename with its full path if the rename was successful, otherwise None.
    :rtype: Union[str, None]

    :raises FileNotFoundError: If the source file doesn't exist.
    :raises FileExistsError: If the destination file already exists and overwrite is False.
    """

    # check if the source file exists
    src_full_path = Path(src_folder) / force_extension(src_filename, src_file_type.name.lower())
    if not src_full_path.is_file():
        raise FileNotFoundError(f"{src_filename} not found in {src_folder}.")

    # generate the new filename
    dest_folder = dest_folder or src_folder
    dest_filename = dest_filename or src_filename
    dest_file_type = dest_file_type or src_file_type
    dest_full_path = Path(dest_folder) / force_extension(dest_filename, dest_file_type.name.lower())

    # cCheck if the destination file exists
    if dest_full_path.is_file() and not overwrite:
        raise FileExistsError(f"{dest_filename} already exists in {dest_folder}.")

    # perform the rename
    os.rename(src_full_path, dest_full_path)
    return str(dest_full_path)


def ensure_directory_exists(
    folder: str,
    create_if_missing: bool = True
) -> Optional[str]:
    """
    Ensures that a directory exists at the given path.

    This function checks if a directory exists at the specified folder path.
    If the directory does not exist and create_if_missing is True, it will create the directory.

    :param folder: The path where the directory should exist.
    :type folder: str
    :param create_if_missing: Whether to create the directory if it doesn't exist.
                              Default is True.
    :type create_if_missing: bool, optional
    :return: The path of the directory if it exists or was successfully created,
             None otherwise.
    :rtype: Optional[str]

    :raises FileExistsError: If the path exists but is not a directory.
    :raises PermissionError: If the function does not have permission to create the directory.

    :Example:

    >>> ensure_directory_exists("/path/to/folder")
    "/path/to/folder"  # Returns the folder path if it exists or was successfully created

    >>> ensure_directory_exists("/path/to/folder", create_if_missing=False)
    None  # Returns None if the folder doesn't exist and create_if_missing is False
    """

    path = Path(folder)

    # check if the directory already exists
    if path.is_dir():
        return str(path)

    # if the path exists but is not a directory, raise an error
    if path.exists():
        raise FileExistsError(f"The path {folder} exists but is not a directory.")

    # create the directory if it doesn't exist and if create_if_missing is True
    if create_if_missing:
        try:
            os.makedirs(folder)
            return str(path)
        except PermissionError:
            raise PermissionError(f"Do not have permission to create directory at {folder}")
    else:
        return None


def directory_cleanup(
    directory: str,
    older_than_days: Optional[int] = None,
    extensions: Optional[List[str]] = None
) -> int:
    """
    Cleans up a directory by deleting files based on conditions.

    Deletes files in the given directory that meet the conditions specified by `older_than_days`
    and `extensions`. If no conditions are specified, all files in the directory will be deleted.

    :param directory: The directory to clean up.
    :type directory: str
    :param older_than_days: Optional; delete files older than this many days.
    :type older_than_days: int, optional
    :param extensions: Optional; list of file extensions to consider for deletion.
    :type extensions: List[str], optional
    :return: The number of files deleted.
    :rtype: int

    :raises FileNotFoundError: If the specified directory does not exist.
    :raises PermissionError: If the function lacks permission to delete any file.

    :Example:

    >>> directory_cleanup("/path/to/folder", older_than_days=30)
    5  # Deletes 5 files older than 30 days

    >>> directory_cleanup("/path/to/folder", extensions=[".txt", ".log"])
    3  # Deletes 3 files with .txt or .log extensions

    >>> directory_cleanup("/path/to/folder")
    10  # Deletes all 10 files in the directory
    """

    # check if directory exists
    dir_path = Path(directory)
    if not dir_path.is_dir():
        raise FileNotFoundError(f"The specified directory {directory} does not exist.")

    deleted_files_count = 0

    # get the current time
    current_time = time.time()

    for file_path in dir_path.iterdir():
        if file_path.is_file():  # ignore sub-directories
            delete_file = True

            # check file age if specified
            if older_than_days is not None:
                file_age_days = (current_time - file_path.stat().st_mtime) / (24 * 60 * 60)
                delete_file = file_age_days > older_than_days

            # check file extension if specified
            if delete_file and extensions is not None:
                file_extension = file_path.suffix.lower()
                delete_file = file_extension in [ext.lower() for ext in extensions]

            # delete the file if it meets the conditions
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
    Retrieve the size of a file in bytes.

    This function takes a folder path and a filename to find the file and return its size.
    Optionally, it also accepts a FileType enum to standardize the file extension.

    :param folder: The folder where the file is located.
    :type folder: str
    :param filename: The name of the file.
    :type filename: str
    :param file_type: The type of the file, specified as an enum (FileType). Optional.
    :type file_type: FileType, optional
    :return: The file size in bytes.
    :rtype: int

    :raises FileNotFoundError: If the specified file is not found in the given folder.

    :Example:

    >>> get_file_size("/path/to/folder", "file", FileType.JSON)
    2048  # Returns the file size in bytes

    >>> get_file_size("/path/to/folder", "file.json")
    2048  # Returns the file size in bytes
    """

    # standardize the file extension if FileType is provided
    if file_type:
        filename = force_extension(filename, file_type.name.lower())

    filepath = Path(folder) / filename

    # check if the file exists
    if not filepath.is_file():
        raise FileNotFoundError(f"{filename} not found in {folder}.")

    # get and return the file size
    return os.path.getsize(filepath)


def get_last_modified(
    folder: str,
    filename: str,
    file_type: Optional[FileType] = None
) -> Union[datetime, None]:
    """
    Get the last modified timestamp of a file.

    This function takes a folder path, filename, and optionally a FileType enum.
    It returns the last modified timestamp of the specified file.

    :param folder: The folder where the file is located.
    :type folder: str
    :param filename: The name of the file.
    :type filename: str
    :param file_type: Optional type of the file, specified as an enum (FileType).
    :type file_type: FileType, optional
    :return: The last modified timestamp of the file as a datetime object, or None if the file doesn't exist.
    :rtype: Union[datetime, None]

    :Example:

    >>> get_last_modified("/path/to/folder", "file", FileType.JSON)
    datetime.datetime(2023, 9, 3, 14, 55, 3)

    >>> get_last_modified("/path/to/folder", "file")
    datetime.datetime(2023, 9, 3, 14, 55, 3)
    """

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
    Validate that a file's contents match its expected type.

    :param folder: The folder where the file is located.
    :type folder: str
    :param filename: The name of the file.
    :type filename: str
    :param expected_type: The expected file type, specified as an enum (FileType).
    :type expected_type: FileType
    :return: A validation message or None if the file is valid.
    :rtype: Optional[str]

    :Example:

    >>> validate_file_type("/path/to/folder", "file", FileType.JSON)
    None  # Returns None if the file is valid

    >>> validate_file_type("/path/to/folder", "file", FileType.PNG)
    "Invalid PNG file."  # Returns an error message if the file is invalid
    """

    # use force_extension to standardize the file extension
    standardized_filename = force_extension(filename, expected_type.name.lower())
    filepath = Path(folder) / standardized_filename

    # validate based on expected file type
    if expected_type == FileType.JSON:
        try:
            with open(filepath, 'r') as file:
                json.load(file)
            return None  # file is valid
        except json.JSONDecodeError:
            return "Invalid JSON file."

    elif expected_type == FileType.HTML:
        try:
            with open(filepath, 'r') as file:
                # simple validation: check if the file contains '<html>' tag
                if '<html>' in file.read().lower():
                    return None  # file is valid
            return "Invalid HTML file."
        except:
            return "Could not read HTML file."

    elif expected_type == FileType.XML:
        try:
            ET.parse(str(filepath))
            return None  # file is valid
        except ET.ParseError:
            return "Invalid XML file."

    elif expected_type in [FileType.PNG, FileType.JPG]:
        try:
            with Image.open(filepath) as img:
                img.verify()
            return None  # file is valid
        except:
            return f"Invalid {expected_type.name} file."

    else:
        return "File type not supported for validation."


def concatenate_files(
    folder: str,
    filenames: List[str],
    file_type: FileType,
    output_filename: str,
    delimiter: Optional[str] = None
) -> None:
    """
    Concatenate multiple files of the same type into a single file.

    :param folder: The folder where the files are located.
    :type folder: str
    :param filenames: List of filenames to concatenate.
    :type filenames: List[str]
    :param file_type: The type of the files, specified as an enum (FileType).
    :type file_type: FileType
    :param output_filename: The name of the output file.
    :type output_filename: str
    :param delimiter: Optional delimiter to insert between file contents.
    :type delimiter: str, optional

    :raises FileNotFoundError: If any of the specified files are not found in the given folder.
    :raises RuntimeError: If an error occurs during file reading or writing.

    :Example:

    >>> concatenate_files("/path/to/folder", ["file1.txt", "file2.txt"], FileType.TXT, "output.txt", "\\n")
    # This will concatenate "file1.txt" and "file2.txt" with a newline delimiter and save it as "output.txt"
    """

    contents = []

    for filename in filenames:
        try:
            file_content = get_file(folder, filename, file_type)
            if not isinstance(file_content, str):
                raise RuntimeError(f"File {filename} content is not text-based.")
            contents.append(file_content)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File {filename} not found. {str(e)}")

    # add delimiters if provided
    combined_content = delimiter.join(contents) if delimiter else ''.join(contents)

    output_filepath = Path(folder) / force_extension(output_filename, file_type.name.lower())

    # save the concatenated content to the output file
    with open(output_filepath, 'w') as file:
        file.write(combined_content)


def count_lines(
    folder: str,
    filename: str,
    file_type: FileType
) -> Union[int, str]:
    """
    Count the number of lines in a file.

    This function takes a folder path, filename, and FileType enum to read the file.
    It then returns the number of lines for text-based files.

    :param folder: The folder where the file is located.
    :type folder: str
    :param filename: The name of the file.
    :type filename: str
    :param file_type: The type of the file, specified as an enum (FileType).
    :type file_type: FileType
    :return: The number of lines for text-based files or a message for binary files.
    :rtype: Union[int, str]

    :raises FileNotFoundError: If the specified file is not found in the given folder.

    :Example:

    >>> count_lines("/path/to/folder", "file.txt", FileType.TXT)
    42  # Assuming the TXT file has 42 lines

    >>> count_lines("/path/to/folder", "image.jpg", FileType.JPG)
    "Line count is not applicable for binary files."
    """

    # get the file content using the `get_file` function
    file_content = get_file(folder, filename, file_type)

    # handle text-based and binary files differently
    if isinstance(file_content, str):
        # count the number of lines for text-based files
        return len(file_content.splitlines())
    else:
        # for binary files, line counting is not applicable
        return "Line count is not applicable for binary files."


def convert_file_encoding(
    folder: str,
    filename: str,
    file_type: FileType,
    target_encoding: str,
    source_encoding: Optional[str] = None
) -> None:
    """
    Convert the encoding of a file.

    :param folder: The folder where the file is located.
    :param filename: The name of the file.
    :param file_type: The type of the file, specified as an enum (FileType).
    :param target_encoding: The target encoding to convert the file to.
    :param source_encoding: The source encoding of the file. If None, the function will attempt to detect it.
    :return: None

    :Example:

    >>> convert_file_encoding("/path/to/folder", "file", FileType.TXT, "utf-8", "latin1")
    # This will convert a file from 'latin1' to 'utf-8' encoding.
    """

    # use get_file to read the file content
    file_content = get_file(folder, filename, file_type)

    # if source_encoding is not provided, use chardet to detect it
    if source_encoding is None:
        detection_result = chardet.detect(file_content.encode())
        source_encoding = detection_result['encoding']

    # convert the file content to the target encoding
    converted_content = file_content.encode(source_encoding).decode(target_encoding)

    # write the converted content back to the file
    output_filename = force_extension(filename, file_type.name.lower())
    output_filepath = f'{folder}/{output_filename}'
    with codecs.open(output_filepath, 'w', encoding=target_encoding) as file:
        file.write(converted_content)


def search_text_in_file(
    folder: str,
    filename: str,
    query: str,
    is_regex: bool = False,
    case_sensitive: bool = False,
    file_type: Optional[FileType] = None
) -> List[str]:
    """
    Search for a text string or regular expression pattern in a file.

    This function takes a folder path, filename, and query string or regular expression to perform
    the search. The function returns a list of lines where the query is found.

    :param folder: The folder where the file is located.
    :type folder: str
    :param filename: The name of the file.
    :type filename: str
    :param query: The text or regular expression pattern to search for.
    :type query: str
    :param is_regex: Whether the query is a regular expression pattern.
    :type is_regex: bool, default is False
    :param case_sensitive: Whether the search is case-sensitive.
    :type case_sensitive: bool, default is False
    :param file_type: Optional file type to force the extension.
    :type file_type: FileType, optional
    :return: A list of lines where the query is found.
    :rtype: List[str]

    :Example:

    >>> search_text_in_file("/path/to/folder", "file.txt", "search_text")
    ["Line containing search_text", ...]

    >>> search_text_in_file("/path/to/folder", "file.txt", "regex_pattern", is_regex=True)
    ["Line matching regex_pattern", ...]
    """

    # if file_type is provided, standardize the file extension
    if file_type:
        filename = force_extension(filename, file_type.name.lower())

    filepath = Path(folder) / filename

    # check if the file exists
    if not filepath.is_file():
        raise FileNotFoundError(f"{filename} not found in {folder}.")

    found_lines = []

    with open(filepath, 'r') as file:
        for line in file:
            # determine the search function: regex search or string search
            search_func = re.search if is_regex else lambda q, l: q in l

            # determine the target line: original or lowercase
            target_line = line if case_sensitive else line.lower()

            # determine the query: original or lowercase
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
    Calculate the checksum of a file.

    This function calculates the checksum of a file located in a specified folder.
    The checksum algorithm can be specified (default is SHA-256).

    :param folder: The folder where the file is located.
    :type folder: str
    :param filename: The name of the file.
    :type filename: str
    :param checksum_type: The type of checksum to calculate, specified as an enum (ChecksumType).
    :type checksum_type: ChecksumType
    :param buffer_size: The size of the buffer to use when reading the file. Increase for large files.
    :type buffer_size: int
    :return: The calculated checksum as a hexadecimal string.
    :rtype: str, optional

    :raises FileNotFoundError: If the specified file is not found in the given folder.

    :Example:

    >>> calculate_checksum("/path/to/folder", "file.txt")
    "af2379a30923abf..."
    """

    # standardize the file extension (if needed, based on your use case)
    # standardized_filename = force_extension(filename, ...)
    filepath = Path(folder) / filename

    # check if the file exists
    if not filepath.is_file():
        raise FileNotFoundError(f"{filename} not found in {folder}.")

    # initialize the hash object
    hash_obj = hashlib.new(checksum_type.value)

    # read the file and update hash object
    with open(filepath, 'rb') as f:
        while chunk := f.read(buffer_size):
            hash_obj.update(chunk)

    return hash_obj.hexdigest()


def bulk_rename(
    folder: str,
    rename_func: Callable[[str], str]
) -> None:
    """
    Rename multiple files in a directory according to a specific pattern or rule.

    This function takes a folder path and a renaming function as arguments.
    The renaming function itself takes a filename as an argument and returns the new name for that file.

    :param folder: The folder where the files to be renamed are located.
    :type folder: str
    :param rename_func: A function that takes the old filename (without extension)
                        and returns the new filename (also without extension).
    :type rename_func: Callable[[str], str]

    :Example:

    >>> def add_prefix(filename: str) -> str:
    ...     return f"prefix_{filename}"
    ...
    >>> bulk_rename("/path/to/folder", add_prefix)

    """
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
    standardize_extensions: Optional[str] = None
) -> None:
    """
    Move or copy multiple files from a source folder to a destination folder.

    :param src_folder: The source folder from which to move or copy files.
    :type src_folder: str
    :param dest_folder: The destination folder to which to move or copy files.
    :type dest_folder: str
    :param filenames: A list of filenames to move or copy.
    :type filenames: List[str]
    :param operation: The type of operation to perform: 'move' or 'copy'.
    :type operation: OperationType
    :param standardize_extensions: Optional extension to standardize all files.
        If None, no standardization is performed.
    :type standardize_extensions: str, optional

    :raises FileNotFoundError: If any file in the list does not exist in the source folder.
    :raises FileExistsError: If a file with the same name exists in the destination folder.

    :Example:

    >>> bulk_move_copy("/path/to/src", "/path/to/dest", ["file1.txt", "file2.txt"], OperationType.MOVE)
    # Moves file1.txt and file2.txt from /path/to/src to /path/to/dest

    >>> bulk_move_copy("/path/to/src", "/path/to/dest", ["file1.txt", "file2.txt"], OperationType.COPY, "TXT")
    # Copies and standardizes the extensions of file1.txt and file2.txt from /path/to/src to /path/to/dest
    """

    src_folder_path = Path(src_folder)
    dest_folder_path = Path(dest_folder)

    # create destination folder if it doesn't exist
    dest_folder_path.mkdir(parents=True, exist_ok=True)

    for filename in filenames:
        src_filepath = src_folder_path / filename
        dest_filepath = dest_folder_path / filename

        # standardize file extension if needed
        if standardize_extensions:
            dest_filepath = dest_folder_path / force_extension(filename, standardize_extensions)

        # check if the source file exists
        if not src_filepath.is_file():
            raise FileNotFoundError(f"{filename} not found in {src_folder}.")

        # check if the destination file already exists
        if dest_filepath.is_file():
            raise FileExistsError(f"A file with the name {dest_filepath.name} already exists in {dest_folder}.")

        # perform the move or copy operation
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
    Acquire a lock on a file and read its contents.

    :param folder: The folder where the file is located.
    :type folder: str
    :param filename: The name of the file.
    :type filename: str
    :param file_type: The type of the file, specified as an enum (FileType).
    :type file_type: FileType
    :param timeout: The maximum time to wait for the lock, in seconds.
    :type timeout: int, optional
    :param find_replace: Optional dictionary containing find-replace pairs for text-based files.
    :type find_replace: dict, optional
    :return: The file contents. For text-based files, this could be a string or a dictionary (for JSON).
             For binary files, this will be a bytes object.
    :rtype: Union[dict, str, bytes]
    :raises Timeout: If the lock cannot be acquired within the specified timeout.
    :raises FileNotFoundError: If the specified file is not found in the given folder.
    :raises RuntimeError: If find_replace is used on a binary file type.

    :Example:

    >>> lock_file("/path/to/folder", "file", FileType.JSON)
    {"key": "value"}  # Assuming the JSON file contains this data
    """

    lock_path = f"{folder}/{filename}.lock"
    lock = FileLock(lock_path, timeout=timeout)

    try:
        with lock.acquire():
            # lock acquired, perform file operations
            content = get_file(folder, filename, file_type, find_replace)
            return content
    except Timeout:
        raise Timeout(f"Could not acquire lock on {filename} within {timeout} seconds.")


def save_versioned_file(
    folder: str,
    filename: str,
    file_type: FileType,
    content: str,
    timestamp_format: str = "%Y%m%d%H%M%S",
    max_versions: int = 5
) -> str:
    """
    Save a versioned copy of a file.

    This function saves a new version of a file in the specified folder.
    It appends a timestamp to the filename to distinguish between different versions.
    It also manages the number of versions to keep, deleting the oldest if it exceeds `max_versions`.

    :param folder: The folder where the file is located.
    :type folder: str
    :param filename: The name of the file.
    :type filename: str
    :param file_type: The type of the file, specified as an enum (FileType).
    :type file_type: FileType
    :param content: The content to save in the new version.
    :type content: str
    :param timestamp_format: The format of the timestamp to append to the filename.
    :type timestamp_format: str, optional
    :param max_versions: The maximum number of versions to keep.
    :type max_versions: int, optional
    :return: The path of the saved versioned file.
    :rtype: str

    :Example:

    >>> save_versioned_file("/path/to/folder", "file", FileType.TXT, "new content")
    "/path/to/folder/file_20210903010101.txt"
    """

    # standardize the file extension
    standardized_filename = force_extension(filename, file_type.name.lower())

    # generate a timestamp
    timestamp = datetime.now().strftime(timestamp_format)

    # create a versioned filename
    versioned_filename = f"{standardized_filename}_{timestamp}"
    versioned_filepath = Path(folder) / versioned_filename

    # save the new version
    with open(versioned_filepath, 'w') as file:
        file.write(content)

    # manage the number of versions
    base_name = Path(standardized_filename).stem
    version_files = sorted(
        Path(folder).glob(f"{base_name}_*.{file_type.name.lower()}"),
        key=os.path.getmtime
    )

    while len(version_files) > max_versions:
        oldest_file = version_files.pop(0)
        oldest_file.unlink()

    return str(versioned_filepath)


def serialize_deserialize(
    operation: str,
    filepath: str,
    data: Optional[Any] = None,
    serialization_type: SerializationType = SerializationType.JSON
) -> Any:
    """
    Serialize or deserialize data to/from a file.

    This function can either write a Python object to a file (serialize) or read
    data back into a Python object (deserialize), depending on the specified
    operation. The serialization format can be either JSON or Pickle.

    :param operation: The operation to perform: 'serialize' or 'deserialize'.
    :type operation: str
    :param filepath: The path where the serialized file will be saved or read from.
    :type filepath: str
    :param data: The data to serialize. Required if operation is 'serialize'.
    :type data: Any, optional
    :param serialization_type: The serialization format: JSON or Pickle (default is JSON).
    :type serialization_type: SerializationType

    :return: If operation is 'deserialize', returns the deserialized data.
    :rtype: Any

    :raises ValueError: If an invalid operation is specified.
    :raises FileNotFoundError: If a file is not found during deserialization.

    :Example:

    >>> serialize_deserialize('serialize', 'data.json', {'key': 'value'}, SerializationType.JSON)
    None  # File 'data.json' is created with the serialized data

    >>> serialize_deserialize('deserialize', 'data.json', serialization_type=SerializationType.JSON)
    {'key': 'value'}  # Data is read from 'data.json' and returned as a dictionary
    """

    # Standardize the file extension
    standardized_filepath = force_extension(filepath, serialization_type.value)

    if operation == 'serialize':
        with open(standardized_filepath, 'w' if serialization_type == SerializationType.JSON else 'wb') as file:
            if serialization_type == SerializationType.JSON:
                json.dump(data, file)
            else:
                pickle.dump(data, file)
    elif operation == 'deserialize':
        if not Path(standardized_filepath).is_file():
            raise FileNotFoundError(f"{standardized_filepath} not found.")

        with open(standardized_filepath, 'r' if serialization_type == SerializationType.JSON else 'rb') as file:
            if serialization_type == SerializationType.JSON:
                return json.load(file)
            else:
                return pickle.load(file)
    else:
        raise ValueError("Invalid operation specified. Use 'serialize' or 'deserialize'.")


def read_large_file_in_chunks(
    folder: str,
    filename: str,
    file_type: FileType,
    chunk_size: int = 1024  # 1KB by default
) -> Generator[str, None, None]:
    """
    Reads a large text file in chunks.

    This function takes a folder path, filename, and FileType enum to read the file in chunks.
    It yields each chunk for further processing.

    :param folder: The folder where the file is located.
    :type folder: str
    :param filename: The name of the file.
    :type filename: str
    :param file_type: The type of the file, specified as an enum (FileType).
    :type file_type: FileType
    :param chunk_size: The size of each chunk in bytes. Defaults to 1024 bytes (1 KB).
    :type chunk_size: int, optional
    :return: Yields each chunk as a string.
    :rtype: Generator[str, None, None]

    :Example:

    >>> for chunk in read_large_file_in_chunks("/path/to/folder", "large_file", FileType.TXT):
    >>>     # Process each chunk here
    """

    # standardize the file extension
    standardized_filename = force_extension(filename, file_type.name.lower())
    filepath = Path(folder) / standardized_filename

    # check if the file exists
    if not filepath.is_file():
        raise FileNotFoundError(f"{standardized_filename} not found in {folder}.")

    # read the file in chunks
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
    chunk_size: int = 1024  # 1KB by default
) -> None:
    """
    Writes a large string to a text file in chunks.

    :param folder: The folder where the file will be saved.
    :type folder: str
    :param filename: The name of the file.
    :type filename: str
    :param file_type: The type of the file, specified as an enum (FileType).
    :type file_type: FileType
    :param large_string: The large string to write.
    :type large_string: str
    :param chunk_size: The size of each chunk in bytes. Defaults to 1024 bytes (1 KB).
    :type chunk_size: int, optional

    :Example:

    >>> write_large_string_in_chunks("/path/to/folder", "large_file", FileType.TXT, large_string)
    """

    # standardize the file extension
    standardized_filename = force_extension(filename, file_type.name.lower())
    filepath = Path(folder) / standardized_filename

    with open(filepath, 'w') as file:
        for i in range(0, len(large_string), chunk_size):
            file.write(large_string[i:i+chunk_size])
