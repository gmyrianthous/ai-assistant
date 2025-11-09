from google.adk.agents import LlmAgent

from ai_assistant.common.clients.langfuse import get_langfuse_client
from ai_assistant.common.settings import settings
from ai_assistant.services.ai.adk.agents.recipe_assistant.agent import recipe_agent
from ai_assistant.services.ai.adk.agents.weather_assistant.agent import root_agent as weather_agent

langfuse_prompt = get_langfuse_client().get_prompt(
    name='orchestrator',
    label=settings.ENVIRONMENT,
)

orchestrator_agent = LlmAgent(
    name='orchestrator',
    model=langfuse_prompt.config.get('model', settings.DEFAULT_MODEL),
    instruction=langfuse_prompt.prompt,
    sub_agents=[weather_agent, recipe_agent],
    generate_content_config=langfuse_prompt.config.get('generate_content_config'),
)
