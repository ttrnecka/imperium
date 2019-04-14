from models.base_model import db
from models.data_models import Pack, Card, Coach, Tournament
from imperiumbase import ImperiumSheet
from sqlalchemy.orm import joinedload
import random

class PackService:

    MIXED_TEAMS = [
        {"code":"aog",  "name":"Alliance of Goodness",   "races":['Bretonnian' , 'Human', 'Dwarf', 'Halfling', 'Wood Elf'] },
        {"code":"au",   "name":'Afterlife United',       "races":['Undead','Necromantic','Khemri','Vampire']},
        {"code":"afs",  "name":'Anti-Fur Society',       "races":['Kislev' , 'Norse', 'Amazon', 'Lizardman']},
        {"code":"cgs",  "name":'Chaos Gods Selection',   "races":['Chaos' , 'Nurgle']},
        {"code":"cpp",  "name":'Chaotic Player Pact',    "races":['Chaos' , 'Skaven', 'Dark Elf', 'Underworld']},
        {"code":"egc",  "name":'Elfic Grand Coalition',  "races":['High Elf' , 'Dark Elf', 'Wood Elf', 'Pro Elf']},
        {"code":"fea",  "name":'Far East Association',   "races":['Chaos Dwarf' , 'Orc', 'Goblin', 'Skaven', 'Ogre']},
        {"code":"hl",   "name":'Human League',           "races":['Bretonnian' , 'Human', 'Kislev', 'Norse', 'Amazon']},
        {"code":"sbr",  "name":'Superior Being Ring',    "races":['Bretonnian' , 'High Elf', 'Vampire', 'Chaos Dwarf']},
        {"code":"uosp", "name":'Union of Small People',  "races":['Ogre' , 'Goblin','Halfling']},
        {"code":"vt",   "name":'Violence Together',      "races":['Ogre' , 'Goblin','Orc', 'Lizardman']}
    ]

    PACK_PRICES = {
        "booster_budget": 5,
        "booster_premium": 15,
        "player": 10,
        "training": 10,
        "starter": 0
    }

    @classmethod
    def filter_cards(cls,rarity,ctype=None,races=None):
        if races is not None:
            return [card for card in ImperiumSheet.cards() if card["Rarity"]==rarity and card["Type"]==ctype and card["Race"] in races]
        if ctype is not None:
            return [card for card in ImperiumSheet.cards() if card["Rarity"]==rarity and card["Type"]==ctype]
        return [card for card in ImperiumSheet.cards() if card["Rarity"]==rarity]

    @classmethod
    def rarity(cls,pack_type, quality="budget"):
        budgetCommon = 80+1
        budgetRare = 95+1
        budgetEpic = 99+1
        budgetLegendary = 100+1
        trainingCommon = 65+1
        trainingRare = 97+1
        trainingEpic = 100+1
        premiumRare = 65+1
        premiumEpic = 97+1
        premiumLegendary = 100+1

        roll = random.randint(1,100)

        if pack_type=='booster' and quality == "budget":
            if roll in range(budgetEpic,budgetLegendary):
                rarity = "Legendary"
            elif roll in range(budgetRare,budgetEpic):
                rarity = "Epic"
            elif roll in range(budgetCommon,budgetRare):
                rarity = "Rare"
            else:
                rarity = "Common"
        elif pack_type=="training":
            if roll in range(trainingRare,trainingEpic):
                rarity = "Epic"
            elif roll in range(trainingCommon,trainingRare):
                rarity = "Rare"
            else:
                rarity = "Common"
        else:
            if roll in range(premiumEpic,premiumLegendary):
                rarity = "Legendary"
            elif roll in range(premiumRare,premiumEpic):
                rarity = "Epic"
            else:
                rarity = "Rare"

        return rarity

    @classmethod
    def generate(cls,ptype="booster_budget",team = None):
        if ptype not in cls.PACK_PRICES:
            raise InvalidPackType(ptype)

        if team is not None and team not in cls.team_codes():
            raise InvalidTeam(team)

        if ptype == "player":
            if not team:
                raise  ValueError(f"Missing team value for {ptype} pack")
            elif team.lower() not in cls.team_codes():
                raise  ValueError(f"Team {team} unknow")
            else:
                team = team.lower()
        price = cls.PACK_PRICES[ptype]
        
        pack = Pack(price=price,pack_type=ptype, team=team)
        cards = []
        if ptype == "starter":
            cards.extend(ImperiumSheet.starter_cards())
        if ptype == "player":
            races = cls.team_by_code(team)["races"]
            for _ in range(3):
                rarity = cls.rarity(ptype)
                fcards = cls.filter_cards(rarity,"Player",races)
                cards.append(random.choice(fcards))
        if ptype == "training":
            for _ in range(3):
                rarity = cls.rarity(ptype)
                fcards = cls.filter_cards(rarity,"Training")
                cards.append(random.choice(fcards))
        if ptype in ["booster_budget","booster_premium"] :
            q = "budget" if "budget" in ptype else "premium"
            rarity = cls.rarity("booster","premium")
            fcards = cls.filter_cards(rarity)
            cards.append(random.choice(fcards))
            for _ in range(4):
                rarity = cls.rarity("booster",q)
                fcards = cls.filter_cards(rarity)
                cards.append(random.choice(fcards))

        for card in cards:
            pack.cards.append(CardService.init_Card_from_card(card))
        return pack

    @classmethod
    def admin_pack(cls,price=0, card_names=[]):
        pack = Pack(price=price,pack_type="admin")
        for name in card_names:
            card = CardService.get_card_from_sheet(name)
            if card:
                pack.cards.append(CardService.init_Card_from_card(card))
        return pack

    @classmethod
    def team_by_code(cls,code):
        return next(t for t in cls.MIXED_TEAMS if t["code"] == code)

    @classmethod
    def team_codes(cls):
        return [team["code"] for team in cls.MIXED_TEAMS]
    
    @classmethod
    def description(cls,pack):
        desc = ' '.join(pack.pack_type.split('_')).capitalize()
        if pack.team:
            desc+=" " + cls.team_by_code(pack.team)["name"]
        desc+=" pack"

        return desc


