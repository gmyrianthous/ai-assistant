"""
Seed the local Langfuse instance with the prompts the app fetches at startup.

The agents load their instructions from Langfuse (`orchestrator`,
`weather_assistant_agent`, `recipe_assistant_agent`) using the label that
matches ENVIRONMENT, so a fresh self-hosted Langfuse must be seeded once
before the API can boot. Existing prompts are left untouched.

Usage:
    uv run python scripts/seed_langfuse_prompts.py
"""

import logging

from langfuse.api import NotFoundError

from ai_assistant.common.clients.langfuse import get_langfuse_client
from ai_assistant.common.settings import settings

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

PROMPTS = {
    'orchestrator': (
        'You are an orchestrator for a conversational AI assistant. '
        'Route weather questions to the weather_assistant agent and recipe or '
        'cooking questions to the recipe_assistant agent. Answer anything else '
        'yourself, briefly and helpfully.'
    ),
    'weather_assistant_agent': (
        'You are a weather assistant. Use the get_weather tool to look up the '
        'weather for the requested location and summarise the result for the user.'
    ),
    'recipe_assistant_agent': (
        'You are a recipe assistant. Use the get_recipe tool to find a recipe '
        'for the requested dish and present it clearly to the user.'
    ),
}


def main() -> None:
    label = settings.ENVIRONMENT
    langfuse = get_langfuse_client()

    for name, prompt in PROMPTS.items():
        try:
            langfuse.get_prompt(name, label=label, cache_ttl_seconds=0)
            logger.info(f'Prompt `{name}` (label=`{label}`) already exists, skipping')
        except NotFoundError:
            langfuse.create_prompt(
                name=name,
                prompt=prompt,
                labels=[label],
                type='text',
                config={'model': settings.DEFAULT_MODEL},
            )
            logger.info(f'Created prompt `{name}` (label=`{label}`)')


if __name__ == '__main__':
    main()
