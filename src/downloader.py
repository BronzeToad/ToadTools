import shutil
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union
from urllib.parse import urlparse

import requests
import yaml


class Downloader:

    def __init__(
        self,
        download_directory: Optional[Union[str, Path]] = None,
        download_urls: Optional[List[str]] = None,
        derive_filename: Optional[str] = None
    ):
        self.cfg = self._load_config()
        self.download_directory = download_directory or self.cfg.get('download_directory', '')
        self.download_urls = download_urls or self.cfg.get('download_urls', [])
        self.derive_filename = derive_filename or self.cfg.get('derive_filename')
        self.filename_callable = self.get_filename_callable()

    @staticmethod
    def _load_config() -> Dict[str, Any]:
        config_dir = Path(__file__).parents[1] / 'cfg'
        downloader_cfg = config_dir / 'downloader.yml'
        try:
            with open(downloader_cfg, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Config file not found: {downloader_cfg}")
            return {}
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")
            return {}

    @staticmethod
    def _create_progress_bar(percent: int, width: int = 50) -> str:
        filled_width = int(width * percent // 100)
        bar = '█' * filled_width + '-' * (width - filled_width)
        return f'|{bar}| {percent}%'

    @staticmethod
    def _derive_filename(url: str) -> str:
        parsed_url = urlparse(url)
        filename = Path(parsed_url.path).name

        if not filename:
            filename = Path(parsed_url.path.rstrip('/')).name

        return filename

    def get_filename_callable(self) -> Callable[[str], str]:
        if not isinstance(self.derive_filename, str):
            return self._derive_filename

        def filename_func(url: str) -> str:
            # Use a dictionary with a limited set of allowed functions
            safe_dict = {
                'url': url,
                'split': str.split,
                'rsplit': str.rsplit,
                'Path': Path
            }
            try:
                # Evaluate the string in a restricted environment
                result = eval(self.derive_filename, {"__builtins__": {}}, safe_dict)
                return str(result)  # Ensure the result is a string
            except Exception as e:
                print(f"Error in deriving filename: {e}")
                return self._derive_filename(url)

        return filename_func


    def download_file(
        self,
        url: str,
        block_size: int = 8192,
        custom_filename: Optional[str] = None
    ) -> None:
        filename = custom_filename or self.filename_callable(url)
        tmp_directory = self.download_directory / 'tmp'
        tmp_file_path = tmp_directory / filename
        final_file_path = self.download_directory / filename

        tmp_directory.mkdir(parents=True, exist_ok=True)

        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            block_size = 8192
            downloaded_size = 0

            with open(tmp_file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=block_size):
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)

                        if total_size > 0:
                            percent = int((downloaded_size / total_size) * 100)
                            progress_bar = self._create_progress_bar(percent)
                            print(f"\r{filename}: {progress_bar}", end='', flush=True)

            print(f"\n{filename}: Download complete.")

            # Move file from tmp to final directory
            shutil.move(str(tmp_file_path), str(final_file_path))
            print(f"{filename}: Moved to final location.")

        except requests.RequestException as e:
            print(f"Error downloading {url}: {str(e)}")
        except Exception as e:
            print(f"Unexpected error while downloading {url}: {str(e)}")
        finally:
            # Clean up tmp file if it exists
            if tmp_file_path.exists():
                tmp_file_path.unlink()


    def sequential_downloader(self, urls: Optional[List[str]] = None) -> None:
        urls_to_download = urls or self.download_urls
        total_files = len(urls_to_download)

        print(f"Starting download of {total_files} files...")

        for index, url in enumerate(urls_to_download, start=1):
            print(f"\nDownloading file {index} of {total_files}")
            print(f"URL: {url}")

            start_time = time.time()
            self.download_file(url)
            end_time = time.time()

            download_time = end_time - start_time
            print(f"Download completed in {download_time:.2f} seconds")

        print("\nAll downloads completed!")

        # Clean up tmp directory
        tmp_directory = self.download_directory / 'tmp'
        if tmp_directory.exists() and not any(tmp_directory.iterdir()):
            tmp_directory.rmdir()
            print("Temporary directory cleaned up.")


if __name__ == "__main__":
    downloader = Downloader()
    downloader.sequential_downloader()
