import requests

class Agent:
    BASE_URL="http://web.cyanide-studio.com/ws/bb2/"
    def __init__(self,api_key):
        self.api_key = api_key

    def team(self,name):
        r = self.call("team", name=name)
        data = r.json() 
        return data

    def call(self,method,**kwargs):
        URL = self.__class__.BASE_URL + method+"/"
        kwargs['key'] = self.api_key
        return requests.get(url = URL, params = kwargs) 
