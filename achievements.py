from services import PackService
from web import db, app
from models.data_models import Coach
from sqlalchemy.orm.attributes import flag_modified

app.app_context().push()

achievements_template = {
  'team':{
  },
  'match':{
    'score1game1': {
      'desc': "Score 4+ touchdowns in one game",
      'completed': False,
      'award_text': "10 Coins",
      'award': 'grant, 10',
      'best':0,
      'target':4
    },
    'score1game2': {
      'desc': "Score 6+ touchdowns in one game",
      'completed': False,
      'award_text': "20 Coins",
      'award': 'grant, 20',
      'best':0,
      'target':6
    },
    'cas1game1': {
      'desc': "Cause 5+ Casualties in one game",
      'completed': False,
      'award_text': "10 Coins",
      'award': 'grant, 10',
      'best':0,
      'target':5
    },
    'cas1game2': {
      'desc': "Cause 8+ Casualties in one game",
      'completed': False,
      'award_text': "20 Coins",
      'award': 'grant, 20',
      'best':0,
      'target':8
    },
    'int1game1': {
      'desc': "Perform 2+ Interceptions in one game",
      'completed': False,
      'award_text': "20 Coins",
      'award': 'grant, 20',
      'best':0,
      'target':2
    },
    'blocks1game1': {
      'desc': "Throw 50+ blocks in one game",
      'completed': False,
      'award_text': "10 Coins",
      'award': 'grant, 10',
      'best':0,
      'target':50
    },
    'blocks1game2': {
      'desc': "Throw 80+ blocks in one game",
      'completed': False,
      'award_text': "20 Coins",
      'award': 'grant, 20',
      'best':0,
      'target':80
    },
    'breaks1game1': {
      'desc': "Manage 20+ armour breaks in one game",
      'completed': False,
      'award_text': "10 Coins",
      'award': 'grant, 10',
      'best':0,
      'target':20
    },
    'breaks1game2': {
      'desc': "Manage 30+ armour breaks in one game",
      'completed': False,
      'award_text': "20 Coins",
      'award': 'grant, 20',
      'best':0,
      'target':30
    },
    'runningtotal1': {
      'desc': "Total 500 running yards",
      'completed': False,
      'award_text': "10 Coins",
      'award': 'grant, 10',
      'best':0,
      'target':500
    },
    'runningtotal2': {
      'desc': "Total 1000 running yards",
      'completed': False,
      'award_text': "20 Coins",
      'award': 'grant, 20',
      'best':0,
      'target':1000
    },
    'passingtotal1': {
      'desc': "Total 250 passing yards",
      'completed': False,
      'award_text': "10 Coins",
      'award': 'grant, 10',
      'best':0,
      'target':250
    },
    'passingtotal2': {
      'desc': "Total 500 passing yards",
      'completed': False,
      'award_text': "20 Coins",
      'award': 'grant, 20',
      'best':0,
      'target':500
    },
    'surfstotal1': {
      'desc': "Surf 10 players",
      'completed': False,
      'award_text': "10 Coins",
      'award': 'grant, 10',
      'best':0,
      'target':10
    },
    'surfstotal2': {
      'desc': "Surf 20 players",
      'completed': False,
      'award_text': "20 Coins",
      'award': 'grant, 20',
      'best':0,
      'target':20
    },
    'sufferandwin1': {
      'desc': "Suffer 5+ casualties and win",
      'completed': False,
      'award_text': "10 Coins",
      'award': 'grant, 10',
      'best':0,
      'target':5
    },
    'sufferandwin2': {
      'desc': "Suffer 8+ casualties and win",
      'completed': False,
      'award_text': "20 Coins",
      'award': 'grant, 20',
      'best':0,
      'target':8
    },
    'winwithall': {
      'desc': "Win one match with every mixed team",
      'completed': False,
      'award_text': "20 Coins",
      'award': 'grant, 20',
      'best':0,
      'target':11
    },
  }
}


