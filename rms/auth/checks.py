from flask import session
from .permissions import REQUEST_DISPLAY_OWN

def can_display_own(request):
    user = session.get('user', {})
    roles = user.get('roles', [])
    name = user.get("name")

    return (REQUEST_DISPLAY_OWN in roles and request.requestor == name)