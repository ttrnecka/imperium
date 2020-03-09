

import os
import json

from models.data_models import db

ROOT = os.path.dirname(__file__)

def cfg():
  return db.get_app().config

def stat_folder():
  return os.path.join(ROOT, '..', 'data', f"season{cfg()['SEASON']}")

def stats_file():
  return os.path.join(stat_folder(), "stats.json")

def matches_folder():
  return os.path.join(stat_folder(), "matches")

def get_stats(fresh=False):
    """pulls data from stats file"""
    if not fresh and os.path.isfile(stats_file()):
        file = open(stats_file(), "r")
        data = json.loads(file.read())
        file.close()
        return data
    else:
        return {
            'coaches': {},
            'teams': {},
            'matchfiles':[]
        }

def save_stats(data):
    file = open(stats_file(), "w")
    file.write(json.dumps(data))
    file.close()


def set_folders():
    if not os.path.isdir(stat_folder()):
        os.mkdir(stat_folder())

    if not os.path.isdir(matches_folder()):
        os.mkdir(matches_folder())