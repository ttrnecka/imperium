"""resets coaches and tournaments in DB"""
from web import db, app
from models.data_models import Coach, Tournament
from services import TournamentNotificationService, TournamentService, ImperiumSheetService, TournamentError

app.app_context().push()

tournaments = Tournament.query.filter_by(status="OPEN").all()
manual = []
for tournament in tournaments:
    if len(tournament.tournament_signups) == tournament.coach_limit:
        if not tournament.can_auto_start():
            manual.append(tournament)

c = Coach.find_all_by_name(app.config['TOURNAMENT_MASTER_ADMIN'])
if manual:
    msg=f"{c[0].mention()}\nFull tournaments:\n"
    for t in manual:
        msg += f"{t.tournament_id}. {t.name}\n"
    TournamentNotificationService.notify(msg)
