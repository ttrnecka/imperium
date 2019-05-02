# Works with Python 3.6
import logging
from logging.handlers import RotatingFileHandler
import discord
import os

from imperiumbase import ImperiumSheet
from web import db, create_app
from sqlalchemy import func
from models.data_models import Coach, Account, Card, Pack, Transaction, TransactionError, Tournament, TournamentSignups
from misc.helpers import CardHelper
from services import PackService, SheetService, CoachService, CardService, TournamentService, DusterService, RegistrationError

app = create_app()
app.app_context().push()

ROOT = os.path.dirname(__file__)

with open(os.path.join(ROOT, 'config/TOKEN'), 'r') as token_file:
    TOKEN=token_file.read()
client = discord.Client()

@client.event
async def on_ready():
    print("Deleting old coaches")
    for coach in Coach.query.with_deleted().filter_by(deleted=True):
        db.session.delete(coach)

    print("Updating existing coaches")    
    for coach in Coach.query.with_deleted().all():
        member = discord.utils.get(client.get_all_members(), name=coach.short_name(), discriminator=coach.discord_id())
        if member is not None:
            print(f"found user {coach.name} with ID {member.id}")
            coach.disc_id = member.id
            print(coach.disc_id)

    db.session.commit()
    for coach in Coach.query.with_deleted().filter_by(disc_id=0).all():
        print(f"coach {coach.name} discord id not found")
    client.logout()
client.run(TOKEN)