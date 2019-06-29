"""DeckService helper module"""
import uuid
from sqlalchemy.orm.attributes import flag_modified

from models.base_model import db
from models.marsh_models import card_schema
from models.data_models import date_now, Card, Coach

from .card_service import CardService
from .notification_service import LedgerNotificationService

class DeckService:
    """DeckeService namespace"""
    @classmethod
    def update(cls, deck, deck_params):
        """Updates deck with new parameters"""
        deck.update(**cls.init_dict_from_params(deck_params))
        db.session.commit()

        return deck

    @classmethod
    def init_dict_from_params(cls, params):
        """Pulls deck related params from provided dict"""
        return {
            "team_name":params["team_name"],
            "mixed_team":params["mixed_team"],
            "comment":params["comment"],
        }

    @classmethod
    def deck_type(cls, deck):
        """Returns deck type based on tournament type"""
        return deck.tournament_signup.tournament.type

    @classmethod
    def addextracard(cls, deck, name):
        """Adds extra card defined by `name` to `deck`"""
        card = CardService.get_card_from_sheet(name)

        if card:
            tmp_card = CardService.init_card_model_from_card(card)
            # cards added in inducement phase can count towards double
            if deck.tournament_signup.tournament.phase == "inducement":
                tmp_card.deck_type = "extra_inducement"
            # any other type is ignored
            else:
                tmp_card.deck_type = "extra"
            tmp_card.assigned_to_array = {}
            tmp_card.uuid = str(uuid.uuid4())
            deck.unused_extra_cards.append(card_schema.dump(tmp_card).data)
            flag_modified(deck, "unused_extra_cards")
            deck.to_log(f"{date_now()}: Extra Card {tmp_card.name} inserted to the collection")
            db.session.commit()
            return deck
        else:
            raise DeckError(f"Card {name} does not exist")

    @classmethod
    def removeextracard(cls, deck, card):
        """Removes extra `card` from `deck`"""
        if card:
            deck.unused_extra_cards.remove(card)
            if card in deck.extra_cards:
                deck.extra_cards.remove(card)
                flag_modified(deck, "extra_cards")
            flag_modified(deck, "unused_extra_cards")
            deck.to_log(f"{date_now()}: Extra Card {card['name']} removed from the collection")
            db.session.commit()
            return deck
        else:
            raise DeckError(f"Card does not exist")

    @classmethod
    def assigncard(cls, deck, card):
        """Assign assignable `card` in `deck`"""
        if card['card_type'] != "Training" and card['name'] != "Bodyguard":
            raise DeckError(f"{card['name']} is not assignable!")
        if card["id"]:
            tmp_card = Card.query.get(card["id"])
            tmp_card.assigned_to_array = card["assigned_to_array"]
            deck.to_log(f"{date_now()}: Card {card['name']} assignment changed")
            db.session.commit()
        else:
            # starting pack handling - there should not be any training starter card
            if card["deck_type"] in ["base", None]:
                raise DeckError(f"Unexpected card type!")
            else:
                #only other assignable cards can be extra cards
                #find it my uuid in the holder array
                tcard = next((c for c in deck.unused_extra_cards
                              if c['uuid'] == card['uuid']), None)
                if tcard:
                    # remove the card from both arrays, update it and stick it back
                    deck.unused_extra_cards.remove(tcard)
                    deck.extra_cards.remove(tcard)
                    if cls.deck_type(deck) == "Development":
                        tcard['in_development_deck'] = True
                    else:
                        tcard['in_imperium_deck'] = True

                    tcard['assigned_to_array'] = card['assigned_to_array']
                    deck.extra_cards.append(tcard)
                    deck.unused_extra_cards.append(tcard)
                    deck.to_log(f"{date_now()}: Card {card['name']} assignment changed")
                    flag_modified(deck, "extra_cards")
                    flag_modified(deck, "unused_extra_cards")
                else:
                    raise DeckError("Extra card not found")
            db.session.commit()
        return deck

    @classmethod
    def addcard(cls, deck, card):
        """Adds card to the deck"""
        if card["id"]:
            tmp_card = Card.query.get(card["id"])
            if tmp_card is not None:
                if deck in tmp_card.decks:
                    raise DeckError("Card is already in the deck")
                elif tmp_card.duster is not None:
                    raise DeckError("Cannot add card - card is flagged for dusting!")
                else:
                    if cls.deck_type(deck) == "Development":
                        tmp_card.in_development_deck = True
                    else:
                        tmp_card.in_imperium_deck = True
                    # set the deck id in assignment array
                    tmp_card.assigned_to_array[deck.id] = []
                    flag_modified(tmp_card, "assigned_to_array")
                    deck.cards.append(tmp_card)
                    db.session.commit()
            else:
                raise DeckError("Card not found")
        else:
            # add starting pack handling
            if card["deck_type"] in ["base", None]:
                if cls.deck_type(deck) == "Development":
                    card['in_development_deck'] = True
                else:
                    card['in_imperium_deck'] = True
                card['uuid'] = str(uuid.uuid4())
                # set the deck id in assignment array
                card['assigned_to_array'][deck.id] = []
                deck.starter_cards.append(card)
                flag_modified(deck, "starter_cards")
            else:
                #extra cards
                if card in deck.unused_extra_cards:
                    deck.unused_extra_cards.remove(card)
                    if cls.deck_type(deck) == "Development":
                        card['in_development_deck'] = True
                    else:
                        card['in_imperium_deck'] = True
                    # set the deck id in assignment array
                    card['assigned_to_array'][deck.id] = []
                    deck.extra_cards.append(card)
                    deck.unused_extra_cards.append(card)
                    flag_modified(deck, "extra_cards")
                    flag_modified(deck, "unused_extra_cards")
                else:
                    raise DeckError("Extra card not found")
            deck.to_log(f"{date_now()}: Card {card['name']} added to the deck")
            db.session.commit()
        return deck

    @classmethod
    def removecard(cls, deck, card):
        """Removes `card` from `deck` """
        if card["id"]:
            tmp_card = Card.query.get(card["id"])
            if tmp_card:
                if deck in tmp_card.decks:
                    if cls.deck_type(deck) == "Development":
                        tmp_card.in_development_deck = False
                    else:
                        tmp_card.in_imperium_deck = False

                    tmp_card.assigned_to_array[deck.id] = []
                    flag_modified(tmp_card, "assigned_to_array")
                    deck.cards.remove(tmp_card)
                    db.session.commit()
                else:
                    raise DeckError("Card is not in the deck")
            else:
                raise DeckError("Card not found")
        else:
            # remove starting pack handling
            if card["deck_type"] in ["base", None]:
                deck.starter_cards.remove(card)
                flag_modified(deck, "starter_cards")
            else:
                #extra cards
                if card in deck.unused_extra_cards:
                    deck.unused_extra_cards.remove(card)
                    deck.extra_cards.remove(card)
                    if cls.deck_type(deck) == "Development":
                        card['in_development_deck'] = False
                    else:
                        card['in_imperium_deck'] = False
                    card['assigned_to_array'][deck.id] = []
                    deck.unused_extra_cards.append(card)
                    flag_modified(deck, "extra_cards")
                    flag_modified(deck, "unused_extra_cards")
                else:
                    raise DeckError("Extra card not found")
            deck.to_log(f"{date_now()}: Card {card['name']} removed from the deck")
            db.session.commit()
        return deck

    @classmethod
    def get_used_starter_cards(cls, coach):
        """Return starter cards for `coach` that are used in any of their decks"""
        decks = [ts.deck for ts in coach.tournament_signups]
        return sum([deck.starter_cards for deck in decks], [])

    @classmethod
    def commit(cls, deck):
        """Commit deck and notify admin"""
        deck.commited = True
        db.session.commit()
        coach = deck.tournament_signup.coach
        tournament = deck.tournament_signup.tournament
        admins = Coach.find_all_by_name(tournament.admin)
        if len(admins) == 1:
            admin_mention = f'<@{admins[0].disc_id}>'
        elif len(admins) > 1:
            match_admins = [admin for admin in admins if admin.short_name() == tournament.admin]
            # special scenario where admin is empty string
            if match_admins:
                admin_mention = f'<@{match_admins[0].disc_id}>'
            else:
                admin_mention = "Unknown admin"
        else:
            admin_mention = deck.tournament_signup.admin

        coach_mention = coach.short_name()

        LedgerNotificationService.notify(
            f'{admin_mention} - {coach_mention} submitted ledger for ' +
            f'{tournament.tournament_id}. {tournament.name} - channel {tournament.discord_channel}')

        # check if all ledgers are commited
        deck_states = [ts.deck.commited for ts in tournament.tournament_signups]
        if False not in deck_states:
            LedgerNotificationService.notify(
                f'{admin_mention} - All ledgers are locked & committed now for ' +
                f'{tournament.tournament_id}. {tournament.name} - channel ' +
                f'{tournament.discord_channel}'
            )
            tournament.phase = "locked"
            db.session.commit()
        return deck

class DeckError(Exception):
    """Exception for Deck related issues"""
