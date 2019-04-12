# REBBL Imperium 

This package include s both bot and web application.

Bot to automate pack generation and admin tasks for REBBL Imperium game based on Blood Bowl 2

Web application to display the current coaches and their cards

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 

### Prerequisites

Download the copy from git HUB. For development obtain TOKEN, MASTERSHEET_ID and client_secret.json and config.py from the author. Ask the author to add you to the testing discord server.

```
github clone https://github.com/ttrnecka/imperium.git
```

Install python 3.6. Version 3.7 is not supported.

### Installing

Install the dependencies

```
pip install -r requirements.txt
```

Create a DB

```
py -3.6 dbcreate.py
```

Set migration revision. When you create db all the migration are skipped. So it is required to set the current revision on DB manually

```
py -3.6 flask db head
```

Use the revision from previous step

```
py -3.6 flask stamp <revison>
```
Run bot

```
py -3.6 bot.py
```
Check in the development discord if the bot came up.

Run bot

```
py -3.6 web.py
```


## Authors

* **Tomas Trnecka**