from bb2.rebblnetapi import Api, SighanideError


"""BB2Service proxy helpers"""
class BB2Service:

    cyanide_api = None

    @classmethod
    def api(cls):
        if not cls.cyanide_api:
            cls.cyanide_api = Api()
        return cls.cyanide_api

    """Namespace"""
    @classmethod
    def register_agent(cls, agent):
        """Register bb2 api agent"""
        cls.agent = agent

    @classmethod
    def team(cls, name):
        """Wrapper around team api"""
        return cls.agent.team(name)

    @classmethod
    def league(cls, name):
        """Wrapper around team api"""
        return cls.agent.league(name)

    @classmethod
    def competitions(cls, leagues):
        """Wrapper around team api"""
        return cls.agent.competitions(leagues=leagues)

    @classmethod
    def delete_competition(cls,competition_id):
        api = cls.api()
        return api.delete_competition(competition_id)

    @classmethod
    def start_competition(cls,competition_id):
        api = cls.api()
        return api.start_competition(competition_id)

    @classmethod
    def create_competition(cls,**kwargs):
        api = cls.api()
        return api.create_competition(
            league_id=kwargs['league_id'],
            name=kwargs['name'],
            owner_id=kwargs['owner_id'],
            team_count=kwargs['team_count'],
            competition_type=kwargs['competition_type'],
            turn_duration=kwargs['turn_duration'],
            aging=kwargs['aging'], 
            enhancement=kwargs['enhancement'],
            resurrection=kwargs['resurrection'],
            custom_teams=kwargs['custom_teams'], 
            mixed_teams=kwargs['mixed_teams'], 
            experienced_teams=kwargs['experienced_teams'],
            kick_off_events=kwargs['kick_off_events'], 
            autovalidate_match=kwargs['autovalidate_match'],
            registration_type=kwargs['registration_type'])

