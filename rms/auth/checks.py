from flask import session
from . import permissions

def current_user():
    user = session.get("user", {})
    return {
        "user": user,
        "roles": user.get("roles", []),
        "name": user.get("name")
    }

def can_create():
    cu = current_user()
    return permissions.REQUEST_CREATE in cu["roles"]

def can_display(request):
    cu = current_user()
    return ((permissions.REQUEST_DISPLAY_OWN in cu["roles"] and request.requestor == cu["name"])
            or permissions.REQUEST_DISPLAY_ALL in cu["roles"])

def can_delete_own(request):
    cu = current_user()
    return permissions.REQUEST_DELETE_OWN in cu["roles"] and request.requestor == cu["name"]

def can_update_own(request):
    cu = current_user()
    return permissions.REQUEST_UPDATE_OWN in cu["roles"] and request.requestor == cu["name"]