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


# =========================================================================== #

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

    if not filepath.is_file():
        raise FileNotFoundError(f"{standardized_filename} not found in {folder}.")

    # mapping file types to their read modes
    file_type_map = {
        FileType.JSON: ('r', json.load),
        FileType.HTML: ('r', lambda f: f.read()),
        FileType.SQL : ('r', lambda f: f.read()),
        # ... (other file types)    # TODO
    }

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
        raise ValueError("Source folder, source filename, and destination folder cannot be empty or None.")

    source_content = get_file(source_folder, source_filename, file_type)

    if source_content is None:
        raise RuntimeError(f"File type {file_type.name} is not supported for duplication.")

    if dest_filename is None:
        dest_filename = source_filename

    dest_filename = force_extension(dest_filename, file_type.name.lower())
    Path(dest_folder).mkdir(parents=True, exist_ok=True)
    dest_filepath = Path(dest_folder) / dest_filename

    if dest_filepath.is_file():
        raise FileExistsError(f"{dest_filepath} already exists.")

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
    require_confirmation: Optional[bool] = False,
    confirm_programmatically: Optional[bool] = False
) -> bool:
    """
    Deletes a file with optional confirmation steps.

    This function deletes a specified file and can also require a manual or
    programmatic confirmation before proceeding with the deletion.

    Args:
        folder (str): The path to the folder containing the file to delete.
        filename (str): The name of the file to delete.
        file_type (FileType): Enum representing the file type.
        require_confirmation (Optional[bool]): Whether to require a
            confirmation before deletion. Defaults to False.
        confirm_programmatically (Optional[bool]): Whether to confirm the
            deletion programmatically. If True, logic for programmatic
            confirmation should be added. Defaults to False.

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

    if not filepath.is_file():
        raise FileNotFoundError(f"{standardized_filename} not found in {folder}.")

    if require_confirmation:
        if confirm_programmatically:
            # Logic for programmatic confirmation can be added here.    # TODO
            pass
        else:
            confirm = input(f"Are you sure you want to delete '{standardized_filename}'? [y/N]: ")
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
        raise ValueError("Source folder and source filename cannot be empty or None.")

    src_full_path = Path(src_folder) / force_extension(src_filename, src_file_type.name.lower())

    if not src_full_path.is_file():
        raise FileNotFoundError(f"{src_filename} not found in {src_folder}.")

    dest_folder = dest_folder or src_folder
    dest_filename = dest_filename or src_filename
    dest_file_type = dest_file_type or src_file_type

    dest_full_path = Path(dest_folder) / force_extension(dest_filename, dest_file_type.name.lower())

    if dest_full_path.is_file() and not overwrite:
        raise FileExistsError(f"{dest_filename} already exists in {dest_folder}.")

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
        raise FileExistsError(f"The path {folder} exists but is not a directory.")

    if create_if_missing:
        try:
            path.mkdir(parents=True, exist_ok=True)
            return str(path)
        except PermissionError:
            raise PermissionError(f"Do not have permission to create directory at {folder}")

    return None


def directory_cleanup(
    directory: str,
    older_than_days: Optional[int] = None,
    extensions: Optional[List[str]] = None
) -> int:


    if not directory:
        raise ValueError("Directory cannot be empty or None.")

    dir_path = Path(directory)
    if not dir_path.is_dir():
        raise FileNotFoundError(f"The specified directory {directory} does not exist.")

    deleted_files_count = 0
    current_time = time.time()

    for file_path in dir_path.iterdir():
        if not file_path.is_file():
            continue

        delete_file = True

        if older_than_days is not None:
            file_age_days = (current_time - file_path.stat().st_mtime) / (24 * 60 * 60)
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


    if not folder or not filename:
        raise ValueError("Folder and filename cannot be empty or None.")

    if file_type:
        filename = force_extension(filename, file_type.name.lower())

    filepath = Path(folder) / filename

    if not filepath.is_file():
        raise FileNotFoundError(f"{filename} not found in {folder}.")

    return os.path.getsize(filepath)


def get_last_modified(
    folder: str,
    filename: str,
    file_type: Optional[FileType] = None
) -> Union[datetime, None]:


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


    if not folder or not filename:
        raise ValueError("Folder and filename cannot be empty or None.")

    standardized_filename = force_extension(filename, expected_type.name.lower())
    filepath = Path(folder) / standardized_filename

    # Mapping file types to their validation functions
    type_validators = {
        FileType.JSON: lambda f: json.load(f),
        FileType.HTML: lambda f: '<html>' in f.read().lower(),
        FileType.XML : lambda f: ET.parse(str(filepath)),
        FileType.PNG : lambda f: Image.open(filepath).verify(),
        FileType.JPG : lambda f: Image.open(filepath).verify(),
        # ... (other file types)    # TODO
    }

    if expected_type not in type_validators:
        return "File type not supported for validation."

    try:
        with open(filepath, 'r') as file:
            if not type_validators[expected_type](file):
                return f"Invalid {expected_type.name} file."
    except Exception as e:
        return str(e)

    return None


def concatenate_files(
    folder: str,
    filenames: List[str],
    file_type: FileType,
    output_filename: str,
    delimiter: Optional[str] = None
) -> None:


    if not folder or not filenames or not output_filename:
        raise ValueError("Folder, filenames, and output filename cannot be empty or None.")

    try:
        contents = [
            get_file(folder, filename, file_type)
            for filename in filenames
        ]
    except FileNotFoundError as e:
        raise FileNotFoundError(f"One or more files not found. {str(e)}")

    combined_content = delimiter.join(contents) if delimiter else ''.join(contents)
    output_filepath = Path(folder) / force_extension(output_filename, file_type.name.lower())

    with open(output_filepath, 'w') as file:
        file.write(combined_content)


def count_lines(
    folder: str,
    filename: str,
    file_type: FileType
) -> Union[int, str]:


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


    if not folder or not filename:
        raise ValueError("Folder and filename cannot be empty or None.")

    file_content = get_file(folder, filename, file_type)

    if source_encoding is None:
        detection_result = chardet.detect(file_content.encode())
        source_encoding = detection_result['encoding']

    converted_content = file_content.encode(source_encoding).decode(target_encoding)
    output_filepath = Path(folder) / force_extension(filename, file_type.name.lower())

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


    if not folder or not filename or not query:
        raise ValueError("Folder, filename, and query cannot be empty or None.")

    if file_type:
        filename = force_extension(filename, file_type.name.lower())

    filepath = Path(folder) / filename

    if not filepath.is_file():
        raise FileNotFoundError(f"{filename} not found in {folder}.")

    found_lines = []
    text_search = lambda q, l: q in l

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


    if not folder or not filename:
        raise ValueError("Folder and filename cannot be empty or None.")

    filepath = Path(folder) / filename

    if not filepath.is_file():
        raise FileNotFoundError(f"{filename} not found in {folder}.")

    hash_obj = hashlib.new(checksum_type.value)

    with open(filepath, 'rb') as f:
        while chunk := f.read(buffer_size):
            hash_obj.update(chunk)

    return hash_obj.hexdigest()


def bulk_rename(
    folder: str,
    rename_func: Callable[[str], str]
) -> None:


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
    standardize_extensions: Optional[str] = None
) -> None:


    if not src_folder or not dest_folder or not filenames:
        raise ValueError("Source folder, destination folder, and filenames cannot be empty or None.")

    src_folder_path = Path(src_folder)
    dest_folder_path = Path(dest_folder)
    dest_folder_path.mkdir(parents=True, exist_ok=True)

    for filename in filenames:
        src_filepath = src_folder_path / filename
        dest_filepath = dest_folder_path / filename

        if standardize_extensions:
            dest_filepath = dest_folder_path / force_extension(filename, standardize_extensions)

        if not src_filepath.is_file():
            raise FileNotFoundError(f"{filename} not found in {src_folder}.")

        if dest_filepath.is_file():
            raise FileExistsError(f"A file with the name {dest_filepath.name} already exists in {dest_folder}.")

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


    if not folder or not filename:
        raise ValueError("Folder and filename cannot be empty or None.")

    lock_path = f"{folder}/{filename}.lock"
    lock = FileLock(lock_path, timeout=timeout)

    try:
        with lock.acquire():
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


    if not folder or not filename or content is None:
        raise ValueError("Folder, filename, and content cannot be empty or None.")

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


def _serialize(data: Any, filepath: str, serialization_type: SerializationType) -> None:
    with open(filepath, 'w' if serialization_type == SerializationType.JSON else 'wb') as file:
        if serialization_type == SerializationType.JSON:
            json.dump(data, file)
        else:
            pickle.dump(data, file)


def _deserialize(filepath: str, serialization_type: SerializationType) -> Any:
    with open(filepath, 'r' if serialization_type == SerializationType.JSON else 'rb') as file:
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
        raise ValueError("Invalid operation specified. Use 'serialize' or 'deserialize'.")


def read_large_file_in_chunks(
    folder: str,
    filename: str,
    file_type: FileType,
    chunk_size: int = 1024  # 1KB by default
) -> Generator[str, None, None]:


    if not folder or not filename or chunk_size <= 0:
        raise ValueError("Folder, filename, and chunk size cannot be empty, None, or non-positive.")

    standardized_filename = force_extension(filename, file_type.name.lower())
    filepath = Path(folder) / standardized_filename

    if not filepath.is_file():
        raise FileNotFoundError(f"{standardized_filename} not found in {folder}.")

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


    if not folder or not filename or large_string is None or chunk_size <= 0:
        raise ValueError("Folder, filename, large string, and chunk size cannot be empty, None, or non-positive.")

    standardized_filename = force_extension(filename, file_type.name.lower())
    filepath = Path(folder) / standardized_filename

    with open(filepath, 'w') as file:
        for i in range(0, len(large_string), chunk_size):
            file.write(large_string[i:i + chunk_size])
