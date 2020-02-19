"""DeckService helper module"""
import uuid
from itertools import chain
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import event

from models.base_model import db
from models.marsh_models import card_schema
from models.data_models import date_now, Card, Coach, Tournament
from models.general import MIXED_TEAMS

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
            "injury_map":params["injury_map"],
            "phase_done":params['phase_done'],
        }

    @classmethod
    def deck_type(cls, deck):
        """Returns deck type based on tournament type"""
        return deck.tournament_signup.tournament.type

    @classmethod
    def addextracard(cls, deck, name):
        """Adds extra card defined by `name` to `deck`"""
        card = CardService.get_card_by_name(name.strip())

        if card:
            tmp_card = Card.from_template(card)
            # remove the card from session
            db.session.expunge(tmp_card)
            # cards added in inducement phase can count towards double
            if deck.tournament_signup.tournament.phase == Tournament.PHASES[3]:
                tmp_card.deck_type = "extra_inducement"
            # any other type is ignored
            else:
                tmp_card.deck_type = "extra"
            tmp_card.assigned_to_array = {}
            tmp_card.uuid = str(uuid.uuid4())
            deck.unused_extra_cards.append(card_schema.dump(tmp_card).data)
            flag_modified(deck, "unused_extra_cards")
            deck.to_log(f"{date_now()}: Extra Card {tmp_card.template.name} inserted into the collection")
            db.session.commit()
            return deck
        else:
            raise DeckError(f"Card {name} does not exist")

    @classmethod
    def removeextracard(cls, deck, card):
        """Removes extra `card` from `deck`"""
        if card:
            tcard = next((c for c in deck.unused_extra_cards
                              if c['uuid'] == card['uuid']), None)
            deck.unused_extra_cards.remove(tcard)

            tcard = next((c for c in deck.extra_cards
                              if c['uuid'] == card['uuid']), None)
            if tcard:
                deck.extra_cards.remove(tcard)
                flag_modified(deck, "extra_cards")
            flag_modified(deck, "unused_extra_cards")
            deck.to_log(f"{date_now()}: Extra Card {card['template']['name']} removed from the collection")
            db.session.commit()
            return deck
        else:
            raise DeckError(f"Card does not exist")

    @classmethod
    def assigncard(cls, deck, card):
        """Assign assignable `card` in `deck`"""
        if card['template']['card_type'] != "Training" and card['template']['name'] not in ["Bodyguard", "Hired Muscle", "Personal Army"]:
            raise DeckError(f"{card['template']['name']} is not assignable!")
        if card["id"]:
            tmp_card = Card.query.get(card["id"])
            tmp_card.assigned_to_array = card["assigned_to_array"]
            deck.to_log(f"{date_now()}: Card {card['template']['name']} assignment changed")
            db.session.commit()
        else:
            # extra cards
            # find it my uuid in the holder array
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
                deck.to_log(f"{date_now()}: Card {card['template']['name']} assignment changed")
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
            #extra cards
            tcard = next((c for c in deck.unused_extra_cards
                            if c['uuid'] == card['uuid']), None)
            if tcard:
                deck.unused_extra_cards.remove(tcard)
                if cls.deck_type(deck) == "Development":
                    tcard['in_development_deck'] = True
                else:
                    tcard['in_imperium_deck'] = True
                # set the deck id in assignment array
                tcard['assigned_to_array'][deck.id] = []
                deck.extra_cards.append(tcard)
                deck.unused_extra_cards.append(tcard)
                flag_modified(deck, "extra_cards")
                flag_modified(deck, "unused_extra_cards")
            else:
                raise DeckError("Extra card not found")
            deck.to_log(f"{date_now()}: Card {card['template']['name']} added to the deck")
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
            deck.to_log(f"{date_now()}: Card {card['template']['name']} removed from the deck")
            db.session.commit()
        return deck

    @classmethod
    def commit(cls, deck):
        """Commit deck and notify admin"""
        deck.commited = True
        deck.phase_done = True
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
            admin_mention = deck.tournament_signup.tournament.admin

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
            tournament.phase = Tournament.LOCKED_PHASE
            db.session.commit()
        return deck

    @classmethod
    def reset(cls, deck):
        for card in deck.cards.all() + deck.extra_cards:
            card = card_schema.dump(card).data
            cls.removecard(deck,card)
        return deck

    @classmethod
    def assigned_cards(cls, deck):
        """Returns all cards that are assigned"""
        assigned_cards = [card for card in deck.cards if card.assigned_to_array[str(deck.id)]]
        assigned_extra_cards = [card for card in deck.extra_cards if card['assigned_to_array'][str(deck.id)]]
        return assigned_cards, assigned_extra_cards

    @classmethod
    def assigned_cards_to(cls, deck, card):
        """Returns all cards that are assigned to given card"""
        assigned_cards, assigned_extra_cards = cls.assigned_cards(deck)
        # normal cards
        if isinstance(card, Card):
            return [tcard for tcard in assigned_cards if str(card.id) in getattr(tcard, 'assigned_to_array')[str(deck.id)]], [tcard for tcard in assigned_extra_cards if str(card.id) in tcard['assigned_to_array'][str(deck.id)]]
        else:
            return [tcard for tcard in assigned_cards if str(card['uuid']) in getattr(tcard, 'assigned_to_array')[str(deck.id)]], [tcard for tcard in assigned_extra_cards if str(card['uuid']) in tcard['assigned_to_array'][str(deck.id)]]

    @classmethod
    def skills_for(cls, deck, card):
        original_cards, extra_cards = cls.assigned_cards_to(deck, card)
        names1 = [CardService.skills_for_training_card(tcard.template.name) for tcard in original_cards]
        names1 = list(chain.from_iterable(names1))
        names2 = [CardService.skills_for_training_card(tcard['template']['name']) for tcard in extra_cards]
        names2 = list(chain.from_iterable(names2))
        printed_skills = CardService.builtin_skills_for(card)
        return printed_skills + names1 + names2

    @classmethod
    def legends_in_deck(cls, deck):
        """Returns all cards with 6 skills"""
        legends = []
        for card in list(deck.cards) + deck.extra_cards:
            skills = cls.skills_for(deck, card)
            if len(skills) == 6:
                legends.append((card, skills))
        return legends

    @classmethod
    def value(cls, deck):
        team = next((t for t in MIXED_TEAMS if t['name'] == deck.mixed_team), {'tier_tax':0})
        return sum(c.template.value for c in deck.cards) + team['tier_tax']

class DeckError(Exception):
    """Exception for Deck related issues"""
