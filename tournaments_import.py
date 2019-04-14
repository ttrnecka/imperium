# Works with Python 3.6
import logging
import os

from imperiumbase import ImperiumSheet
from web import db, create_app
from models.data_models import Tournament
from services import TournamentService


app = create_app()
app.app_context().push()

ROOT = os.path.dirname(__file__)

logger = logging.getLogger('import')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=os.path.join(ROOT, 'logs/import.log'), encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

for tournament in ImperiumSheet.tournaments():
    t_dict = TournamentService.init_dict_from_tournament(tournament)
    t = Tournament.query.filter_by(tournament_id = t_dict['tournament_id']).all()
    if len(t)==0:
        T = Tournament()
        db.session.add(T)
    else:
        T = t[0]
    T.update(**t_dict)

db.session.commit()
    