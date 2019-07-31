"""Coach service helpers"""
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import event

from models.data_models import Coach, Deck, Tournament
from models.base_model import db
from .pack_service import PackService
from .deck_service import DeckService
from .notification_service import AchievementNotificationService, NotificationService

class CoachService:
    """CoachService helpers namespace"""
    @classmethod
    def remove_softdeletes(cls):
        """Removes all softdeleted Coaches from DB"""
        for coach in Coach.query.with_deleted().filter_by(deleted=True):
            db.session.delete(coach)
        db.session.commit()

    @classmethod
    def link_bb2_coach(cls,bb2_name,team_name):
        """Links coach bb2 name to Coach account
        If the coach is already linked or the team does not exists then return None"""
        coach = Coach.query.filter_by(bb2_name=bb2_name).first()
        if not coach:
            """Coach is not linked yet, find the team"""
            deck = Deck.query.filter_by(team_name=team_name).first()
            if deck:
                coach = deck.tournament_signup.coach
                coach.bb2_name = bb2_name
                return coach
            else:
                return None
        return None

    @classmethod
    def set_achievement(cls, coach, achievement_keys=None, value=True, best = None):
        if achievement_keys is None:
            achievement_keys = []

        achievement = coach.achievements
        for key in achievement_keys:
            if key in achievement:
                achievement = achievement[key]
            else:
                raise Exception("Achievement missing key %s" % key)
        achievement['completed'] = value
        if best:
            achievement['best'] = best
        else:
            achievement['best'] = achievement['target']
        flag_modified(coach, "achievements")
        
    @classmethod
    def check_achievement(cls, coach, achievement_keys=None):
        if achievement_keys is None:
            achievement_keys = []

        achievement = coach.achievements
        for key in achievement_keys:
            if key in achievement:
                achievement = achievement[key]
            else:
                raise Exception("Achievement missing key %s" % key)

        if achievement['target'] <= achievement['best'] and not achievement['completed']:
            achievement_bank_text = f"{achievement['award_text']} awarded - {achievement['desc']}"
            AchievementNotificationService.notify(
                f"{coach.short_name()}: {achievement['desc']} - completed"
            )

            call, arg = achievement['award'].split(",")
            res, error = getattr(coach, call)(arg, achievement['desc'])

            if res:
                NotificationService.notify(
                    f"{coach.mention()}: {achievement_bank_text}"
                )
                return True
            else:
                NotificationService.notify(
                    f"{coach.mention()}: {achievement['award_text']} " +
                    f"could not be awarded - {error}"
                )
        return False

    @classmethod
    def check_collect_three_legends_quest(cls, coach):
        achievement = coach.achievements['quests']['collect3legends']
        legends = [card for card in coach.cards if card.get('subtype') == "REBBL Legend"]
        legends_count = len(legends)
        if achievement['best'] < legends_count: 
            achievement['best'] = legends_count
            flag_modified(coach, "achievements")

        if cls.check_achievement(coach, ["quests","collect3legends"]):
            # need to refer through coach as the check may have commited the session
            coach.achievements['quests']['collect3legends']['completed'] = True
            flag_modified(coach, "achievements")
        
        db.session.commit()
