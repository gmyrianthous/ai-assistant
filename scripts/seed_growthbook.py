"""
Bootstrap the local GrowthBook instance end-to-end, no UI clicks required.

Idempotently:
    1. Registers the first admin account (or logs in if it already exists)
    2. Creates a Python SDK connection and prints its client key
    3. Creates the `orchestrator-prompt-label` string feature with a 50/50
       experiment rule between the default prompt label (= ENVIRONMENT) and a
       variant label (`<ENVIRONMENT>-b`)
    4. Seeds the variant orchestrator prompt in Langfuse so the experiment
       serves a real prompt
    5. Writes the SDK client key into `.env` if GROWTHBOOK_CLIENT_KEY is empty

Usage:
    uv run python scripts/seed_growthbook.py
"""

import logging
import re
from pathlib import Path

import httpx
from langfuse.api import NotFoundError

from ai_assistant.common.clients.langfuse import get_langfuse_client
from ai_assistant.common.settings import settings

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

API_HOST = settings.GROWTHBOOK_API_HOST
ADMIN = {
    'companyname': 'Local',
    'name': 'Local Dev',
    'email': 'dev@example.com',
    'password': 'growthbook-local',
}
SDK_CONNECTION_NAME = 'local-python'
FEATURE_KEY = 'orchestrator-prompt-label'
CONTROL_LABEL = settings.ENVIRONMENT
VARIANT_LABEL = f'{settings.ENVIRONMENT}-b'
VARIANT_PROMPT = (
    'You are an enthusiastic orchestrator for a conversational AI assistant. '
    'Route weather questions to the weather_assistant agent and recipe or '
    'cooking questions to the recipe_assistant agent. Answer anything else '
    'yourself with a friendly, upbeat tone.'
)
ENV_FILE = Path(__file__).parent.parent / '.env'


def get_token(client: httpx.Client) -> str:
    """Register the first admin account, or log in if one already exists."""
    response = client.post(f'{API_HOST}/auth/firsttime', json=ADMIN)
    if response.status_code == 200:
        logger.info(f'Registered admin account `{ADMIN["email"]}`')
        return response.json()['token']

    logger.info('Installation already configured, logging in')
    response = client.post(
        f'{API_HOST}/auth/login',
        json={'email': ADMIN['email'], 'password': ADMIN['password']},
    )
    response.raise_for_status()
    return response.json()['token']


def ensure_sdk_connection(client: httpx.Client) -> str:
    """Create the Python SDK connection if missing and return its client key."""
    connections = client.get(f'{API_HOST}/sdk-connections').json().get('connections', [])
    for connection in connections:
        if connection['name'] == SDK_CONNECTION_NAME:
            logger.info(f'SDK connection `{SDK_CONNECTION_NAME}` already exists')
            return connection['key']

    response = client.post(
        f'{API_HOST}/sdk-connections',
        json={
            'name': SDK_CONNECTION_NAME,
            'languages': ['python'],
            'environment': 'production',
            'projects': [],
        },
    )
    response.raise_for_status()
    logger.info(f'Created SDK connection `{SDK_CONNECTION_NAME}`')
    return response.json()['connection']['key']


def ensure_feature_with_experiment(client: httpx.Client) -> None:
    """Create the prompt-label feature with a 50/50 experiment rule if missing."""
    response = client.get(f'{API_HOST}/feature/{FEATURE_KEY}')
    if response.status_code == 200 and response.json().get('feature'):
        logger.info(f'Feature `{FEATURE_KEY}` already exists')
        return

    response = client.post(
        f'{API_HOST}/feature',
        json={
            'id': FEATURE_KEY,
            'valueType': 'string',
            'defaultValue': CONTROL_LABEL,
            'description': 'Langfuse prompt label served per user for the orchestrator agent',
            'project': '',
            'tags': [],
            'environmentSettings': {
                'production': {
                    'enabled': True,
                    'rules': [
                        {
                            'type': 'experiment',
                            'description': 'Orchestrator prompt A/B test',
                            'id': '',
                            'trackingKey': FEATURE_KEY,
                            'hashAttribute': 'id',
                            'coverage': 1,
                            'enabled': True,
                            'values': [
                                {'value': CONTROL_LABEL, 'weight': 0.5, 'name': 'control'},
                                {'value': VARIANT_LABEL, 'weight': 0.5, 'name': 'variant-b'},
                            ],
                        }
                    ],
                }
            },
        },
    )
    response.raise_for_status()
    logger.info(
        f'Created feature `{FEATURE_KEY}` with a 50/50 experiment '
        f'({CONTROL_LABEL} vs {VARIANT_LABEL})'
    )


def ensure_variant_prompt() -> None:
    """Seed the variant orchestrator prompt in Langfuse if missing."""
    langfuse = get_langfuse_client()
    try:
        langfuse.get_prompt('orchestrator', label=VARIANT_LABEL, cache_ttl_seconds=0)
        logger.info(f'Langfuse prompt `orchestrator` (label=`{VARIANT_LABEL}`) already exists')
    except NotFoundError:
        langfuse.create_prompt(
            name='orchestrator',
            prompt=VARIANT_PROMPT,
            labels=[VARIANT_LABEL],
            type='text',
            config={'model': settings.DEFAULT_MODEL},
        )
        logger.info(f'Created Langfuse prompt `orchestrator` (label=`{VARIANT_LABEL}`)')


def write_client_key_to_env(client_key: str) -> None:
    """Set GROWTHBOOK_CLIENT_KEY in .env to the actual local SDK client key."""
    if not ENV_FILE.exists():
        logger.info(f'No .env file found, set GROWTHBOOK_CLIENT_KEY={client_key} manually')
        return

    content = ENV_FILE.read_text()
    match = re.search(r'^GROWTHBOOK_CLIENT_KEY=(.*)$', content, flags=re.M)
    if match:
        if match.group(1) == client_key:
            logger.info('GROWTHBOOK_CLIENT_KEY already up to date in .env')
            return
        content = re.sub(
            r'^GROWTHBOOK_CLIENT_KEY=.*$',
            f'GROWTHBOOK_CLIENT_KEY={client_key}',
            content,
            flags=re.M,
        )
    else:
        content = content.rstrip('\n') + f'\nGROWTHBOOK_CLIENT_KEY={client_key}\n'
    ENV_FILE.write_text(content)
    logger.info('Wrote GROWTHBOOK_CLIENT_KEY to .env')


def main() -> None:
    with httpx.Client(timeout=30) as client:
        token = get_token(client)
        client.headers['Authorization'] = f'Bearer {token}'

        # Scope subsequent requests to the (single) local organization
        organizations = client.get(f'{API_HOST}/user').json()['organizations']
        client.headers['X-Organization'] = organizations[0]['id']

        client_key = ensure_sdk_connection(client)
        ensure_feature_with_experiment(client)

    ensure_variant_prompt()
    write_client_key_to_env(client_key)

    logger.info('')
    logger.info(f'GrowthBook UI:  {API_HOST.replace("3101", "3002")}')
    logger.info(f'Login:          {ADMIN["email"]} / {ADMIN["password"]}')
    logger.info(f'SDK client key: {client_key}')


if __name__ == '__main__':
    main()
