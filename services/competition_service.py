"""Coach service helpers"""
from sqlalchemy import func

from models.data_models import Competition, Coach, Tournament
from models.base_model import db
from .bb2_service import BB2Service, SighanideError
from .notification_service import TournamentNotificationService


class CompetitionError(Exception):
    """Exception to raise for tournament registration issues"""

def imperium_default_comp_params():
    return {        
        "turn_duration": Competition.TurnDuration.TWO_MINUTES.value,
        "resurrection":True,
        "enhancement":True,
        "custom_teams":True,
        "mixed_teams":True,
        "experienced_teams":True,
        "owner_id":0,
        "kick_off_events": True,
        "autovalidate_match": True,
        "registration_type": "InviteOnly"
    }

class CompetitionService:
    """CompetitionService helpers namespace"""

    @staticmethod
    def import_competitions():
        config = db.get_app().config
        data = BB2Service.competitions(leagues=",".join(config['LEAGUES']))

        ids = []
        for comp in data['competitions']:
            if not comp['id']:
                break
            cid = int(comp['id'])
            ids.append(cid)
            c = Competition.query.filter_by(comp_id=cid).one_or_none()
            if not c:
                c = Competition(comp_id = comp['id'])
            c.name = comp['name']
            c.competition_type = comp['format']
            c.team_count = comp['teams_max']
            c.turn_duration = comp['turn_duration']
            c.status = comp['status']
            c.league_id = comp['league']['id']
            c.league_name = comp['league']['name']
            db.session.add(c)

        cs = Competition.query.filter(~Competition.comp_id.in_(ids)).all()
        for c in cs:
            db.session.delete(c)
        db.session.commit()

    @staticmethod
    def delete_competition(competition: Competition):
        try:
            BB2Service.delete_competition(competition.comp_id)
            db.session.delete(competition)
            db.session.commit()
            TournamentNotificationService.notify(f"Created in-game room **{competition.name}** in **{competition.league_name}**")
        except SighanideError as e:
            raise CompetitionError(str(e))

    @classmethod
    def create_imperium_comp(cls, name, competition_type=0, team_count=0):
        CompetitionService.import_competitions()

        comp = Competition.query.filter(func.lower(Competition.name) == func.lower(name)).one_or_none()

        if comp and Competition.Status(comp.status) != Competition.Status.COMPLETED:
            raise CompetitionError(f"Active competition with name **{name}** exists already in **{comp.league_name}**")

        if comp: # if it exists it is completed so delete it
            CompetitionService.delete_competition(comp)

        # select the league
        selected_league = None
        for league in db.get_app().config["LEAGUES"]:
            comp_len = Competition.query.filter(Competition.league_name==league,Competition.status!=Competition.Status.COMPLETED.value).count()
            if comp_len < 20:
                selected_league = league
                break
        
        if not selected_league:
            raise CompetitionError(f"Competition cannot be created, all leagues are full!!!")

        league_id = BB2Service.league(selected_league)['league']['id']
        params = imperium_default_comp_params()
        params["league_id"] = league_id
        params["name"] = name
        params["competition_type"] = competition_type
        params["team_count"] = team_count
        return cls.__create_competition(**params)

    @classmethod
    def create_imperium_ladder(cls,name):
        return cls.create_imperium_comp(name, competition_type=Competition.CompetitionType.LADDER.value)

    @classmethod
    def create_imperium_rr(cls,name):
        return cls.create_imperium_comp(name,competition_type=Competition.CompetitionType.ROUND_ROBIN.value, team_count=2)

    @classmethod
    def create_imperium_knockout(cls, name, team_count):
        return cls.create_imperium_comp(name,competition_type=Competition.CompetitionType.KNOCKOUT.value, team_count=team_count)

    @classmethod
    def ticket_competition(cls, competition_name: str, coach: Coach, tournament: Tournament):
        # get deck
        decks = [ts.deck for ts in tournament.tournament_signups if ts.coach == coach]
        if not decks:
            raise CompetitionError(f"Coach **{coach.short_name()}** does not have team in this tournament")
        deck = decks[0]
        if not deck.team_name:
            raise CompetitionError(f"No team name is specified in the deck")
        #get comp
        comp = Competition.query.filter_by(name=competition_name).one_or_none()
        if not comp:
            raise CompetitionError(f"Competition **{competition_name}** does not exist")

        result = BB2Service.team(deck.team_name)
        if not result:
            raise CompetitionError(f"Team {deck.team_name} does not exist")

        team_id = result['team']['id']
        coach_id = result['coach']['id']
        coach_name = result['coach']['name']
        if coach.bb2_name and coach.bb2_name != coach_name:
            raise CompetitionError(f"Team {team_name} does not belong to coach {coach.bb2_name}")
        try:
            result = BB2Service.api().send_ticket(comp.comp_id, 0, coach_id, team_id)
            TournamentNotificationService.notify(f"{coach.short_name()} ticketed **{deck.team_name}** into **{competition_name}**")
        except SighanideError as e:
            raise CompetitionError(str(e))
        return result

    @classmethod
    def __create_competition(cls, league_id=0, name="", owner_id=0, team_count=0, competition_type=0, turn_duration=0, aging=False, resurrection=False, enhancement=False, custom_teams=False, mixed_teams=False, experienced_teams=False, kick_off_events=True, autovalidate_match=True, registration_type="InviteOnly"):
        comp = {
            "league_id":league_id,
            "name":name,
            "owner_id": owner_id,
            "team_count":team_count,
            "competition_type":competition_type,
            "turn_duration":turn_duration,
            "aging":aging, 
            "enhancement":enhancement,
            "resurrection":resurrection,
            "custom_teams":custom_teams, 
            "mixed_teams":mixed_teams, 
            "experienced_teams":experienced_teams,
            "kick_off_events": kick_off_events,
            "autovalidate_match": autovalidate_match,
            "registration_type": registration_type
        }

        comp_types = {
            0: "swiss",
            1: "round_robin",
            2: "single_elimination",
            3: "ladder"
        }

        try:
            response = BB2Service.create_competition(**comp)
        except SighanideError as e:
            raise CompetitionError(str(e))

        c = Competition()
        c.comp_id = int(response['CompetitionData']['RowCompetition']['Id']['Value'].split(":")[1].split("-")[0])
        c.name = name
        c.league_id = league_id
        c.league_name = response['CompetitionData']['RowLeague']['Name']
        c.competition_type = comp_types[competition_type]
        c.team_count = team_count
        c.turn_duration = turn_duration
        c.status = int(response['CompetitionData']['RowCompetition']['CompetitionStatus'])
        c.owner_id = int(response['CompetitionData']['Owner']['IdUser'])

        db.session.add(c)
        db.session.commit()
        TournamentNotificationService.notify(f"Created in-game room **{c.name}** in **{c.league_name}**")
        return c