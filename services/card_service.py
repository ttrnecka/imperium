"""CardsService helpers"""
import re

from models.data_models import Card, Coach, CardTemplate, CrackerCardTemplate, CrackerCard
from models.base_model import db
from misc.helpers import represents_int, CardHelper
from misc import INJURYREG, SKILLREG
from misc.base_statline import mutation_positionals
from .imperium_sheet_service import ImperiumSheetService


name_map = {'Card ID':'id', 'Card Name':'name', 'Description':'description', 'Race':'race', 'Rarity':'rarity', 'Type':'card_type',
    'Subtype':'subtype', 'Notes':'notes', 'Card Value':'value', 'Skill Access':'skill_access', 'Multiplier':'multiplier',
    'Starter Multiplier':'starter_multiplier', 'One Time Use':'one_time_use', "Position":"position"}

cracker_name_map = {'Card ID':'id', 'Card Name':'name', 'Description':'description', 'Race':'race', 'Rarity':'rarity', 'Card Type':'card_type',
    'Team':'team', 'Notes':'notes', 'Class':'klass', 'Multiplier':'multiplier', 'One Time Use':'one_time_use', "Position":"position", "Built-In Skill":"built_in_skill"}

skills_map = {
    'G': ['Dauntless', 'Dirty Player', 'Fend', 'Kick-Off Return', 'Pass Block', 'Shadowing', 'Tackle', 'Wrestle', 'Block', 'Frenzy', 'Kick', 'Pro', 'Strip Ball', 'Sure Hands'],
    'A': ['Catch', 'Diving Catch', 'Diving Tackle', 'Jump Up', 'Leap', 'Sidestep', 'SideStep', 'Sneaky Git', 'Sprint', 'Dodge', 'Sure Feet'],
    'P': ['Accurate', 'Dump-Off', 'Hail Mary Pass', 'Nerves of Steel', 'Pass', 'Safe Throw', 'Leader'],
    'S': ['Break Tackle', 'Grab', 'Juggernaut', 'Multiple Block', 'Piling On', 'Stand Firm', 'Strong Arm', 'Thick Skull', 'Guard', 'Mighty Blow'],
    'M': ['Big Hand', 'Disturbing Presence', 'Extra Arms', 'Foul Appearance', 'Horns', 'Prehensile Tail', 'Tentacles', 'Two Heads', 'Very Long Legs', 'Claw'],
}

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
            if card.get('rarity') in [CardTemplate.RARITY_UNIQUE,CardTemplate.RARITY_LEGEND,CardTemplate.RARITY_INDUCEMENT, CardTemplate.RARITY_BLESSED, CardTemplate.RARITY_CURSED]:
                string = card.get('description')
            else:
                string = card.get('name')
        else:
            if card['rarity'] in [CardTemplate.RARITY_UNIQUE,CardTemplate.RARITY_LEGEND,CardTemplate.RARITY_INDUCEMENT, CardTemplate.RARITY_BLESSED, CardTemplate.RARITY_CURSED]:
                string = card['description']
            else:
                string = card['name']

        skills = re.findall(cls.skillreg,string)
        return [skill[0] for skill in skills]

    @staticmethod
    def mutation_allowed(card):
        c = CardHelper.card_fix(card)
        positional = f"{c.get('race').split('/')[0]}_{c.get('position')}"
        return positional in mutation_positionals

    @staticmethod
    def can_take_skills(player_card, skills):
        p_skills = CardService.skill_names_for_player_card(player_card, api_format=False) + CardService.default_skill_names_for(player_card, api_format=False)
        if set(skills) & set(p_skills):
            return False
        
        # check for mutation access
        for skill in skills:
            if skill in skills_map['M'] and not CardService.mutation_allowed(player_card):
                return False

        return True

    @staticmethod
    def default_skill_names_for(card, api_format=True):
      if isinstance(card,dict):
          matches = card['default_skills']
      else:
          matches = card.default_skills()

      if api_format:
        return [skill_to_api_skill(match) for match in matches]
      return matches

    @staticmethod
    def skill_names_for(card, api_format=True):
      if isinstance(card,dict):
          name = card['template']['name']
      else:
          name = card.template.name
      if name == "Block Party":
          skills = ["Block"]
      elif name == "Dodge like a Honeybadger, Sting like the Floor":
          skills = ["Tackle"]
      elif name == "Gengar Mode":
          skills = ["Dirty Player"]
      elif name == "Roger Dodger":
          skills = ["Dodge"]
      elif name == "Packing a Punch":
          skills = ["Mighty Blow"]
      elif name == "Ballhawk":
          skills = ["Wrestle","Tackle","Strip Ball"]
      elif name == "Roadblock":
          skills = ["Block","Dodge","Stand Firm"]
      elif name == "Cold-Blooded Killer":
          skills = ["Mighty Blow","Piling On"]
      elif name == "Sniper":
          skills = ["Accurate","Strong Arm"]
      elif name == "A Real Nuisance":
          skills = ["Side Step","Diving Tackle"]
      elif name == "Insect DNA":
          skills = ["Two Heads","Extra Arms"]
      elif name == "Super Wildcard":
          skills = ["MVPCondition"]
      elif name == "I Didn't Read The Rules":
          skills = ["MVPCondition","MVPCondition","MVPCondition"]
      elif name == "Counterfeit Skill Shop":
          skills = ["Diving Tackle"]
      elif name == "Laying the Smackdown":
          skills = ["Wrestle"]
      elif name == "Need for Speed":
          skills = ["IncreaseMovement"]
      elif name == "The Great Wall":
          skills = ["Guard"]
      elif name == "Tubthumping":
          skills = ["Piling On","Jump Up","Dauntless"]
      elif name == "Training Wildcard":
          skills = ["MVPCondition2"]
      elif name == "Sidestep":
          skills = ["Side Step"]
      elif name == "Crowd Pleaser":
          skills = ["Frenzy","Juggernaut"]
      elif name == "Designated Ball Carrier":
          skills = ["Block", "Sure Hands"]
      elif name in ["Bodyguard","Hired Muscle","Personal Army"]:
          skills = []
      else:
          skills = [name]
      if api_format:
        return [skill_to_api_skill(match) for match in skills]
      return skills

    @staticmethod
    def number_of_assignments(card):
      c = CardHelper.card_fix(card)
      name = c.get('name')
      if c.get('card_type') != 'Training':
        return 0
      if name == 'Bodyguard':
        return 1
      if name == 'Hired Muscle':
        return 2
      if name == 'Personal Army':
        return 3
      if name == 'Super Wildcard':
        return 3
      if name == "I Didn't Read The Rules":
        return 1
      if ' one ' in c.get('description'):
        return 1
      if ' three ' in c.get('description'):
        return 3
      return 1

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

    @staticmethod
    def assignable(card):
        """Return true if card can be assigned training card"""
        if isinstance(card, Card):
            rarity = card.get('rarity')
        else:
            rarity = card['template']['rarity']
        
        return rarity not in ['Legendary', 'Inducement', 'Unique', 'Blessed', 'Cursed']

    @staticmethod
    def card_id_or_uuid(card):
      if isinstance(card, dict):
        id = card.get('id') if card.get('id', None) else card.get('uuid')
      else:
        id = card.id if card.id else card.uuid
      return str(id)

    @staticmethod
    def injury_names_for_player_card(card):
      #return card descritpion for non player cards
      if card.template.card_type!=CardTemplate.TYPE_PLAYER:
          return card.template.name

      string = ""
      if card.template.rarity in [CardTemplate.RARITY_UNIQUE,CardTemplate.RARITY_LEGEND,CardTemplate.RARITY_INDUCEMENT, CardTemplate.RARITY_BLESSED, CardTemplate.RARITY_CURSED]:
          string = card.template.description
      else:
          string = card.template.name

      matches = [match[0] for match in INJURYREG.findall(string)]
      
      return [injury_to_api_injury(match) for match in matches]

    @staticmethod
    def skill_names_for_player_card(card, api_format=True):
      card = CardHelper.card_fix(card)
      #return card descritpion for non player cards
      if card.get('card_type')!=CardTemplate.TYPE_PLAYER:
          return card.get('name')

      string = ""
      if card.get('rarity') in [CardTemplate.RARITY_UNIQUE,CardTemplate.RARITY_LEGEND,CardTemplate.RARITY_INDUCEMENT, CardTemplate.RARITY_BLESSED, CardTemplate.RARITY_CURSED]:
          string = card.get('description')
      else:
          string = card.get('name')

      matches = [match[0] for match in SKILLREG.findall(string)]

      # Pro Elf extra case
      if len(re.findall("Pro Elf",string)):
          # remove one accidental Pro skill
          matches.remove("Pro")
      if api_format:
        return [skill_to_api_skill(match) for match in matches]
      return matches

def injury_to_api_injury(injury):
    if injury == "Smashed Collarbone":
        name = "SmashedCollarBone"
    else:
        name = re.sub(r'[\s-]', '',injury)
    return name

def skill_to_api_skill(skill):
  if skill in ["Strength Up!","ST+","+ST"]:
      name = "IncreaseStrength"
  elif skill in ["Agility Up!","AG+","+AG"]:
      name = "IncreaseAgility"
  elif skill in ["Movement Up!","MA+","+MA"]:
      name = "IncreaseMovement"
  elif skill in ["Armour Up!","AV+","+AV"]:
      name = "IncreaseArmour"
  elif skill == "Nerves of Steel":
      name = "NervesOfSteel"
  elif skill == "Sidestep":
      name = "SideStep"
  elif skill == "Mutant Roshi's Scare School":
      name = ""
  else:
      name = re.sub(r'[\s-]', '',skill)
  return name