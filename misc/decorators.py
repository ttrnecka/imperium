"""Web decorators"""
import functools
from misc.helpers import current_user, InvalidUsage

def authenticated(func):
    """Raises exception if not authenticated"""
    @functools.wraps(func)
    def wrapper_authenticated(*args, **kwargs):
        if not current_user():
            raise InvalidUsage('You are not authenticated', status_code=401)
        return func(*args, **kwargs)
    return wrapper_authenticated
