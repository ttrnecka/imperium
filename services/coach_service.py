"""Coach service helpers"""
from models.data_models import Coach, Deck
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
