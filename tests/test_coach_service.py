from datetime import datetime, timedelta
import unittest
from unittest import mock
from services import CoachService as cs

class TestCoachService(unittest.TestCase):

    def test_late_join_bonus(self):
      today = datetime.now()
      days6_ago = today - timedelta(days=6) 
      week_ago = today - timedelta(days=7)
      week2_ago = today - timedelta(days=14)
      self.assertEqual(cs.late_join_bonus(days6_ago), 0)
      self.assertEqual(cs.late_join_bonus(week_ago), 5)
      self.assertEqual(cs.late_join_bonus(week2_ago), 10)

if __name__ == '__main__':
    unittest.main()