import logging

from google.adk.agents import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext

from ai_assistant.common.clients.growthbook import get_feature_value
from ai_assistant.common.clients.langfuse import get_langfuse_client
from ai_assistant.common.settings import settings
from ai_assistant.services.ai.adk.agents.recipe_assistant.agent import recipe_agent
from ai_assistant.services.ai.adk.agents.weather_assistant.agent import root_agent as weather_agent

logger = logging.getLogger(__name__)

# Feature flag (string) holding the Langfuse prompt label to serve. Point it
# at different labels in GrowthBook to A/B test orchestrator prompt variants.
ORCHESTRATOR_PROMPT_LABEL_FLAG = 'orchestrator-prompt-label'

langfuse_prompt = get_langfuse_client().get_prompt(
    name='orchestrator',
    label=settings.ENVIRONMENT,
)


def orchestrator_instruction(context: ReadonlyContext) -> str:
    """
    Resolve the orchestrator instruction per request.

    The prompt label is controlled by a GrowthBook feature flag so prompt
    variants can be rolled out or A/B tested per user. Falls back to the
    default prompt (label = ENVIRONMENT) when the flag is off or the variant
    label does not exist in Langfuse.

    Args:
        context: The ADK readonly invocation context.

    Returns:
        str: The instruction text for this invocation.
    """
    label = get_feature_value(
        ORCHESTRATOR_PROMPT_LABEL_FLAG,
        default=settings.ENVIRONMENT,
        user_id=context.user_id,
    )
    if label == settings.ENVIRONMENT:
        return langfuse_prompt.prompt

    try:
        return get_langfuse_client().get_prompt(name='orchestrator', label=label).prompt
    except Exception as e:
        logger.warning(f'Prompt label `{label}` not available, using default: {e}')
        return langfuse_prompt.prompt


orchestrator_agent = LlmAgent(
    name='orchestrator',
    model=langfuse_prompt.config.get('model', settings.DEFAULT_MODEL),
    instruction=orchestrator_instruction,
    sub_agents=[weather_agent, recipe_agent],
    generate_content_config=langfuse_prompt.config.get('generate_content_config'),
)
