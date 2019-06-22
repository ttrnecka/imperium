import os
from bb2api import Agent
from web import db, app, store, stats_file
import datetime as DT
import json
import logging
import services
from logging.handlers import RotatingFileHandler
from models.data_models import Coach
from sqlalchemy.orm.attributes import flag_modified
from services import NotificationService, AchievementNotificationService

app.app_context().push()

ROOT = os.path.dirname(__file__)

logger = logging.getLogger('collector')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(os.path.join(ROOT, 'logs/collector.log'), maxBytes=10000000, backupCount=5, encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

matches_folder = os.path.join(store,"matches")
start_date = DT.date.today() - DT.timedelta(days=1)

a = Agent(app.config['BB2_API_KEY'])

stats = {
  'coaches': {},
  'teams': {},
}

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

  for file in matchfiles:
    f = open(os.path.join(matches_folder,file), "r")
    data = json.loads(f.read())
    f.close()

    # initialize coaches
    coachA = data['match']['coaches'][0]
    if not coachA['coachname'] in stats['coaches']:
      stats['coaches'][coachA['coachname']] = {'wins':0,'losses':0,'draws':0,'matches':0,'points':0, 'max':{}}
      stats['coaches'][coachA['coachname']]['name'] = coachA['coachname']
      stats['coaches'][coachA['coachname']]['teams'] = {}
    coachB = data['match']['coaches'][1]
    if not coachB['coachname'] in stats['coaches']:
      stats['coaches'][coachB['coachname']] = {'wins':0,'losses':0,'draws':0,'matches':0,'points':0, 'max':{}}
      stats['coaches'][coachB['coachname']]['name'] = coachB['coachname']
      stats['coaches'][coachB['coachname']]['teams'] = {}
    
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

    # initialize the team under coach

    if teamA['idraces'] not in coachA_stats['teams']:
      coachA_stats['teams'][teamA['idraces']] = {'wins':0,'losses':0,'draws':0,'matches':0, 'points':0}
    if teamB['idraces'] not in coachB_stats['teams']:
      coachB_stats['teams'][teamB['idraces']] = {'wins':0,'losses':0,'draws':0,'matches':0, 'points':0}

    # coach team alias
    coachA_team_stats = coachA_stats['teams'][teamA['idraces']]
    coachB_team_stats = coachB_stats['teams'][teamB['idraces']]

    coachA_stats['matches']+=1
    teamA_stats['matches']+=1
    coachA_team_stats['matches']+=1
    coachB_stats['matches']+=1
    teamB_stats['matches']+=1
    coachB_team_stats['matches']+=1

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

      if not stat in coachA_team_stats:
        coachA_team_stats[stat]=0
      coachA_team_stats[stat]+=teamA[stat]
      if not stat in coachB_team_stats:
        coachB_team_stats[stat]=0
      coachB_team_stats[stat]+=teamB[stat]
    
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

    if not 'sustainedtouchdowns' in coachA_team_stats:
        coachA_team_stats['sustainedtouchdowns']=0  
    coachA_team_stats['sustainedtouchdowns']+=teamB['inflictedtouchdowns']
    if not 'sustainedtouchdowns' in coachB_team_stats:
        coachB_team_stats['sustainedtouchdowns']=0  
    coachB_team_stats['sustainedtouchdowns']+=teamA['inflictedtouchdowns']

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

    if not 'inflictedpushouts' in coachA_team_stats:
        coachA_team_stats['inflictedpushouts']=0  
    coachA_team_stats['inflictedpushouts']+=sum([player['stats']['inflictedpushouts'] for player in teamA['roster']])
    if not 'inflictedpushouts' in coachB_team_stats:
        coachB_team_stats['inflictedpushouts']=0  
    coachB_team_stats['inflictedpushouts']+=sum([player['stats']['inflictedpushouts'] for player in teamB['roster']])


    # max tracking
    for stat in ["inflictedtouchdowns","inflictedtackles","inflictedcasualties",'inflictedinjuries','inflictedinterceptions']:
      if not stat in coachA_stats['max']:
        coachA_stats['max'][stat]=0  
      if teamA[stat] > coachA_stats['max'][stat]:
        coachA_stats['max'][stat]=teamA[stat]

      if not stat in coachB_stats['max']:
        coachB_stats['max'][stat]=0  
      if teamB[stat] > coachB_stats['max'][stat]:
        coachB_stats['max'][stat]=teamB[stat]

    # wins/drawslosses
    if teamA['inflictedtouchdowns']>teamB['inflictedtouchdowns']:
      coachA_stats['wins']+=1
      coachA_stats['points']+=3
      coachB_stats['losses']+=1

      teamA_stats['wins']+=1
      teamA_stats['points']+=3
      teamB_stats['losses']+=1

      coachA_team_stats['wins']+=1
      coachA_team_stats['points']+=3
      coachB_team_stats['losses']+=1

      # cas achievement check
      if not 'max_cas_win' in coachA_stats['max']:
        coachA_stats['max']['max_cas_win']=0
      if not 'max_cas_win' in coachB_stats['max']:
        coachB_stats['max']['max_cas_win']=0
      if teamA['sustainedcasualties'] > coachA_stats['max']['max_cas_win']:
        coachA_stats['max']['max_cas_win']=teamA['sustainedcasualties']

    elif teamA['inflictedtouchdowns']<teamB['inflictedtouchdowns']:
      coachB_stats['wins']+=1
      coachB_stats['points']+=3
      coachA_stats['losses']+=1

      teamB_stats['wins']+=1
      teamB_stats['points']+=3
      teamA_stats['losses']+=1

      coachB_team_stats['wins']+=1
      coachB_team_stats['points']+=3
      coachA_team_stats['losses']+=1

      # cas achievement check
      if not 'max_cas_win' in coachA_stats['max']:
        coachA_stats['max']['max_cas_win']=0
      if not 'max_cas_win' in coachB_stats['max']:
        coachB_stats['max']['max_cas_win']=0  
      if teamB['sustainedcasualties'] > coachB_stats['max']['max_cas_win']:
        coachB_stats['max']['max_cas_win']=teamB['sustainedcasualties']

    else:
      coachA_stats['draws']+=1
      coachA_stats['points']+=1
      coachB_stats['draws']+=1
      coachB_stats['points']+=1

      teamA_stats['draws']+=1
      teamA_stats['points']+=1
      teamB_stats['draws']+=1
      teamB_stats['points']+=1

      coachA_team_stats['draws']+=1
      coachA_team_stats['points']+=1
      coachB_team_stats['draws']+=1
      coachB_team_stats['points']+=1

  try:
      stats['coaches'].pop('', None)
      f = open(stats_file, "w")
      f.write(json.dumps(stats))
      f.close()
  except Exception as e:
      logger.error(e)
      raise e
  logger.info(f"Stats recalculated")

  # update achievements
  for coach in Coach.query.all():
    if not coach.bb2_name:
      continue
    coach.achievements['match']['winwithall']['best']=0
    coach_stats = stats['coaches'][coach.bb2_name]
    # team achievements
    for team_id, data in coach_stats['teams'].items():
      team_id = str(team_id)
      # win for all achievement
      if data['wins'] > 0:
        coach.achievements['match']['winwithall']['best']+=1

      for key, ach in coach.achievements['team'][team_id]['played'].items():
        ach['best'] = data['matches']
      for key, ach in coach.achievements['team'][team_id]['wins'].items():
        ach['best'] = data['wins']
      for key, ach in coach.achievements['team'][team_id]['touchdowns'].items():
        ach['best'] = data['inflictedtouchdowns']
      for key, ach in coach.achievements['team'][team_id]['casualties'].items():
        ach['best'] = data['inflictedcasualties']
      for key, ach in coach.achievements['team'][team_id]['kills'].items():
        ach['best'] = data['inflicteddead']
      for key, ach in coach.achievements['team'][team_id]['passes'].items():
        ach['best'] = data['inflictedpasses']

    # match achievements
    coach.achievements['match']['passingtotal1']['best'] = coach_stats['inflictedmeterspassing']
    coach.achievements['match']['passingtotal2']['best'] = coach_stats['inflictedmeterspassing']

    coach.achievements['match']['runningtotal1']['best'] = coach_stats['inflictedmetersrunning']
    coach.achievements['match']['runningtotal2']['best'] = coach_stats['inflictedmetersrunning']
    
    coach.achievements['match']['surfstotal1']['best'] = coach_stats['inflictedpushouts']
    coach.achievements['match']['surfstotal2']['best'] = coach_stats['inflictedpushouts']

    coach.achievements['match']['blocks1game1']['best'] = coach_stats['max']['inflictedtackles']
    coach.achievements['match']['blocks1game2']['best'] = coach_stats['max']['inflictedtackles']

    coach.achievements['match']['breaks1game1']['best'] = coach_stats['max']['inflictedinjuries']
    coach.achievements['match']['breaks1game2']['best'] = coach_stats['max']['inflictedinjuries']

    coach.achievements['match']['cas1game1']['best'] = coach_stats['max']['inflictedcasualties']
    coach.achievements['match']['cas1game2']['best'] = coach_stats['max']['inflictedcasualties']

    coach.achievements['match']['score1game1']['best'] = coach_stats['max']['inflictedtouchdowns']
    coach.achievements['match']['score1game2']['best'] = coach_stats['max']['inflictedtouchdowns']

    coach.achievements['match']['int1game1']['best'] = coach_stats['max']['inflictedinterceptions']

    coach.achievements['match']['sufferandwin1']['best'] = coach_stats['max']['max_cas_win']
    coach.achievements['match']['sufferandwin2']['best'] = coach_stats['max']['max_cas_win']

    flag_modified(coach, "achievements")
    db.session.commit()

    # update achievements
    coach_mention=f'<@{coach.disc_id}>'
    for key,achievement in coach.achievements['match'].items():
        if achievement['target']<=achievement['best'] and achievement['completed']==False:
            AchievementNotificationService.notify(f"{coach_mention}: {achievement['desc']} - completed")
            call, arg = achievement['award'].split(",")
            res, error = getattr(coach, call)(arg,achievement['desc'])
            if res:
                print(f"{coach_mention}: {achievement['desc']} awarded")
                NotificationService.notify(f"{coach_mention}: {achievement['award_text']} awarded")
                coach.achievements['match'][key]['completed']=True
                flag_modified(coach, "achievements")
            else:
                print(error)
                NotificationService.notify(f"{coach_mention}: {achievement['award_text']} could not be awarded - {error}")
    for key1,stat in coach.achievements['team'].items():
        for key2,item in stat.items():
            for key3,achievement in item.items():
                if achievement['target']<=achievement['best'] and achievement['completed']==False:
                    AchievementNotificationService.notify(f"{coach_mention}: {achievement['desc']} - completed")
                    call, arg = achievement['award'].split(",")
                    res, error = getattr(coach, call)(arg,achievement['desc'])
                    if res:
                        print(f"{coach_mention}: {achievement['desc']} awarded")
                        coach.achievements['team'][key1][key2][key3]['completed']=True
                        flag_modified(coach, "achievements")
                        NotificationService.notify(f"{coach_mention}: {achievement['award_text']} awarded")
                    else:
                        print(error)
                        NotificationService.notify(f"{coach_mention}: {achievement['award_text']} could not be awarded - {error}")
    db.session.commit()