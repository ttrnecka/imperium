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
from models.data_models import Card, CardTemplate, Coach, Account
from models.marsh_models import leaderboard_coach_schema
from sqlalchemy.orm import joinedload,subqueryload,selectinload
all_coaches = Coach.query.all()
#c = Coach.query.first()
print("")
print("")
#c = Coach.query.options(selectinload(Coach.account, Account.transactions),selectinload(Coach.cards, Card.template)).first()
leaderboard_coach_schema.dump(all_coaches).data
#leaderboard_coach_schema.dump([c]).data
'''

# timeit statement 
print(timeit.timeit(setup = mysetup, 
                    stmt = mycode, 
                    number = 10))
