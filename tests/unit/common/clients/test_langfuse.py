from collections.abc import Generator
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from langfuse import Langfuse

from ai_assistant.common.clients.langfuse import LangfuseClientSingleton


class TestLangfuseClientSingleton:
    @pytest.fixture
    def reset_client(self) -> Generator[None, None, None]:
        """
        Reset the singleton between tests to maintain test isolation.
        """
        LangfuseClientSingleton._client = None
        yield
        LangfuseClientSingleton._client = None

    @patch('ai_core.common.clients.langfuse.Langfuse')
    def test_get_langfuse_client_success(
        self,
        mock_langfuse: MagicMock,
        reset_client: None,
    ) -> None:
        # arrange
        mock_instance = MagicMock(spec=Langfuse)
        mock_langfuse.return_value = mock_instance

        # act
        client = LangfuseClientSingleton.get_langfuse_client()

        # assert
        assert client == mock_instance
        assert LangfuseClientSingleton._client == mock_instance

    @patch('ai_core.common.clients.langfuse.Langfuse')
    def test_get_langfuse_client_singleton(
        self,
        mock_langfuse: MagicMock,
        reset_client: None,
    ) -> None:
        # arrange
        mock_langfuse.return_value = MagicMock(spec=Langfuse)

        # act
        client1 = LangfuseClientSingleton.get_langfuse_client()
        client2 = LangfuseClientSingleton.get_langfuse_client()

        # assert
        assert client1 == client2
        mock_langfuse.assert_called_once()

    @patch('ai_core.common.clients.langfuse.Langfuse')
    @patch('ai_core.common.clients.langfuse.logger.error')
    def test_get_langfuse_client_exception(
        self,
        mock_logger_error: MagicMock,
        mock_langfuse: MagicMock,
        reset_client: None,
    ) -> None:
        # arrange
        mock_langfuse.side_effect = Exception('Connection error')

        # act
        client = LangfuseClientSingleton.get_langfuse_client()

        # assert
        assert client is None
        mock_logger_error.assert_called_once_with(
            'Failed to initialize Langfuse client: Connection error'
        )
        assert LangfuseClientSingleton._client is None
