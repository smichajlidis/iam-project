from flask import session
from . import permissions

def current_user():
    user = session.get("user", {})
    return {
        "user": user,
        "roles": user.get("roles", []),
        "name": user.get("name"),
    }

def can_create():
    cu = current_user()
    return permissions.EMPLOYEE_CREATE in cu["roles"]

def can_display():
    cu = current_user()
    return permissions.EMPLOYEE_DISPLAY in cu["roles"]

def can_delete():
    cu = current_user()
    return permissions.EMPLOYEE_DELETE in cu["roles"]

def can_update():
    cu = current_user()
    return permissions.EMPLOYEE_UPDATE in cu["roles"]

def can_change_status():
    cu = current_user()
    return permissions.EMPLOYEE_CHANGE_STATUS in cu["roles"]