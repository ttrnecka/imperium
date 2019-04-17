# Works with Python 3.6
from web import db, create_app
from services import CardService

app = create_app()
app.app_context().push()

CardService.update()