"""resets coaches and tournaments in DB"""
from web import db, create_app
from models.data_models import Card, CardTemplate, Deck
from services import CardService

app = create_app()
app.app_context().push()


CardService.update()

templates = CardTemplate.query.all()

for template in templates:
    cards = Card.query.filter_by(name = template.name).all()
    template.cards = cards

db.session.commit()

for deck in Deck.query.all():
    deck.injury_map = {}

db.session.commit()
