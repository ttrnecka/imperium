"""Web decorators"""
import functools

from misc.helpers import current_user, InvalidUsage, current_coach

def authenticated(func):
    """Raises exception if not authenticated"""
    @functools.wraps(func)
    def wrapper_authenticated(*args, **kwargs):
        if not current_user():
            raise InvalidUsage('You are not authenticated', status_code=401)
        return func(*args, **kwargs)
    return wrapper_authenticated

def registered(func):
    """Raises exception if coach is not registered through discord bot"""
    @functools.wraps(func)
    def wrapper_registered(*args, **kwargs):
        coach = current_coach()
        if not coach:
            raise InvalidUsage("Coach not found", status_code=403)
        kwargs['coach'] = coach
        return func(*args, **kwargs)
    return wrapper_registered

def webadmin(func):
    """Raises exception if coach is webadmin"""
    @functools.wraps(func)
    def wrapper_webadmin(*args, **kwargs):
        coach = current_coach()
        if not coach:
            raise InvalidUsage("Coach not found", status_code=403)
        if not coach.web_admin:
            raise InvalidUsage("Coach does not have webadmin role", status_code=403)
        return func(*args, **kwargs)
    return wrapper_webadmin
