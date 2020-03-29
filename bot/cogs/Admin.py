import discord
import inspect
import traceback

from discord.ext import commands
from bot.helpers import send_embed, logger, send_message, sign, resign, coach_unique, BotHelp, bank_notification
from bot.command import DiscordCommand
from misc.helpers import CardHelper
from models.data_models import db, Transaction, Coach, Tournament
from services import CoachService


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    def is_admin_channel(self, dchannel):
      """checks if it is admin channel"""
      if dchannel.name is not None and dchannel.name == "admin-channel":
          return True
      raise Exception(f"Insuficient rights")

    def coach_collection_msg(self, coach):
      """Creates message out of coaches collection"""
      msg = [
        f"Coach **{coach.name}**\n",
        f"**Bank:** {coach.account.amount} coins\n",
        f"**Tournaments:**",
        *[f'{t.tournament_id}. {t.name}, status: {t.status}, '+
          f'expected start: {t.expected_start_date}' for t in coach.tournaments],
        "\n**Collection**:",
        "-" * 65 + "",
        f"{DiscordCommand.format_pack(CardHelper.sort_cards_by_rarity_with_quatity(coach.active_cards()), show_hidden=True)}",
        "-" * 65 + "\n"
      ]

      admin_in = Tournament.query.filter(
        Tournament.admin == coach.short_name(), Tournament.status.in_(("OPEN", "RUNNING"))
      ).all()

      if admin_in:
        msg.append(f"**Tournament Admin:**")
        msg.extend(
          [(f'{t.tournament_id}. {t.name}, status: {t.status}, channel: {t.discord_channel}')
            for t in admin_in]
        )
      return msg
    
    @commands.command()
    async def adminsign(self, ctx, tournament_id:int, coach_name):
      """Sign coach to a tournament"""
      self.is_admin_channel(ctx.channel)
      coach = await coach_unique(coach_name, ctx)
      if coach is None:
        return
      if not await sign(tournament_id, coach, ctx, admin=True):
        await Exception(f"Could not sign {coach.short_name()}")
      return

    @commands.command()
    async def adminresign(self, ctx, tournament_id:int, coach_name):
      """Resign coach from a tournament"""
      self.is_admin_channel(ctx.channel)
      coach = await coach_unique(coach_name, ctx)
      if coach is None:
        return
      if not await resign(tournament_id, coach, ctx, admin=True):
        await Exception(f"Could not resign {coach.short_name()}")
      return

    @commands.command()
    async def adminrole(self, ctx, action:str, coach_name:str, role:str):
      """Change role for a coach"""
      self.is_admin_channel(ctx.channel)
      if action not in ["add", "remove"]:
        raise ValueError("Invalid action")

      if role not in ["webadmin"]:
        raise ValueError("Invalid role")

      coach = await coach_unique(coach_name, ctx)
      if coach is None:
        return

      if action == "add":
        coach.web_admin = True
      if action == "remove":
        coach.web_admin = False
      db.session.commit()
      await ctx.send(f"Role updated for {coach.short_name()}: {role} - {coach.web_admin}")
      return

    @commands.command()
    async def adminquest(self, ctx, action:str, coach_name:str, quest:str):
      """Set quest for a coach"""
      self.is_admin_channel(ctx.channel)
      if action not in ["on", "off"]:
        raise ValueError("Invalid action")

      if quest not in ["collect3legends", "buildyourownlegend"]:
        raise ValueError("Invalid quest")

      coach = await coach_unique(coach_name, ctx)
      if coach is None:
          return

      if action == "on":
          value = True
      if action == "off":
          value = False
      CoachService.set_achievement(coach, ["quests",quest], value)
      db.session.commit()
      await ctx.send(f"Quest updated for {coach.short_name()}: {quest} - {action}")
      return

    @commands.command()
    async def adminbank(self, ctx, amount:int, coach_name:str, *reason):
      """Add or remove cash from coach"""
      self.is_admin_channel(ctx.channel)

      coach = await coach_unique(coach_name, ctx)
      if coach is None:
          return

      reason = ' '.join(reason) + " - updated by " + str(ctx.author.name)

      tran = Transaction(description=reason, price=-1*amount)
      coach.make_transaction(tran)

      msg = [
          f"Bank for {coach.name} updated to **{coach.account.amount}** coins:\n",
          f"Note: {reason}\n",
          f"Change: {amount} coins"
      ]
      await send_message(ctx.channel, msg)
      await bank_notification(ctx, f"Your bank has been updated by **{amount}** coins - {reason}", coach)

    @commands.command()
    async def adminlist(self, ctx, coach:str):
      """List details of coach"""
      coaches = Coach.find_all_by_name(coach)
      msg = []

      if not coaches:
        msg.append("No coaches found")

      for coach in coaches:
        for messg in self.coach_collection_msg(coach):
          msg.append(messg)
      await send_message(ctx.channel, msg)
      return

    async def cog_command_error(self, ctx, error):
      await ctx.send(error)
      text = type(error).__name__ +": "+str(error)
      logger.error(text)
      logger.error(traceback.format_exc())
      if ctx.command.name == "adminsign":
        await ctx.send(BotHelp.adminsign_help())
      if ctx.command.name == "adminresign":
        await ctx.send(BotHelp.adminresign_help())
      if ctx.command.name == "adminrole":
        await ctx.send(BotHelp.adminrole_help())
      if ctx.command.name == "adminquest":
        await ctx.send(BotHelp.adminquest_help())
      if ctx.command.name == "adminbank":
        await ctx.send(BotHelp.adminbank_help())
      await self.cog_after_invoke(ctx)

    async def cog_after_invoke(self, ctx):
      db.session.remove()

def setup(bot):
    bot.add_cog(Admin(bot))