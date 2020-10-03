"""Various helpers"""
import os
import logging
import discord
from discord.ext.commands import DefaultHelpCommand, HelpCommand
from logging.handlers import RotatingFileHandler
from models.data_models import Tournament, Coach
from services import TournamentService

ROOT = os.path.dirname(__file__)
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
logger.propagate = False
handler = RotatingFileHandler(
    os.path.join(ROOT,'..', 'logs','discord.log'), maxBytes=1000000,
    backupCount=5, encoding='utf-8', mode='a'
)
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

wastebasket_emoji = '🗑️'

class LongMessage:
    """Class to handle long message sending in chunks"""
    def __init__(self, channel, block=False):
        self.limit = 1994 # to allow ``` before and after
        self.parts = []
        self.channel = channel
        self.block = block

    def add(self, part):
        """Adds part of long message"""
        self.parts.append(part)

    async def send(self):
        """sends the message to channel in limit chunks"""
        for chunk in self.chunks():
            await self.channel.send(chunk)
        logger.info("Response:\n%s", '\n'.join(self.lines()))

    def lines(self):
        """transforms the message to lines"""
        lines = []
        for part in self.parts:
            lines.extend(part.split("\n"))
        return lines

    def chunks(self):
        """Transform the lines to limit sized chunks"""
        lines = self.lines()
        while True:
            msg = "```asciidoc\n" if self.block else ""
            if not lines:
                break
            while lines and len(msg + lines[0]) < self.limit:
                msg += lines.pop(0) + "\n"
            if self.block:
                msg += '```'
            yield msg

async def sign(tournament_id, coach, ctx, admin=False):
  """routine to sign a coach to tournament"""
  if admin:
      tourn = Tournament.query.filter_by(tournament_id=tournament_id).one_or_none()
  else:
      tourn = Tournament.query.filter_by(
          status="OPEN", tournament_id=tournament_id
      ).one_or_none()
  if not tourn:
      raise ValueError("Incorrect **tournament_id** specified")

  signup = TournamentService.register(tourn, coach, admin)
  add_msg = "" if signup.mode == "active" else " as RESERVE"
  await ctx.send(f"Signup succeeded{add_msg}!!!")
  return True

async def resign(tournament_id, coach, ctx, admin=False):
  """routine to resign a coach to tournament"""
  if admin:
      tourn = Tournament.query.filter_by(tournament_id=tournament_id).one_or_none()
  else:
      tourn = Tournament.query.filter_by(
          status="OPEN", tournament_id=tournament_id
      ).one_or_none()

  if not tourn:
      raise ValueError("Incorrect **tournament_id** specified")

  if TournamentService.unregister(tourn, coach, admin):
      await ctx.send(f"Resignation succeeded!!!")

      coaches = [
          discord.utils.get(ctx.guild.members, id=str(signup.coach.disc_id))
          for signup in TournamentService.update_signups(tourn)
      ]
      msg = [coach.mention for coach in coaches if coach]
      msg.append(f"Your signup to {tourn.name} has been updated from RESERVE to ACTIVE")

      if len(msg) > 1:
          tourn_channel = discord.utils.get(
              ctx.bot.get_all_channels(), name='tournament-notice-board'
          )
          if tourn_channel:
              await tourn_channel.send("\n".join(msg))
          else:
              await ctx.send("\n".join(msg))
  return True

async def coach_unique(name, ctx):
  """finds uniq coach by name"""
  coaches = Coach.find_all_by_name(name)
  if not coaches:
      raise ValueError(f"<coach> __{name}__ not found!!!")

  if len(coaches) > 1:
      emsg = f"<coach> __{name}__ not **unique**!!!\n"
      emsg += "Select one: "
      for coach in coaches:
          emsg += coach.name
          emsg += " "
      await ctx.send(emsg)
      return None
  return coaches[0]

class ImperiumHelpCommand(DefaultHelpCommand):
  async def send_pages(self):
    """A helper utility to send the page output from :attr:`paginator` to the destination."""
    destination = self.get_destination()
    for page in self.paginator.pages:
        msg = await destination.send(page)
        await msg.add_reaction(wastebasket_emoji)