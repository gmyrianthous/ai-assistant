from unittest.mock import MagicMock
from unittest.mock import patch

from pydantic import SecretStr

from ai_assistant.common.clients.growthbook import get_feature_value


class TestGetFeatureValue:
    def test_returns_default_when_no_client_key(self) -> None:
        # arrange & act
        with patch('ai_assistant.common.clients.growthbook.settings') as mock_settings:
            mock_settings.GROWTHBOOK_CLIENT_KEY = SecretStr('')
            result = get_feature_value('some-flag', default='fallback', user_id='user-1')

        # assert
        assert result == 'fallback'

    @patch('ai_assistant.common.clients.growthbook.GrowthBook')
    def test_evaluates_feature_for_user(self, mock_growthbook_class: MagicMock) -> None:
        # arrange
        mock_gb = MagicMock()
        mock_gb.get_feature_value.return_value = 'variant-b'
        mock_growthbook_class.return_value = mock_gb

        # act
        with patch('ai_assistant.common.clients.growthbook.settings') as mock_settings:
            mock_settings.GROWTHBOOK_CLIENT_KEY = SecretStr('sdk-key')
            mock_settings.GROWTHBOOK_API_HOST = 'http://localhost:3101'
            result = get_feature_value('some-flag', default='fallback', user_id='user-1')

        # assert
        assert result == 'variant-b'
        assert mock_growthbook_class.call_args.kwargs['attributes'] == {'id': 'user-1'}
        mock_gb.load_features.assert_called_once()
        mock_gb.get_feature_value.assert_called_once_with('some-flag', 'fallback')
        mock_gb.destroy.assert_called_once()

    @patch('ai_assistant.common.clients.growthbook.GrowthBook')
    def test_returns_default_on_error(self, mock_growthbook_class: MagicMock) -> None:
        # arrange
        mock_gb = MagicMock()
        mock_gb.load_features.side_effect = ConnectionError('GrowthBook unreachable')
        mock_growthbook_class.return_value = mock_gb

        # act
        with patch('ai_assistant.common.clients.growthbook.settings') as mock_settings:
            mock_settings.GROWTHBOOK_CLIENT_KEY = SecretStr('sdk-key')
            mock_settings.GROWTHBOOK_API_HOST = 'http://localhost:3101'
            result = get_feature_value('some-flag', default='fallback', user_id='user-1')

        # assert
        assert result == 'fallback'
        mock_gb.destroy.assert_called_once()
