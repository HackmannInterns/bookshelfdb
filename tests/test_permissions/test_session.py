from unittest.mock import Mock, patch
from permissions import set_session_permissions


def test_set_session_permissions():
    mock_session = {}

    mock_get_permissions = Mock()
    mock_permissions = Mock()
    mock_permissions.desc_permission = 'You cannot add with your current authentication level'
    mock_permissions.req_perms_permission = Mock(
        name='Editor')
    mock_get_permissions.return_value = mock_permissions

    with patch('app.session', mock_session), \
            patch('permissions.get_permissions', mock_get_permissions):

        # Check empty before run
        assert 'description' not in mock_session
        assert 'required_permission' not in mock_session
        assert 'insufficient_perm' not in mock_session

        set_session_permissions('permission')

        # Check here after run
        assert mock_session['description'] == mock_permissions.desc_permission
        assert mock_session['required_permission'] == mock_permissions.req_perms_permission.name
        assert mock_session['insufficient_perm'] is True
