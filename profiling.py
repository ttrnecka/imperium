import timeit
from web import db, create_app
from models.data_models import Card, CardTemplate, Coach
from services import CardService
from models.marsh_models import leaderboard_coach_schema
from sqlalchemy.orm import subqueryload

app = create_app()
app.app_context().push()

mysetup = ""

mycode = '''
from models.data_models import Card, CardTemplate, Coach, Account, Tournament, TournamentSignups
from models.marsh_models import tournaments_schema
from sqlalchemy.orm import joinedload,subqueryload,selectinload,raiseload
all_tournaments = Tournament.query.options(
    raiseload(Tournament.coaches)
).filter(Tournament.status.in_(("OPEN", "RUNNING"))).all()

result = tournaments_schema.dump(all_tournaments)
'''

# timeit statement 
print(timeit.timeit(setup = mysetup, 
                    stmt = mycode, 
                    number = 1))
