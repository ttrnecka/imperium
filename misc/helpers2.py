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

def etagjsonify(*args, **kwargs):
    response = jsonify(*args, **kwargs)
    response.last_modified = dt.utcnow()
    response.add_etag()
    return response
