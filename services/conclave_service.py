"""ConclaveService helpers"""
import re
import itertools
import random
from collections import Counter

from models.data_models import Deck, ConclaveRule, CardTemplate
from models.base_model import db
from misc import KEYWORDS

from .deck_service import DeckService
from .card_service import CardService

MUTATIONS = [
    "DisturbingPresence", "Horns", "Claw", "TwoHeads", "Tentacles","ExtraArms", "FoulAppearance", "PrehensileTail","BigHand","VeryLongLegs"
]

class ConclaveService:
    """ConclaveService helpers namespace"""

    @classmethod
    def all_triggered(cls,deck):
        """Returns all ConclaveRule that would trigger based on the deck"""
        triggered = Counter()
        for rule in [*ConclaveRule.consecrations(), *ConclaveRule.corruptions()]:
          level = cls.check_trigger(deck,name=rule.name)
          if level:
            triggered[rule] = level
        return triggered
        
    @classmethod
    def select_rules(cls,rules_counters):
        """Randomly select rules from the list"""
        sum_counter = sum(rules_counters,Counter())
        sorted_sum_counter = sum_counter.most_common()

        max_rules = 3
        max_same_type_rules = 2
        selected = []

        for rule in sorted_sum_counter:
          if rule[0] not in selected and not any(rule[0].same_class(srule) for srule in selected) \
                and not len([rule[0] for srule in selected if srule.type == rule[0].type])>=max_same_type_rules:
                selected.append(rule[0])
          if len(selected) == max_rules:
            break
        
        return selected
    
    @classmethod 
    def ignore(cls,deck,rule):
        """Hardcoded for the moment"""
        tournament = deck.tournament_signup.tournament
        # not hitting cripple cup with corruption of the cripple
        if rule.name == "Corruption of the Cripple" and tournament.sponsor == "Cripple Cup":
            return True

        # ignore efficiency for low value tournaments as it is very hard to fit in anyway
        if rule.name in ["Consecration of Efficiency","Corruption of Efficiency"] and tournament.deck_value_limit < 100:
            return True
        False

    @classmethod
    def check_trigger(cls, deck, name=""):
        """Returns 0 if it does not trigger, otherwise returns 1 2 or 3 based on the trigger level
           Returns None if rule does not exists
        """
        
        rule = cls.get_conclave_rule(name)
        if not rule or cls.ignore(deck,rule):
            return None

        checker = rule.klass().lower()
        value = getattr(cls,checker)(deck)

        return trigger_level(rule,value)

    @classmethod
    def get_conclave_rule(cls,name):
        return ConclaveRule.query.filter_by(name=name).one_or_none()

    #conclave checkers
    #TESTED
    @classmethod
    def power(cls,deck):
        i = 0
        for player in DeckService.players(deck):
            if player.strength() + printed(player,"IncreaseStrength") + skill_ups(player,deck,"IncreaseStrength") >= 5:
                i+=1
        return i

    #TESTED
    @classmethod
    def deftness(cls,deck):
        i = 0
        for player in DeckService.players(deck):
            if player.agility() + printed(player,"IncreaseAgility") + skill_ups(player,deck,"IncreaseAgility") >= 5:
                i+=1
        return i

    #TESTED
    @classmethod
    def lethargy(cls,deck):
        i = 0
        for player in DeckService.players(deck):
            if player.agility() + printed(player,"IncreaseAgility") + skill_ups(player,deck,"IncreaseAgility") <= 2:
                i+=1
        return i

    #TESTED
    @classmethod
    def swiftness(cls,deck):
        i = 0
        for player in DeckService.players(deck):
            if player.movement() + printed(player,"IncreaseMovement") + skill_ups(player,deck,"IncreaseMovement") >= 8:
                i+=1
        return i

    #TESTED
    @classmethod
    def idleness(cls,deck):
        i = 0
        for player in DeckService.players(deck):
            if player.movement() + printed(player,"IncreaseMovement") + skill_ups(player,deck,"IncreaseMovement") <= 5:
                i+=1
        return i

    #TESTED
    @classmethod
    def teachings(cls,deck):
        return len(DeckService.training_cards(deck))
    
    #TESTED
    @classmethod
    def efficiency(cls,deck):
        return deck.tournament_signup.tournament.deck_value_limit - DeckService.deck_value(deck)

    #TESTED
    @classmethod
    def hero(cls,deck):
        sorted_values = sorted([card.template.value for card in deck.cards],reverse=True)
        return sorted_values[0] - sorted_values[1]

    #TESTED
    @classmethod
    def chaos(cls,deck):
        return len(DeckService.special_play_cards(deck))

    #TESTED
    @classmethod
    def destitution(cls,deck):
        return len([card for card in deck.cards if card.template.rarity in [CardTemplate.RARITY_COMMON,CardTemplate.RARITY_STARTER]])
    
    #TESTED
    @classmethod
    def anonymous(cls,deck):
        return len([card for card in deck.cards if card.template.subtype == CardTemplate.SUBTYPE_LINEMAN])

    #TESTED
    @classmethod
    def teamwork(cls,deck):
        i = 0
        for player in DeckService.players(deck):
            if printed(player,"Guard") + skill_ups(player,deck,"Guard", ignore_extra=True) >= 1:
                i+=1
        return i

    #TESTED
    @classmethod
    def mutants(cls,deck):
        i = 0
        for player in DeckService.players(deck):
            for mutation in MUTATIONS:
                if printed(player,mutation) + skill_ups(player,deck,mutation, ignore_extra=True) >= 1:
                    i+=1
        return i

    #TESTED
    @classmethod
    def violence(cls,deck):
        i = 0
        for player in DeckService.players(deck):
            if printed(player,"MightyBlow") + skill_ups(player,deck,"MightyBlow", ignore_extra=True) >= 1:
                i+=1
        return i

    #TESTED
    @classmethod
    def balance(cls,deck):
        i = 0
        for player in DeckService.players(deck):
            if printed(player,"Dodge") + skill_ups(player,deck,"Dodge", ignore_extra=True) >= 1:
                i+=1
        return i

    #TESTED
    @classmethod
    def foul_play(cls,deck):
        i = 0
        for player in DeckService.players(deck):
            if printed(player,"DirtyPlayer") + skill_ups(player,deck,"DirtyPlayer", ignore_extra=True) >= 1:
                i+=1
        return i

    #TESTED
    @classmethod
    def situational(cls,deck):
        return len([card for card in DeckService.training_cards(deck) if card.template.subtype == CardTemplate.SUBTYPE_BASIC])

    #TESTED
    @classmethod
    def specialist(cls,deck):
        return len([card for card in DeckService.training_cards(deck) if card.template.subtype == CardTemplate.SUBTYPE_SPECIALIZED])

    @classmethod
    def coach_o_matic(cls,deck):
        return len([card for card in DeckService.special_play_cards(deck) if KEYWORDS(card.template.description).is_randomise()])

    #TESTED
    @classmethod
    def unsung(cls,deck):
        return len(DeckService.staff_cards(deck))

    #TESTED TODO check if other RR granting cards should count
    @classmethod
    def cautious(cls,deck):
        return len([card for card in DeckService.staff_cards(deck) if card.template.name == "Re-roll"])

    #TESTED 
    @classmethod
    def legends(cls,deck):
        return len([card for card in DeckService.players(deck) if card.template.rarity == CardTemplate.RARITY_LEGEND])

    #TESTED
    @classmethod
    def solitude(cls,deck):
        return len([card for card in deck.cards if card.template.rarity == CardTemplate.RARITY_UNIQUE])

    #TESTED
    @classmethod
    def popular(cls,deck):
        return len([card for card in deck.cards if card.template.subtype == CardTemplate.SUBTYPE_POSITIONAL])

    #TESTED
    @classmethod
    def commitment(cls,deck):
        return len([card for card in deck.cards if card.template.one_time_use])

    #TESTED
    @classmethod
    def cripple(cls,deck):
        i = 0
        for player in DeckService.players(deck):
            i+=len(CardService.injury_names_for_player_card(player)+DeckService.assigned_injuries(player,deck))
        return i

    #TESTED
    @classmethod
    def fundamentals(cls,deck):
        return len([card for card in DeckService.training_cards(deck) if card.template.subtype == CardTemplate.SUBTYPE_CORE])

    #TESTED
    @classmethod
    def stunty(cls,deck):
        i = 0
        for player in DeckService.players(deck):
            if player.stunty():
                i+=1
        return i

    #TESTED
    @classmethod
    def preparation(cls,deck):
        i = 0
        for player in DeckService.players(deck):
            if player.template.rarity not in [CardTemplate.RARITY_UNIQUE,CardTemplate.RARITY_LEGEND] and len(CardService.skill_names_for_player_card(player)):
                i+=1
        return i

    #TESTED
    @classmethod
    def affluence(cls,deck):
        return len([card for card in deck.cards if card.template.rarity == CardTemplate.RARITY_EPIC])

    #TESTED
    @classmethod
    def freaks(cls,deck):
        i = 0
        for player in DeckService.players(deck):
            if printed(player,"IncreaseMovement") + skill_ups(player,deck,"IncreaseMovement") \
                + printed(player,"IncreaseStrength") + skill_ups(player,deck,"IncreaseStrength") \
                + printed(player,"IncreaseAgility") + skill_ups(player,deck,"IncreaseAgility") \
                + printed(player,"IncreaseArmour") + skill_ups(player,deck,"IncreaseArmour"):
                i+=1
        return i

def printed(player,skill):
    """Return number of printed skill type for player"""
    return CardService.skill_names_for_player_card(player).count(skill)

def skill_ups(player,deck,skill, ignore_extra = False):
    """Return number of assigned skill type for player"""
    return list(itertools.chain.from_iterable([CardService.skill_names_for(card) for card in DeckService.assigned_cards_to(deck,player,ignore_extra=ignore_extra)])).count(skill)

def trigger_level(rule,value):
    # order
    level = 0
    if rule.level1 < rule.level2:
        if rule.level1 <= value < rule.level2:
            level = 1
        elif rule.level2 <= value < rule.level3:
            level = 2
        elif rule.level3 <= value:
            level = 3
    else:
        if rule.level2 < value <= rule.level1:
            level = 1
        elif rule.level3 < value <= rule.level2:
            level = 2
        elif rule.level3 >= value:
            level = 3

    return level
