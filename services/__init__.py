"""__init__"""
from sqlalchemy import event
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.orm.attributes import set_committed_value

from models.data_models import Tournament, Card, Deck
from models.base_model import db

from .pack_service import PackService
from .card_service import CardService
from .coach_service import CoachService
from .transaction_service import TransactionService
from .imperium_sheet_service import ImperiumSheetService
from .notification_service import NotificationService, LedgerNotificationService, AdminNotificationService
from .notification_service import AchievementNotificationService, Notificator, NotificationRegister, TournamentNotificationService
from .tournament_service import RegistrationError, TournamentService, TournamentError
from .bb2_service import BB2Service
from .web_hook_service import WebHook
from .duster_service import DusterService, DustingError
from .deck_service import DeckService, DeckError
from .cracker_service import CrackerService, InvalidCrackerType, InvalidCrackerTeam
from .conclave_service import ConclaveService

@event.listens_for(Tournament.phase,'set')
def after_phase_set_hook(target, value, oldvalue, initiator):
    """After tournament is put into BB mode, the decks are evaluated for self create legend and achievements granted based on that"""
    if value!=oldvalue:
        # automatic phase move except for first 2 phases
        if value in Tournament.PHASES[2:]:
            decks = [signup.deck for signup in target.tournament_signups]
            for deck in decks:
                deck.phase_done = False
            AdminNotificationService.notify(
                f"!admincomp {value} {target.tournament_id}"
            )
        
        # when tournament reaches last phase check for buildyourownlegend achievements
        if value == Tournament.BB_PHASE:
            decks = [signup.deck for signup in target.tournament_signups]
            for deck in decks:
                coach = deck.tournament_signup.coach
                achievement = coach.achievements['quests']['buildyourownlegend']
                if achievement['completed']:
                    continue
                
                legends = DeckService.legends_in_deck(deck)
                
                built_legends = []
                for legend in legends:
                    if isinstance(legend[0], Card) and not legend[0].template.rarity in ["Unique","Legendary","Inducement"] or \
                        isinstance(legend[0], dict) and not legend[0]['template']['rarity'] in ["Unique","Legendary","Inducement"]:
                            built_legends.append(legend[0])
                
                if built_legends:
                    achievement['best'] = len(built_legends)
                    flag_modified(coach, "achievements")
                
                    if CoachService.check_achievement(coach, ["quests","buildyourownlegend"]):
                        # need to refer through coach as the check may have commited the session
                        coach.achievements['quests']['buildyourownlegend']['completed'] = True

@event.listens_for(Tournament.status,'set')
def release_signups_when_finished(target, value, oldvalue, initiator):
    """Release all signups from FINISHED tournament"""
    if target.id and value!=oldvalue and value=="FINISHED":
        TournamentService.release_reserves(target)
        TournamentService.release_actives(target)

@event.listens_for(db.session,'before_commit')
def phase_done_handler(session):
    # do it for every deck
    with session.no_autoflush:
        for instance in session.dirty:
            if not isinstance(instance, Deck):
                continue
            state = db.inspect(instance)
            history = state.attrs.phase_done.load_history()
            # if Deck phase_done was set to True
            if history.added and history.added[0] == True:
                tourn = instance.tournament_signup.tournament
                signups = tourn.tournament_signups
                decks = [ts.deck for ts in signups]
                decks.remove(instance)
                if tourn.phase in Tournament.PHASES[2:] and (len(decks) == 0 or all(deck.phase_done for deck in decks)):
                    TournamentService.next_phase(tourn)