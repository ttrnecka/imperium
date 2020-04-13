import requests
import os
from web import app
from flask_migrate import upgrade
app.app_context().push()

username = 'trnecka'

ROOT = os.path.dirname(__file__)

print("Environment variables")
print(os.environ)

obsolete_files = [
  "bot/command.py"
]
print("Removing obsolete files")
for ofile in obsolete_files:
  file_path = os.path.join(ROOT,ofile)
  if os.path.exists(file_path):
    os.remove(file_path)
print("Done")

print("Upgrading DB models")
upgrade(directory=os.path.join(ROOT,'migrations'))
print("Done")

print("Restarting Bot")
response = requests.post(
  'https://eu.pythonanywhere.com/api/v0/user/{username}/always_on/13/restart/'.format(
      username=username
  ),
  headers={'Authorization': 'Token {token}'.format(token=os.environ['PA_TOKEN'])}
)
if response.status_code == 200:
  print("Successfull restart")
  exit(0)
else:
  print('Got unexpected status code {}: {!r}'.format(response.status_code, response.content))
  exit(1)
