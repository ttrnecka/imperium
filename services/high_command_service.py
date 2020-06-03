"""DusterService helpers"""

from models.data_models import Coach, Transaction
from models.base_model import db
from .notification_service import Notificator

class HighCommandError(Exception):
    """Exception used for High Commands Errors"""

MAX_LEVEL_ERROR = "Max High Command level reached"

HC_PRICES = [
  10,20,30,40,50,60
]

def level(coach):
    """Level high command"""
    hc = coach.high_command

    # check if max level
    if len(HC_PRICES) == hc.level - 1:
      raise HighCommandError(MAX_LEVEL_ERROR)
    
    hc.level += 1
    reason = f"Updated High Command to level {hc.level}"
    tran = Transaction(description=reason, price=HC_PRICES[hc.level-2])
    coach.make_transaction(tran)
    Notificator("bank").notify(
        f"{coach.short_name()}: {reason}"
    )
    return True
