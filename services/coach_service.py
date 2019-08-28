"""Coach service helpers"""
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import event

from models.data_models import Coach, Deck, Tournament, Card, Transaction, Pack
from models.base_model import db
from .pack_service import PackService
from .deck_service import DeckService
from .notification_service import AchievementNotificationService, NotificationService

class CoachService:
    """CoachService helpers namespace"""

    @staticmethod
    def new_coach(name, discord_id):
        coach = Coach.create(str(name), discord_id)
        pack = PackService.new_starter_pack(coach = coach)
        tran = Transaction(pack=pack, price=pack.price, description=PackService.description(pack))
        coach.make_transaction(tran)
        return coach

    @staticmethod
    def activate_coach(coach = None, card_ids = None):
        """Activates coach and copies cards in card_ids list to new season"""
        if not coach:
            raise ValueError("coach argument is empty")

        if not isinstance(coach, Coach):
            raise TypeError("coach is not of class Coach")

        if coach.active():
            raise ValueError("coach is already active")
        
        if not isinstance(card_ids, list):
            card_ids = []

        selected_cards = Card.query.join(Card.coach).\
                filter(Coach.id == coach.id, Card.id.in_(card_ids)).\
                all()
        selected_card_ids = [card.id for card in selected_cards]
        missing = [id for id in card_ids if id not in selected_card_ids]

        if missing:
            raise ValueError(f"Not all card IDs were found - {str(missing)[1:-1]}")

        total_value = sum([card.template.value for card in selected_cards])
        if total_value > 35:
            raise ValueError(f"Total value is higher than 35!!!")
        

        selected_card_names = [card.template.name for card in selected_cards]
        pack = PackService.admin_pack(card_names=selected_card_names, coach=coach)
        reason = "Account activation - Admin Transfer Pack"
        tran = Transaction(pack=pack, description=reason, price=0)

        coach.activate()
        coach.make_transaction(tran)

        pack = PackService.new_starter_pack(coach=coach)
        reason = "Account activation - Starter Pack"
        tran = Transaction(pack=pack, description=reason, price=0)
        coach.make_transaction(tran)

        coach.account.reset()
        db.session.commit()
        return True

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
        """Sets achievement to value and record to best, if best is not provided best is set to achievement target"""
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
        """Checks if achievement has been reached and grants the prize"""
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
        """callback method to check if hidden quest collect 3 legends has been achieved. Should be called after packs are generated"""
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
