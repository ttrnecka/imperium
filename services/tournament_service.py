"""TournamentService helpers"""
import itertools
from datetime import date, timedelta
import random

from sqlalchemy import asc, func
from models.data_models import Tournament, TournamentSignups, Transaction, Deck, Coach, Card, TournamentTemplate, TournamentAdmin
from models.data_models import TournamentSponsor, TournamentRoom, ConclaveRule
from models.base_model import db
from .notification_service import NotificationService, AdminNotificationService
from .imperium_sheet_service import ImperiumSheetService
from .deck_service import DeckService
from .conclave_service import ConclaveService
from .coach_service import CoachService

class RegistrationError(Exception):
    """Exception to raise for tournament registration issues"""

class TournamentError(Exception):
    """Exception to raise for tournament registration issues"""

class TournamentService:
    """Nampespace for Tournament helpers"""
    @classmethod
    def init_dict_from_tournament(cls, tournament):
        """import sheet tournament line into dict to update the Tournament record"""
        return {
            "tournament_id":int(tournament["Tournament ID"]),
            "name":tournament["Tournament Name"],
            "discord_channel":tournament["Scheduling Room"],
            "type":tournament["Tournament Type"],
            "mode":tournament["Tournament Mode"],
            "signup_close_date":tournament["Signup Close Date"].replace('\x92', ' '),
            "expected_start_date":tournament["Expected Start Date"].replace('\x92', ' '),
            "expected_end_date":tournament["Expected End Date"].replace('\x92', ' '),
            "deadline_date":tournament["Tournament Deadline"].replace('\x92', ' '),
            "fee":int(tournament["Entrance Fee"]),
            "status":tournament["Status"],
            "coach_limit":int(tournament["Coach Count Limit"]),
            "reserve_limit":int(tournament["Reserve Count Limit"]),
            "region":tournament["Region Bias"],
            "deck_limit":int(tournament["Deck Size Limit"]),
            "deck_value_limit":int(tournament["Deck Value Limit"]) if tournament["Deck Value Limit"] else 150,
            "admin":tournament["Tournament Admin"],
            "sponsor":tournament["Tournament Sponsor"],
            "special_rules":tournament["Special Rules"],
            "prizes":tournament["Prizes"],
            "unique_prize":tournament["Unique Prize"],
            "sponsor_description":tournament["Sponsor Description"],
            "conclave_triggers":tournament["Conclave Triggers"]
        }

    @classmethod
    def tournament_to_dict(cls, tournament):
        """Change Tournament to tournament dict to update in sheet"""
        return {
            "Tournament ID": tournament.tournament_id,
            "Tournament Name": tournament.name,
            "Scheduling Room": tournament.discord_channel,
            "Signup Close Date": tournament.signup_close_date,
            "Expected Start Date": tournament.expected_start_date,
            "Expected End Date": tournament.expected_end_date,
            "Tournament Type": tournament.type,
            "Tournament Mode": tournament.mode,
            "Tournament Deadline": tournament.deadline_date,
            "Entrance Fee": tournament.fee,
            "Status": tournament.status,
            "Coach Count Limit": tournament.coach_limit,
            "Reserve Count Limit": tournament.reserve_limit,
            "Region Bias": tournament.region,
            "Deck Size Limit": tournament.deck_limit,
            "Deck Value Limit": tournament.deck_value_limit,
            "Tournament Admin": tournament.admin,
            "Tournament Sponsor": tournament.sponsor,
            "Sponsor Description": tournament.sponsor_description,
            "Special Rules": tournament.special_rules,
            "Prizes": tournament.prizes,
            "Unique Prize": tournament.unique_prize,
            "Conclave Triggers": tournament.conclave_triggers
        }

    @classmethod
    def init_dict_from_tournament_template(cls, template):
        """import sheet tournament template line into dict to update the TournamentTemplate record"""
        return {
            "active":int(template["Active"]),
            "type":template["Tournament Type"],
            "mode":template["Tournament Mode"],
            "coach_limit":int(template["Coach Count Limit"]),
            "deck_limit":int(template["Deck Size Limit"]),
            "deck_value_limit":int(template["Deck Value Limit"]) if template["Deck Value Limit"] else 150,
            "prizes":template["Prizes"]
        }

    @classmethod
    def init_dict_from_tournament_admin(cls, admin):
        """import sheet tournament admin line into dict to update the TournamentAdmin record"""
        return {
            "name":admin["Name"],
            "region":admin["Region Bias"],
            "load":int(admin["Load"]),
            "tournament_types":admin["Tournament Types"]
        }

    @classmethod
    def init_dict_from_tournament_sponsor(cls, sponsor):
        """import sheet tournament sponsor line into dict to update the TournamentSponsor record"""
        return {
            "name":sponsor["Sponsor"],
            "effect":sponsor["Effect"],
            "skill_pack_granted":sponsor["Skill Pack Granted"],
            "special_rules":sponsor["Special Rules"]
        }

    @classmethod
    def init_dict_from_tournament_room(cls, room):
        """import sheet tournament room line into dict to update the TournamentRoom record"""
        return {
            "name":room["Name"],
            "region":room["Region Bias"]
        }
    
    @classmethod
    def init_dict_from_conclave_rule(cls, rule):
        """import sheet tournament room line into dict to update the TournamentRoom record"""
        return {
            "type":rule["Type"],
            "name":rule["Name"],
            "description":rule["Description"],
            "level1":int(rule["Trigger 1"]),
            "level1_description":rule["Level 1 Description"],
            "level2":int(rule["Trigger 2"]),
            "level2_description":rule["Level 2 Description"],
            "level3":int(rule["Trigger 3"]),
            "level3_description":rule["Level 3 Description"],
            "notes":rule["Notes"]
        }

    @classmethod
    def update(cls):
        cls.update_templates()
        cls.update_admins()
        cls.update_sponsors()
        cls.update_rooms()
        cls.update_conclave()
        # update tournaments first to reflect any closings
        cls.update_tournaments()
        # check if new tournamnets have to be opened
        cls.init_new_tournaments()
        # update the sheet again
        cls.update_tournaments()

    @classmethod
    def update_tournaments(cls):
        """Updates tournaments from sheet into DB"""
        for tournament in ImperiumSheetService.tournaments():
            t_dict = cls.init_dict_from_tournament(tournament)
            tourns = Tournament.query.filter_by(tournament_id=t_dict['tournament_id']).all()
            if not tourns:
                tourn = Tournament()
                db.session.add(tourn)
            else:
                tourn = tourns[0]
            tourn.update(**t_dict)

        db.session.commit()

    @classmethod
    def update_conclave(cls):
        """Updates conclave rules from sheet into DB"""
        for rule in ImperiumSheetService.conclave_rules():
            r_dict = cls.init_dict_from_conclave_rule(rule)
            d_rule = ConclaveRule.query.filter_by(name=r_dict['name']).one_or_none()
            if not d_rule:
                d_rule = ConclaveRule()
                db.session.add(d_rule)

            d_rule.update(**r_dict)

        db.session.commit()

    @classmethod
    def update_templates(cls):
        """Updates tournament templates from sheet into DB"""
        cls.update_table(TournamentTemplate,ImperiumSheetService.tournament_templates(),cls.init_dict_from_tournament_template)

    @classmethod
    def update_admins(cls):
        """Updates admins from sheet into DB"""
        cls.update_table(TournamentAdmin,ImperiumSheetService.admins(),cls.init_dict_from_tournament_admin)

    @classmethod
    def update_sponsors(cls):
        """Updates sponsors from sheet into DB"""
        cls.update_table(TournamentSponsor,ImperiumSheetService.sponsors(),cls.init_dict_from_tournament_sponsor)

    @classmethod
    def update_rooms(cls):
        """Updates rooms from sheet into DB"""
        cls.update_table(TournamentRoom,ImperiumSheetService.rooms(),cls.init_dict_from_tournament_room)
        
    @classmethod
    def update_table(cls, table, data, transfer_func):
        table.query.delete()
        for template in data:
            r_dict = transfer_func(template)
            item = table()
            db.session.add(item)
            item.update(**r_dict)

        db.session.commit()

    @classmethod
    def update_signups(cls, tournament):
        """Moves reserve signups to active if possible"""
        updated = []
        signups = tournament.coaches.filter(TournamentSignups.mode != 'reserve').all()
        reserves = tournament.coaches.filter(TournamentSignups.mode == 'reserve') \
            .order_by(asc(TournamentSignups.date_created)).all()

        while len(signups) < tournament.coach_limit and reserves:
            updated.append(cls.move_from_reserve_to_active(tournament, reserves[0]))
            signups = tournament.coaches.filter(TournamentSignups.mode != 'reserve').all()
            reserves = tournament.coaches.filter(TournamentSignups.mode == 'reserve') \
                .order_by(asc(TournamentSignups.date_created)).all()
        return updated

    @classmethod
    def move_from_reserve_to_active(cls, tournament, coach):
        """Move coach from reserve to active signup"""
        singups = TournamentSignups.query.filter_by(
            tournament_id=tournament.id, coach_id=coach.id).all()
        if not singups:
            raise RegistrationError(
                f"Coach {coach.short_name()} is not RESERVE in {tournament.name}!!!")
        if singups[0].mode != "reserve":
            raise RegistrationError(
                f"Coach {coach.short_name()} is not RESERVE in {tournament.name}!!!")

        singups[0].mode = "active"
        db.session.commit()
        return singups[0]

    @classmethod
    def register(cls, tournament, coach, admin=False):
        """Register coach to tournament, admin flag specifies if admin is doing the action"""
        # check for status
        if tournament.status != "OPEN" and not admin:
            raise RegistrationError(f"Tournamnent {tournament.name} signups are not open!!!")
        # check if coach is not registered
        singups = TournamentSignups.query.filter_by(
            tournament_id=tournament.id, coach_id=coach.id).all()
        if singups:
            raise RegistrationError(
                f"Coach {coach.short_name()} is already registered to {tournament.name}!!!")

        # check if the coach is not signed to multiple tournaments
        # only exception is FastTrack Dev and Boot/Regular Development

        if tournament.type == "Imperium":
            singups = coach.tournaments.filter_by(type="Imperium").all()
            if singups:
                raise RegistrationError(
                    f"Coach cannot be registered to more than 1 Imperium tournament!!!")
        # Dev tournaments limited to 1 for Fast Tracks and 2 for Regulars
        elif tournament.type == "Development":
            if tournament.mode == "Fast Track":
                singups = coach.tournaments.filter(
                    Tournament.type == "Development", Tournament.mode == "Fast Track").all()
                if singups:
                    raise RegistrationError(
                        f"Coach cannot be registered to more than \
                        1 Fast Track Development tournament!!!")
            
            if tournament.mode == "Boot Camp":
                singups = coach.tournaments.filter(
                    Tournament.type == "Development", Tournament.mode == "Regular").all()
                if singups:
                    raise RegistrationError(f"Coach cannot be registered to Boot Camp and Regular Development tournament at the same time!!!")

            if tournament.mode == "Regular":
                singups = coach.tournaments.filter(
                    Tournament.type == "Development", Tournament.mode == "Regular").all()
                if len(singups)>1:
                    raise RegistrationError(f"Coach cannot be registered to more \
                        than 2 Regular Development tournaments!!!")

                singups = coach.tournaments.filter(
                    Tournament.type == "Development", Tournament.mode == "Boot Camp").all()
                if singups:
                    raise RegistrationError(f"Coach cannot be registered to Boot Camp \
                        and Regular Development tournament at the same time!!!")

        # check for free slots
        signups = tournament.coaches.filter(TournamentSignups.mode != 'reserve').all()
        reserves = tournament.coaches.filter(TournamentSignups.mode == 'reserve').all()
        if len(signups) == tournament.coach_limit:
            if len(reserves) == tournament.reserve_limit:
                raise RegistrationError(f"{tournament.name} is full !!!")
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
            tran = Transaction(description=reason, price=tournament.fee)

            # deck
            deck = Deck(team_name="", mixed_team="", tournament_signup=signup,
                        extra_cards=[], unused_extra_cards=[], injury_map = {})
            db.session.add(deck)

            coach.make_transaction(tran)
            # db.session.commit()
            if tournament.fee > 0:
                coach_mention = f'<@{coach.disc_id}>'
                fee_msg = f'Fee: {tournament.fee} coins'
            else:
                coach_mention = coach.short_name()
                fee_msg = ""

            NotificationService.notify(
                f'{coach_mention} successfuly signed to tournament. {fee_msg}'
            )
            # if tournament is full initiate update in extra thread, this will recreate free tournaments if needed
            
            if tournament.is_full():
                AdminNotificationService.notify("!admincomp update")

        except Exception as exc:
            raise RegistrationError(str(exc))

        return signup

    @classmethod
    def unregister(cls, tournament, coach, admin=False, refund=True):
        """
           Unregister coach from tournament, admin flag for admin action,
           refund flag if it should be refunded
        """
        # check for status
        if tournament.status not in ["OPEN", "FINISHED"] and not admin:
            raise RegistrationError(f"Coach cannot resign from running tournament!!!")
        # check if coach is registered
        signups = TournamentSignups.query \
            .filter_by(tournament_id=tournament.id, coach_id=coach.id).all()
        if not signups:
            raise RegistrationError(
                f"Coach {coach.short_name()} is not registered to {tournament.name}!!!")

        try:
            for card in signups[0].deck.cards:
                if tournament.type == "Development":
                    card.in_development_deck = False
                else:
                    card.in_imperium_deck = False

            db.session.delete(signups[0])

            if refund:
                reason = f"{tournament.name} resignation - refund {tournament.fee} coins"
                tran = Transaction(description=reason, price=-1*tournament.fee)
                coach.make_transaction(tran)

            db.session.commit()

            if refund and tournament.fee > 0:
                coach_mention = f'<@{coach.disc_id}>'
                fee_msg = f"Refund: {tournament.fee} coins"
            else:
                coach_mention = coach.short_name()
                fee_msg = ""

            NotificationService.notify(
                f'{coach_mention} successfuly resigned from tournament. {fee_msg}'
            )

        except Exception as exp:
            raise RegistrationError(str(exp))

        return True

    @classmethod
    def release_one_time_cards(cls, tournament):
        cards_list = [ts.deck.cards for ts in tournament.tournament_signups]
        cards = list(itertools.chain.from_iterable(cards_list))

        for card in cards:
            if card.get('one_time_use'):
                coach_mention = card.coach.mention()
                db.session.delete(card)
                db.session.commit()
                NotificationService.notify(
                    f'Card {card.get("name")} removed from {coach_mention} collection - one time use.'
                )

    @classmethod
    def release_reserves(cls,tournament):
        reserves = tournament.coaches.filter(TournamentSignups.mode == 'reserve')
        for coach in reserves:
            cls.unregister(tournament, coach, admin=True, refund=True)
    
    @classmethod
    def release_actives(cls,tournament):
        actives = tournament.coaches.filter(TournamentSignups.mode == 'active')
        for coach in actives:
            cls.unregister(tournament, coach, admin=True, refund=True)

    @classmethod
    def reset_phase(cls, tournament):
        return cls.set_phase(tournament, Tournament.PHASES[0])

    @classmethod
    def set_phase(cls, tournament, phase):
        if phase not in Tournament.PHASES:
            raise TypeError("%s is not correct phase" % phase)
        tournament.phase = phase
        return tournament

    @classmethod
    def next_phase(cls, tournament):
        i = Tournament.PHASES.index(tournament.phase)
        max = len(Tournament.PHASES)
        next = i + 1
        if max > next:
            tournament.phase = Tournament.PHASES[next]

    @classmethod
    def generate_conclave_triggers(cls,tournament):
        triggered_conclave_rules = []
        if not tournament.conclave_triggers:
            for signup in tournament.tournament_signups:
                triggered_conclave_rules.append(ConclaveService.all_triggered(signup.deck))
            #flatten and make it unique
            triggered_conclave_rules = list(set(list(itertools.chain.from_iterable(triggered_conclave_rules))))
            selected_conlave_rules = ConclaveService.select_rules(triggered_conclave_rules)

            tournament.conclave_triggers = ",".join([rule.name for rule in selected_conlave_rules])
            db.session.commit()
            cls.update_tournament_in_sheet(tournament)
        
        rules = [ConclaveRule.query.filter_by(name=tr.strip()).one_or_none() for tr in tournament.conclave_triggers.split(",")]
        rules = list(filter(lambda a: a != None, rules))
        return rules

    @classmethod
    def special_play_msg(cls, tournament):
        rules = cls.generate_conclave_triggers(tournament)
        msg = ["__**Special Play Phase**__:"," "]
        
        decks = []
        max_special_plays = 0

        msg.append("**Conclave rituals in place for this tournament:**")
        for rule in rules:
            msg.append(f"{rule.name} - {rule.description}")
        
        msg.append(" ")
        msg2 = []
        msg2.append("**Blessings & Curses:**")
        
        for signup in tournament.tournament_signups:
            #conclave
            for rule in rules:
                rule_level = ConclaveService.check_trigger(signup.deck, rule.name)
                if rule_level > 0:
                    if rule.type == "Consecration":
                        word = "blessing"
                        if not tournament.conclave_triggered:
                            CoachService.increment_blessings(signup.coach)
                    else:
                        word = "curse"
                        if not tournament.conclave_triggered:
                            CoachService.increment_curses(signup.coach)
                    msg2.append(f"{signup.coach.mention()} triggered {rule.name}: {getattr(rule,f'level{rule_level}')}, run **!{word} {rule_level}**")
            
            # special plays
            special_plays1 = [card for card in signup.deck.cards if card.get('card_type') == "Special Play"]
            special_plays2 = [card for card in signup.deck.extra_cards if card.get('template').get('card_type') == "Special Play"]
            special_plays = special_plays1 + special_plays2
            if len(special_plays) > max_special_plays:
                max_special_plays = len(special_plays)

            decks.append((signup.coach.mention(), DeckService.value(signup.deck), special_plays))
        
        msg2.append(" ")
        sorted_decks = sorted(decks, key=lambda d: d[1])
        msg.append("**Special Plays:**")
        for deck in sorted_decks:
            msg.append(f"{deck[0]}: deck value - {deck[1]}")

        msg.extend([" ", "__Order of Play__:", " "])

        for index in range(max_special_plays):
            for deck in sorted_decks:
                if len(deck[2]) >= index + 1:
                    if isinstance(deck[2][index], Card):
                        msg.append(f"{deck[0]} plays **{deck[2][index].get('name')}**:")
                        msg.append(deck[2][index].get('description'))
                    else:
                        msg.append(f"{deck[0]} plays **{deck[2][index]['template'].get('name')}**:")
                        msg.append(deck[2][index]['template'].get('description'))
            msg.append(" ")
        
        msg.extend(msg2)

        msg.append("**Note**: No Inducement shopping in this phase")
        msg.append("**Note 2**: Blessings & Curses are rolled AFTER the special plays")
        msg.append("**Note 3**: Use !done to confirm you are done with the phase, use !left to see who is left")
        tournament.conclave_triggered = True
        db.session.commit()
        return msg
            

    @classmethod
    def inducement_msg(cls, tournament):
        
        msg = ["__**Inducement Phase**__:"," "]
        decks = []
        for signup in tournament.tournament_signups:
            decks.append((signup.coach.mention(), DeckService.value(signup.deck)))

        sorted_decks = sorted(decks, key=lambda d: d[1])

        highest_value = sorted_decks[-1][1]

        msg.extend([" ", "__Order of Play__:", " "])

        for deck in sorted_decks:
            if deck[1] < highest_value:
                msg.append(f"{deck[0]} has **{highest_value - deck[1]}** points of inducements")
        msg.append(" ")
        msg.append("**Note**: Use !done to confirm you are done with the phase, use !left to see who is left")

        return msg

    @classmethod
    def blood_bowl_msg(cls, tournament):
        msg = ["**You have to play Blood Bowl now, we apologize for the inconvenience!**"]
        return msg

    @staticmethod
    def confirm_phase(coach,room):
        if not room:
            raise TournamentError(f"Discord room not defined!")
        tourn = Tournament.query.join(Tournament.tournament_signups,TournamentSignups.coach).filter(Coach.id == coach.id).filter(Tournament.discord_channel==room).all()
        if not tourn:
            raise TournamentError(f"Tournament with {coach.short_name()} using room {room} was not found!")
        if len(tourn)>1:
            raise TournamentError(f"Unable to identify unique tournament for {coach.short_name()} using room {room}. Contact admin!")

        signups = tourn[0].tournament_signups
        deck = [ts.deck for ts in signups if ts.coach_id == coach.id]

        if deck:
            deck[0].phase_done = True
            db.session.commit()
            return True
        return False

    @staticmethod
    def left_phase(room):
        if not room:
            raise TournamentError(f"Discord room not defined!")
        tourn = Tournament.query.join(Tournament.tournament_signups).filter(Tournament.status!="FINISHED").filter(Tournament.discord_channel==room).all()
        if not tourn:
            raise TournamentError(f"Tournament using room {room} was not found!")
        if len(tourn)>1:
            raise TournamentError(f"Unable to identify unique tournament using room {room}. Contact admin!")

        signups = tourn[0].tournament_signups
        coaches = [ts.deck.tournament_signup.coach for ts in signups if not ts.deck.phase_done]

        return coaches

    @staticmethod
    def get_phase(room):
        if not room:
            raise TournamentError(f"Discord room not defined!")
        tourn = Tournament.query.join(Tournament.tournament_signups).filter(Tournament.status!="FINISHED").filter(Tournament.discord_channel==room).all()
        if not tourn:
            raise TournamentError(f"Tournament using room {room} was not found!")
        if len(tourn)>1:
            raise TournamentError(f"Unable to identify unique tournament using room {room}. Contact admin!")

        return tourn[0].phase

    @staticmethod
    def start_check(tourn):
        if not tourn.discord_channel:
            err = "Discord channel is not defined, please update it in Tournament sheet and run **!admincomp update**!\n"
            return False, err

        if not tourn.admin:
            err = f"Tournament admin is not defined, please update it in Tournament sheet and run **!admincomp update**!\n"
            return False, err
    
        coaches = Coach.find_all_by_name(tourn.admin)
        if not coaches:
            err = f"Tournament admin {tourn.admin} was not found on the discord server, check name in the Tournament sheet and run **!admincomp update**!\n"
            return False, err

        return True, None

    @classmethod
    def new_tournaments(cls):
        """Return new tournaments that should be created base on templates"""
        new_tourns = []
        # pull active templates:
        templates = TournamentTemplate.query.filter_by(active=True).all()
        for temp in templates:
            for region in ["GMAN", "REL", "Big O"]:
                # find free tournament
                tourns = Tournament.query.outerjoin(Tournament.tournament_signups).filter( \
                    Tournament.status == "OPEN", \
                    Tournament.type == temp.type, \
                    Tournament.mode == temp.mode, \
                    Tournament.coach_limit == temp.coach_limit, \
                    Tournament.deck_limit == temp.deck_limit, \
                    Tournament.deck_value_limit == temp.deck_value_limit, \
                    Tournament.region == region
                ).group_by(Tournament).having(func.count_(Tournament.tournament_signups) < Tournament.coach_limit+Tournament.reserve_limit).all()
                # create new one if there is not
                if not tourns:
                    new_tourns.append((region,temp))

        return new_tourns

    @classmethod
    def init_new_tournaments(cls):
        new_tournaments = cls.new_tournaments()
        for i, (region, temp) in enumerate(new_tournaments):
            temp = {
                "Tournament ID": 0,
                "Tournament Name": f"{region} {temp.type} {temp.mode}",
                "Scheduling Room": "",
                "Signup Close Date": "",
                "Expected Start Date":"",
                "Expected End Date":"",
                "Tournament Type": temp.type,
                "Tournament Mode": temp.mode,
                "Tournament Deadline": "",
                "Entrance Fee":0,
                "Status": "OPEN",
                "Coach Count Limit": temp.coach_limit,
                "Reserve Count Limit": 0,
                "Region Bias": region,
                "Deck Size Limit": temp.deck_limit,
                "Deck Value Limit": temp.deck_value_limit,
                "Tournament Admin": "",
                "Tournament Sponsor": "",
                "Sponsor Description":"",
                "Special Rules":"",
                "Prizes": temp.prizes,
                "Unique Prize": ""
            }
            new_tournaments[i] = list(temp.values())
        ImperiumSheetService.append_tournaments(new_tournaments)

    @classmethod
    def update_tournament_in_sheet(cls, tournament):
        ImperiumSheetService.update_tournament(cls.tournament_to_dict(tournament))

    @classmethod
    def kick_off(cls, tournament):  
        # set dates
        if not tournament.expected_start_date:
            mode = tournament.mode.lower()
            if mode == "regular":
                duration = 21
            elif mode == "boot camp":
                duration = 7
            elif mode == "fast track":
                duration = 3
            else:
                raise TournamentError(f"Unknown tournament mode: {tournament.mode}")

            start = date.today()
            end = start + timedelta(days=duration)
            tournament.expected_start_date = start.strftime("%b %d").lstrip("0").replace(" 0", " ")
            tournament.expected_end_date = end.strftime("%b %d").lstrip("0").replace(" 0", " ")
            tournament.deadline_date = end.strftime("%b %d").lstrip("0").replace(" 0", " ")

        # set sponsor
        if not tournament.sponsor:
            sponsor = random.choice(TournamentSponsor.query.all())
            tournament.sponsor = sponsor.name
            tournament.sponsor_description = sponsor.effect
            tournament.special_rules = sponsor.special_rules

        # set admin
        if not tournament.admin:
            admins = TournamentAdmin.query.all()
            regional_admins = [admin for admin in admins if tournament.region in admin.region]
            available_admins = []
            for admin in regional_admins:
                if Tournament.query.filter_by(status="OPEN", admin=admin.name).count() < admin.load:
                    available_admins.append(admin)

            if not available_admins:
                raise TournamentError("No admin available, update the Admin tab in master sheet, or configure admin manually")
            tournament.admin = random.choice(available_admins).name

        # set room
        if not tournament.discord_channel:
            rooms = TournamentRoom.query.filter_by(region=tournament.region).all()
            first_room = None
            for room in rooms:
                if Tournament.query.filter(Tournament.status != "FINISHED", Tournament.discord_channel == room.name).count() == 0:
                    first_room = room
                    break

            if not first_room:
                raise TournamentError(f"No room available for {tournament.region}, release room or create new one and update Tournament Rooms tab, or configure room manually")
            tournament.discord_channel = first_room.name

        cls.update_tournament_in_sheet(tournament)
        db.session.commit()

        _, err = cls.start_check(tournament)
        if err:
            raise TournamentError(err)
        
        AdminNotificationService.notify(
            f"!admincomp start {tournament.tournament_id}"
        )
        
    @classmethod
    def set_status(cls,tournament, status="RUNNING"):
        tournament.status = status
        cls.update_tournament_in_sheet(tournament)

    @classmethod
    def close_tournament(cls,tournament):
        cls.release_one_time_cards(tournament)
        
        for coach in tournament.coaches:
            cls.unregister(tournament, coach, admin=True, refund=False)
        cls.reset_phase(tournament)
        tournament.status = "FINISHED"
        tournament.discord_channel = ""
        tournament.expected_start_date = ""
        tournament.expected_end_date = ""
        tournament.deadline_date = ""
        tournament.sponsor = ""
        tournament.sponsor_description = ""
        tournament.special_rules = ""
        tournament.admin = ""
        tournament.consecration = ""
        tournament.Corruption = ""
        cls.update_tournament_in_sheet(tournament)
        db.session.commit()