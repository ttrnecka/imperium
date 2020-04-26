

import os
import json
from misc.helpers2 import current_season

ROOT = os.path.dirname(__file__)

class StatsHandler:
  """Handle stats for given season"""
  def __init__(self, season=None):
    if not season:
      season = current_season()
    self.__season = season

  def stat_folder(self):
    return os.path.join(ROOT, '..', 'data', f"season{self.__season}")

  def stats_file(self):
    return os.path.join(self.stat_folder(), "stats.json")

  def matches_folder(self):
    return os.path.join(self.stat_folder(), "matches")

  def competition_folder(self, competition):
    return os.path.join(self.stat_folder(), "matches", "".join(x for x in competition if x.isalnum()))

  def get_stats(self, fresh=False):
      """pulls data from stats file"""
      if not fresh and os.path.isfile(self.stats_file()):
          file = open(self.stats_file(), "r")
          data = json.loads(file.read())
          file.close()
          return data
      else:
          return {
              'coaches': {},
              'teams': {},
              'matchfiles':[]
          }

  def save_stats(self, data):
      file = open(self.stats_file(), "w")
      file.write(json.dumps(data))
      file.close()

  @staticmethod
  def create_folder(folder):
    if not os.path.isdir(folder):
        os.mkdir(folder)

  def set_folders(self):
      if not os.path.isdir(self.stat_folder()):
          os.mkdir(self.stat_folder())

      if not os.path.isdir(self.matches_folder()):
          os.mkdir(self.matches_folder())
  @staticmethod
  def write_file(file_name, data):
    file = open(file_name, "w")
    file.write(json.dumps(data))
    file.close()