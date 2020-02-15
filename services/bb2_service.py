"""BB2Service proxy helpers"""
class BB2Service:
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
    def competitions(cls, leagues):
        """Wrapper around team api"""
        return cls.agent.competitions(leagues=leagues)

