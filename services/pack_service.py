"""Pack Service helpers"""
import random
from models.general import MIXED_TEAMS
from models.data_models import Pack, Card, CardTemplate
from .card_service import CardService
from .imperium_sheet_service import ImperiumSheetService

class InvalidPackType(Exception):
    """Exception for Invalid pack type"""

class InvalidTeam(Exception):
    """Exception for Invalid team"""

class InvalidQuality(Exception):
    """Exception for Invalid quantity"""

class PackService:
    """Namespace for helpers"""
    MIXED_TEAMS = MIXED_TEAMS

    PACK_PRICES = {
        "booster_budget": 10,
        "booster_premium": 20,
        "player": 0,
        "training": 0,
        "starter": 0,
        "special":0,
        "positional":0,
        "coaching":0,
        "skill":0,
        "legendary":0,
        "brawl":0,
        "hc": 10,
    }

    BUDGET_COMBOS = [
        {"roll":0.4, "rarities":["Rare", "Common", "Common", "Common", "Common"]},
        {"roll":0.6, "rarities":["Rare", "Rare", "Common", "Common", "Common"]},
        {"roll":0.7, "rarities":["Epic", "Common", "Common", "Common", "Common"]},
        {"roll":0.8, "rarities":["Rare", "Rare", "Rare", "Common", "Common"]},
        {"roll":0.85, "rarities":["Epic", "Rare", "Common", "Common", "Common"]},
        {"roll":0.9, "rarities":["Rare", "Rare", "Rare", "Rare", "Common"]},
        {"roll":0.926, "rarities":["Epic", "Rare", "Rare", "Common", "Common"]},
        {"roll":0.952, "rarities":["Epic", "Epic", "Common", "Common", "Common"]},
        {"roll":0.978, "rarities":["Legendary", "Common", "Common", "Common", "Common"]},
        {"roll":0.9843, "rarities":["Rare", "Rare", "Rare", "Rare", "Rare"]},
        {"roll":0.9906, "rarities":["Epic", "Rare", "Rare", "Rare", "Common"]},
        {"roll":0.996875, "rarities":["Epic", "Epic", "Rare", "Common", "Common"]},
        {"roll":1, "rarities":["Legendary", "Rare", "Common", "Common", "Common"]},
    ]

    PREMIUM_COMBOS = [
        {"roll":0.29, "rarities":["Rare", "Rare", "Rare", "Rare", "Rare"]},
        {"roll":0.58, "rarities":["Epic", "Rare", "Rare", "Rare", "Rare"]},
        {"roll":0.74, "rarities":["Epic", "Epic", "Rare", "Rare", "Rare"]},
        {"roll":0.84, "rarities":["Epic", "Epic", "Epic", "Rare", "Rare"]},
        {"roll":0.89, "rarities":["Legendary", "Rare", "Rare", "Rare", "Rare"]},
        {"roll":0.94, "rarities":["Epic", "Epic", "Epic", "Epic", "Rare"]},
        {"roll":0.965, "rarities":["Legendary", "Epic", "Rare", "Rare", "Rare"]},
        {"roll":0.985, "rarities":["Epic", "Epic", "Epic", "Epic", "Epic"]},
        {"roll":0.995, "rarities":["Legendary", "Epic", "Epic", "Rare", "Rare"]},
        {"roll":1, "rarities":["Legendary", "Epic", "Epic", "Epic", "Rare"]},
    ]

    TRAINING_COMBOS = [
        {"roll":0.4, "rarities":["Rare", "Common", "Common"]},
        {"roll":0.6, "rarities":["Rare", "Rare", "Common"]},
        {"roll":0.8, "rarities":["Epic", "Common", "Common"]},
        {"roll":0.89, "rarities":["Rare", "Rare", "Rare"]},
        {"roll":0.98, "rarities":["Epic", "Rare", "Common"]},
        {"roll":1, "rarities":["Epic", "Rare", "Rare"]},
    ]

    SKILL_COMBOS = [
        {"roll":0.27, "rarities":["Rare", "Rare", "Common", "Common", "Common"]},
        {"roll":0.54, "rarities":["Epic", "Common", "Common", "Common", "Common"]},
        {"roll":0.68, "rarities":["Rare", "Rare", "Rare", "Common", "Common"]},
        {"roll":0.82, "rarities":["Epic", "Rare", "Common", "Common", "Common"]},
        {"roll":0.87, "rarities":["Rare", "Rare", "Rare", "Rare", "Common"]},
        {"roll":0.92, "rarities":["Epic", "Rare", "Rare", "Common", "Common"]},
        {"roll":0.97, "rarities":["Epic", "Epic", "Common", "Common", "Common"]},
        {"roll":0.98, "rarities":["Rare", "Rare", "Rare", "Rare", "Rare"]},
        {"roll":0.99, "rarities":["Epic", "Rare", "Rare", "Rare", "Common"]},
        {"roll":1, "rarities":["Epic", "Epic", "Rare", "Common", "Common"]},
    ]

    COACHING_COMBOS = [
        {"roll":0.55, "rarities":["Rare", "Rare", "Rare"]},
        {"roll":0.8, "rarities":["Epic", "Rare", "Rare"]},
        {"roll":0.95, "rarities":["Epic", "Epic", "Rare"]},
        {"roll":1, "rarities":["Epic", "Epic", "Epic"]},
    ]

    PLAYER_COMBOS = [
        {"roll":0.37, "rarities":["Rare", "Rare", "Rare"]},
        {"roll":0.64, "rarities":["Epic", "Rare", "Rare"]},
        {"roll":0.86, "rarities":["Epic", "Epic", "Rare"]},
        {"roll":0.9375, "rarities":["Epic", "Epic", "Epic"]},
        {"roll":0.975, "rarities":["Legendary", "Rare", "Rare"]},
        {"roll":0.995, "rarities":["Legendary", "Epic", "Rare"]},
        {"roll":1, "rarities":["Legendary", "Epic", "Epic"]},
    ]

    POSITIONAL_COMBOS = [
        {"roll":0.35, "rarities":["Rare", "Rare", "Rare"]},
        {"roll":0.6, "rarities":["Epic", "Rare", "Rare"]},
        {"roll":0.8, "rarities":["Epic", "Epic", "Rare"]},
        {"roll":1, "rarities":["Epic", "Epic", "Epic"]},
    ]

    LEGENDARY_COMBOS = [
        {"roll":1, "rarities":["Legendary"]},
    ]

    PLAYER_FIRST_COMBOS = [
        {"roll":0.6, "rarities":["Epic", "Rare", "Rare"]},
        {"roll":0.8625, "rarities":["Epic", "Epic", "Rare"]},
        {"roll":0.9375, "rarities":["Epic", "Epic", "Epic"]},
        {"roll":0.975, "rarities":["Legendary", "Rare", "Rare"]},
        {"roll":0.995, "rarities":["Legendary", "Epic", "Rare"]},
        {"roll":1, "rarities":["Legendary", "Epic", "Epic"]},
    ]

    BRAWL_COMBOS = [
        {"roll":1, "rarities" :["Unique","Unique","Unique"]}
    ]

    HC_COMBOS = [
        {"roll":0.4, "rarities":["Rare", "Common", "Common"]},
        {"roll":0.6, "rarities":["Rare", "Rare", "Common"]},
        {"roll":0.8, "rarities":["Epic", "Common", "Common"]},
        {"roll":0.89, "rarities":["Rare", "Rare", "Rare"]},
        {"roll":0.98, "rarities":["Epic", "Rare", "Common"]},
        {"roll":1, "rarities":["Epic", "Rare", "Rare"]},
    ]

    @classmethod
    def filter_cards(cls, rarity, ctype=None, races=None, subtype=None):
        """Pull cards of given rarity, ctype, races and subtype from All cards"""
        pool = CardService.template_pool()
        if subtype is not None:
            return [card for card in pool
                    if card.rarity == rarity and card.card_type == ctype
                    and card.race in races and card.subtype == subtype]
        if races is not None:
            return [card for card in pool
                    if card.rarity == rarity and card.card_type == ctype
                    and card.race in races]
        if ctype is not None:
            return [card for card in pool
                    if card.rarity == rarity and card.card_type == ctype]
        return [card for card in pool if card.rarity == rarity]

    @classmethod
    def generate(cls, ptype="booster_budget", team=None, first=False, coach = None):
        """Generate pack of ptype, for team, flag if that is first pack"""
        if ptype not in cls.PACK_PRICES:
            raise InvalidPackType(ptype)

        if team is not None and team not in cls.team_codes():
            raise InvalidTeam(team)

        if ptype in ["player", "positional", "legendary"]:
            if not team:
                raise  ValueError(f"Missing team value for {ptype} pack")
            elif team.lower() not in cls.team_codes():
                raise  ValueError(f"Team {team} unknown")
            else:
                team = team.lower()
        price = cls.PACK_PRICES[ptype]

        pack = Pack(price=price, pack_type=ptype, team=team, coach=coach)
        cards = []
        if ptype == "starter":
            cards.extend(CardService.starter_template_pool())
        else:
            if ptype in ["player"]:
                combos = cls.PLAYER_COMBOS
                if first:
                    combos = cls.PLAYER_FIRST_COMBOS
            elif ptype in ["positional"]:
                combos = cls.POSITIONAL_COMBOS
            elif ptype in ["training", "special"]:
                combos = cls.TRAINING_COMBOS
            elif ptype == "coaching":
                combos = cls.COACHING_COMBOS
            elif ptype == "skill":
                combos = cls.SKILL_COMBOS
            elif ptype == "legendary":
                combos = cls.LEGENDARY_COMBOS
            elif ptype == "booster_premium":
                combos = cls.PREMIUM_COMBOS
            elif ptype == "brawl":
                combos = cls.BRAWL_COMBOS
            elif ptype == "hc":
                combos = cls.HC_COMBOS  
            else:
                combos = cls.BUDGET_COMBOS

            roll = random.random()
            rarities = [combo for combo in combos if combo['roll'] >= roll][0]['rarities']
            for rarity in rarities:
                if ptype in ["player", "positional", "legendary"]:
                    races = cls.team_by_code(team)["races"]
                    subtype = "Positional" if ptype == "positional" else None
                    fcards = cls.filter_cards(rarity, "Player", races, subtype)
                elif ptype in ["training", "skill", "coaching"]:
                    fcards = cls.filter_cards(rarity, "Training")
                elif ptype == "special":
                    fcards = cls.filter_cards(rarity, "Special Play")
                elif ptype == "brawl":
                    fcards = cls.filter_cards(rarity, "Bloodweiser")
                elif ptype == "hc":
                    fcards = cls.filter_cards(rarity, CardTemplate.TYPE_HC)
                else:
                    fcards = cls.filter_cards(rarity)
                cards.append(random.choice(fcards))

        for card in cards:
            pack.cards.append(Card.from_template(card))
        return pack

    @classmethod
    def new_starter_pack(cls, coach = None):
        pack = cls.generate("starter", coach=coach)
        for card in pack.cards:
            card.is_starter = True
        return pack

    @classmethod
    def admin_pack(cls, price=0, card_names=None, coach = None):
        """Generate admin pack from card_name"""
        if card_names is None:
            card_names = []
        pack = Pack(price=price, pack_type="admin", coach=coach)
        for name in card_names:
            card = CardTemplate.query.filter_by(name=name).one_or_none()
            if card:
                pack.cards.append(Card.from_template(card))
        return pack

    @classmethod
    def team_by_code(cls, code):
        """returns mixed team by its code"""
        return next(t for t in cls.MIXED_TEAMS if t["code"] == code)

    @classmethod
    def team_codes(cls):
        """returns all team codes"""
        return [team["code"] for team in cls.MIXED_TEAMS]

    @classmethod
    def description(cls, pack):
        """returns pack description"""
        desc = ' '.join(pack.pack_type.split('_')).capitalize()
        if pack.pack_type == "hc":
          desc = "High Command"
        if pack.team:
            desc += " " + cls.team_by_code(pack.team)["name"]
        desc += " pack"

        return desc
