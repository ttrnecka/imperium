"""REBBL Net api agent modul"""
import requests, json
import functools, urllib
from threading import Timer
from models.base_model import db

def needs_token(func):
    @functools.wraps(func)
    def wrapper_needs_token(*args, **kwargs):
        if not args[0].token:
            args[0].get_token()
        return func(*args, **kwargs)
    return wrapper_needs_token

def encodeURIComponent(str):
    return urllib.parse.quote(str, safe='~()*!.\'')

class Api:
    """REBBL api Cyanide agent"""

    def __init__(self):
        conf = db.get_app().config
        self.client_id = conf["API_CLIENT_ID"]
        self.client_secret = conf["API_CLIENT_SECRET"]
        self.tennant_id = conf["TENNANT_ID"]
        self.api_url = conf["API_URL"]
        self.scope = conf["API_SCOPE"]
        self.token = ""
    
    def _headers(self):
        return {'Authorization': f"Bearer {self.token}"}

    def clear_token(self):
        self.token = ""

    def get_token(self):
        url = f"https://login.microsoftonline.com/{self.tennant_id}/oauth2/v2.0/token"
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        r = requests.post(url=url, data = {
            'client_id':self.client_id,
            'client_secret':self.client_secret,
            'grant_type':"client_credentials",
            'scope':self.scope      
        }, headers=headers)

        self.token = r.json()['access_token']
        t = Timer(59*60, self.clear_token)
        t.start()

    @needs_token
    def get_coach_info(self,coach_id):
        r = requests.get(f"{self.api_url}/api/coach/{coach_id}", headers=self._headers())
        return r.json()

    @needs_token
    def expel(self,competition_id, team_id):
        r = requests.delete(f"{self.api_url}/api/competition/{competition_id}/expel/{team_id}", headers=self._headers())
        return r.json()

    @needs_token
    def search_coach(self, coach_name):
        r = requests.get(f"{self.api_url}/api/coach/{encodeURIComponent(coach_name)}/search", headers=self._headers())
        return r.json()

    @needs_token
    def get_league_info(self, leagueId):
        r = requests.get(f"{self.api_url}/api/league/{leagueId}", headers=self._headers())
        return r.json()

    @needs_token
    def get_competition_info(self, competition_id):
        r = requests.get(f"{self.api_url}/api/competition/{competition_id}", headers=self._headers())
        return r.json()

    @needs_token
    def get_board_info(self, leagueId):
        r = requests.get(f"{self.api_url}/api/league/{leagueId}/board", headers=self._headers())
        return r.json()

    @needs_token
    def delete_competition(self, competition_id):
        r = requests.delete(f"{self.api_url}/api/competition/{competition_id}", headers=self._headers())
        return r.json()

    @needs_token
    def get_competition_ticket_info(self, competition_id):
        r = requests.get(f"{self.api_url}/api/ticket/{competition_id}", headers=self._headers())
        return r.json()

    @needs_token
    def get_tickets(self, competition_id):
        r = requests.get(f"{self.api_url}/api/competition/{competition_id}/tickets", headers=self._headers())
        return r.json()

    @needs_token
    def send_ticket(self, competition_id, owner_id, coach_id, team_id):
        data = {
            "competitionId": competition_id,
            "ownerId": owner_id,
            "coachId": coach_id,
            "teamId": team_id
        }

        headers = self._headers()
        headers['content-type'] = 'application/json'
        r = requests.post(f"{self.api_url}/api/ticket", data=json.dumps(data), headers=headers)
        return r.json()

    @needs_token
    def create_competition(self, league_id, name, owner_id, team_count, competition_type, turn_duration, aging, enhancement, resurrection, custom_teams, mixed_teams, experienced_teams):
        data = {
            "leagueId":league_id,
            "name":name,
            "ownerId":owner_id,
            "teamCount":team_count,
            "competitionType":competition_type,
            "turnDuration": turn_duration,
            "aging":aging,
            "enhancement":enhancement,
            "resurrection":resurrection,
            "customTeams":custom_teams,
            "mixedTeams":mixed_teams,
            "experiencedTeams":experienced_teams
        }

        headers = self._headers()
        headers['content-type'] = 'application/json'
        r = requests.post(f"{self.api_url}/api/competition", data=json.dumps(data), headers=headers)
        return r.json()
