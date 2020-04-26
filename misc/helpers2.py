from config.config import SEASONS

def current_season():
    """Returns current season"""
    return SEASONS[-1]

def past_season():
    """Returns current season"""
    return SEASONS[-2]


from datetime import datetime as dt, timedelta
from json import dumps
from flask import request, jsonify
from flask_caching import Cache
from functools import wraps

def etagjsonify(*args, **kwargs):
    response = jsonify(*args, **kwargs)
    response.last_modified = dt.utcnow()
    response.add_etag()
    return response

cache = Cache(config={'CACHE_TYPE': 'simple'})

def make_cache_key(*args, **kwargs):
  return request.url

def cache_header(max_age, **ckwargs):
    def decorator(view):
        ckwargs['key_prefix'] = make_cache_key
        f = cache.cached(max_age, **ckwargs)(view)
        #f = view
        @wraps(f)
        def wrapper(*args, **wkwargs):
            response = f(*args, **wkwargs)
            response.cache_control.max_age = max_age
            response.cache_control.public = True
            extra = timedelta(seconds=max_age)
            response.expires = response.last_modified + extra
            return response.make_conditional(request)
        return wrapper

    return decorator
