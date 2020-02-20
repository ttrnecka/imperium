import re

KEYWORDREG = re.compile(r'\*\*(\S+)\*\*')

def imperium_keywords(text:str):
    return KEYWORDREG.findall(text)