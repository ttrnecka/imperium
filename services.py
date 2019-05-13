from models.base_model import db
from models.data_models import Pack, Card, Coach, Tournament, TournamentSignups, Transaction, Duster, Deck
from imperiumbase import ImperiumSheet
from sqlalchemy.orm import joinedload
from sqlalchemy import asc
import random
import requests
import time
from sqlalchemy.orm.attributes import flag_modified
from models.marsh_models import card_schema

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
        "booster_budget": 10,
        "booster_premium": 20,
        "player": 0,
        "training": 0,
        "starter": 0,
        "special":0,
        "positional":0,
        "coaching":0,
        "skill":0,
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
        {"roll":1, "rarities":["Legendary","Rare","Common","Common","Common"]},
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

    SKILL_COMBOS = [
        {"roll":0.27, "rarities":["Rare","Rare","Common","Common","Common"]},
        {"roll":0.54, "rarities":["Epic","Common","Common","Common","Common"]},
        {"roll":0.68, "rarities":["Rare","Rare","Rare","Common","Common"]},
        {"roll":0.82, "rarities":["Epic","Rare","Common","Common","Common"]},
        {"roll":0.87, "rarities":["Rare","Rare","Rare","Rare","Common"]},
        {"roll":0.92, "rarities":["Epic","Rare","Rare","Common","Common"]},
        {"roll":0.97, "rarities":["Epic","Epic","Common","Common","Common"]},
        {"roll":0.98, "rarities":["Rare","Rare","Rare","Rare","Rare"]},
        {"roll":0.99, "rarities":["Epic","Rare","Rare","Rare","Common"]},
        {"roll":1, "rarities":["Epic","Epic","Rare","Common","Common"]},
    ]

    COACHING_COMBOS = [
        {"roll":0.55, "rarities":["Rare","Rare","Rare"]},
        {"roll":0.8, "rarities":["Epic","Rare","Rare"]},
        {"roll":0.95, "rarities":["Epic","Epic","Rare"]},
        {"roll":1, "rarities":["Epic","Epic","Epic"]},
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

    PLAYER_FIRST_COMBOS = [
        {"roll":0.6, "rarities":["Epic","Rare","Rare"]},
        {"roll":0.8, "rarities":["Epic","Epic","Rare"]},
        {"roll":0.875, "rarities":["Epic","Epic","Epic"]},
        {"roll":0.95, "rarities":["Legendary","Rare","Rare"]},
        {"roll":0.99, "rarities":["Legendary","Epic","Rare"]},
        {"roll":1, "rarities":["Legendary","Epic","Epic"]},
    ]

    @classmethod
    def filter_cards(cls,rarity,ctype=None,races=None,subtype=None):
        if subtype is not None:
            return [card for card in ImperiumSheet.cards() if card["Rarity"]==rarity and card["Type"]==ctype and card["Race"] in races and card["Subtype"]==subtype]
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
    def generate(cls,ptype="booster_budget",team = None, first = False):
        if ptype not in cls.PACK_PRICES:
            raise InvalidPackType(ptype)

        if team is not None and team not in cls.team_codes():
            raise InvalidTeam(team)

        if ptype in ["player","positional"]:
            if not team:
                raise  ValueError(f"Missing team value for {ptype} pack")
            elif team.lower() not in cls.team_codes():
                raise  ValueError(f"Team {team} unknown")
            else:
                team = team.lower()
        price = cls.PACK_PRICES[ptype]

        pack = Pack(price=price,pack_type=ptype, team=team)
        cards = []
        if ptype == "starter":
            cards.extend(ImperiumSheet.starter_cards())
        else:
            if ptype in ["player","positional"]:
                combos = cls.PLAYER_COMBOS
                if first:
                    combos = cls.PLAYER_FIRST_COMBOS
            elif ptype in ["training","special"]:
                combos = cls.TRAINING_COMBOS
            elif ptype == "coaching":
                combos = cls.COACHING_COMBOS
            elif ptype == "skill":
                combos = cls.SKILL_COMBOS
            elif ptype == "booster_premium":
                combos = cls.PREMIUM_COMBOS
            else:
                combos = cls.BUDGET_COMBOS

            roll = random.random()
            rarities = [combo for combo in combos if combo['roll']>=roll][0]['rarities']
            for rarity in rarities:
                if ptype in ["player","positional"]:
                    races = cls.team_by_code(team)["races"]
                    subtype = "Positional" if ptype=="positional" else None
                    fcards = cls.filter_cards(rarity,"Player",races,subtype)
                elif ptype in ["training","skill","coaching"]:
                    fcards = cls.filter_cards(rarity,"Training")
                elif ptype == "special":
                    fcards = cls.filter_cards(rarity,"Special Play")
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
            value = int(card["Card Value"]) if "Card Value" in card and RepresentsInt(card["Card Value"]) else 0,
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
            "value":int(card["Card Value"]) if "Card Value" in card and RepresentsInt(card["Card Value"]) else 0,
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
            "Card Value": card.value,
            "Notes": card.notes
        }

    # return card from sheet in dict format, name must be exact match, case insensitive
    @classmethod
    def get_card_from_sheet(cls,name):
        name_low = name.lower()
        for card in ImperiumSheet.cards():
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

    @classmethod
    def get_undusted_Card_from_coach(cls,coach,name):
        cards = Card.query.join(Card.coach).filter(Coach.id == coach.id, Card.name == name, Card.duster_id == None).all()

        if len(cards)==0:
            return None
        else:
            return cards[0]

    @classmethod
    def get_dusted_Card_from_coach(cls,coach,name):
        cards = Card.query.join(Card.coach).filter(Coach.id == coach.id, Card.name == name, Card.duster_id != None).all()

        if len(cards)==0:
            return None
        else:
            return cards[0]

    @classmethod
    def update(cls):
        for card in ImperiumSheet.cards(True):
            c_dict = cls.init_dict_from_card(card)
            cards = Card.query.filter_by(name = c_dict['name']).all()

            for scard in cards:
                scard.update(**c_dict)

        db.session.commit()



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

    @classmethod
    def get_starter_cards(cls,coach):
        used_starter_cards = DeckService.get_used_starter_cards(coach)
        starter_cards = PackService.generate("starter").cards

        for card in used_starter_cards:
            ctype  = "in_development_deck" if card['in_development_deck']==True else "in_imperium_deck"
            g = (i for i, acard in enumerate(starter_cards) if getattr(acard,ctype)!=True and acard.name==card['name'])
            index = next(g)
            setattr(starter_cards[index],ctype,True)

        print(starter_cards)
        return starter_cards

