"""REBBL Net api agent modul"""
import requests, json
from models.base_model import db

class REBBL_CYANIDE_API:
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

    def get_coach_info(self,coach_id):
        if not self.token:
            self.get_token()
        r = requests.get(f"{self.api_url}/api/coach/{coach_id}", headers=_headers())
        return r.json()
