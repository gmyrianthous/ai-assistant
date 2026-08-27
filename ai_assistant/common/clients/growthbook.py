"""
GrowthBook client for feature flags and experimentation.

Feature evaluation happens in-process: the SDK fetches feature definitions
from the GrowthBook API and caches them (60s TTL by default), so flag checks
do not add a network round-trip per request. Flags fail open: any error (or
a missing client key) yields the provided default value, so feature flags can
never break the application.
"""

import logging
from typing import Any

from growthbook import Experiment
from growthbook import GrowthBook
from growthbook import Result
from growthbook.common_types import UserContext

from ai_assistant.common.settings import settings

logger = logging.getLogger(__name__)


def _on_experiment_viewed(
    *,
    experiment: Experiment[Any],
    result: Result[Any],
    user_context: UserContext,
) -> None:
    """Log experiment exposure (assignment of a user to a variation)."""
    logger.info(
        f'Experiment exposure: experiment={experiment.key}, '
        f'variation={result.variationId}, value={result.value}'
    )


def get_feature_value(key: str, default: str, user_id: str) -> str:
    """
    Evaluate a feature flag for a user.

    Args:
        key: The GrowthBook feature key.
        default: Value returned when flags are disabled, the feature is
            missing, or evaluation fails.
        user_id: The user the flag is evaluated for (used for consistent
            experiment bucketing).

    Returns:
        str: The evaluated feature value, or the default.
    """
    client_key = settings.GROWTHBOOK_CLIENT_KEY.get_secret_value()
    if not client_key:
        return default

    gb = GrowthBook(
        api_host=settings.GROWTHBOOK_API_HOST,
        client_key=client_key,
        attributes={'id': user_id},
        on_experiment_viewed=_on_experiment_viewed,
    )
    try:
        gb.load_features()
        value = gb.get_feature_value(key, default)
        return str(value)
    except Exception as e:
        logger.warning(f'Feature flag evaluation failed for `{key}`: {e}')
        return default
    finally:
        gb.destroy()
