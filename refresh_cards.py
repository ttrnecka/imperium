# Works with Python 3.6
import logging
import os

from imperiumbase import ImperiumSheet
from web import db, create_app
from models.data_models import Card
from services import CardService

app = create_app()
app.app_context().push()

ROOT = os.path.dirname(__file__)

logger = logging.getLogger('refresh')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=os.path.join(ROOT, 'logs/refresh.log'), encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

for card in ImperiumSheet.cards():
    c_dict = CardService.init_dict_from_card(card)
    cards = Card.query.filter_by(name = c_dict['name']).all()
    
    for scard in cards:
        scard.update(**c_dict)

db.session.commit()
    