for team in PackService.MIXED_TEAMS:
  id = str(team['idraces'])
  achievements_template['team'][id] = {}
  achievements_template['team'][id]['played'] = {
    '1': {
      'desc': f"Play 3 matches with {team['name']}",
      'completed': False,
      'award_text': "10 Coins",
      'award': 'grant, 10',
      'best':0,
      'target':3
    },
    '2': {
      'desc': f"Play 10 matches with {team['name']}",
      'completed': False,
      'award_text': "20 Coins",
      'award': 'grant, 20',
      'best':0,
      'target':10
    },
    '3': {
      'desc': f"Play 25 matches with {team['name']}",
      'completed': False,
      'award_text': "30 Coins",
      'award': 'grant, 30',
      'best':0,
      'target':25
    },
  }
  achievements_template['team'][id]['casualties'] = {
    '1': {
      'desc': f"Inflict 10 casualties with {team['name']}",
      'completed': False,
      'award_text': "10 Coins",
      'award': 'grant, 10',
      'best':0,
      'target':10
    },
    '2': {
      'desc': f"Inflict 20 casualties with {team['name']}",
      'completed': False,
      'award_text': "20 Coins",
      'award': 'grant, 20',
      'best':0,
      'target':20
    },
    '3': {
      'desc': f"Inflict 50 casualties with {team['name']}",
      'completed': False,
      'award_text': "30 Coins",
      'award': 'grant, 30',
      'best':0,
      'target':50
    },
  }
  achievements_template['team'][id]['passes'] = {
    '1': {
      'desc': f"Complete 10 passes with {team['name']}",
      'completed': False,
      'award_text': "10 Coins",
      'award': 'grant, 10',
      'best':0,
      'target':10
    },
    '2': {
      'desc': f"Complete 25 passes with {team['name']}",
      'completed': False,
      'award_text': "20 Coins",
      'award': 'grant, 20',
      'best':0,
      'target':25
    },
    '3': {
      'desc': f"Complete 50 casualties with {team['name']}",
      'completed': False,
      'award_text': "30 Coins",
      'award': 'grant, 30',
      'best':0,
      'target':50
    },
  }
  achievements_template['team'][id]['touchdowns'] = {
    '1': {
      'desc': f"Score 5 touchdowns with {team['name']}",
      'completed': False,
      'award_text': "Booster Pack",
      'award': 'grant, booster_budget',
      'best':0,
      'target':5
    },
    '2': {
      'desc': f"Score 15 touchdowns with {team['name']}",
      'completed': False,
      'award_text': "Booster Premium Pack",
      'award': 'grant, booster_premium',
      'best':0,
      'target':15
    },
    '3': {
      'desc': f"Score 40 touchdowns with {team['name']}",
      'completed': False,
      'award_text': "Player Pack",
      'award': 'grant, player',
      'best':0,
      'target':40
    },
  }
  achievements_template['team'][id]['kills'] = {
    '1': {
      'desc': f"Kill 3 players with {team['name']}",
      'completed': False,
      'award_text': "Booster Pack",
      'award': 'grant, booster_budget',
      'best':0,
      'target':3
    },
    '2': {
      'desc': f"Kill 8 players with {team['name']}",
      'completed': False,
      'award_text': "Booster Premium Pack",
      'award': 'grant, booster_premium',
      'best':0,
      'target':8
    },
    '3': {
      'desc': f"Kill 15 players with {team['name']}",
      'completed': False,
      'award_text': "Player Pack",
      'award': 'grant, player',
      'best':0,
      'target':15
    },
  }
  achievements_template['team'][id]['wins'] = {
    '1': {
      'desc': f"Win 3 games with {team['name']}",
      'completed': False,
      'award_text': "Booster Pack",
      'award': 'grant, booster_budget',
      'best':0,
      'target':3
    },
    '2': {
      'desc': f"Win 10 games with {team['name']}",
      'completed': False,
      'award_text': "Booster Premium Pack",
      'award': 'grant, booster_premium',
      'best':0,
      'target':10
    },
    '3': {
      'desc': f"Win 25 games with {team['name']}",
      'completed': False,
      'award_text': "Player Pack",
      'award': 'grant, player',
      'best':0,
      'target':25
    },
  }

# run the application
if __name__ == "__main__":
  for coach in Coach.query.all():
    if not coach.achievements:
      coach.achievements = achievements_template
    else:
      # match achievements
      for key, ach in achievements_template['match'].items():
        for attr in ['desc','award_text','award','target']:
          coach.achievements['match'][key][attr] = ach[attr]
      
      # team achievements
      for team in PackService.MIXED_TEAMS:
        for metric in ['played','touchdowns','casualties','kills','passes','wins']:
          for key, ach in achievements_template['team'][str(team['idraces'])][metric].items():
            for attr in ['desc','award_text','award','target']:
              coach.achievements['team'][str(team['idraces'])][metric][key][attr] = ach[attr]
        
    flag_modified(coach, "achievements")

  db.session.commit()