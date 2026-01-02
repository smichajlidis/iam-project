from flask import session
from . import permissions

def current_user():
    user = session.get("user", {})
    return {
        "user": user,
        "roles": user.get("roles", []),
        "name": user.get("name"),
        "subordinates": user.get("subordinates", [])
    }

def can_create():
    cu = current_user()
    return permissions.REQUEST_CREATE in cu["roles"]

def can_display(request):
    cu = current_user()
    return ((permissions.REQUEST_DISPLAY_OWN in cu["roles"] and request.requestor == cu["name"])
            or (permissions.REQUEST_DISPLAY_SUBORDINATES in cu["roles"] and request.requestor in cu["subordinates"])
            or (permissions.REQUEST_CHANGE_STATUS_SUPPORTED_SCOPE in cu["roles"] and (request.status != "Submitted" and request.status != "Rejected"))
            or permissions.REQUEST_DISPLAY_ALL in cu["roles"])

def can_delete(request):
    cu = current_user()
    return ((permissions.REQUEST_DELETE_OWN in cu["roles"] and request.requestor == cu["name"])
            or permissions.REQUEST_DELETE_ALL in cu["roles"])

def can_update(request):
    cu = current_user()
    return ((permissions.REQUEST_UPDATE_OWN in cu["roles"] and request.requestor == cu["name"] and request.status == "Submitted")
            or permissions.REQUEST_UPDATE_ALL in cu["roles"])

def can_change_status_manager_scope(request):
    cu = current_user()
    return ((permissions.REQUEST_CHANGE_STATUS_MANAGER_SCOPE in cu["roles"] and request.requestor in cu["subordinates"])
            or (permissions.REQUEST_CHANGE_STATUS_ALL in cu["roles"]))

def can_change_status_support_scope(request):
    cu = current_user()
    return ((permissions.REQUEST_CHANGE_STATUS_SUPPORTED_SCOPE in cu["roles"] and (request.status != "Submitted" and request.status != "Rejected"))
            or (permissions.REQUEST_CHANGE_STATUS_ALL in cu["roles"]))
