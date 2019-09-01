"""resets coaches and tournaments in DB"""
from web import db, app
from models.data_models import Coach, Tournament
from services import AdminNotificationService

app.app_context().push()

tournaments = Tournament.query.filter_by(status="OPEN").all()
full = []
for tournament in tournaments:
    if len(tournament.tournament_signups) == tournament.coach_limit:
        full.append(tournament)

c = Coach.find_all_by_name(app.config['TOURNAMENT_MASTER_ADMIN'])
if full:
    msg=f"{c[0].mention()}\nFull tournaments:\n"
    for t in full:
        msg += f"{t.tournament_id}. {t.name}\n"
    AdminNotificationService.notify(msg)