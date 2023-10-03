import requests

import utilities as Utils
from utilities import ConfigType

# =========================================================================== #

def get_base_api_url() -> str:
    """Retrieve the GitHub API URL."""
    return Utils.get_config_val(
        section='GitHub',
        key='BASE_API_URL'
    )

def get_batch_size() -> int:
    """Retrieve the batch size from the config file."""
    return Utils.get_config_val('Github', 'BATCH_SIZE')


def get_max_retries() -> int:
    """Retrieve the max retries from the config file."""
    return Utils.get_config_val('Github', 'MAX_RETRIES')

# =========================================================================== #

if __name__ == '__main__':
    pass