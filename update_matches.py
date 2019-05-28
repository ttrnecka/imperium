import os
from bb2api import Agent
from web import db, app
import datetime as DT
import json
import logging
from logging.handlers import RotatingFileHandler


ROOT = os.path.dirname(__file__)

logger = logging.getLogger('collector')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(os.path.join(ROOT, 'logs/collector.log'), maxBytes=10000000, backupCount=5, encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


store = os.path.join(ROOT, 'data', f"season{app.config['SEASON']}")
matches_folder = os.path.join(store,"matches")
start_date = DT.date.today() - DT.timedelta(days=1)

a = Agent(app.config['BB2_API_KEY'])

logger.info(f"Getting matches since {start_date}")

try:
  data = a.matches(start=start_date)
except Exception as e:
  logger.error(e)
  raise e

if not os.path.isdir(store): 
  os.mkdir(store)

if not os.path.isdir(matches_folder): 
  os.mkdir(matches_folder)

for match in data['matches']:
  filename = os.path.join(matches_folder,f"{match['uuid']}.json")
  if os.path.isfile(filename):
    logger.info(f"File {filename} exists")
    continue
  logger.info(f"Collecting match {match['uuid']}")
  try:
    detailed = a.match(id=match['uuid'])
    f = open(filename, "a")
    f.write(json.dumps(detailed))
    f.close()
  except Exception as e:
    logger.error(e)
    raise e
  logger.info(f"Match {match['uuid']} saved")

# stats rebuilding
matchfiles = [f for f in os.listdir(matches_folder) if os.path.isfile(os.path.join(matches_folder, f))]

stats_file = os.path.join(store,"stats.json")
stats = {
  'coaches': {},
  'teams': {}
}


for file in matchfiles:
  f = open(os.path.join(matches_folder,file), "r")
  data = json.loads(f.read())
  f.close()
  coachA = data['match']['coaches'][0]
  if not coachA['coachname'] in stats['coaches']:
    stats['coaches'][coachA['coachname']] = {'wins':0,'losses':0,'draws':0,'matches':0,'points':0, 'inflictedtouchdowns':0, 'sustainedtouchdowns':0, 'inflictedtackles':0, 'inflictedinjuries':0,
    'inflictedcasualties':0}
    stats['coaches'][coachA['coachname']]['name'] = coachA['coachname']
  coachB = data['match']['coaches'][1]
  if not coachB['coachname'] in stats['coaches']:
    stats['coaches'][coachB['coachname']] = {'wins':0,'losses':0,'draws':0,'matches':0,'points':0, 'inflictedtouchdowns':0, 'sustainedtouchdowns':0, 'inflictedtackles':0, 'inflictedinjuries':0,
    'inflictedcasualties':0}
    stats['coaches'][coachB['coachname']]['name'] = coachB['coachname']
  teamA = data['match']['teams'][0]
  if not teamA['idraces'] in stats['teams']:
    stats['teams'][teamA['idraces']] = {'wins':0,'losses':0,'draws':0,'matches':0,'points':0,'inflictedinjuries':0,'inflictedcasualties':0}
    stats['teams'][teamA['idraces']]['idraces'] = teamA['idraces']
  teamB = data['match']['teams'][1]
  if not teamB['idraces'] in stats['teams']:
    stats['teams'][teamB['idraces']] = {'wins':0,'losses':0,'draws':0,'matches':0,'points':0,'inflictedinjuries':0,'inflictedcasualties':0}
    stats['teams'][teamB['idraces']]['idraces'] = teamB['idraces']

  stats['coaches'][coachA['coachname']]['matches']+=1
  stats['teams'][teamA['idraces']]['matches']+=1
  stats['coaches'][coachB['coachname']]['matches']+=1
  stats['teams'][teamB['idraces']]['matches']+=1

  #tds
  stats['coaches'][coachA['coachname']]['inflictedtouchdowns']+=teamA['inflictedtouchdowns']
  stats['coaches'][coachB['coachname']]['inflictedtouchdowns']+=teamB['inflictedtouchdowns']
  stats['coaches'][coachA['coachname']]['sustainedtouchdowns']+=teamB['inflictedtouchdowns']
  stats['coaches'][coachB['coachname']]['sustainedtouchdowns']+=teamA['inflictedtouchdowns']

  #tackles
  stats['coaches'][coachA['coachname']]['inflictedtackles']+=teamA['inflictedtackles']
  stats['coaches'][coachB['coachname']]['inflictedtackles']+=teamB['inflictedtackles']

  #injuries
  stats['coaches'][coachA['coachname']]['inflictedinjuries']+=teamA['inflictedinjuries']
  stats['coaches'][coachB['coachname']]['inflictedinjuries']+=teamB['inflictedinjuries']
  stats['teams'][teamA['idraces']]['inflictedinjuries']+=teamA['inflictedinjuries']
  stats['teams'][teamB['idraces']]['inflictedinjuries']+=teamB['inflictedinjuries']

  #cas
  stats['coaches'][coachA['coachname']]['inflictedcasualties']+=teamA['inflictedcasualties']
  stats['coaches'][coachB['coachname']]['inflictedcasualties']+=teamB['inflictedcasualties']
  stats['teams'][teamA['idraces']]['inflictedcasualties']+=teamA['inflictedcasualties']
  stats['teams'][teamB['idraces']]['inflictedcasualties']+=teamB['inflictedcasualties']
  # wins/drawslosses
  if teamA['inflictedtouchdowns']>teamB['inflictedtouchdowns']:
    stats['coaches'][coachA['coachname']]['wins']+=1
    stats['coaches'][coachA['coachname']]['points']+=3
    stats['coaches'][coachB['coachname']]['losses']+=1

    stats['teams'][teamA['idraces']]['wins']+=1
    stats['teams'][teamA['idraces']]['points']+=3
    stats['teams'][teamB['idraces']]['losses']+=1
  elif teamA['inflictedtouchdowns']<teamB['inflictedtouchdowns']:
    stats['coaches'][coachB['coachname']]['wins']+=1
    stats['coaches'][coachB['coachname']]['points']+=3
    stats['coaches'][coachA['coachname']]['losses']+=1

    stats['teams'][teamB['idraces']]['wins']+=1
    stats['teams'][teamB['idraces']]['points']+=3
    stats['teams'][teamA['idraces']]['losses']+=1
  else:
    stats['coaches'][coachA['coachname']]['draws']+=1
    stats['coaches'][coachA['coachname']]['points']+=1
    stats['coaches'][coachB['coachname']]['draws']+=1
    stats['coaches'][coachB['coachname']]['points']+=1

    stats['teams'][teamA['idraces']]['draws']+=1
    stats['teams'][teamA['idraces']]['points']+=1
    stats['teams'][teamB['idraces']]['draws']+=1
    stats['teams'][teamB['idraces']]['points']+=1

try:
    f = open(stats_file, "w")
    f.write(json.dumps(stats))
    f.close()
except Exception as e:
    logger.error(e)
    raise e
logger.info(f"Stats recalculated")

coaches = list(stats['coaches'].values())

def customSort(e):
  return e['inflictedcasualties']

coaches.sort(key=customSort)

print(coaches)