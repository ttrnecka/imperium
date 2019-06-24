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
py dbcreate.py
```

Set migration revision. When you create db all the migration are skipped. So it is required to set the current revision on DB manually

```
py -m flask db show head
```

Use the revision from previous step

```
py flask stamp <revison>
```
Populate local history
```
py update_stats.py
```
Run bot

```
py bot.py
```
Check in the development discord if the bot came up.

Run bot

```
py web.py
```


## Authors

* **Tomas Trnecka**