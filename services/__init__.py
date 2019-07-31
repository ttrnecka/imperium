"""__init__"""
from sqlalchemy import event
from sqlalchemy.orm.attributes import flag_modified

from models.data_models import Tournament, Card
from models.base_model import db

from .pack_service import PackService
from .card_service import CardService
from .coach_service import CoachService
from .transaction_service import TransactionService
from .imperium_sheet_service import ImperiumSheetService
from .notification_service import NotificationService, LedgerNotificationService, AdminNotificationService
from .notification_service import AchievementNotificationService, Notificator, NotificationRegister
from .tournament_service import RegistrationError, TournamentService
from .bb2_service import BB2Service
from .web_hook_service import WebHook
from .duster_service import DusterService, DustingError
from .deck_service import DeckService, DeckError

@event.listens_for(Tournament.phase,'set')
def check_build_own_legend_quest(target, value, oldvalue, initiator):
    """After tournament is put into BB mode, the decks are evaluated for self create legend and achievements granted based on that"""
    if value!=oldvalue:
        if value in Tournament.PHASES[2:4]:
            AdminNotificationService.notify(
                f"!admincomp {value} {target.tournament_id}"
            )
        if value == Tournament.PHASES[4]:
            decks = [signup.deck for signup in target.tournament_signups]
            for deck in decks:
                coach = deck.tournament_signup.coach
                achievement = coach.achievements['quests']['buildyourownlegend']
                if achievement['completed']:
                    continue

                legends = DeckService.legends_in_deck(deck)
                built_legends = []
                for legend in legends:
                    if isinstance(legend[0], Card) and not legend[0].rarity in ["Unique","Legendary","Inducement"] or \
                        isinstance(legend[0], dict) and not legend[0]['rarity'] in ["Unique","Legendary","Inducement"]:
                            built_legends.append(legend[0])
                if built_legends:
                    achievement['best'] = len(built_legends)
                    flag_modified(coach, "achievements")

                    if CoachService.check_achievement(coach, ["quests","buildyourownlegend"]):
                        # need to refer through coach as the check may have commited the session
                        coach.achievements['quests']['buildyourownlegend']['completed'] = True
                        flag_modified(coach, "achievements")
            
                    db.session.commit()

@event.listens_for(Tournament.status,'set')
def release_signups_when_finished(target, value, oldvalue, initiator):
    """After tournament is put into BB mode, the decks are evaluated for self create legend and achievements granted based on that"""
    if value!=oldvalue and value=="FINISHED":
        TournamentService.release_reserves(target)
        TournamentService.release_actives(target)