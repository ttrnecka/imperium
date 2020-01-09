from web import db, app
from models.data_models import Coach, Tournament
from services import TournamentNotificationService, TournamentService, ImperiumSheetService, TournamentError

app.app_context().push()

tournaments = Tournament.query.filter_by(status="OPEN").all()
auto = []
for tournament in tournaments:
    if len(tournament.tournament_signups) == tournament.coach_limit:
        if tournament.can_auto_start():
            auto.append(tournament)

c = Coach.find_all_by_name(app.config['TOURNAMENT_MASTER_ADMIN'])

# automatic kick off
if auto:
    msg="Automatically started tournaments:\n"
    for t in auto:
        try:
            TournamentService.kick_off(t)
            TournamentNotificationService.notify(f"Tournament {t.tournament_id}. {t.name} kicked off: deadline {t.deadline_date}, admin {t.admin}, sponsor {t.sponsor}, room {t.discord_channel}")
        except TournamentError as e:
            TournamentNotificationService.notify(f"{c[0].mention()}: {msg}")