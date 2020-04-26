from config.config import SEASONS

def current_season():
    """Returns current season"""
    return SEASONS[-1]

def past_season():
    """Returns current season"""
    return SEASONS[-2]