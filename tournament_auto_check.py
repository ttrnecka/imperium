from web import db, app
from models.data_models import Coach, Tournament
from services import Notificator, TournamentService, ImperiumSheetService, TournamentError

app.app_context().push()

tournaments = Tournament.query.filter_by(status="OPEN").all()
auto = []
for tournament in tournaments:
    if len(tournament.tournament_signups) == tournament.coach_limit:
        if tournament.can_auto_start():
            auto.append(tournament)


# automatic kick off
if auto:
    msg="Automatically started tournaments:\n"
    for t in auto:
        try:
            TournamentService.kick_off(t)
            Notificator('tournament').notify(f"Tournament {t.tournament_id}. {t.name} kicked off: deadline {t.deadline_date}, admin {t.admin}, sponsor {t.sponsor}, room {t.discord_channel}")
        except TournamentError as e:
            Notificator('tournament').notify(str(e))