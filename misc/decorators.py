"""Web decorators"""
import functools
from flask import request

from misc.helpers import current_user, InvalidUsage, current_coach, current_coach_with_inactive, db

def cracker_api_user(func):
    """Raises expcetion of not api user"""
    @functools.wraps(func)
    def wrapper_cracker_api_user(*args, **kwargs):
        key = request.headers.get('CRACKER-API-KEY')
        if not key or key != "hz@ue}Kh10*r7Td&@D`igA{6g2zv7X":
            raise InvalidUsage('You are not authorized to use this API', status_code=401)
        return func(*args, **kwargs)
    return wrapper_cracker_api_user

def authenticated(func):
    """Raises exception if not authenticated"""
    @functools.wraps(func)
    def wrapper_authenticated(*args, **kwargs):
        if not current_user():
            raise InvalidUsage('You are not authenticated', status_code=401)
        return func(*args, **kwargs)
    return wrapper_authenticated

def registered(func):
    """Raises exception if coach is not registered through discord bot and is inactive"""
    @functools.wraps(func)
    def wrapper_registered(*args, **kwargs):
        coach = current_coach()
        if not coach:
            raise InvalidUsage("Coach not found", status_code=403)
        kwargs['coach'] = coach
        return func(*args, **kwargs)
    return wrapper_registered

def registered_with_inactive(func):
    """Raises exception if coach is not registered through discord bot"""
    @functools.wraps(func)
    def wrapper_registered(*args, **kwargs):
        coach = current_coach_with_inactive()
        if not coach:
            raise InvalidUsage("Coach not found", status_code=403)
        kwargs['coach'] = coach
        return func(*args, **kwargs)
    return wrapper_registered

def webadmin(func):
    """Raises exception if coach is not webadmin"""
    @functools.wraps(func)
    def wrapper_webadmin(*args, **kwargs):
        coach = current_coach()
        if not coach:
            raise InvalidUsage("Coach not found", status_code=403)
        if not coach.web_admin:
            raise InvalidUsage("Coach does not have webadmin role", status_code=403)
        return func(*args, **kwargs)
    return wrapper_webadmin

def masteradmin(func):
    """Raises exception if coach is master admin"""
    @functools.wraps(func)
    def wrapper_masteradmin(*args, **kwargs):
        coach = current_coach()
        if not coach:
            raise InvalidUsage("Coach not found", status_code=403)
        if not coach.short_name() == db.get_app().config['TOURNAMENT_MASTER_ADMIN']:
            raise InvalidUsage(f"Only {db.get_app().config['TOURNAMENT_MASTER_ADMIN']} can do this!", status_code=403)
        return func(*args, **kwargs)
    return wrapper_masteradmin

