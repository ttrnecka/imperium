import timeit
from web import db, app

app.app_context().push()

mysetup = ""

mycode = '''
from web import get_stats
from models.data_models import Coach
from models.marsh_models import leaderboard_coach_schema
all_coaches = Coach.query.all()
result = {}
result['coaches'] = leaderboard_coach_schema.dump(all_coaches).data
result['coach_stats'] = list(get_stats()['coaches'].values())
'''

# timeit statement 
print(timeit.timeit(setup = mysetup, 
                    stmt = mycode, 
                    number = 1))
