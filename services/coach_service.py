"""Coach service helpers"""
from models.data_models import Coach
from models.base_model import db
from .pack_service import PackService
from .deck_service import DeckService

class CoachService:
    """CoachService helpers namespace"""
    @classmethod
    def remove_softdeletes(cls):
        """Removes all softdeleted Coaches from DB"""
        for coach in Coach.query.with_deleted().filter_by(deleted=True):
            db.session.delete(coach)
        db.session.commit()

    @classmethod
    def get_starter_cards(cls, coach):
        """Returns all starter cards for coach indicating their use in decks"""
        used_starter_cards = DeckService.get_used_starter_cards(coach)
        starter_cards = PackService.generate("starter").cards

        for card in used_starter_cards:
            if card['in_development_deck']:
                try:
                    gen = (i for i, acard in enumerate(starter_cards)
                           if not getattr(acard, 'in_development_deck')
                           and acard.name == card['name'])
                    index = next(gen)
                    setattr(starter_cards[index], 'in_development_deck', True)
                except StopIteration:
                    pass
            if card['in_imperium_deck']:
                try:
                    gen = (i for i, acard in enumerate(starter_cards)
                           if not getattr(acard, 'in_imperium_deck')
                           and acard.name == card['name'])
                    index = next(gen)
                    setattr(starter_cards[index], 'in_imperium_deck', True)
                except StopIteration:
                    pass

        return starter_cards
