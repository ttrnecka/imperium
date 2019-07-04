"""Match helpers"""

def is_concede(data):
    """Given match data returns True if the match was conceded"""
    if (data['match']['teams'][0]['mvp'] == 2
            or data['match']['teams'][1]['mvp'] == 2):
        return True
    return False
