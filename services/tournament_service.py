"""TournamentService helpers"""
from sqlalchemy import asc
from models.data_models import Tournament, TournamentSignups, Transaction, Deck
from models.base_model import db
from .notification_service import NotificationService
from .imperium_sheet_service import ImperiumSheetService
from .deck_service import DeckService

class RegistrationError(Exception):
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
            "admin":tournament["Tournament Admin"],
            "sponsor":tournament["Tournament Sponsor"],
            "special_rules":tournament["Special Rules"],
            "prizes":tournament["Prizes"],
            "unique_prize":tournament["Unique Prize"],
            "sponsor_description":tournament["Sponsor Description"],
        }

    @classmethod
    def update(cls):
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
        # Deve tournaments limited to 1 for Fast Tracks and 2 for Regulars
        else:
            if tournament.mode == "Fast Track":
                singups = coach.tournaments.filter(
                    Tournament.type != "Imperium", Tournament.mode == "Fast Track").all()
                if singups:
                    raise RegistrationError(
                        f"Coach cannot be registered to more than \
                        1 Fast Track Development tournament!!!")

            if tournament.mode == "Regular":
                singups = coach.tournaments.filter(
                    Tournament.type != "Imperium", Tournament.mode == "Regular").all()
                if len(singups)>1:
                    raise RegistrationError(f"Coach cannot be registered to more \
                        than 2 Regular Development tournaments!!!")

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
            coach.make_transaction(tran)

            # deck
            deck = Deck(team_name="", mixed_team="", tournament_signup=signup,
                        extra_cards=[], unused_extra_cards=[], starter_cards=[])
            db.session.add(deck)

            db.session.commit()
            if tournament.fee > 0:
                coach_mention = f'<@{coach.disc_id}>'
            else:
                coach_mention = coach.short_name()

            NotificationService.notify(
                f'{coach_mention} successfuly signed to {tournament.tournament_id}.' +
                f' {tournament.name} - fee {tournament.fee} coins')
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
                fee_msg = f" - refund {tournament.fee} coins"
            else:
                coach_mention = coach.short_name()
                fee_msg = ""

            NotificationService.notify(
                f'{coach_mention} successfuly resigned from' +
                f' {tournament.tournament_id}. {tournament.name}{fee_msg}'
            )

        except Exception as exp:
            raise RegistrationError(str(exp))

        return True

    @classmethod
    def release_reserves(cls,tournament):
        reserves = tournament.coaches.filter(TournamentSignups.mode == 'reserve')
        for coach in reserves:
            cls.unregister(tournament, coach, admin=True, refund=False)

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
    def special_play_msg(cls, tournament):

        msg = ["__**Special Play Phase**__:"," "]
        decks = []
        max_special_plays = 0
        for signup in tournament.tournament_signups:
            special_plays = [card for card in signup.deck.cards if card.card_type == "Special Play"]
            if len(special_plays) > max_special_plays:
                max_special_plays = len(special_plays)

            decks.append((signup.coach.mention(), DeckService.value(signup.deck), special_plays))
        
        sorted_decks = sorted(decks, key=lambda d: d[1])

        for deck in sorted_decks:
            msg.append(f"{deck[0]}: deck value - {deck[1]}")

        msg.extend([" ", "__Order of Play__:", " "])

        for index in range(max_special_plays):
            for deck in sorted_decks:
                if len(deck[2]) >= index + 1:
                    msg.append(f"{deck[0]} plays **{deck[2][index].name}**:")
                    msg.append(deck[2][index].description)
            msg.append(" ")
        
        msg.append("**Note**: No Inducement shopping in this phase")
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
                msg.append(f"{deck[0]} has **{highest_value - deck[1]}** value of inducements:")
        msg.append(" ")

        return msg