class NotificationService:
    notificators = []

    @classmethod
    def notify(cls,msg):
        for notificator in cls.notificators:
            notificator(msg)

    @classmethod
    def register_notifier(cls,func):
        cls.notificators.append(func)

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
            "unique_prize":tournament["Unique Prize"],
            "sponsor_description":tournament["Sponsor Description"],
        }

    @classmethod
    def update(cls):
        for tournament in ImperiumSheet.tournaments():
            t_dict = cls.init_dict_from_tournament(tournament)
            t = Tournament.query.filter_by(tournament_id = t_dict['tournament_id']).all()
            if len(t)==0:
                T = Tournament()
                db.session.add(T)
            else:
                T = t[0]
            T.update(**t_dict)

        db.session.commit()

    @classmethod
    def update_signups(cls,tournament):
        updated = []
        signups = tournament.coaches.filter(TournamentSignups.mode != 'reserve').all()
        reserves = tournament.coaches.filter(TournamentSignups.mode == 'reserve').order_by(asc(TournamentSignups.date_created)).all()

        while len(signups) < tournament.coach_limit and len(reserves) > 0:
            updated.append(cls.move_from_reserve_to_active(tournament,reserves[0]))
            signups = tournament.coaches.filter(TournamentSignups.mode != 'reserve').all()
            reserves = tournament.coaches.filter(TournamentSignups.mode == 'reserve').order_by(asc(TournamentSignups.date_created)).all()
        return updated

    @classmethod
    def move_from_reserve_to_active(cls,tournament,coach):
        ts = TournamentSignups.query.filter_by(tournament_id= tournament.id, coach_id = coach.id).all()
        if len(ts)==0:
            raise RegistrationError(f"Coach {coach.short_name()} is not RESERVE in {tournament.name}!!!")
        if ts[0].mode!="reserve":
            raise RegistrationError(f"Coach {coach.short_name()} is not RESERVE in {tournament.name}!!!")

        ts[0].mode = "active"
        db.session.commit()
        return ts[0]

    @classmethod
    def register(cls,tournament,coach,admin=False):
        # check for status
        if tournament.status != "OPEN" and not admin:
            raise RegistrationError(f"Tournamnent {tournament.name} signups are not open!!!")
        # check if coach is not registered
        ts = TournamentSignups.query.filter_by(tournament_id= tournament.id, coach_id = coach.id).all()
        if len(ts)>0:
            raise RegistrationError(f"Coach {coach.short_name()} is already registered to {tournament.name}!!!")

        # check if the coach is not signed to multiple tournaments,  only exception is FastTrack Dev and Boot/Regular Development

        if tournament.type=="Imperium":
            ts = coach.tournaments.filter_by(type="Imperium").all()
            if len(ts)>0:
                raise RegistrationError(f"Coach cannot be registered to more than 1 Imperium tournament!!!")
        else:
            ts = coach.tournaments.filter(Tournament.type!="Imperium").all()
            if len(ts)>1:
                raise RegistrationError(f"Coach cannot be registered to more than 2 Development tournaments!!!")
            if len(ts)==1:
                etour = ts[0]
                if not ((etour.mode=="Boot Camp" or etour.mode=="Regular") and tournament.mode=="Fast-Track") and not ((tournament.mode=="Boot Camp" or tournament.mode=="Regular") and etour.mode=="Fast-Track"):
                    raise RegistrationError(f"Coach cannot be registered to {tournament.type} {tournament.mode} tournament and {etour.type} {etour.mode} tournament at the same time!!!")

        # check for free slots
        signups = tournament.coaches.filter(TournamentSignups.mode != 'reserve').all()
        reserves = tournament.coaches.filter(TournamentSignups.mode == 'reserve').all()
        if len(signups) == tournament.coach_limit:
            if len(reserves) == tournament.reserve_limit:
                raise RegistrationError(f"{tournament.name} is full !!!")
            else:
                register_as = "reserve"
        else:
            register_as = "active"

        # tournament is open, has free slot and coach is not signed to it yet
        try:
            signup = TournamentSignups(mode=register_as)
            signup.coach = coach
            signup.tournament = tournament
            db.session.add(signup)

            reason = f"{tournament.name} signup - cost {tournament.fee} coins"
            t = Transaction(description=reason,price=tournament.fee)
            coach.make_transaction(t)

            # deck
            deck = Deck(team_name="",mixed_team="", tournament_signup = signup, extra_cards = [], unused_extra_cards = [], starter_cards = [])
            db.session.add(deck)
            
            db.session.commit()
            if tournament.fee>0:
                coach_mention=f'<@{coach.disc_id}>'
            else:
                coach_mention=coach.short_name()

            NotificationService.notify(f'{coach_mention} successfuly signed to {tournament.id}. {tournament.name} - fee {tournament.fee} coins')
        except Exception as e:
            raise RegistrationError(str(e))

        return signup

    @classmethod
    def unregister(cls,tournament,coach,admin=False,refund=True):
        # check for status
        if tournament.status not in ["OPEN","FINISHED"] and not admin:
            raise RegistrationError(f"Coach cannot resign from running tournament!!!")
        # check if coach is registered
        ts = TournamentSignups.query.filter_by(tournament_id= tournament.id, coach_id = coach.id).all()
        if len(ts)<1:
            raise RegistrationError(f"Coach {coach.short_name()} is not registered to {tournament.name}!!!")

        try:
            for card in ts[0].deck.cards:
                if tournament.type=="Development":
                    card.in_development_deck = False
                else:
                    card.in_imperium_deck = False

            db.session.delete(ts[0])
        
            if refund:
                reason = f"{tournament.name} resignation - refund {tournament.fee} coins"
                t = Transaction(description=reason,price=-1*tournament.fee)
                coach.make_transaction(t)

            db.session.commit()

            if refund and tournament.fee>0:
                coach_mention=f'<@{coach.disc_id}>'
                fee_msg = f" - refund {tournament.fee} coins"
            else:
                coach_mention=coach.short_name()
                fee_msg=""

            NotificationService.notify(f'{coach_mention} successfuly resigned from {tournament.id}. {tournament.name}{fee_msg}')
        except Exception as e:
            raise RegistrationError(str(e))

        return True

