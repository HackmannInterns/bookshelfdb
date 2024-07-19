from permissions import get_permissions
from unittest.mock import patch, MagicMock


def test_no_additional():
    with patch('app.session', MagicMock()) as mock_session:
        with patch('admin.get_settings') as mock_get_settings:
            mock_session.get.side_effect = lambda key, default=None: {
                'recent': [1],
                'authenticated': 'Admin'
            }.get(key, default)

            mock_settings_instance = MagicMock()
            mock_settings_instance.viewer_can_add = False
            mock_settings_instance.editor_can_remove = False
            mock_get_settings.return_value = mock_settings_instance

            p = get_permissions()
            assert p.req_perms_can_view_library.name == 'Viewer'
            assert p.req_perms_can_add.name == 'Editor'
            assert p.req_perms_can_edit.name == 'Editor'
            assert p.req_perms_can_remove.name == 'Admin'
            assert p.req_perms_can_view_admin.name == 'Admin'


def test_viewer_add():
    with patch('app.session', MagicMock()) as mock_session:
        with patch('admin.get_settings') as mock_get_settings:
            mock_session.get.side_effect = lambda key, default=None: {
                'recent': [1],
                'authenticated': 'Admin'
            }.get(key, default)

            mock_settings_instance = MagicMock()
            mock_settings_instance.viewer_can_add = True
            mock_settings_instance.editor_can_remove = False
            mock_get_settings.return_value = mock_settings_instance

            p = get_permissions()
            assert p.req_perms_can_view_library.name == 'Viewer'
            assert p.req_perms_can_add.name == 'Viewer'
            assert p.req_perms_can_edit.name == 'Editor'
            assert p.req_perms_can_remove.name == 'Admin'
            assert p.req_perms_can_view_admin.name == 'Admin'


def test_viewer_add_editor_remove():
    with patch('app.session', MagicMock()) as mock_session:
        with patch('admin.get_settings') as mock_get_settings:
            mock_session.get.side_effect = lambda key, default=None: {
                'recent': [1],
                'authenticated': 'Admin'
            }.get(key, default)

            mock_settings_instance = MagicMock()
            mock_settings_instance.viewer_can_add = True
            mock_settings_instance.editor_can_remove = True
            mock_get_settings.return_value = mock_settings_instance

            p = get_permissions()
            assert p.req_perms_can_view_library.name == 'Viewer'
            assert p.req_perms_can_add.name == 'Viewer'
            assert p.req_perms_can_edit.name == 'Editor'
            assert p.req_perms_can_remove.name == 'Editor'
            assert p.req_perms_can_view_admin.name == 'Admin'


def test_editor_remove():
    with patch('app.session', MagicMock()) as mock_session:
        with patch('admin.get_settings') as mock_get_settings:
            mock_session.get.side_effect = lambda key, default=None: {
                'recent': [1],
                'authenticated': 'Admin'
            }.get(key, default)

            mock_settings_instance = MagicMock()
            mock_settings_instance.viewer_can_add = False
            mock_settings_instance.editor_can_remove = True
            mock_get_settings.return_value = mock_settings_instance

            p = get_permissions()
            assert p.req_perms_can_view_library.name == 'Viewer'
            assert p.req_perms_can_add.name == 'Editor'
            assert p.req_perms_can_edit.name == 'Editor'
            assert p.req_perms_can_remove.name == 'Editor'
            assert p.req_perms_can_view_admin.name == 'Admin'


def test_descriptions():
    with patch('app.session', MagicMock()) as mock_session:
        with patch('admin.get_settings') as mock_get_settings:
            mock_session.get.side_effect = lambda key, default=None: {
                'recent': [1],
                'authenticated': 'Admin'
            }.get(key, default)

            mock_settings_instance = MagicMock()
            mock_settings_instance.viewer_can_add = False
            mock_settings_instance.editor_can_remove = True
            mock_get_settings.return_value = mock_settings_instance

            p = get_permissions()
            assert p.desc_can_view_library == 'You cannot view the library page with your current authentication level'
            assert p.desc_can_add == 'You cannot add with your current authentication level'
            assert p.desc_can_edit == 'You cannot edit with your current authentication level'
            assert p.desc_can_remove == 'You cannot remove with your current authentication level'
            assert p.desc_can_view_admin == 'You cannot view admin with your current authentication level'
