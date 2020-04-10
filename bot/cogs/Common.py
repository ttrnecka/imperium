import discord
import inspect

from discord.ext import commands
from bot.command import DiscordCommand
from bot.actions import common
from bot.base_cog import ImperiumCog
from misc.helpers import CardHelper
from models.data_models import db, Coach, Tournament
from services import CoachService

RULES_LINK = "https://bit.ly/2P9Y07F"

class Common(ImperiumCog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def injury(self, ctx):
        """Roll a D8 to see what inujury to apply"""

        # calls the same named method from special_play
        data = getattr(common, inspect.currentframe().f_code.co_name)()
        await self.send_embed(data, ctx)

    @commands.command()
    async def newcoach(self, ctx):
      """Creates new coach account"""
      coach = CoachService.discord_user_to_coach(ctx.author)
      if coach:
        await ctx.send(f"**{ctx.author.mention}** account exists already")
      elif Coach.get_by_discord_id(ctx.author.id, deleted=True):
        await ctx.send(f"**{ctx.author.mention}** account is inactive, use the web page to activate it")
      else:
        coach = CoachService.new_coach(ctx.author, ctx.author.id)
        msg = f"**{ctx.author.mention}** account created\n" \
            + f"**Bank:** {coach.account.amount} coins\n" \
            + f"**Rules**: <{RULES_LINK}>"
        await ctx.send(msg)

    @commands.command()
    async def list(self, ctx, all=None):
      """List details about coach's collection"""
      with db.session.no_autoflush:
        coach = CoachService.discord_user_to_coach(ctx.author)
        show_starter = True if all == "all" else False

        if coach is None:
          await ctx.send(f"Coach {ctx.author.mention} does not exist. Use !newcoach to create coach first.")
          return

        all_cards = coach.active_cards()
        sp_msg = " (with Starter Pack)"
        if not show_starter:
          all_cards = [card for card in all_cards if not card.is_starter]
          sp_msg = ""

        msg = [
          f"**Bank:** {coach.account.amount} coins\n",
          f"**Tournaments:**",
          *[f'{t.tournament_id}. {t.name}, status: {t.status}, expected start: {t.expected_start_date}' for t in coach.tournaments],
          f"\n**Collection**{sp_msg}:",
          "-" * 65 + "",
          DiscordCommand.format_pack(CardHelper.sort_cards_by_rarity_with_quatity(all_cards), show_hidden=True),
          "-" * 65 + "\n"
        ]

        if coach.duster:
          msg.append(f"**Dusting** - {coach.duster.type} - {coach.duster.status}")

        admin_in = Tournament.query.filter(Tournament.admin == coach.short_name(), Tournament.status.in_(("OPEN", "RUNNING"))).all()

        if admin_in:
          msg.append(f"**Tournament Admin:**")
          msg.extend([f'{t.tournament_id}. {t.name}, status: {t.status}, channel: {t.discord_channel}' for t in admin_in])

        free_packs = coach.get_freepacks()
        if free_packs:
          msg.append(f"**Free Packs:**")
          msg.append((', ').join(free_packs))

        await self.send_message(ctx.author, msg)
        await ctx.send("Info sent to PM")

def setup(bot):
    bot.add_cog(Common(bot))