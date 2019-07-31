import timeit
from web import db, create_app
from models.data_models import Card, CardTemplate, Coach
from services import CardService

app = create_app()
app.app_context().push()

mysetup = ""

mycode = ''' 
def example(): 
    CardService.template_pool()
'''

# timeit statement 
print(timeit.timeit(setup = mysetup, 
                    stmt = mycode, 
                    number = 100))
