import unittest
from flask import Flask

from web import db
from models.data_models import Coach
from services import CoachService

class appDBTests(unittest.TestCase):

    def setUp(self):
        """
        Creates a new database for the unit test to use
        """
        self.app = Flask(__name__)
        db.init_app(self.app)
        with self.app.app_context():
            db.create_all()
            self.populate_db() # Your function that adds test data.

    def tearDown(self):
        """
        Ensures that the database is emptied for next unit test
        """
        self.app = Flask(__name__)
        db.init_app(self.app)
        with self.app.app_context():
            db.drop_all()

    def populate_db(self):
      with self.app.app_context():
        c = CoachService.new_coach("TomasT", "1")
        db.session.add(c)
        db.session.commit()

    def test_has_coach(self):
        with self.app.app_context():
          self.assertEqual(len(Coach.query.all()), 1)

if __name__ == '__main__':
    unittest.main()