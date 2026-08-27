from unittest.mock import MagicMock
from unittest.mock import patch

from ai_assistant.common.settings import settings
from ai_assistant.services.ai.adk.agents.orchestrator.agent import langfuse_prompt
from ai_assistant.services.ai.adk.agents.orchestrator.agent import orchestrator_agent
from ai_assistant.services.ai.adk.agents.orchestrator.agent import orchestrator_instruction


def _context(user_id: str = 'user-1') -> MagicMock:
    context = MagicMock()
    context.user_id = user_id
    return context


class TestOrchestratorInstruction:
    def test_agent_uses_instruction_provider(self) -> None:
        assert orchestrator_agent.instruction is orchestrator_instruction

    @patch('ai_assistant.services.ai.adk.agents.orchestrator.agent.get_feature_value')
    def test_returns_default_prompt_when_flag_off(self, mock_flag: MagicMock) -> None:
        # arrange: flag evaluates to the default label (= ENVIRONMENT)
        mock_flag.return_value = settings.ENVIRONMENT

        # act
        instruction = orchestrator_instruction(_context())

        # assert
        assert instruction == langfuse_prompt.prompt
        mock_flag.assert_called_once_with(
            'orchestrator-prompt-label',
            default=settings.ENVIRONMENT,
            user_id='user-1',
        )

    @patch('ai_assistant.services.ai.adk.agents.orchestrator.agent.get_langfuse_client')
    @patch('ai_assistant.services.ai.adk.agents.orchestrator.agent.get_feature_value')
    def test_fetches_variant_prompt_for_flagged_label(
        self,
        mock_flag: MagicMock,
        mock_langfuse: MagicMock,
    ) -> None:
        # arrange
        mock_flag.return_value = 'variant-b'
        variant_prompt = MagicMock()
        variant_prompt.prompt = 'You are variant B.'
        mock_langfuse.return_value.get_prompt.return_value = variant_prompt

        # act
        instruction = orchestrator_instruction(_context())

        # assert
        assert instruction == 'You are variant B.'
        mock_langfuse.return_value.get_prompt.assert_called_once_with(
            name='orchestrator', label='variant-b'
        )

    @patch('ai_assistant.services.ai.adk.agents.orchestrator.agent.get_langfuse_client')
    @patch('ai_assistant.services.ai.adk.agents.orchestrator.agent.get_feature_value')
    def test_falls_back_to_default_when_variant_prompt_missing(
        self,
        mock_flag: MagicMock,
        mock_langfuse: MagicMock,
    ) -> None:
        # arrange
        mock_flag.return_value = 'variant-does-not-exist'
        mock_langfuse.return_value.get_prompt.side_effect = Exception('prompt not found')

        # act
        instruction = orchestrator_instruction(_context())

        # assert
        assert instruction == langfuse_prompt.prompt
