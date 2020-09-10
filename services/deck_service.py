"""DeckService helper module"""
import uuid
from itertools import chain
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import event

from models.base_model import db
from models.marsh_models import card_schema
from models.data_models import date_now, Card, Coach, Tournament, CardTemplate
from models.general import MIXED_TEAMS
from misc import KEYWORDS
from misc.helpers import CardHelper

from .card_service import CardService, GUARDS
from .notification_service import Notificator
import services.high_command_service as hcs

class DeckService:
    """DeckService namespace"""
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
    def disable_card(cls, deck, card):
        """Disable `card` in `deck`"""
        id = CardService.card_id_or_uuid(card)
        # init for old decks
        if deck.disabled_cards == "":
            deck.disabled_cards = []

        if id in deck.disabled_cards:
            raise DeckError(f"Card is already disabled")
        deck.disabled_cards.append(id)
        flag_modified(deck, "disabled_cards")
        c = CardHelper.card_fix(card)
        deck.to_log(f"{date_now()}: Card Id. {id}. {c.get('name')} was disabled")
        db.session.commit()
        return deck

    @classmethod
    def enable_card(cls, deck, card):
        """Disable `card` in `deck`"""
        id = CardService.card_id_or_uuid(card)

        if id not in deck.disabled_cards:
            raise DeckError(f"Card is not disabled")
        deck.disabled_cards.remove(id)
        flag_modified(deck, "disabled_cards")
        c = CardHelper.card_fix(card)
        deck.to_log(f"{date_now()}: Card Id. {id}. {c.get('name')} was enabled")
        db.session.commit()
        return deck

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
            card_dump=card_schema.dump(tmp_card).data
            deck.unused_extra_cards.append(card_dump)
            flag_modified(deck, "unused_extra_cards")
            deck.to_log(f"{date_now()}: Extra Card {tmp_card.template.name} inserted into the collection")
            db.session.commit()
            return cls.addcard(deck, card_dump)
            #return deck
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
        if card['template']['card_type'] != "Training" and card['template']['name'] not in GUARDS:
            raise DeckError(f"{card['template']['name']} is not assignable!")

        new_players = [player for player in cls.all_players(deck) if CardHelper.card_id_or_uuid(player) in card["assigned_to_array"][str(deck.id)]]
        def valid_skill_or_raise(card):
            if isinstance(card, dict):
              assigned_ids = card['assigned_to_array'][str(deck.id)]
            else:
              assigned_ids = card.assigned_to_array[str(deck.id)]

            old_players = [player for player in cls.all_players(deck) if CardHelper.card_id_or_uuid(player) in assigned_ids]
            diff_players = [player for player in new_players if player not in old_players]

            for player in diff_players:
              skills = DeckService.skills_for(deck, player, api_format=False)
              cskills = CardService.skill_names_for(card, api_format=False)
              if not CardService.valid_skill_combination(skills, cskills) or not CardService.can_take_skills(player, cskills):
                raise DeckError(f"Invalid skill assignment!")
        if card["id"]:
            tmp_card = Card.query.get(card["id"])
            valid_skill_or_raise(tmp_card)
            tmp_card.assigned_to_array = card["assigned_to_array"]
            deck.to_log(f"{date_now()}: Card {card['template']['name']} assignment changed")
            db.session.commit()
        else:
            # extra cards
            # find it my uuid in the holder array
            tcard = next((c for c in deck.extra_cards
                            if c['uuid'] == card['uuid']), None)
            if tcard:
                valid_skill_or_raise(tcard)
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
        if cls.is_banned(deck, card):
          raise DeckError("Card is banned in the tournament!")

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
                    tmp_card.increment_use()
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
    def addcard_to_squad(cls, deck, card):
      card = Card.query.get(card["id"])
      # check if it is banned
      if DeckService.is_banned(deck, card):
        raise DeckError("Card is banned in the tournament!")

      if card.duster is not None:
        raise DeckError("Cannot add card - card is flagged for dusting!")

      hcs.add_card_to_squad(deck.squad, card)
      return deck

    @classmethod
    def removecard_from_squad(cls, deck, card):
      card = Card.query.get(card["id"])
      hcs.remove_card_from_squad(deck.squad, card)
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
                    tmp_card.decrement_use()
                    db.session.commit()
                else:
                    raise DeckError("Card is not in the deck")
            else:
                raise DeckError("Card not found")
        else:
            #extra cards
            tcard = next((c for c in deck.unused_extra_cards
                            if c['uuid'] == card['uuid']), None)
            if tcard:
                deck.unused_extra_cards.remove(tcard)
                deck.extra_cards.remove(tcard)
                if cls.deck_type(deck) == "Development":
                    tcard['in_development_deck'] = False
                else:
                    tcard['in_imperium_deck'] = False
                tcard['assigned_to_array'][deck.id] = []
                deck.unused_extra_cards.append(tcard)
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

        Notificator("ledger").notify(
            f'{admin_mention} - {coach_mention} submitted ledger for ' +
            f'{tournament.tournament_id}. {tournament.name} - channel {tournament.discord_channel}')

        # check if all ledgers are commited
        deck_states = [ts.deck.commited for ts in tournament.tournament_signups]
        if False not in deck_states:
            Notificator("ledger").notify(
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
        # reset squad
        for card in deck.squad.cards.all():
            card = card_schema.dump(card).data
            cls.removecard_from_squad(deck,card)
        return deck

    @classmethod
    def eligible_players(cls, deck, card):
        """Returns list of eligible player Cards or cards that can be assigned given training card"""
        # only players that can be assigned skill
        players = DeckService.assignable_players(deck)
        # remove disabled or guarded ones
        players = [player for player in players if cls.is_enabled(deck, player) and not cls.is_guarded(deck, player)]
        # get the skills the cards gives
        skills = CardService.skill_names_for(card, api_format=False)
        eligible = []
        for player in players:
            # check if the card does not have the skill assigned in the dekc already
            askills = DeckService.skills_for(deck, player, api_format=False)
            if not CardService.valid_skill_combination(askills, skills):
              continue

            # check if card can be assigned the skill
            if CardService.can_take_skills(player, skills):
                eligible.append(player)
        return eligible

    @classmethod
    def assigned_cards(cls, deck):
        """Returns all cards that are assigned"""
        assigned_cards = [card for card in deck.cards if card.assigned_to_array[str(deck.id)]]
        assigned_extra_cards = [card for card in deck.extra_cards if card['assigned_to_array'][str(deck.id)]]
        return assigned_cards, assigned_extra_cards

    @classmethod
    def assigned_cards_to(cls, deck, card, ignore_extra = False):
        """Returns all cards that are assigned to given card"""
        assigned_cards, assigned_extra_cards = cls.assigned_cards(deck)
        if ignore_extra:
          assigned_extra_cards = []

        # normal cards
        if isinstance(card, Card):
            return [tcard for tcard in assigned_cards if str(card.id) in getattr(tcard, 'assigned_to_array')[str(deck.id)]] + [tcard for tcard in assigned_extra_cards if str(card.id) in tcard['assigned_to_array'][str(deck.id)]]
        else:
            return [tcard for tcard in assigned_cards if str(card['uuid']) in getattr(tcard, 'assigned_to_array')[str(deck.id)]] + [tcard for tcard in assigned_extra_cards if str(card['uuid']) in tcard['assigned_to_array'][str(deck.id)]]

    @classmethod
    def skills_for(cls, deck, card, api_format=True):
        """Returns printed and assigned skills for a card"""
        assigned_cards = cls.assigned_cards_to(deck, card)
        names1 = [CardService.skill_names_for(tcard, api_format=api_format) for tcard in assigned_cards]
        names1 = list(chain.from_iterable(names1))
        printed_skills = CardService.builtin_skills_for(card)
        return printed_skills + names1

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

    @staticmethod
    def assignable_players(deck):
        """Return list of cards that can be assigned a card"""
        return [card for card in DeckService.players(deck) if CardService.assignable(card)] + \
            [card for card in DeckService.extra_players(deck) if CardService.assignable(card)]
    
    @staticmethod
    def players(deck):
      return [card for card in deck.cards if card.template.card_type == CardTemplate.TYPE_PLAYER]

    @staticmethod
    def extra_players(deck):
      return [card for card in deck.extra_cards if card['template']['card_type'] == CardTemplate.TYPE_PLAYER]

    @staticmethod
    def all_players(deck):
        return DeckService.players(deck) + DeckService.extra_players(deck)

    @staticmethod
    def training_cards(deck):
      return [card for card in deck.cards if card.template.card_type == CardTemplate.TYPE_TRAINING]
    
    @staticmethod
    def special_play_cards(deck):
      return [card for card in deck.cards if card.template.card_type == CardTemplate.TYPE_SP]

    @staticmethod
    def staff_cards(deck):
      return [card for card in deck.cards if card.template.card_type == CardTemplate.TYPE_STAFF]

    @staticmethod
    def deck_value(deck):
      return sum([card.template.value for card in deck.cards])

    @staticmethod
    def assigned_injuries(card,deck):
      injuries = []
      uid = CardService.card_id_or_uuid(card)
      if deck.injury_map.get(uid,None):
          injuries.append(deck.injury_map[uid])
      return injuries

    @staticmethod
    def is_enabled(deck, card):
      if deck.disabled_cards and CardService.card_id_or_uuid(card) in deck.disabled_cards:
        return False
      return True

    @staticmethod
    def is_guarded(deck, card):
      assigned = DeckService.assigned_cards_to(deck, card)
      for card in assigned:
        c = CardHelper.card_fix(card)
        if c.get('name') in GUARDS:
          return True
      return False

    @staticmethod
    def is_banned(deck, card):
      if isinstance(card, dict):
        name = card['template']['name']
        desc = card['template']['description']
      else:
        name = card.template.name
        desc = card.template.description

      if name in deck.tournament_signup.tournament.banned_cards.split(";"):
        return True

      # imp tournaments cannot use Event cards
      if deck.tournament_signup.tournament.is_imperium() and \
            KEYWORDS(desc).is_event():
        return True
      
      return False


class DeckError(Exception):
    """Exception for Deck related issues"""
