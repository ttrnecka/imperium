import discord
import traceback
import random

from discord.ext import commands
from bot.helpers import logger, BotHelp
from bot.actions import common
from models.data_models import db, Tournament as Tourn, ConclaveRule
from misc.helpers import image_merge
from services import TournamentService, CoachService


async def sign(tournament_id, coach, ctx, admin=False):
  """routine to sign a coach to tournament"""
  if admin:
      tourn = Tourn.query.filter_by(tournament_id=tournament_id).one_or_none()
  else:
      tourn = Tourn.query.filter_by(
          status="OPEN", tournament_id=tournament_id
      ).one_or_none()
  if not tourn:
      raise Exception("Incorrect **tournament_id** specified")

  signup = TournamentService.register(tourn, coach, admin)
  add_msg = "" if signup.mode == "active" else " as RESERVE"
  await ctx.send(f"Signup succeeded{add_msg}!!!")
  return True

async def resign(tournament_id, coach, ctx, admin=False):
  """routine to resign a coach to tournament"""
  if admin:
      tourn = Tourn.query.filter_by(tournament_id=tournament_id).one_or_none()
  else:
      tourn = Tourn.query.filter_by(
          status="OPEN", tournament_id=tournament_id
      ).one_or_none()

  if not tourn:
      raise Exception("Incorrect **tournament_id** specified")

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

async def conclave(ctype, level, ctx):
  rule1 = random.choice(getattr(ConclaveRule,f'{ctype}s')())
  rule2 = None

  if ctype == "blessing":
    rule2 = random.choice(getattr(ConclaveRule,f'{ctype}s')())
    while rule1.same_class(rule2):
      rule2 = random.choice(getattr(ConclaveRule,f'{ctype}s')())

  r1_file = rule1.img(level)
  files = []
  if ctype == "blessing":
    r2_file = rule2.img(level)
    if r1_file and r2_file:
      files = [r1_file,ConclaveRule.divider_img(),r2_file]
  else:
    if r1_file:
      files = [r1_file]

  if files:
    buf = image_merge(files)
    d_file = discord.File(image_merge(files), filename=f"{ctype}.png")
    buf.close()
    async with ctx.channel.typing():
      await ctx.send(f"Conclave is undergoing the ritual, please stand by...")
      await ctx.send(file=d_file)
  else:
    if rule2:
      await ctx.send(f"Conclave casts upon you:\n**{rule1.name}**: {getattr(rule1,f'level{level}_description')}\nOR\n**{rule2.name}**: {getattr(rule2,f'level{level}_description')}")
    else:
      await ctx.send(f"Conclave casts upon you **{rule1.name}**: {getattr(rule1,f'level{level}_description')}")
  return
class Tournament(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def sign(self, ctx, tournament_id:int):
      """Sign to the tournament"""
      coach = CoachService.discord_user_to_coach(ctx.author)
      if coach is None:
          await ctx.send(f"Coach {ctx.author.mention} does not exist. Use !newcoach to create coach first.")
          return
      await sign(tournament_id, coach, ctx)
      return

    @commands.command()
    async def resign(self, ctx, tournament_id:int):
      """Resign from the tournament"""
      coach = CoachService.discord_user_to_coach(ctx.author)
      if coach is None:
          await ctx.send(f"Coach {ctx.author.mention} does not exist. Use !newcoach to create coach first.")
          return
      await resign(tournament_id, coach, ctx)
      return

    @commands.command()
    async def blessing(self, ctx, level:int):
      """Generates blessing"""
      await conclave("blessing", level, ctx)

    @commands.command()
    async def curse(self, ctx, level:int):
      """Generates curse"""
      await conclave("curse", level, ctx)

    @commands.command()
    async def left(self, ctx):
      """List coaches left to finish current tournament phase"""
      room = ctx.channel.name

      coaches = TournamentService.left_phase(room)
      phase = TournamentService.get_phase(room)
      msg = f"**Phase:** {phase}\n**Left:**\n"
      for coach in coaches:
        msg += f"{coach.short_name()}\n"
      await ctx.send(msg)

    @commands.command()
    async def done(self, ctx):
      """Confirm Special Play, Inducement and Blood Bowl phase"""
      coach = CoachService.discord_user_to_coach(ctx.author)
      room = ctx.channel.name

      if coach is None:
        await ctx.send(f"Coach {ctx.author.mention} does not exist. Use !newcoach to create coach first.")
        return

      if TournamentService.get_phase(room) in [Tourn.DB_PHASE, Tourn.LOCKED_PHASE]:
          msg = "This command has no effect in this phase. Go and commit your deck!"
      elif TournamentService.confirm_phase(coach,room):
          msg = f"Phase confirmed for {coach.short_name()}"
      else:
          msg = "No deck found!"
      await ctx.send(msg)

    async def cog_command_error(self, ctx, error):
      await ctx.send(error)
      text = type(error).__name__ +": "+str(error)
      logger.error(text)
      logger.error(traceback.format_exc())

      if ctx.command.name == "sign":
        await ctx.send(BotHelp.sign_help())
      if ctx.command.name == "resign":
        await ctx.send(BotHelp.resign_help())
      if ctx.command.name == "curse":
        await ctx.send(BotHelp.curse_help())
      if ctx.command.name == "blessing":
        await ctx.send(BotHelp.blessing_help())

      await self.cog_after_invoke(ctx)

    async def cog_after_invoke(self, ctx):
      db.session.remove()

  
def setup(bot):
    bot.add_cog(Tournament(bot))