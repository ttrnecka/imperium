import timeit
from web import db, app

app.app_context().push()

mysetup = ""

mycode = '''
from models.data_models import Coach
from models.marsh_models import coach_schema
coach = Coach.query.get(2)
result = coach_schema.dump(coach)
'''

# timeit statement 
print(timeit.timeit(setup = mysetup, 
                    stmt = mycode, 
                    number = 1))
