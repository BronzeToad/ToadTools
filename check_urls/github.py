from typing import Dict, List, Optional, Union

import requests

import utilities as Utils
from utilities import ConfigType, EnvType

# =========================================================================== #

def get_base_api_url() -> str:
    """Retrieve the GitHub API URL."""
    return Utils.get_config_val('GitHub', 'BASE_API_URL')


def get_public_access_token() -> str:
    """Retrieve the GitHub public access token."""
    return Utils.get_config_val(
        section='GitHubPublicAccess',
        key='ACCESS_TOKEN',
        config_type=ConfigType.SECRETS
    )


def get_batch_size() -> int:
    """Retrieve the batch size from the config file."""
    return Utils.get_config_val('GitHub', 'BATCH_SIZE')


def check_github_username(username: str) -> bool:
    """Check if a GitHub username is available."""
    headers = {'Authorization': f'token {get_public_access_token()}'}
    url = f"{get_base_api_url()}{username}"

    try:
        response = requests.get(url=url, headers=headers)

        if response.status_code == 404:
            return True
        elif response.status_code == 200:
            return False
        else:
            print(f"ERROR: {response.status_code} -> {response.text}")
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False


def check_username_list(batch: List[str]) -> List[Dict[str, Union[str, bool]]]:
    results = []

    for username in batch:
        is_available = check_github_username(username)
        results.append({'name': username, 'GitHub': is_available})

    return results


def main(
    usernames: List[str],
    env_type: Optional[EnvType] = None,
    batch_size: Optional[int] = None,
    limit: Optional[int] = None
) -> None:
    print("\n\nChecking GitHub username availability...")
    _env_type = env_type or EnvType.PRD
    _batch_size = batch_size or get_batch_size()

    if limit is not None:
        usernames = usernames[:limit]

    batches = Utils.create_batches(usernames, _batch_size)

    total_available = 0
    total_processed = 0

    for i, batch in enumerate(batches):
        print(f"\nProcessing batch {i + 1} of {len(batches)}...")
        print(f"Batch items: {batch}")
        results = check_username_list(batch)

        batch_available = 0
        for item in results:
            if item['GitHub'] is True:
                batch_available += 1

        total_available += batch_available
        total_processed += len(batch)

        save_loc = None if _env_type == EnvType.PRD else 'test_output.json'
        Utils.save_results_to_json(results, save_loc)

        batch_percent = 100 * batch_available // len(batch)
        total_percent = 100.0 * total_available / total_processed

        print(f"Batch: {batch_available} of {len(batch)} available ({batch_percent}%).")
        print(f"Total: {total_available} of {total_processed} available ({total_percent:.1f}%).")


# =========================================================================== #

if __name__ == '__main__':
    # Test variables
    tst_usernames = ['FakeNameAlpha', 'FakeNameBravo',
                     'FakeNameCharlie', 'BronzeToad']
    tst_env_type = EnvType.DEV
    tst_batch_size = 2
    tst_username = 'FakeNameAlpha'

    # Testing get_base_api_url function
    print("Testing get_base_api_url function...")
    print(f"Base API URL: {get_base_api_url()}")

    # Testing get_public_access_token function
    print("\nTesting get_public_access_token function...")
    print(f"Public Access Token (first 4 chars for safety): {get_public_access_token()[:4]}...")

    # Testing get_batch_size function
    print("\nTesting get_batch_size function...")
    print(f"Batch Size: {get_batch_size()}")

    # Testing check_github_username function
    print(f"\nTesting check_github_username function for username: {tst_username}...")
    is_available = check_github_username(tst_username)
    print(f"Is '{tst_username}' available? {is_available}")

    # Testing check_username_list function
    print("\nTesting check_username_list function...")
    print(f"Batch Results: {check_username_list(tst_usernames)}")

    # Test main function
    print("\nTesting main function...")
    main(tst_usernames, tst_env_type, tst_batch_size)
