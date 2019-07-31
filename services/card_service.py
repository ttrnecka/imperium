"""CardsService helpers"""
import re

from models.data_models import Card, Coach, CardTemplate
from models.base_model import db
from misc.helpers import represents_int
from .imperium_sheet_service import ImperiumSheetService


name_map = {'Card ID':'id', 'Card Name':'name', 'Description':'description', 'Race':'race', 'Rarity':'rarity', 'Type':'card_type',
    'Subtype':'subtype', 'Notes':'notes', 'Card Value':'value', 'Skill Access':'skill_access', 'Multiplier':'multiplier',
    'Starter Multiplier':'starter_multiplier'}

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
    def get_card_by_name(cls, name):
        card = CardTemplate.query.filter_by(name=name).one_or_none()
        return card

    @classmethod
    def get_card_from_coach(cls, coach, name):
        """returns card from coach by `name`"""
        cards = list(filter(lambda card: card.get('name').lower() == name.lower(), coach.cards))

        if not cards:
            return None
        return cards[0]

    @classmethod
    def get_undusted_card_from_coach(cls, coach, name):
        """returns undusted card from coach by `name`"""
        cards = Card.query.join(Card.coach, Card.template) \
            .filter(Coach.id == coach.id, CardTemplate.name == name, Card.duster_id == None, # pylint: disable=singleton-comparison
                    Card.in_development_deck == False, Card.in_imperium_deck == False).all() # pylint: disable=singleton-comparison

        if not cards:
            return None
        return cards[0]

    @classmethod
    def get_dusted_card_from_coach(cls, coach, name):
        """returns dusted card from coach by `name`"""
        cards = Card.query.join(Card.coach, Card.template) \
            .filter(Coach.id == coach.id, CardTemplate.name == name, Card.duster_id != None).all() # pylint: disable=singleton-comparison

        if not cards:
            return None
        return cards[0]

    # TODO renamen template_update to update once DB is migrated
    @classmethod
    def update(cls):
        """Update cards in DB from the cards in the sheet"""
        for card in ImperiumSheetService.cards(True):
            c_dict = cls.init_dict_from_card(card)
            cards = Card.query.filter_by(name=c_dict['name']).all()

            for scard in cards:
                scard.update(**c_dict)
        # temporarily so it updates the templates already
        cls.update_templates()
        db.session.commit()

    @classmethod
    def update_templates(cls):
        """Update card teplates from sheet to DB"""
        templates = ImperiumSheetService.templates()
        for template_dict in templates:
            template_dict = {name_map[name]: val for name, val in template_dict.items() if name_map.get(name, None)}
            template = CardTemplate.query.get(template_dict['id'])
            if template:
                template.update(**template_dict)
            else:
                db.session.add(CardTemplate(**template_dict))
        db.session.commit()

    @classmethod
    def builtin_skills_for(cls, card):
        if isinstance(card, Card):
            if card.get('rarity') in ["Unique","Legendary","Inducement"]:
                string = card.get('description')
            else:
                string = card.get('name')
        else:
            if card['rarity'] in ["Unique","Legendary","Inducement"]:
                string = card['description']
            else:
                string = card['name']

        skills = re.findall(cls.skillreg,string)
        return [skill[0] for skill in skills]

    @classmethod
    def template_pool(cls):
        """Returns pool of CardTemplates"""
        return cls._pool("multiplier")

    @classmethod
    def starter_template_pool(cls):
        """Returns pool of Starter CardTemplates"""
        return cls._pool("starter_multiplier")

    @classmethod
    def _pool(cls,attribute):
        templates = CardTemplate.query.all()
        pool = []
        for template in templates:
            for _ in range(getattr(template,attribute)):
                pool.append(template)
        return pool

