"""Match helpers"""

from collections import Counter

def is_concede(data):
    """Given match data returns True if the match was conceded"""
    if (data['match']['teams'][0]['mvp'] == 2
            or data['match']['teams'][1]['mvp'] == 2):
        return True
    return False

class Match:
    def __init__(self,data):
      self.data = data

    def uuid(self):
      return self.data['uuid']
    
    def competition(self):
      return self.data['match']['competitionname']

    def coach1(self):
      return self.data['match']['coaches'][0]

    def coach2(self):
      return self.data['match']['coaches'][1]

    def team1(self):
      return self.data['match']['teams'][0]

    def team2(self):
      return self.data['match']['teams'][1]

    def winner(self):
      if self.team1()['inflictedtouchdowns'] > self.team2()['inflictedtouchdowns']:
        return self.coach1()
      elif self.team1()['inflictedtouchdowns'] < self.team2()['inflictedtouchdowns']:
        return self.coach2()
      else:
        return None

class Tournament:
    def __init__(self, *args:Match):
      self.matches = args

    def leaderboard(self):
      coaches = {}
      for match in self.matches:
        for coach in [match.coach1(), match.coach2()]:
          if not coach['coachname'] in coaches:
            coaches[coach['coachname']] = Counter({'name': coach['coachname']})
        winner = match.winner()
        coach1_name = match.coach1()['coachname']
        coach2_name = match.coach2()['coachname']
        coaches[coach1_name]['matches'] += 1
        coaches[coach2_name]['matches'] += 1
        for stat in ["inflictedtouchdowns", "inflictedtackles", "inflictedcasualties",
                     'inflictedinjuries', 'inflictedko', 'inflicteddead', 'inflictedmetersrunning',
                     'inflictedpasses', 'inflictedcatches', 'inflictedinterceptions',
                     'sustainedexpulsions', 'sustainedcasualties', 'sustainedko',
                     'sustainedinjuries', 'sustaineddead', 'inflictedmeterspassing',]:
          coaches[coach1_name][stat] += match.team1()[stat]
          coaches[coach2_name][stat] += match.team2()[stat]

        coaches[coach1_name]['sustainedtouchdowns'] += match.team2()['inflictedtouchdowns']
        coaches[coach2_name]['sustainedtouchdowns'] += match.team1()['inflictedtouchdowns']

        coaches[coach1_name]['inflictedpushouts'] += sum(
            [player['stats']['inflictedpushouts'] for player in match.team1()['roster']]
        )
        coaches[coach2_name]['inflictedpushouts'] += sum(
            [player['stats']['inflictedpushouts'] for player in match.team2()['roster']]
        )
        coaches[coach1_name]['sustainedtackles'] += sum(
            [player['stats']['sustainedtackles'] for player in match.team1()['roster']]
        )
        coaches[coach2_name]['sustainedtackles'] += sum(
            [player['stats']['sustainedtackles'] for player in match.team2()['roster']]
        )

        if winner:
          if winner == match.coach1():
            coaches[coach1_name]['wins'] += 1
            coaches[coach1_name]['points'] += 3
            coaches[coach2_name]['losses'] += 1
          else:
            coaches[coach2_name]['wins'] += 1
            coaches[coach2_name]['points'] += 3
            coaches[coach1_name]['losses'] += 1
        else:
          coaches[coach1_name]['draws'] += 1
          coaches[coach1_name]['points'] += 1
          coaches[coach2_name]['draws'] += 1
          coaches[coach2_name]['points'] += 1

      return [v for k, v in sorted(coaches.items(), key=lambda item: item[1]['points'], reverse=True)]
