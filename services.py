from models.base_model import db
from models.data_models import Pack, Card, Coach, Tournament, TournamentSignups, Transaction
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

    BUDGET_COMBOS = [
        {"roll":0.4, "rarities":["Rare","Common","Common","Common","Common"]},
        {"roll":0.6, "rarities":["Rare","Rare","Common","Common","Common"]},
        {"roll":0.7, "rarities":["Epic","Common","Common","Common","Common"]},
        {"roll":0.8, "rarities":["Rare","Rare","Rare","Common","Common"]},
        {"roll":0.85, "rarities":["Epic","Rare","Common","Common","Common"]},
        {"roll":0.9, "rarities":["Rare","Rare","Rare","Rare","Common"]},
        {"roll":0.925, "rarities":["Epic","Rare","Rare","Common","Common"]},
        {"roll":0.95, "rarities":["Epic","Epic","Common","Common","Common"]},
        {"roll":0.975, "rarities":["Legendary","Common","Common","Common","Common"]},
        {"roll":0.98125, "rarities":["Rare","Rare","Rare","Rare","Rare"]},
        {"roll":0.9875, "rarities":["Epic","Rare","Rare","Rare","Common"]},
        {"roll":0.99375, "rarities":["Epic","Epic","Rare","Common","Common"]},
        {"roll":1, "rarities":["Epic","Rare","Common","Common","Common"]},
    ]

    PREMIUM_COMBOS = [
        {"roll":0.25, "rarities":["Rare","Rare","Rare","Rare","Rare"]},
        {"roll":0.5, "rarities":["Epic","Rare","Rare","Rare","Rare"]},
        {"roll":0.65, "rarities":["Epic","Epic","Rare","Rare","Rare"]},
        {"roll":0.75, "rarities":["Epic","Epic","Epic","Rare","Rare"]},
        {"roll":0.85, "rarities":["Legendary","Rare","Rare","Rare","Rare"]},
        {"roll":0.9, "rarities":["Epic","Epic","Epic","Epic","Rare"]},
        {"roll":0.95, "rarities":["Legendary","Epic","Rare","Rare","Rare"]},
        {"roll":0.97, "rarities":["Epic","Epic","Epic","Epic","Epic"]},
        {"roll":0.99, "rarities":["Legendary","Epic","Epic","Rare","Rare"]},
        {"roll":1, "rarities":["Legendary","Epic","Epic","Epic","Rare"]},
    ]

    TRAINING_COMBOS = [
        {"roll":0.4, "rarities":["Rare","Common","Common"]},
        {"roll":0.6, "rarities":["Rare","Rare","Common"]},
        {"roll":0.8, "rarities":["Epic","Common","Common"]},
        {"roll":0.89, "rarities":["Rare","Rare","Rare"]},
        {"roll":0.98, "rarities":["Epic","Rare","Common"]},
        {"roll":1, "rarities":["Epic","Rare","Rare"]},
    ]

    PLAYER_COMBOS = [
        {"roll":0.35, "rarities":["Rare","Rare","Rare"]},
        {"roll":0.6, "rarities":["Epic","Rare","Rare"]},
        {"roll":0.8, "rarities":["Epic","Epic","Rare"]},
        {"roll":0.875, "rarities":["Epic","Epic","Epic"]},
        {"roll":0.95, "rarities":["Legendary","Rare","Rare"]},
        {"roll":0.99, "rarities":["Legendary","Epic","Rare"]},
        {"roll":1, "rarities":["Legendary","Epic","Epic"]},
    ]

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
        else:
            if ptype == "player":
                combos = cls.PLAYER_COMBOS
            elif ptype == "training":
                combos = cls.TRAINING_COMBOS
            elif ptype == "booster_premium":
                combos = cls.PREMIUM_COMBOS
            else:
                combos = cls.BUDGET_COMBOS

            roll = random.random()
            rarities = [combo for combo in combos if combo['roll']>=roll][0]['rarities']
            for rarity in rarities:
                if ptype == "player":
                    races = cls.team_by_code(team)["races"]
                    fcards = cls.filter_cards(rarity,"Player",races)
                elif ptype == "training":
                    fcards = cls.filter_cards(rarity,"Training")
                else:
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
    def init_dict_from_card(cls,card):
        return {
            "name":card["Card Name"],
            "rarity":card["Rarity"],
            "race":card["Race"],
            "description":card["Description"],
            "card_type":card["Type"],
            "subtype":card["Subtype"],
            "notes":card["Notes"] if hasattr(card, "Notes") else "",
        }

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
            "discord_channel":tournament["Scheduling Room"],
            "type":tournament["Tournament Type"],
            "mode":tournament["Tournament Mode"],
            "signup_close_date":tournament["Signup Close Date"].replace('\x92',' '),
            "expected_start_date":tournament["Expected Start Date"].replace('\x92',' '),
            "expected_end_date":tournament["Expected End Date"].replace('\x92',' '),
            "deadline_date":tournament["Tournament Deadline"].replace('\x92',' '),
            "fee":int(tournament["Entrance Fee"]),
            "status":tournament["Status"],
            "coach_limit":int(tournament["Coach Count Limit"]),
            "reserve_limit":int(tournament["Reserve Count Limit"]),
            "region":tournament["Region Bias"],
            "deck_limit":int(tournament["Deck Size Limit"]),
            "admin":tournament["Tournament Admin"],
            "sponsor":tournament["Tournament Sponsor"],
            "special_rules":tournament["Special Rules"],
            "prizes":tournament["Prizes"],
        }

    @classmethod
    def register(cls,tournament,coach):
        # check for status
        if tournament.status != "OPEN":
            raise RegistrationError(f"Tournamnent {tournament.name} signups are not open!!!")
        # check if coach is not registered
        ts = TournamentSignups.query.filter_by(tournament_id= tournament.id, coach_id = coach.id).all()
        if len(ts)>0:
            raise RegistrationError(f"Coach {coach.short_name()} is already registered to {tournament.name}!!!")
        
        # check if the coach is not signed to multiple tournaments,  only exception is FastTrack and Boot/Regular for Development

        if tournament.type=="Imperium":
            ts = coach.tournaments.filter_by(type="Imperium").all()
            if len(ts)>0:
                raise RegistrationError(f"You cannot be registered to more than 1 Imperium tournament!!!")
        else:
            ts = coach.tournaments.filter(Tournament.type!="Imperium").all()
            if len(ts)>1:
                raise RegistrationError(f"You cannot be registered to more than 2 Development tournaments!!!")
            if len(ts)==1:
                etour = ts[0]
                if etour.type == "Development" and tournament.type == "Development":
                    if not ((etour.mode=="Boot Camp" or etour.mode=="Regular") and tournament.mode=="Fast-Track") and not ((tournament.mode=="Boot Camp" or tournament.mode=="Regular") and etour.mode=="Fast-Track"):
                        raise RegistrationError(f"You cannot be registered to {tournament.mode} tournament and {etour.mode} tournament at the same time!!!")    
                else:
                    raise RegistrationError(f"You cannot be registered to {tournament.type} tournament and {etour.type} tournament at the same time!!!")
        
        # check for free slots
        signups = tournament.coaches.filter(TournamentSignups.mode != 'reserve').all()
        reserves = tournament.coaches.filter(TournamentSignups.mode == 'reserve').all()
        if len(signups) == tournament.coach_limit:
            if len(reserves) == tournament.reserve_limit:
                raise RegistrationError(f"{tournament.name} is full !!!")
            else:
                register_as = "reserve"
        else:
            register_as = None

        # tournament is open, has free slot and coach is not signed to it yet
        try:
            signup = TournamentSignups(mode=register_as)
            signup.coach = coach
            signup.tournament = tournament
            db.session.add(signup)
            db.session.commit()
        except Exception as e:
            raise RegistrationError(str(e))
        
        return signup

    @classmethod
    def unregister(cls,tournament,coach):
        # check for status
        if tournament.status not in ["OPEN","FINISHED"]:
            raise RegistrationError(f"You cannot resign from running tournament!!!")
        # check if coach is registered
        ts = TournamentSignups.query.filter_by(tournament_id= tournament.id, coach_id = coach.id).all()
        if len(ts)<1:
            raise RegistrationError(f"Coach {coach.short_name()} is not registered to {tournament.name}!!!")

        try:
            db.session.delete(ts[0])
            db.session.commit()
        except Exception as e:
            raise RegistrationError(str(e))

        return True
        

class RegistrationError(Exception):
    pass

class InvalidTeam(Exception):
    pass

class InvalidQuality(Exception):
    pass

class InvalidPackType(Exception):
    pass