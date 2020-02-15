"""resets coaches and tournaments in DB"""
import bb2
from web import db, app
from models.data_models import Competition

app.app_context().push()

agent = bb2.api.Agent(app.config['BB2_API_KEY'])

data = agent.competitions(leagues=",".join(app.config['LEAGUES']))

for comp in data['competitions']:
    c = Competition.query.filter_by(comp_id=int(comp['id'])).one_or_none()
    if not c:
        c = Competition(comp_id = comp['id'])
    c.name = comp['name']
    c.competition_type = comp['format']
    c.team_count = comp['teams_max']
    c.turn_duration = comp['turn_duration']
    c.status = comp['status']
    c.league_id = comp['league']['id']
    c.league_name = comp['league']['name']
    db.session.add(c)

db.session.commit()