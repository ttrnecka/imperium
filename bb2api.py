import requests

class Agent:
    BASE_URL="http://web.cyanide-studio.com/ws/bb2/"
    def __init__(self,api_key):
        self.api_key = api_key

    def team(self,name):
        r = self.call("team", name=name)
        data = r.json() 
        return data

    def match(self,id):
        r = self.call("match", match_id=id)
        data = r.json() 
        return data

    def matches(self, **kwargs):
        if 'limit' not in kwargs:
            kwargs['limit']=10000
        if 'v' not in kwargs:
            kwargs['v']=1
        if 'exact' not in kwargs:
            kwargs['exact']=0
        if 'start' not in kwargs:
            kwargs['start']='2016-01-01'
        if 'league' not in kwargs:
            kwargs['league']='REBBL Imperium'
        r = self.call("matches",**kwargs)
        data = r.json() 
        return data

    def call(self,method,**kwargs):
        URL = self.__class__.BASE_URL + method+"/"
        kwargs['key'] = self.api_key
        kwargs['order'] = 'CreationDate'
        return requests.get(url = URL, params = kwargs) 