class CardService:
    @classmethod
    def init_Card_from_card(cls,card):
        return Card(
            name=card["Card Name"],
            rarity=card["Rarity"],
            race=card["Race"],
            description = card["Description"],
            card_type = card["Type"],
            subtype = card["Subtype"],
            notes = card["Notes"] if hasattr(card, "Notes") else "",
        )

    @classmethod
    def turn_Card_to_card(cls,card):
        return {
            "Coach": card.coach.short_name(),
            "Card Name": card.name,
            "Rarity": card.rarity,
            "Race": card.race,
            "Description": card.description,
            "Type": card.card_type,
            "Subtype": card.subtype,
            "Notes": card.notes
        }

    # return card from sheet in dict format, name must be exact match, case insensitive
    @classmethod
    def get_card_from_sheet(cls,name):
        name_low = name.lower()
        for card in ImperiumSheet.cards():
            print(card)
            if name_low == str(card["Card Name"]).lower():
                return card 
        return None

    @classmethod
    def get_Card_from_coach(cls,coach,name):
        cards = list(filter(lambda card: card.name.lower() == name.lower(), coach.cards))

        if len(cards)==0:
            return None
        else:
            return cards[0]

        
class SheetService:
    @classmethod
    def export_cards(cls):
        cards = []

        for coach in Coach.query.options(joinedload('cards').joinedload('coach')).all():
            for card in coach.cards:
                cards.append(CardService.turn_Card_to_card(card))

        ImperiumSheet.store_cards(cards)

class CoachService:
    @classmethod
    def remove_softdeletes(cls):
        for coach in Coach.query.with_deleted().filter_by(deleted=True):
            db.session.delete(coach)
        db.session.commit()

class TournamentService:
    @classmethod
    def init_dict_from_tournament(cls,tournament):
        return {
            "tournament_id":int(tournament["Tournament ID"]),
            "name":tournament["Tournament Name"],
            "type":tournament["Tournament Type"],
            "mode":tournament["Tournament Mode"],
            "signup_close_date":tournament["Signup Close Date"].replace('\x92',' '),
            "expected_start_date":tournament["Expected Start Date"].replace('\x92',' '),
            "expected_end_date":tournament["Expected End Date"].replace('\x92',' '),
            "fee":int(tournament["Entrance Fee"]),
            "status":tournament["Signup Status"],
            "coach_limit":int(tournament["Coach Count Limit"]),
            "region":tournament["Region Bias"],
            "deck_limit":int(tournament["Deck Size Limit"]),
            "admin":tournament["Tournament Admin"],
            "sponsor":tournament["Tournament Sponsor"],
            "special_rules":tournament["Special Rules"],
            "prizes":tournament["Prizes"],
        }


class InvalidTeam(Exception):
    pass

class InvalidQuality(Exception):
    pass

class InvalidPackType(Exception):
    pass