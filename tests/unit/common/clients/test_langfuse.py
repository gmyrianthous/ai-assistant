from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from langfuse import Langfuse


class TestGetLangfuseClient:
    def setup_method(self) -> None:
        import ai_assistant.common.clients.langfuse as langfuse_module

        langfuse_module._langfuse_client = None

    @patch('ai_assistant.common.clients.langfuse.Langfuse')
    def test_get_langfuse_client_success(
        self,
        mock_langfuse_class: MagicMock,
    ) -> None:
        # arrange
        mock_instance = MagicMock(spec=Langfuse)
        mock_instance.auth_check.return_value = True
        mock_langfuse_class.return_value = mock_instance

        # act
        from ai_assistant.common.clients.langfuse import get_langfuse_client

        client = get_langfuse_client()

        # assert
        assert client is not None
        assert client == mock_instance
        mock_instance.auth_check.assert_called_once()

    @patch('ai_assistant.common.clients.langfuse.Langfuse')
    def test_get_langfuse_client_singleton_behavior(
        self,
        mock_langfuse_class: MagicMock,
    ) -> None:
        # arrange
        mock_instance = MagicMock(spec=Langfuse)
        mock_instance.auth_check.return_value = True
        mock_langfuse_class.return_value = mock_instance

        # act
        from ai_assistant.common.clients.langfuse import get_langfuse_client

        client1 = get_langfuse_client()
        client2 = get_langfuse_client()

        # assert
        assert client1 is client2
        mock_langfuse_class.assert_called_once()
        mock_instance.auth_check.assert_called_once()

    @patch('ai_assistant.common.clients.langfuse.Langfuse')
    def test_get_langfuse_client_auth_failure(
        self,
        mock_langfuse_class: MagicMock,
    ) -> None:
        # arrange
        mock_instance = MagicMock(spec=Langfuse)
        mock_instance.auth_check.return_value = False
        mock_langfuse_class.return_value = mock_instance

        # act & assert
        from ai_assistant.common.clients.langfuse import get_langfuse_client

        with pytest.raises(RuntimeError, match='Langfuse authentication failed'):
            get_langfuse_client()

    @patch('ai_assistant.common.clients.langfuse.Langfuse')
    def test_get_langfuse_client_initialization_failure(
        self,
        mock_langfuse_class: MagicMock,
    ) -> None:
        # arrange
        mock_langfuse_class.side_effect = Exception('Connection error')

        # act & assert
        from ai_assistant.common.clients.langfuse import get_langfuse_client

        with pytest.raises(Exception, match='Connection error'):
            get_langfuse_client()

    @patch('ai_assistant.common.clients.langfuse.Langfuse')
    def test_get_langfuse_client_resets_on_failure(
        self,
        mock_langfuse_class: MagicMock,
    ) -> None:
        # arrange
        mock_instance = MagicMock(spec=Langfuse)
        mock_instance.auth_check.return_value = False
        mock_langfuse_class.return_value = mock_instance

        # act
        import ai_assistant.common.clients.langfuse as langfuse_module
        from ai_assistant.common.clients.langfuse import get_langfuse_client

        try:
            get_langfuse_client()
        except RuntimeError:
            pass

        # assert
        assert langfuse_module._langfuse_client is None
