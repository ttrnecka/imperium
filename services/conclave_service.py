"""ConclaveService helpers"""
import re
import itertools

from models.data_models import Deck, ConclaveRule, CardTemplate
from models.base_model import db

SKILLREG = re.compile(r'(Diving Catch|Kick-Off Return|Safe Throw|Shadowing|Disturbing Presence|Sneaky Git|Horns|Guard|Mighty Blow|ST\+|\+ST|MA\+|\+MA|AG\+|\+AG|AV\+|\+AV|Block|Accurate|Strong Arm|Dodge|Juggernaut|Claw|Sure Feet|Break Tackle|Jump Up|Two Heads|Wrestle|Frenzy|Multiple Block|Tentacles|Pro|Strip Ball|Sure Hands|Stand Firm|Grab|Hail Mary Pass|Dirty Player|Extra Arms|Foul Appearance|Dauntless|Thick Skull|Tackle|Nerves of Steel|Catch|Pass Block|Piling On|Pass|Fend|Sprint|Grab|Kick|Pass Block|Leap|Sprint|Leader|Diving Tackle|Tentacles|Prehensile Tail|Sidestep|Dump-Off|Big Hand|Very Long Legs)( |,|\.|$)')
INJURYREG = re.compile(r'(Smashed Knee|Damaged Back|Niggle|Smashed Ankle|Smashed Hip|Serious Concussion|Fractured Skull|Broken Neck|Smashed Collarbone)( |,|\.|$)')

MUTATIONS = [
    "Disturbing Presence", "Horns", "Claw", "Two Heads", "Tentacles","Extra Arms", "Foul Appearance", "Prehensile Tail","Big Hand","Very Long Legs"
]
class ConclaveService:
    """ConclaveService helpers namespace"""

    @classmethod
    def check_trigger(cls, deck, name=""):
        """Returns 0 if it does not trigger, otherwise returns 1 2 or 3 based on the trigger level
           Returns None if rule does not exists
        """
        
        rule = cls.get_conclave_rule(name)
        if not rule:
            return None

        checker = rule.klass().lower()
        value = getattr(cls,checker)(deck)

        if value >= rule.level1 and value < rule.level2:
            return 1
        elif value >= rule.level2 and value < rule.level3:
            return 2
        elif value >= rule.level3:
            return 3
        else:
            return 0

    @classmethod
    def get_conclave_rule(cls,name):
        return ConclaveRule.query.filter_by(name=name).one_or_none()

    #conclave checkers
    @classmethod
    def strength(cls,deck):
        i = 0
        for player in players(deck):
            if player.strength() + printed(player,"IncreaseStrength") + skill_ups(player,deck,"IncreaseStrength") >= 5:
                i+=1
        return i

    @classmethod
    def agility(cls,deck):
        i = 0
        for player in players(deck):
            if player.agility() + printed(player,"IncreaseAgility") + skill_ups(player,deck,"IncreaseAgility") >= 5:
                i+=1
        return i

    @classmethod
    def speed(cls,deck):
        i = 0
        for player in players(deck):
            if player.movement() + printed(player,"IncreaseMovement") + skill_ups(player,deck,"IncreaseMovement") >= 8:
                i+=1
        return i


    @classmethod
    def teachings(cls,deck):
        return len(training_cards(deck))
    
    @classmethod
    def efficiency(cls,deck):
        return deck.tournament_signup.tournament.deck_value_limit - deck_value(deck)

    @classmethod
    def chaos(cls,deck):
        return len(special_play_cards(deck))

    @classmethod
    def destitution(cls,deck):
        return len([card for card in card if card.template.rarity == CardTemplate.RARITY_COMMON])
    
    @classmethod
    def anonymous(cls,deck):
        return len([card for card in card if card.template.subtype == CardTemplate.SUBTYPE_LINEMAN])

    @classmethod
    def teamwork(cls,deck):
        i = 0
        for player in players(deck):
            if printed(player,"Guard") + skill_ups(player,deck,"Guard") >= 1:
                i+=1
        return i

    @classmethod
    def mutants(cls,deck):
        i = 0
        for player in players(deck):
            for mutation in MUTATIONS:
                if printed(player,mutation) + skill_ups(player,deck,mutation) >= 1:
                    i+=1
        return i


    @classmethod
    def violence(cls,deck):
        i = 0
        for player in players(deck):
            if printed(player,"MightyBlow") + skill_ups(player,deck,"MightyBlow") >= 1:
                i+=1
        return i

    @classmethod
    def balance(cls,deck):
        i = 0
        for player in players(deck):
            if printed(player,"Dodge") + skill_ups(player,deck,"Dodge") >= 1:
                i+=1
        return i

    @classmethod
    def situational(cls,deck):
        return len([card for card in training_cards(deck) if card.template.subtype == CardTemplate.SUBTYPE_BASIC])

    @classmethod
    def specialist(cls,deck):
        return len([card for card in training_cards(deck) if card.template.subtype == CardTemplate.SUBTYPE_SPECIALIZED])

    @classmethod
    def coach_o_matic(cls,deck):
        pass

    @classmethod
    def unsung(cls,deck):
        return len(staff_cards(deck))

    @classmethod
    def legends(cls,deck):
        return len([card for card in players(deck) if card.template.rarity == CardTemplate.RARITY_LEGEND])

    @classmethod
    def cripple(cls,deck):
        pass

    @classmethod
    def crucial(cls,deck):
        return len([card for card in training_cards(deck) if card.template.subtype == CardTemplate.SUBTYPE_CORE])

    @classmethod
    def stunty(cls,deck):
        i = 0
        for player in players(deck):
            if player.stunty():
                i+=1
        return i

    @classmethod
    def preparation(cls,deck):
        i = 0
        for player in players(deck):
            if player.template.rarity not in [CardTemplate.RARITY_UNIQUE,CardTemplate.RARITY_LEGEND] and len(skill_names_for_player_card(player)):
                i+=1
        return i

    @classmethod
    def affluence(cls,deck):
        return len([card for card in card if card.template.rarity == CardTemplate.RARITY_EPIC])

    @classmethod
    def freaks(cls,deck):
        i = 0
        for player in players(deck):
            if printed(player,"IncreaseMovement") + skill_ups(player,deck,"IncreaseMovement") \
                + printed(player,"IncreaseStrength") + skill_ups(player,deck,"IncreaseStrength") \
                + printed(player,"IncreaseAgility") + skill_ups(player,deck,"IncreaseAgility") \
                + printed(player,"IncreaseArmour") + skill_ups(player,deck,"IncreaseArmour"):
                i+=1
        return i

