from functools import wraps   ###
from flask import abort   # abort(403)
from flask_login import current_user
from .models import Permission

def permission_required(permission):   # @permission_required(Permission.MODERATE)
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission): # when the current user does not have the requested permission
                abort(403)   # return a 403 response, the “Forbidden” HTTP status code
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):   # @admin_required
    return permission_required(Permission.ADMIN)(f)
