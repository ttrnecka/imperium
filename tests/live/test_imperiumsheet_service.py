import unittest
import services

class TestImperiumSheetService(unittest.TestCase):

    def test_mastersheet(self):
        self.assertEqual(services.ImperiumSheetService.SPREADSHEET_ID, "1t5IoiIjPAS2CD63P6xI4hWwx9c1SEzW9AL1LJ4LK6og", "Should be using production master sheet")

    def test_cards(self):
        cards = services.ImperiumSheetService.cards()
        self.assertGreater(len(cards), 1000, "Cards count less than 1000")
        must_have_keys = ["Multiplier", "Type", "Subtype", "Rarity", "Card Name", "Race",
                          "Description", "Card Value", "Skill Access", "Notes"]
        self.assertTrue(set(must_have_keys) <= set(list(cards[0].keys())), "Cards missing must have keys")

    def test_starter_cards(self):
        cards = services.ImperiumSheetService.starter_cards()
        self.assertGreater(len(cards), 100, "Starter Cards count less than 100")
        must_have_keys = ["Type", "Subtype", "Rarity", "Card Name", "Race",
                          "Description", "Card Value", "Skill Access"]
        self.assertTrue(set(must_have_keys) <= set(list(cards[0].keys())), "Starter Cards missing must have keys")

    def test_tournaments(self):
        ts = services.ImperiumSheetService.tournaments()
        self.assertGreater(len(ts), 10, "Tournaments count less than 10")
        must_have_keys = ["Tournament ID", "Tournament Name", "Scheduling Room", "Signup Close Date", "Expected Start Date",
                          "Expected End Date", "Tournament Type", "Tournament Mode", "Tournament Deadline", "Entrance Fee", "Status",
                          "Coach Count Limit", "Reserve Count Limit", "Region Bias", "Deck Size Limit", "Tournament Admin",
                          "Tournament Sponsor", "Sponsor Description", "Special Rules", "Prizes", "Unique Prize"]
        self.assertTrue(set(must_have_keys) <= set(list(ts[0].keys())), "Tournaments missing must have keys")
if __name__ == '__main__':
    unittest.main()