def players(deck):
    return [card for card in deck.cards if card.template.card_type == CardTemplate.TYPE_PLAYER]

def training_cards(deck):
    return [card for card in deck.cards if card.template.card_type == CardTemplate.TYPE_TRAINING]

def special_play_cards(deck):
    return [card for card in deck.cards if card.template.card_type == CardTemplate.TYPE_SP]

def staff_cards(deck):
    return [card for card in deck.cards if card.template.card_type == CardTemplate.TYPE_STAFF]

def printed(player,skill):
    """Return number of printed skill type for player"""
    return skill_names_for_player_card(player).count(skill)

def skill_ups(player,deck,skill):
    """Return number of assigned skill type for player"""
    return list(itertools.chain.from_iterable([skill_names_for(card) for card in assigned_cards(player,deck)])).count(skill)

def skill_names_for_player_card(card):
    #return card descritpion for non player cards
    if card.template.card_type!=CardTemplate.TYPE_PLAYER:
        return card.template.name

    string = ""
    if card.template.rarity in [CardTemplate.RARITY_UNIQUE,CardTemplate.RARITY_LEGEND,CardTemplate.RARITY_INDUCEMENT]:
        string = card.template.description
    else:
        string = card.template.name

    matches = [match[0] for match in SKILLREG.findall(string)]

    # Pro Elf extra case
    if len(re.findall("Pro Elf",string)):
        # remove one accidental Pro skill
        matches.remove("Pro")
    
    return [skill_to_api_skill(match) for match in matches]

def skill_names_for(card):
    if isinstance(card,dict):
        name = card['template']['name']
    else:
        name = card.template.name
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
    elif name in ["Bodyguard","Hired Muscle","Personal Army"]:
        skills = []
    else:
        skills = [name]
    return [skill_to_api_skill(match) for match in skills]

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

def assigned_cards(card, deck):
    cards = []
    for c in (deck.cards.all()+deck.extra_cards):
        if card_id_or_uuid(card) in get_card_assignment(c,deck):
            cards.append(c)

    return cards

def get_card_assignment(card,deck):
    asgn = []
    if isinstance(card,dict):
        if card["assigned_to_array"].get(str(deck.id),None):
            asgn = card["assigned_to_array"][str(deck.id)]
    else:        
        if card.assigned_to_array.get(deck.id,None):
            asgn = card.assigned_to_array[deck.id]
    return [str(a) for a in asgn]

def card_id_or_uuid(card):
    id = card.id if card.id else card.uuid
    return str(id)


def deck_value(deck):
    return sum([card.template.value for card in deck.cards])