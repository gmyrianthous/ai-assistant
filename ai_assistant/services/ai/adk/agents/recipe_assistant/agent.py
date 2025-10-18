from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ai_assistant.common.clients.langfuse import get_langfuse_client
from ai_assistant.common.settings import settings
from ai_assistant.services.ai.adk.tools.recipe_tools import get_recipe

langfuse_prompt = get_langfuse_client().get_prompt(
    name='recipe_assistant_agent',
    label=settings.ENVIRONMENT,
)

recipe_agent = LlmAgent(
    name='recipe_assistant',
    model=langfuse_prompt.config.get('model', settings.DEFAULT_MODEL),
    instruction=langfuse_prompt.prompt,
    tools=[FunctionTool(get_recipe)],
    generate_content_config=langfuse_prompt.config.get('generate_content_config'),
)
