from enum import Enum
import admin as admin_settings


class Auth(Enum):
    Viewer = 0
    Editor = 1
    Admin = 2


def is_permitted(permission, check_for_recent=False):
    from app import session
    is_recent = check_for_recent if check_for_recent is False else check_for_recent in session.get(
        'recent', [])
    perms = get_permissions(is_recent=is_recent)
    permitted = getattr(perms, permission)

    # if not permitted:
    #     set_session_permissions(permission)
    return permitted


def set_session_permissions(permission):
    from app import session

    perms = get_permissions()
    session['description'] = getattr(perms, f"desc_{permission}")
    session['required_permission'] = getattr(
        perms, f"req_perms_{permission}").name
    session['insufficient_perm'] = True


def get_permissions(is_recent=False):
    from app import session

    user_type = Auth[session.get('authenticated', 'Viewer')]
    yaml_settings = admin_settings.get_settings()

    class Permissions:

        # setting viewing perms
        req_perms_can_view_library = Auth['Viewer']
        desc_can_view_library = 'You cannot view the library page with your current authentication level'
        can_view_library = user_type.value >= Auth['Viewer'].value

        # setting add perms
        req_perms_can_add = Auth['Viewer'] if yaml_settings.visitor_can_add else Auth['Editor']
        desc_can_add = 'You cannot add with your current authentication level'
        can_add = user_type.value >= req_perms_can_add.value

        # setting edit perms
        req_perms_can_edit = Auth['Viewer'] if is_recent else Auth['Editor']
        desc_can_edit = 'You cannot edit with your current authentication level'
        can_edit = user_type.value >= req_perms_can_edit.value

        # setting remove perms
        req_perms_can_remove = Auth['Viewer'] if is_recent else Auth[
            'Editor'] if yaml_settings.editor_can_remove else Auth['Admin']
        desc_can_remove = 'You cannot remove with your current authentication level'
        can_remove = user_type.value >= req_perms_can_remove.value

        # setting admin perms
        req_perms_can_view_admin = Auth['Admin']
        desc_can_view_admin = 'You cannot view admin with your current authentication level'
        can_view_admin = user_type.value >= Auth['Admin'].value

    return Permissions()
