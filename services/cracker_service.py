"""Pack Service helpers"""
import random
from models.general import MIXED_TEAMS
from models.data_models import CrackerCard, CrackerCardTemplate, CrackerTeam
from .imperium_sheet_service import ImperiumSheetService

class InvalidCrackerType(Exception):
    """Exception for Invalid pack type"""

class InvalidCrackerTeam(Exception):
    """Exception for Invalid team"""

class CrackerService:
    """Namespace for helpers"""
    MIXED_TEAMS = MIXED_TEAMS

    PACKS = ["nice","naughty","huge bonus","immortal"]

    CRACKER_COMBOS = [
        {"roll":0.4, "rarities":["Rare", "Common", "Common"]},
        {"roll":0.6, "rarities":["Rare", "Rare", "Common"]},
        {"roll":0.8, "rarities":["Epic", "Common", "Common"]},
        {"roll":0.89, "rarities":["Rare", "Rare", "Rare"]},
        {"roll":0.98, "rarities":["Epic", "Rare", "Common"]},
        {"roll":1, "rarities":["Epic", "Rare", "Rare"]},
    ]

    HB_COMBOS = [
        {"roll":1, "rarities":["Unique"]},
    ]

    IMMORTAL_COMBOS = [
        {"roll":1, "rarities":["Legendary"]},
    ]

    @classmethod
    def cracker_team(cls, coach):
        team = CrackerTeam.query.filter(CrackerTeam.coach == coach, CrackerTeam.active == True).first()

        if not team:
            team = CrackerTeam(coach=coach,active=True)

        return team

    @classmethod
    def generate_pack(cls, ptype="nice", team="aog"):
        """Generate pack of ptype, for team, flag if that is first pack"""
        ptype = ptype.lower()
        if ptype.lower() not in cls.PACKS:
            raise InvalidCrackerType(f"Invalid pack type {ptype}")

        team = team.lower()
        if team not in cls.team_codes():
            raise InvalidCrackerTeam(f"Invalid team {team}")

        cards = []
        if ptype in ["nice", "naughty"]:
            combos = cls.CRACKER_COMBOS
        elif ptype == "huge_bonus":
            combos = cls.HB_COMBOS
        else:
            combos = cls.IMMORTAL_COMBOS

        roll = random.random()
        rarities = [combo for combo in combos if combo['roll'] >= roll][0]['rarities']
        for rarity in rarities:
            fcards = cls.filter_cards(rarity, team, ptype)
            cards.append(random.choice(fcards))

        max_pack_id = CrackerCard.max_pack_id()
        if not max_pack_id:
            new_pack_id = 1
        else:
            new_pack_id = max_pack_id + 1

        tmp_cards = []
        for card in cards:
            crackerCard = CrackerCard.from_template(card)
            crackerCard.pack_id = new_pack_id
            tmp_cards.append(crackerCard)
        return tmp_cards

    @classmethod
    def team_by_code(cls, code):
        """returns mixed team by its code"""
        return next(t for t in cls.MIXED_TEAMS if t["code"] == code)

    @classmethod
    def team_codes(cls):
        """returns all team codes"""
        return [team["code"] for team in cls.MIXED_TEAMS]

    @classmethod
    def filter_cards(cls, rarity, team, ptype):
        """Pull cards of given rarity, ctype, races and subtype from All cards"""

        templates = CrackerCardTemplate.query.all()
        pool = []
        for template in templates:
            if (template.team.lower() == team or template.team.lower() == "all") and (template.klass.lower() == ptype or template.klass.lower() == "stocking filler") and template.rarity == rarity:
                for _ in range(template.multiplier):
                    pool.append(template)
    
        return pool

    @classmethod
    def active_cards(cls,coach = None):
        if coach:
            return CrackerCard.query.join(CrackerCard.team).filter(CrackerTeam.active == True, CrackerTeam.coach == coach).all()
        else:
            return CrackerCard.query.join(CrackerCard.team).filter(CrackerTeam.active == True).all()