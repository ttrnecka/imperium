import discord
import inspect
import traceback

from discord.ext import commands
from bot.helpers import send_embed, logger, BotHelp
from bot.command import DiscordCommand
from services import PackService, CoachService

from misc.helpers import CardHelper

GEN_PACKS_TMP = ["player", "training", "booster", "special", "skill", "coaching", "positional", "legendary","brawl"]
GEN_QUALITY = ["premium", "budget"]

def check_gentemp_command(pack_type, subtype):
    """Checks the validity if genpacktemp parameters"""  
    if pack_type not in GEN_PACKS_TMP:
        return False
    # skill/coaching/special/booster without quality
    if not subtype and pack_type not in ["skill", "coaching", "special", "booster", "training", "brawl"]:
        return False
    # skill/coaching/special takes not other parameter
    if subtype and pack_type in ["skill", "coaching", "special", "training", "brawl"]:
        return False
    # booster with allowed quality
    if subtype and pack_type == "booster" and subtype not in GEN_QUALITY:
        return False
    # player with teams
    if (subtype and pack_type in ["player", "positional", "legendary"]
            and subtype not in PackService.team_codes()):
        return False

    return True

class Pack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def genpacktemp(self, ctx, pack_type:str, subtype:str=None):
        """Generates special play or inducement packs. These packs are for one time use and are not assigned to coaches permanent collection"""
        #await send_embed(data, ctx)
        if not check_gentemp_command(pack_type, subtype):
          raise discord.ext.commands.CommandError("Invalid usage!")

        coach = CoachService.discord_user_to_coach(ctx.author)
        if coach is None:
          await ctx.send(f"Coach {ctx.author.mention} does not exist. Use !newcoach to create coach first.")
          return

        if pack_type in ["player", "positional", "legendary"]:
            pack = PackService.generate(pack_type, team=subtype)
        elif pack_type in ["training", "special", "skill", "coaching", "brawl"]:
            pack = PackService.generate(pack_type)
        elif pack_type == "booster":
            pack_type = "booster_budget" if not subtype else f"booster_{subtype}"
            pack = PackService.generate(pack_type)

        title = f"**Temporary {PackService.description(pack)}**"
        description = "**Note**: This is one time pack for Special Play or Inducement purposes only!!!"
        pieces = DiscordCommand.format_pack_to_pieces(CardHelper.sort_cards_by_rarity_with_quatity(pack.cards), show_hidden=False)
        efs = []
        efs.append({
            'name': "Cards:",
            'value': pieces['cards'],
            'inline': False,
        })
        for desc in pieces['descriptions']:
          efs.append({
            'name': desc['name'],
            'value': desc['description'],
            'inline': False,
          })
        embed = {
          'embed_title': title,
          'embed_desc': description,
          'thumbnail_url': 'https://cdn2.rebbl.net/images/cards/dice_small.png',
          'embed_fields': efs,
        }
        await send_embed(embed, ctx)

    @genpacktemp.error
    async def genpacktemp_error(self, ctx, error):
      await ctx.send(error)
      await ctx.send(BotHelp.gentemp_help())
      logger.error(error)
      logger.error(traceback.format_exc())

def setup(bot):
    bot.add_cog(Pack(bot))