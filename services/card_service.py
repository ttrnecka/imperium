"""CardsService helpers"""
import re

from models.data_models import Card, Coach, CardTemplate, CrackerCardTemplate, CrackerCard
from models.base_model import db
from misc.helpers import represents_int
from .imperium_sheet_service import ImperiumSheetService


name_map = {'Card ID':'id', 'Card Name':'name', 'Description':'description', 'Race':'race', 'Rarity':'rarity', 'Type':'card_type',
    'Subtype':'subtype', 'Notes':'notes', 'Card Value':'value', 'Skill Access':'skill_access', 'Multiplier':'multiplier',
    'Starter Multiplier':'starter_multiplier', 'One Time Use':'one_time_use', "Position":"position", "Base Statline":"base_statline"}

cracker_name_map = {'Card ID':'id', 'Card Name':'name', 'Description':'description', 'Race':'race', 'Rarity':'rarity', 'Card Type':'card_type',
    'Team':'team', 'Notes':'notes', 'Class':'klass', 'Multiplier':'multiplier', 'One Time Use':'one_time_use', "Position":"position", "Built-In Skill":"built_in_skill"}

class CardService:
    skillreg = r"(Kick-Off Return|Safe Throw|Shadowing|Disturbing Presence|Sneaky Git|Horns|Guard|Mighty Blow|ST\+|\+ST|MA\+|\+MA|AG\+|\+AG|AV\+|\+AV|Block|Accurate|Strong Arm|Dodge|Juggernaut|Claw|Sure Feet|Break Tackle|Jump Up|Two Heads|Wrestle|Frenzy|Multiple Block|Tentacles|Pro|Strip Ball|Sure Hands|Stand Firm|Grab|Hail Mary Pass|Dirty Player|Extra Arms|Foul Appearance|Dauntless|Thick Skull|Tackle|Nerves of Steel|Catch|Pass Block|Piling On|Pass|Fend|Sprint|Grab|Kick|Pass Block|Leap|Sprint|Leader|Diving Tackle|Tentacles|Prehensile Tail|Sidestep|Dump-Off)( |,|\.|$)"
    """CardService helper namespace"""

    @classmethod
    def get_card_by_name(cls, name):
        card = CardTemplate.query.filter_by(name=name).one_or_none()
        return card

    @classmethod
    def get_card_from_coach(cls, coach, name):
        """returns card from coach by `name`"""
        cards = list(filter(lambda card: card.get('name').lower() == name.lower(), coach.active_cards()))

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

    @classmethod
    def update(cls):
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

        # cracker cards

        templates = ImperiumSheetService.cracker_templates()
        for template_dict in templates:
            template_dict = {cracker_name_map[name]: val for name, val in template_dict.items() if cracker_name_map.get(name, None)}
            template = CrackerCardTemplate.query.get(template_dict['id'])
            if template:
                template.update(**template_dict)
            else:
                db.session.add(CrackerCardTemplate(**template_dict))
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
    def skills_for_training_card(cls, name):
        skills = []
        if name == "Block Party":
          skills = ["Block"]
        elif name == "Dodge like a Honeybadger, Sting like the Floor":
          skills = ["Tackle"]
        elif name == "Gengar Mode":
          skills = ["DirtyPlayer"]
        elif name == "Roger Dodger":
          skills = ["Dodge"]
        elif name == "Packing a Punch":
          skills = ["MightyBlow"]
        elif name == "Ballhawk":
          skills = ["Wrestle","Tackle","StripBall"]
        elif name == "Roadblock":
          skills = ["Block","Dodge","StandFirm"]
        elif name == "Cold-Blooded Killer":
          skills = ["MightyBlow","PilingOn"]
        elif name == "Sniper":
          skills = ["Accurate","StrongArm"]
        elif name == "A Real Nuisance":
          skills = ["SideStep","DivingTackle"]
        elif name == "Insect DNA":
          skills = ["TwoHeads","ExtraArms"]
        elif name == "Super Wildcard":
          skills = ["MVPCondition"]
        elif name == "I Didn't Read The Rules":
          skills = ["MVPCondition","MVPCondition","MVPCondition"]
        elif name == "Counterfeit Skill Shop":
          skills = ["DivingTackle"]
        elif name == "Laying the Smackdown":
          skills = ["Wrestle"]
        elif name == "Need for Speed":
          skills = ["IncreaseMovement"]
        elif name == "The Great Wall":
          skills = ["Guard"]
        elif name == "Tubthumping":
          skills = ["PilingOn","JumpUp","Dauntless"]
        elif name == "Training Wildcard":
          skills = ["MVPCondition2"]
        elif name == "Sidestep":
          skills = ["SideStep"]
        elif name == "Bodyguard" or name == "Hired Muscle" or name == "Personal Army":
          skills = []
        else:
          skills = [name]
        
        return skills

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

