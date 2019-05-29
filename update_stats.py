import os
from bb2api import Agent
from web import db, app, store, stats_file
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

matches_folder = os.path.join(store,"matches")
start_date = DT.date.today() - DT.timedelta(days=1)

a = Agent(app.config['BB2_API_KEY'])

# run the application
if __name__ == "__main__":
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

  stats = {
    'coaches': {},
    'teams': {}
  }

  for file in matchfiles:
    f = open(os.path.join(matches_folder,file), "r")
    data = json.loads(f.read())
    f.close()

    # initialize coaches
    coachA = data['match']['coaches'][0]
    if not coachA['coachname'] in stats['coaches']:
      stats['coaches'][coachA['coachname']] = {'wins':0,'losses':0,'draws':0,'matches':0,'points':0}
      stats['coaches'][coachA['coachname']]['name'] = coachA['coachname']
    coachB = data['match']['coaches'][1]
    if not coachB['coachname'] in stats['coaches']:
      stats['coaches'][coachB['coachname']] = {'wins':0,'losses':0,'draws':0,'matches':0,'points':0}
      stats['coaches'][coachB['coachname']]['name'] = coachB['coachname']
    
    # initialize teams
    teamA = data['match']['teams'][0]
    if not teamA['idraces'] in stats['teams']:
      stats['teams'][teamA['idraces']] = {'wins':0,'losses':0,'draws':0,'matches':0,'points':0}
      stats['teams'][teamA['idraces']]['idraces'] = teamA['idraces']
    teamB = data['match']['teams'][1]
    if not teamB['idraces'] in stats['teams']:
      stats['teams'][teamB['idraces']] = {'wins':0,'losses':0,'draws':0,'matches':0,'points':0}
      stats['teams'][teamB['idraces']]['idraces'] = teamB['idraces']

    #alias coaches and teams
    coachA_stats = stats['coaches'][coachA['coachname']]
    coachB_stats = stats['coaches'][coachB['coachname']]
    teamA_stats = stats['teams'][teamA['idraces']]
    teamB_stats = stats['teams'][teamB['idraces']]

    coachA_stats['matches']+=1
    teamA_stats['matches']+=1
    coachB_stats['matches']+=1
    teamB_stats['matches']+=1

    for stat in ["inflictedtouchdowns","inflictedtackles","inflictedcasualties",'inflictedinjuries','inflictedko','inflicteddead','inflictedmetersrunning','inflictedpasses',
    'inflictedcatches', 'inflictedinterceptions','inflictedmeterspassing','sustainedexpulsions','sustainedcasualties','sustainedko',
    'sustainedinjuries','sustaineddead']:
      if not stat in coachA_stats:
        coachA_stats[stat]=0  
      coachA_stats[stat]+=teamA[stat]
      if not stat in coachB_stats:
        coachB_stats[stat]=0
      coachB_stats[stat]+=teamB[stat]

      if not stat in teamA_stats:
        teamA_stats[stat]=0  
      teamA_stats[stat]+=teamA[stat]
      if not stat in teamB_stats:
        teamB_stats[stat]=0  
      teamB_stats[stat]+=teamB[stat]

    
    #sustd workaround
    if not 'sustainedtouchdowns' in coachA_stats:
        coachA_stats['sustainedtouchdowns']=0  
    coachA_stats['sustainedtouchdowns']+=teamB['inflictedtouchdowns']
    if not 'sustainedtouchdowns' in coachB_stats:
        coachB_stats['sustainedtouchdowns']=0  
    coachB_stats['sustainedtouchdowns']+=teamA['inflictedtouchdowns']

    if not 'sustainedtouchdowns' in teamA_stats:
        teamA_stats['sustainedtouchdowns']=0  
    teamA_stats['sustainedtouchdowns']+=teamB['inflictedtouchdowns']
    if not 'sustainedtouchdowns' in teamB_stats:
        teamB_stats['sustainedtouchdowns']=0  
    teamB_stats['sustainedtouchdowns']+=teamA['inflictedtouchdowns']

    # inflictedpushouts fix
    if not 'inflictedpushouts' in coachA_stats:
        coachA_stats['inflictedpushouts']=0  
    coachA_stats['inflictedpushouts']+=sum([player['stats']['inflictedpushouts'] for player in teamA['roster']])
    if not 'inflictedpushouts' in coachB_stats:
        coachB_stats['inflictedpushouts']=0  
    coachB_stats['inflictedpushouts']+=sum([player['stats']['inflictedpushouts'] for player in teamB['roster']])

    if not 'inflictedpushouts' in teamA_stats:
        teamA_stats['inflictedpushouts']=0  
    teamA_stats['inflictedpushouts']+=sum([player['stats']['inflictedpushouts'] for player in teamA['roster']])
    if not 'inflictedpushouts' in teamB_stats:
        teamB_stats['inflictedpushouts']=0  
    teamB_stats['inflictedpushouts']+=sum([player['stats']['inflictedpushouts'] for player in teamB['roster']])

    
    # wins/drawslosses
    if teamA['inflictedtouchdowns']>teamB['inflictedtouchdowns']:
      coachA_stats['wins']+=1
      coachA_stats['points']+=3
      coachB_stats['losses']+=1

      teamA_stats['wins']+=1
      teamA_stats['points']+=3
      teamB_stats['losses']+=1
    elif teamA['inflictedtouchdowns']<teamB['inflictedtouchdowns']:
      coachB_stats['wins']+=1
      coachB_stats['points']+=3
      coachA_stats['losses']+=1

      teamB_stats['wins']+=1
      teamB_stats['points']+=3
      teamA_stats['losses']+=1
    else:
      coachA_stats['draws']+=1
      coachA_stats['points']+=1
      coachB_stats['draws']+=1
      coachB_stats['points']+=1

      teamA_stats['draws']+=1
      teamA_stats['points']+=1
      teamB_stats['draws']+=1
      teamB_stats['points']+=1

  try:
      stats['coaches'].pop('', None)
      f = open(stats_file, "w")
      f.write(json.dumps(stats))
      f.close()
  except Exception as e:
      logger.error(e)
      raise e
  logger.info(f"Stats recalculated")

  #coaches = list(stats['coaches'].values())

  #def customSort(e):
  #  return e['inflictedcasualties']

  #coaches.sort(key=customSort)

  #print(coaches)