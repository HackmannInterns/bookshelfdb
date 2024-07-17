from permissions import is_permitted
from unittest.mock import patch, MagicMock


def test_viewer():
    with patch('app.session', MagicMock()) as mock_session:
        with patch('admin.get_settings') as mock_get_settings:
            mock_session.get.side_effect = lambda key, default=None: {
                'recent': [1],
                'authenticated': 'Viewer'
            }.get(key, default)

            mock_settings_instance = MagicMock()
            mock_settings_instance.viewer_can_add = False
            mock_settings_instance.editor_can_remove = False
            mock_get_settings.return_value = mock_settings_instance

            assert is_permitted('can_view_library')
            assert not is_permitted('can_add')
            assert not is_permitted('can_edit')
            assert not is_permitted('can_remove')
            assert not is_permitted('can_view_admin')


def test_viewer_recent():
    with patch('app.session', MagicMock()) as mock_session:
        with patch('admin.get_settings') as mock_get_settings:
            mock_session.get.side_effect = lambda key, default=None: {
                'recent': [1],
                'authenticated': 'Viewer'
            }.get(key, default)
            mock_session.get

            mock_settings_instance = MagicMock()
            mock_settings_instance.viewer_can_add = False
            mock_settings_instance.editor_can_remove = False
            mock_get_settings.return_value = mock_settings_instance

            assert is_permitted('can_view_library', 1)
            assert not is_permitted('can_add', 1)
            assert is_permitted('can_edit', 1)
            assert is_permitted('can_remove', 1)
            assert not is_permitted('can_view_admin', 1)


def test_viewer_recent_can_add():
    with patch('app.session', MagicMock()) as mock_session:
        with patch('admin.get_settings') as mock_get_settings:
            mock_session.get.side_effect = lambda key, default=None: {
                'recent': [1],
                'authenticated': 'Viewer'
            }.get(key, default)
            mock_session.get

            mock_settings_instance = MagicMock()
            mock_settings_instance.viewer_can_add = True
            mock_settings_instance.editor_can_remove = False
            mock_get_settings.return_value = mock_settings_instance

            assert is_permitted('can_view_library', 1)
            assert is_permitted('can_add', 1)
            assert is_permitted('can_edit', 1)
            assert is_permitted('can_remove', 1)
            assert not is_permitted('can_view_admin', 1)


def test_viewer_can_add():
    with patch('app.session', MagicMock()) as mock_session:
        with patch('admin.get_settings') as mock_get_settings:
            mock_session.get.side_effect = lambda key, default=None: {
                'recent': [1],
                'authenticated': 'Viewer'
            }.get(key, default)
            mock_session.get

            mock_settings_instance = MagicMock()
            mock_settings_instance.viewer_can_add = True
            mock_settings_instance.editor_can_remove = False
            mock_get_settings.return_value = mock_settings_instance

            assert is_permitted('can_view_library')
            assert is_permitted('can_add')
            assert not is_permitted('can_edit')
            assert not is_permitted('can_remove')
            assert not is_permitted('can_view_admin')
