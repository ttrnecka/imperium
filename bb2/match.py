"""Match helpers"""

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
            coaches[coach['coachname']] = {'name': coach['coachname'], 'wins':0, 'losses':0, 'draws':0, 'matches':0, 'points':0}
        winner = match.winner()
        coaches[match.coach1()['coachname']]['matches'] += 1
        coaches[match.coach2()['coachname']]['matches'] += 1
        if winner:
          if winner == match.coach1():
            coaches[match.coach1()['coachname']]['wins'] += 1
            coaches[match.coach1()['coachname']]['points'] += 3
            coaches[match.coach2()['coachname']]['losses'] += 1
          else:
            coaches[match.coach2()['coachname']]['wins'] += 1
            coaches[match.coach2()['coachname']]['points'] += 3
            coaches[match.coach1()['coachname']]['losses'] += 1
        else:
          coaches[match.coach1()['coachname']]['draws'] += 1
          coaches[match.coach1()['coachname']]['points'] += 1
          coaches[match.coach2()['coachname']]['draws'] += 1
          coaches[match.coach2()['coachname']]['points'] += 1

      return [v for k, v in sorted(coaches.items(), key=lambda item: item[1]['points'], reverse=True)]
