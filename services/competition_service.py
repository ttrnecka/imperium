"""Coach service helpers"""
from sqlalchemy import func

from models.data_models import Competition
from models.base_model import db
from .bb2_service import BB2Service


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
        "owner_id":0
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
    def delete_competition(competition):
        if not isinstance(competition,Competition):
            raise CompetitionError("competition is not Competition class")
        response = BB2Service.delete_competition(competition.comp_id)

        if response["ResponseDeleteCompetition"]["CallResult"]["ErrLabel"]:
            raise CompetitionError(response["ResponseDeleteCompetition"]["CallResult"]["ErrLabel"])

        db.session.delete(competition)
        db.session.commit()

    @classmethod
    def create_imperium_comp(cls, name, competition_type=0, team_count=0):
        # refresh comps
        CompetitionService.import_competitions()

        # check if it exists
        comp = Competition.query.filter(func.lower(Competition.name) == func.lower(name)).one_or_none()

        # if exists check if it is running
        if comp and Competition.Status(comp.status) != Competition.Status.COMPLETED:
            raise CompetitionError(f"Active competition with name {name} exists already in {comp.league_name}")

        if comp: # if it exists and is completed, delete it
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
        # check if it exists and is running
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
    def create_imperium_rr(cls, league_id, name):
        return cls.create_imperium_comp(name,competition_type=Competition.CompetitionType.ROUND_ROBIN.value, team_count=2)

    #@classmethod
    #def create_imperium_knockout(cls, league_id, name, owner_id, team_count):
    #    cls.create_imperium_comp(league_id,name,owner_id,competition_type=Competition.CompetitionType.KNOCKOUT.value, team_count=team_count)

    @classmethod
    def __create_competition(cls, league_id=0, name="", owner_id=0, team_count=0, competition_type=0, turn_duration=0, aging=False, resurrection=False, enhancement=False, custom_teams=False, mixed_teams=False, experienced_teams=False):
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
            "experienced_teams":experienced_teams
        }

        comp_types = {
            0: "swiss",
            1: "round_robin",
            2: "single_elimination",
            3: "ladder"
        }

        response = BB2Service.create_competition(**comp)

        if response['CompetitionData']['RowLeague']['IdOwner'] == "0":
            raise CompetitionError("Unable to create competition")
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

        return c