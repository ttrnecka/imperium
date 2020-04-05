import requests
username = 'trnecka'
token = '3cbf4126c5a5f69fba078bf5e4eb6773a2f8d8f2'

response = requests.post(
  'https://eu.pythonanywhere.com/api//api/v0/user/{username}/always_on/13/restart/'.format(
      username=username
  ),
  headers={'Authorization': 'Token {token}'.format(token=token)}
)
if response.status_code == 200:
  print("Successfull restart")
  exit(0)
else:
  print('Got unexpected status code {}: {!r}'.format(response.status_code, response.content))
  exit(1)