class DusterService:
    @classmethod
    def get_duster(cls,coach):
        duster = coach.duster
        if not duster:
            duster = Duster()
            coach.duster=duster
        return duster

    @classmethod
    def dust_card(cls,duster,card):
        if len(duster.cards)==0:
            if card.card_type=="Player":
                duster.type = "Tryouts"
            else:
                duster.type = "Drills"
        duster.cards.append(card)
        db.session.commit()
    
    @classmethod
    def check_and_dust(cls,coach,card):
        if card.coach.id != coach.id:
            raise DustingError("Coach ID mismatch!!!")
        duster = cls.get_duster(coach)
        if duster.status!="OPEN":
            raise DustingError(f"Dusting has been already committed, please generate the pack before dusting again")
        if len(duster.cards)==10:
            raise DustingError(f"Card **{card.name}** - cannot be dusted, duster is full")
        if duster.type=="Tryouts" and card.card_type!="Player":
            raise DustingError(f"Card **{card.name}** - cannot be used in {duster.type}")
        if duster.type=="Drills" and card.card_type=="Player":
            raise DustingError(f"Card **{card.name}** - cannot be used in {duster.type}")

        cls.dust_card(duster,card)
        return f"Card **{card.name}** - flagged for dusting"

    @classmethod
    def check_and_undust(cls,coach,card):
        if card.coach.id != coach.id:
            raise DustingError("Coach ID mismatch!!!")

        card.duster_id = None
        db.session.commit()
        return f"Card **{card.name}** - dusting flag removed"

    @classmethod
    def dust_card_by_name(cls,coach,card_name):
        card=CardService.get_undusted_Card_from_coach(coach,card_name)
        if card is None:
            raise DustingError(f"Card **{card_name}** - not found, check spelling, or maybe it is already dusted")
        return cls.check_and_dust(coach,card)

    @classmethod
    def undust_card_by_name(cls,coach,card_name):
        card=CardService.get_dusted_Card_from_coach(coach,card_name)
        if card is None:
            raise DustingError(f"Card **{card_name}** - not flagged for dusting")
        return cls.check_and_undust(coach,card)

    @classmethod
    def dust_card_by_id(cls,coach,card_id):
        card=Card.query.get(card_id)
        if card is None:
            raise DustingError(f"Card not found") 
        if card.duster_id is not None:
            raise DustingError(f"Card **{card.name}** is already flagged for dusting")     
        return cls.check_and_dust(coach,card)

    @classmethod
    def undust_card_by_id(cls,coach,card_id):
        card=Card.query.get(card_id)
        if card is None:
            raise DustingError(f"Card not found") 
        if card.duster_id is None:
            raise DustingError(f"Card **{card.name}** is not flagged for dusting")  
        return cls.check_and_undust(coach,card)

    @classmethod
    def cancel_duster(cls,coach):
        duster = cls.get_duster(coach)
        if duster.status!="OPEN":
            raise DustingError(f"Cannot cancel dusting. It has been already committed.")
        db.session.delete(coach.duster)
        db.session.commit()

    @classmethod
    def commit_duster(cls,coach):
        duster = cls.get_duster(coach)
        if len(duster.cards)<10:
            raise DustingError("Not enough cards flagged for dusting. Need 10!!!")

        reason = f"{duster.type}: {';'.join([card.name for card in duster.cards])}"
        t = Transaction(description=reason,price=0)
        cards = duster.cards
        for card in cards:
            db.session.delete(card)
        duster.status="COMMITTED"
        coach.make_transaction(t)
        NotificationService.notify(f"<@{coach.disc_id}>: Card(s) **{' ,'.join([card.name for card in cards])}** removed from your collection by {duster.type}")
        return True

