"""DusterService helpers"""

from models.data_models import Duster, Card, Transaction
from models.base_model import db
from .card_service import CardService
from .notification_service import NotificationService

class DustingError(Exception):
    """Exception used for Dusting Errors"""

class DusterService:
    """DusterService helpers namespace"""
    @classmethod
    def get_duster(cls, coach):
        """Get duster from `coach` model"""
        duster = coach.duster
        if not duster:
            duster = Duster()
            coach.duster = duster
        return duster

    @classmethod
    def dust_card(cls, duster, card):
        """Dust `card` model"""
        if not duster.cards:
            if card.card_type == "Player":
                duster.type = "Tryouts"
            else:
                duster.type = "Drills"
        duster.cards.append(card)
        db.session.commit()

    @classmethod
    def check_and_dust(cls, coach, card):
        """Check if `card` can be dusted and dust it, raise error otherwise"""
        if card.in_development_deck or card.in_imperium_deck:
            raise DustingError("Cannot dust card that is used in the deck!!!")
        if card.coach.id != coach.id:
            raise DustingError("Coach ID mismatch!!!")
        duster = cls.get_duster(coach)
        if duster.status != "OPEN":
            raise DustingError(f"Dusting has been already committed, \
                                please generate the pack before dusting again")
        if len(duster.cards) == 10:
            raise DustingError(f"Card **{card.name}** - cannot be dusted, duster is full")
        if duster.type == "Tryouts" and card.card_type != "Player":
            raise DustingError(f"Card **{card.name}** - cannot be used in {duster.type}")
        if duster.type == "Drills" and card.card_type == "Player":
            raise DustingError(f"Card **{card.name}** - cannot be used in {duster.type}")

        cls.dust_card(duster, card)
        return f"Card **{card.name}** - flagged for dusting"

    @classmethod
    def check_and_undust(cls, coach, card):
        """Check if `card` can be undusted andun dust it, raise error otherwise"""
        if card.coach.id != coach.id:
            raise DustingError("Coach ID mismatch!!!")

        card.duster_id = None
        db.session.commit()
        duster = cls.get_duster(coach)
        if not duster.cards:
            cls.cancel_duster(coach)
        return f"Card **{card.name}** - dusting flag removed"

    @classmethod
    def dust_card_by_name(cls, coach, card_name):
        """Dust undusted coach's card by name"""
        card = CardService.get_undusted_card_from_coach(coach, card_name)
        if card is None:
            raise DustingError(f"Card **{card_name}** - not found, check spelling, \
                                or maybe it is already dusted or used in deck")
        return cls.check_and_dust(coach, card)

    @classmethod
    def undust_card_by_name(cls, coach, card_name):
        """Undust dusted coach's card by name"""
        card = CardService.get_dusted_card_from_coach(coach, card_name)
        if card is None:
            raise DustingError(f"Card **{card_name}** - not flagged for dusting")
        return cls.check_and_undust(coach, card)

    @classmethod
    def dust_card_by_id(cls, coach, card_id):
        """Dust undusted coach's card by id"""
        card = Card.query.get(card_id)
        if card is None:
            raise DustingError(f"Card not found")
        if card.duster_id is not None:
            raise DustingError(f"Card **{card.name}** is already flagged for dusting")
        return cls.check_and_dust(coach, card)

    @classmethod
    def undust_card_by_id(cls, coach, card_id):
        """Undust dusted coach's card by id"""
        card = Card.query.get(card_id)
        if card is None:
            raise DustingError(f"Card not found")
        if card.duster_id is None:
            raise DustingError(f"Card **{card.name}** is not flagged for dusting")
        return cls.check_and_undust(coach, card)

    @classmethod
    def cancel_duster(cls, coach):
        """Destroy duster and release cards"""
        duster = cls.get_duster(coach)
        if duster.status != "OPEN":
            raise DustingError(f"Cannot cancel dusting. It has been already committed.")
        db.session.delete(coach.duster)
        db.session.commit()

    @classmethod
    def commit_duster(cls, coach):
        """Commit duster and remove cards from colletion"""
        duster = cls.get_duster(coach)
        if len(duster.cards) < 10:
            raise DustingError("Not enough cards flagged for dusting. Need 10!!!")

        reason = f"{duster.type}: {';'.join([card.name for card in duster.cards])}"
        tran = Transaction(description=reason, price=0)
        cards = duster.cards
        for card in cards:
            db.session.delete(card)
        duster.status = "COMMITTED"
        coach.make_transaction(tran)
        NotificationService.notify(
            f"<@{coach.disc_id}>: Card(s) **{', '.join([card.name for card in cards])}** " +
            f"removed from your collection by {duster.type}"
        )
        return True
