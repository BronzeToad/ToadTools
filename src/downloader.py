import shutil
from pathlib import Path
from typing import List, Union, Optional, Callable

import requests
import logging

log = logging.getLogger(__name__)


def create_progress_bar(percent: int, width: int = 50) -> str:
    """
    Creates a text-based progress bar.

    This function generates a string that visually represents a progress bar, which can be used
    to indicate the progress of a task in a console application. The progress bar consists of a
    series of filled and unfilled characters, indicating the percentage of the task completed.

    Parameters:
    - percent (int): The completion percentage of the task. This should be a value
        between 0 and 100.
    - width (int, optional): The total width of the progress bar in characters. Defaults to 50.

    Returns:
    - str: A string representing the progress bar, including the current percentage.
    """
    filled_width = int(width * percent // 100)
    bar = '█' * filled_width + '-' * (width - filled_width)
    return f'|{bar}| {percent}%'


def download_file(
        download_url: str,
        save_directory: Union[str, Path],
        filename: str,
        status_bar: bool = False
) -> None:
    """
    Downloads a file from a given URL and saves it to a specified directory.

    This function downloads a file from the specified URL and saves it under the given filename
    within the specified directory. If the file already exists, the download is skipped. Optionally,
    a status bar can be displayed to show the download progress.

    Parameters:
    - download_url (str): The URL from which the file will be downloaded.
    - save_directory (Union[str, Path]): The directory where the file will be saved.
        Can be a string or a Path object.
    - filename (str): The name of the file to save the download as.
    - status_bar (bool, optional): Whether to display a download progress bar. Defaults to False.

    Creates a temporary directory within the save directory to handle the download process. Once
    the download is complete, the file is moved from the temporary directory to the save
    directory. If the download is interrupted or fails, the temporary file is not moved.
    """
    directory = Path(save_directory)
    filepath = directory / filename
    log.info(f"Downloading file: {filename} to: {directory}")

    if filepath.exists():
        log.info(f"{filename}: File already exists. Skipping download.")
        return

    temp_dir = directory / 'tmp'
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_filepath = temp_dir / filename

    response = requests.get(download_url, stream=True)
    response.raise_for_status()

    total_size = int(response.headers.get('content-length', 0))
    log.debug(f"Total file size: {total_size} bytes")

    with open(temp_filepath, 'wb') as file:
        downloaded_size = 0
        last_percent_reported = 0
        for chunk in response.iter_content(chunk_size=None, decode_unicode=False):
            file.write(chunk)

            if status_bar:
                downloaded_size += len(chunk)

                if total_size > 0:
                    percent = (downloaded_size / total_size) * 100

                    if percent - last_percent_reported >= 1:
                        progress_bar = create_progress_bar(int(percent))
                        print(f"\r{filename}: {progress_bar}", end='', flush=True)
                        last_percent_reported = int(percent)

    shutil.move(str(temp_filepath), str(filepath))

    log.info(f"{filename}: Download complete.")


def download_multiple(
        download_urls: List[str],
        save_directory: Union[str, Path],
        filename_function: Optional[Callable] = None,
        status_bar: bool = False
) -> None:
    """
    Downloads multiple files from given URLs and saves them to a specified directory.

    This function iterates over a list of URLs, downloading each file to the specified directory.
    An optional filename function can be provided to determine the filename for each download based
    on its URL. If no filename function is provided, the default behavior is to use the last
    segment of the URL as the filename. Optionally, a status bar can be displayed to show the
    download progress for each file.

    Parameters:
    - download_urls (List[str]): A list of URLs from which files will be downloaded.
    - save_directory (Union[str, Path]): The directory where the files will be saved.
    - filename_function (Optional[Callable]): An optional function that takes a URL as input and
        returns a string filename. If None, the default is to use the last segment of the URL.
    - status_bar (bool, optional): Whether to display a download progress bar for each file.
        Defaults to False.

    The function creates a temporary directory within the save directory to handle the download
    process. Once all downloads are complete, if the temporary directory is empty, it is removed.
    """
    def _default_filename_func(_url: str) -> str:
        return _url.split('/')[-1]

    if filename_function is None:
        filename_function = _default_filename_func

    directory = Path(save_directory)
    directory.mkdir(parents=True, exist_ok=True)

    for url in download_urls:
        try:
            filename = filename_function(url)
            download_file(url, directory, filename, status_bar)
        except Exception:
            log.error(f"Error downloading {url}", exc_info=True)

    temp_dir = directory / 'tmp'
    if temp_dir.exists() and not any(temp_dir.iterdir()):
        temp_dir.rmdir()
