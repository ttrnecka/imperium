import unittest
import services
import bb2_cyanide_api as bb2

class TestBBService(unittest.TestCase):

    def test_agent_registration(self):
        agent = bb2.Agent("dummykey")
        services.BB2Service.register_agent(agent)
        self.assertIs(services.BB2Service.agent, agent, "Service should have agent attribute same as agent")

if __name__ == '__main__':
    unittest.main()