class TransactionService:
    @classmethod
    def process(cls,coach,amount,reason):
        t = Transaction(description=reason,price=amount)
        coach.make_transaction(t)
        NotificationService.notify(f"<@{coach.disc_id}>: Your bank has been updated by **{-1*amount}** coins - {reason}")
        return True
 
class DeckService:
    @classmethod
    def update(cls,deck,deck_params):
        deck.update(**cls.init_dict_from_params(deck_params))
        db.session.commit()

        return deck

    @classmethod
    def init_dict_from_params(cls,params):
        return {
            "team_name":params["team_name"],
            "mixed_team":params["mixed_team"],
        }
    
    @classmethod
    def deck_type(cls,deck):
        return deck.tournament_signup.tournament.type

    @classmethod
    def addextracard(cls,deck,name):
        card = CardService.get_card_from_sheet(name)

        if card:
            cCard= CardService.init_Card_from_card(CardService.get_card_from_sheet(name))
            cCard.deck_type = "extra"
            deck.unused_extra_cards.append(card_schema.dump(cCard).data)
            flag_modified(deck, "unused_extra_cards")
            db.session.commit()
            return deck
        else:
            raise DeckError(f"Card {name} does not exist")
    
    @classmethod
    def removeextracard(cls,deck,name):
        card = CardService.get_card_from_sheet(name)
        if card:
            deck.unused_extra_cards.remove(card_schema.dump(CardService.init_Card_from_card(card)).data)
            flag_modified(deck, "unused_extra_cards")
            db.session.commit()
            return deck
        else:
            raise DeckError(f"Card {name} does not exist")

    @classmethod
    def addcard(cls,deck,card):
        if card["id"]:
            cCard = Card.query.get(card["id"])
            if cCard is not None:
                if deck in cCard.decks:
                    raise DeckError("Card is already in the deck")
                else:
                    if cls.deck_type(deck)=="Development":
                        cCard.in_development_deck = True
                    else:
                        cCard.in_imperium_deck = True

                    deck.cards.append(cCard)
                    db.session.commit()
            else:
                raise DeckError("Card not found")
        else:
            # add starting pack handling
            if card["deck_type"]=="base":
                if cls.deck_type(deck)=="Development":
                    card['in_development_deck'] = True
                else:
                    card['in_imperium_deck'] = True
                deck.starter_cards.append(card)
                flag_modified(deck, "starter_cards")
            else:
                #extra cards
                if card in deck.unused_extra_cards:
                    deck.unused_extra_cards.remove(card)
                    if cls.deck_type(deck)=="Development":
                        card['in_development_deck'] = True
                    else:
                        card['in_imperium_deck'] = True
                    deck.extra_cards.append(card)
                    deck.unused_extra_cards.append(card)
                    flag_modified(deck, "extra_cards")
                    flag_modified(deck, "unused_extra_cards")
                else:
                    raise DeckError("Extra card not found")
            db.session.commit()
        return deck

    @classmethod
    def removecard(cls,deck,card):
        if card["id"]:
            cCard = Card.query.get(card["id"])
            if cCard:
                if deck in cCard.decks:
                    if cls.deck_type(deck)=="Development":
                        cCard.in_development_deck = False
                    else:
                        cCard.in_imperium_deck = False
                        
                    deck.cards.remove(cCard)
                    db.session.commit()
                else:
                    raise DeckError("Card is not in the deck")
            else:
                    raise DeckError("Card not found")
        else:
            # remove starting pack handling
            if card["deck_type"]=="base":
                deck.starter_cards.remove(card)
                flag_modified(deck, "starter_cards")
            else:
                #extra cards
                if card in deck.unused_extra_cards:
                    deck.unused_extra_cards.remove(card)
                    deck.extra_cards.remove(card)
                    if cls.deck_type(deck)=="Development":
                        card['in_development_deck'] = False
                    else:
                        card['in_imperium_deck'] = False
                    deck.unused_extra_cards.append(card)
                    flag_modified(deck, "extra_cards")
                    flag_modified(deck, "unused_extra_cards")
                else:
                    raise DeckError("Extra card not found")
            db.session.commit()
        return deck

    @classmethod
    def get_used_starter_cards(cls,coach):
        decks = [ts.deck for ts in coach.tournament_signups]
        return sum([deck.starter_cards for deck in decks ],[])

class DeckError(Exception):
    pass

class DustingError(Exception):
    pass

class RegistrationError(Exception):
    pass

class InvalidTeam(Exception):
    pass

class InvalidQuality(Exception):
    pass

class InvalidPackType(Exception):
    pass

class WebHook:
    def __init__(self,webhook):
        self.webhook = webhook

    def send(self,msg):
        status_code = 429
        # 429 means rate limited
        while status_code == 429:
            r = requests.post(self.webhook, json={'content': msg})
            status_code = r.status_code
            # rate limited
            if status_code==429:
                wait_for_ms = int(r.json()['retry_after'])
                time.sleep(wait_for_ms/1000)

def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False