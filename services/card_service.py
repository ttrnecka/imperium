"""CardsService helpers"""
import re

from models.data_models import Card, Coach
from models.base_model import db
from misc.helpers import represents_int
from .imperium_sheet_service import ImperiumSheetService

class CardService:
    skillreg = r"(Safe Throw|Shadowing|Disturbing Presence|Sneaky Git|Horns|Guard|Mighty Blow|ST\+|\+ST|MA\+|\+MA|AG\+|\+AG|AV\+|\+AV|Block|Accurate|Strong Arm|Dodge|Juggernaut|Claw|Sure Feet|Break Tackle|Jump Up|Two Heads|Wrestle|Frenzy|Multiple Block|Tentacles|Pro|Strip Ball|Sure Hands|Stand Firm|Grab|Hail Mary Pass|Dirty Player|Extra Arms|Foul Appearance|Dauntless|Thick Skull|Tackle|Nerves of Steel|Catch|Pass Block|Piling On|Pass|Fend|Sprint|Grab|Kick|Pass Block|Leap|Sprint|Leader|Diving Tackle|Tentacles|Prehensile Tail|Sidestep|Dump-Off)( |,|\.|$)"
    """CardService helper namespace"""
    @classmethod
    def init_card_model_from_card(cls, card):
        """init Card from card loaded from Imperium base sheet"""
        return Card(
            name=card["Card Name"],
            rarity=card["Rarity"],
            race=card["Race"],
            description=card["Description"],
            card_type=card["Type"],
            subtype=card["Subtype"],
            value=int(card["Card Value"]) if "Card Value" in card
            and represents_int(card["Card Value"]) else 0,
            notes=card["Notes"] if hasattr(card, "Notes") else "",
            skill_access=card["Skill Access"],
            assigned_to_array={},
        )

    # transform imperium base card into dict that can be mapped to Card attributes
    @classmethod
    def init_dict_from_card(cls, card):
        """turn Sheet presentation of card to dict that can be used to update Card"""
        return {
            "name":card["Card Name"],
            "rarity":card["Rarity"],
            "race":card["Race"],
            "description":card["Description"],
            "card_type":card["Type"],
            "subtype":card["Subtype"],
            "value":int(card["Card Value"]) if "Card Value" in card
                    and represents_int(card["Card Value"]) else 0,
            "notes":card["Notes"] if hasattr(card, "Notes") else "",
            "skill_access":card["Skill Access"],
        }

    @classmethod
    def get_card_from_sheet(cls, name):
        """return card from sheet in dict format, `name` must be exact match, case insensitive"""
        name_low = name.lower()
        for card in ImperiumSheetService.cards():
            if name_low == str(card["Card Name"]).lower():
                return card
        return None

    @classmethod
    def get_card_from_coach(cls, coach, name):
        """returns card from coach by `name`"""
        cards = list(filter(lambda card: card.name.lower() == name.lower(), coach.cards))

        if not cards:
            return None
        return cards[0]

    @classmethod
    def get_undusted_card_from_coach(cls, coach, name):
        """returns undusted card from coach by `name`"""
        cards = Card.query.join(Card.coach) \
            .filter(Coach.id == coach.id, Card.name == name, Card.duster_id == None, # pylint: disable=singleton-comparison
                    Card.in_development_deck == False, Card.in_imperium_deck == False).all() # pylint: disable=singleton-comparison

        if cards:
            return None
        return cards[0]

    @classmethod
    def get_dusted_card_from_coach(cls, coach, name):
        """returns dusted card from coach by `name`"""
        cards = Card.query.join(Card.coach) \
            .filter(Coach.id == coach.id, Card.name == name, Card.duster_id != None).all() # pylint: disable=singleton-comparison

        if cards:
            return None
        return cards[0]

    @classmethod
    def update(cls):
        """Update cards in DB from the cards in the sheet"""
        for card in ImperiumSheetService.cards(True):
            c_dict = cls.init_dict_from_card(card)
            cards = Card.query.filter_by(name=c_dict['name']).all()

            for scard in cards:
                scard.update(**c_dict)

        db.session.commit()

    @classmethod
    def builtin_skills_for(cls, card):
        if isinstance(card, Card):
            if card.rarity in ["Unique","Legendary","Inducement"]:
                string = card.description
            else:
                string = card.name
        else:
            if card['rarity'] in ["Unique","Legendary","Inducement"]:
                string = card['description']
            else:
                string = card['name']

        skills = re.findall(cls.skillreg,string)
        return [skill[0] for skill in skills]
