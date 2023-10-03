import time
from typing import Dict, List, Optional, Union

import requests

import utilities as Utils
from utilities import ConfigType, EnvType


# =========================================================================== #

def get_api_url(env_type: EnvType) -> str:
    """Retrieve the API URL based on the environment type."""
    url_mapping = {
        EnvType.DEV: 'DEV_API_URL',
        EnvType.PRD: 'PROD_API_URL'
    }

    return Utils.get_config_val(
        section='GoDaddy',
        key=url_mapping[env_type]
    )


def get_batch_size() -> int:
    """Retrieve the batch size from the config file."""
    return Utils.get_config_val('GoDaddy', 'BATCH_SIZE')


def get_max_retries() -> int:
    """Retrieve the max retries from the config file."""
    return Utils.get_config_val('GoDaddy', 'MAX_RETRIES')


def get_secrets_section_map(env_type: EnvType) -> str:
    """Determine the appropriate section for config based on the environment."""
    secrets_mapping = {
        EnvType.DEV: 'GoDaddyDev',
        EnvType.PRD: 'GoDaddyProd'
    }

    return secrets_mapping[env_type]


def get_api_key(env_type: EnvType) -> str:
    """Retrieve the API key based on the environment type."""
    return Utils.get_config_val(
        section=get_secrets_section_map(env_type),
        key='API_KEY',
        config_type=ConfigType.SECRETS
    )


def get_api_secret(env_type: EnvType) -> str:
    """Retrieve the API secret based on the environment type."""
    return Utils.get_config_val(
        section=get_secrets_section_map(env_type),
        key='API_SECRET',
        config_type=ConfigType.SECRETS
    )


def check_godaddy_domain(domain: str, env_type: EnvType) -> bool:
    """Check if a domain is available using the GoDaddy API."""
    max_retries = get_max_retries()
    api_url = get_api_url(env_type)
    api_key = get_api_key(env_type)
    api_secret = get_api_secret(env_type)
    endpoint = f"{api_url}?domain={domain}"

    headers = {
        "Authorization": f"sso-key {api_key}:{api_secret}",
        "Accept": "application/json"
    }

    for _ in range(max_retries):
        response = requests.get(endpoint, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return data['available']

        if 'TOO_MANY_REQUESTS' in response.text:
            print("ERROR: TOO_MANY_REQUESTS -> pausing for 30 seconds...")
            time.sleep(30)
        else:
            print(f"ERROR: {response.status_code} -> {response.text}")
            return False

    print(f"ERROR: Failed to fetch data after {max_retries} retries.")
    return False


def get_domain_list(
    host_names: List[str],
    domain_endings: Optional[List[str]] = None
) -> List[str]:
    """Generate a list of full domain names to check."""
    if domain_endings is None:
        domain_endings = ['com']

    domains = []
    for host in host_names:
        for ending in domain_endings:
            domains.append(f"{host}.{ending}")
    return domains


def create_batches(
    items: List[str],
    batch_size: int
) -> List[List[str]]:
    """Split a list into smaller batches."""
    batches = []
    for i in range(0, len(items), batch_size):
        batches.append(items[i:i + batch_size])
    return batches


def check_domain_list(
    batch: List[str],
    env_type: EnvType
) -> List[Dict[str, Union[str, bool]]]:
    """Check domain availability for a batch of domain names."""
    json_results = []
    calc_results = []

    for domain in batch:
        is_available = check_godaddy_domain(domain, env_type)
        host_name, domain_ending = domain.rsplit('.', 1)
        json_results.append({'name': host_name, domain: is_available})
        calc_results.append({'name': host_name, 'domain': is_available})

    return json_results, calc_results


def main(
    host_names: List[str],
    env_type: Optional[EnvType] = None,
    domain_endings: Optional[List[str]] = None,
    batch_size: Optional[int] = None,
    limit: Optional[int] = None
) -> None:
    """Check domain availability for list of host names using GoDaddy API."""
    print("\n\nChecking domain name availability with GoDaddy API...")

    _env_type = env_type or EnvType.PRD
    _domain_endings = domain_endings or ['com']
    _batch_size = batch_size or get_batch_size()

    if limit is not None:
        host_names = host_names[:limit]

    batches = create_batches(
        items=get_domain_list(host_names, _domain_endings),
        batch_size=_batch_size
    )

    total_available = 0
    total_processed = 0

    for i, batch in enumerate(batches):
        print(f"\nProcessing batch {i + 1} of {len(batches)}...")
        print(f"Batch items: {batch}")
        json_results, calc_results = check_domain_list(batch, _env_type)

        batch_available = 0
        for item in calc_results:
            if item['domain'] is True:
                batch_available += 1

        total_available += batch_available
        total_processed += len(batch)

        if _env_type == EnvType.PRD:
            Utils.save_results_to_json(json_results)
        elif _env_type == EnvType.DEV:
            Utils.save_results_to_json(json_results, 'test_output.json')

        batch_percent = 100 * batch_available // len(batch)
        total_percent = 100.0 * total_available / total_processed

        print(f"Batch: {batch_available} of {len(batch)} available ({batch_percent}%).")
        print(f"Total: {total_available} of {total_processed} available ({total_percent:.1f}%).")


# =========================================================================== #

if __name__ == '__main__':
    # Test variables
    tst_host_names = ['FakeNameAlpha', 'FakeNameBravo']
    tst_domain_endings = ['com', 'org']
    tst_env_type = EnvType.DEV
    tst_batch_size = 2
    tst_domain = 'FakeNameCharlie.com'
    tst_domain_list = ['FakeNameDelta.com', 'FakeNameDelta.org']

    # Test get_domain_list function
    print("Testing get_domain_list function...")
    domain_list = get_domain_list(tst_host_names, tst_domain_endings)
    print(f"Domain List: {domain_list}")

    # Test create_batches function
    print("\nTesting create_batches function...")
    batches = create_batches(domain_list, tst_batch_size)
    print(f"Batches: {batches}")

    # Test check_godaddy_domain function
    print("\nTesting check_godaddy_domain function...")
    is_domain_available = check_godaddy_domain(tst_domain, tst_env_type)
    print(f"Is '{tst_domain}' available? {is_domain_available}")

    # Test check_domain_list function
    print("\nTesting check_domain_list function...")
    batch_results = check_domain_list(tst_domain_list, tst_env_type)
    print(f"Batch Results: {batch_results}")

    # Test main function
    print("\nTesting main function...")
    main(tst_host_names, tst_env_type, tst_domain_endings, tst_batch_size)
