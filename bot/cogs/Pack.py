import discord
import inspect
import traceback

from discord.ext import commands
from bot.helpers import send_embed, auto_cards
from bot.command import DiscordCommand
from services import PackService, CoachService
from models.data_models import db, Pack as Pck, TransactionError, Transaction
from bot.base_cog import ImperiumCog

from misc.helpers import CardHelper

GEN_PACKS = ["player", "training", "booster", "special"]
GEN_PACKS_TMP = ["player", "training", "booster", "special", "skill", "coaching", "positional", "legendary","brawl"]
GEN_QUALITY = ["premium", "budget"]

def gen_help():
    """help message"""
    msg = "!genpack command generates new pack and assigns it to coach. The coach "
    msg += "needs to have enough coins to buy the pack or dust appropriate cards.\n \n"
    msg += "= Booster budget pack =\n"
    msg += "Content: 5 cards of any type\n"
    msg += f"Price: {PackService.PACK_PRICES['booster_budget']} coins\n"
    msg += "Rarity: 1 Rare and higher rarity, 4 Common and higher rarity\n"
    msg += "Command: !genpack booster\n \n"

    msg += "= Booster premium pack =\n"
    msg += "Content: 5 cards any type\n"
    msg += f"Price: {PackService.PACK_PRICES['booster_premium']} coins\n"
    msg += "Rarity: Rare and higher\n"
    msg += "Command: !genpack booster premium\n \n"

    msg += "= Training pack =\n"
    msg += "Content: 3 training type cards\n"
    msg += f"Price: {PackService.PACK_PRICES['training']} coins. "
    msg += "Available only by using Drills\n"
    msg += "Rarity: Common or higher\n"
    msg += "Command: !genpack training\n \n"

    msg += "= Special play pack =\n"
    msg += "Content: 3 special play type cards\n"
    msg += f"Price: {PackService.PACK_PRICES['training']} coins. "
    msg += "Available only by using Drills\n"
    msg += "Rarity: Common or higher\n"
    msg += "Command: !genpack special\n \n"

    msg += "= Player pack =\n"
    msg += "Content: 3 player type cards\n"
    msg += f"Price: {PackService.PACK_PRICES['player']} coins. "
    msg += "First player pack free of charge. Next available only by using Tryouts.\n"
    msg += "Rarity: Rare or higher\n"
    msg += "Command: !genpack player <team>\n"
    msg += "where <team> is one of following:\n"
    for team in PackService.MIXED_TEAMS:
        msg += "\t"+team["code"] +" - "+ team["name"] +f" ({', '.join(team['races'])})\n"
    return msg

def gentemp_help():
    """help message"""
    msg = "!genpacktemp command generates temporary packs. "
    msg += "These packs are for one time use"
    msg += "permanent collection.\n \n"
    msg += "= Booster budget pack =\n"
    msg += "Content: 5 cards\n"
    msg += "Rarity: 1 Rare+, 4 Common+\n"
    msg += "Command: !genpacktemp booster\n \n"

    msg += "= Booster premium pack =\n"
    msg += "Content: 5 cards any type\n"
    msg += "Rarity: Rare+\n"
    msg += "Command: !genpacktemp booster premium\n \n"

    msg += "= Training pack =\n"
    msg += "Content: 3 training type cards\n"
    msg += "Rarity: Common+\n"
    msg += "Command: !genpacktemp training\n \n"

    msg += "= Inducement Skill pack =\n"
    msg += "Content: 5 training type cards\n"
    msg += "Rarity: Common+\n"
    msg += "Command: !genpacktemp skill\n \n"

    msg += "= Inducement Coaching pack =\n"
    msg += "Content: 3 training type cards\n"
    msg += "Rarity: Rare or Epic\n"
    msg += "Command: !genpacktemp coaching\n \n"

    msg += "= Special Play pack (incl. Inducement) =\n"
    msg += "Content: 3 special play type cards\n"
    msg += "Rarity: Common+\n"
    msg += "Command: !genpacktemp special\n \n"

    msg += "= Player pack =\n"
    msg += "Content: 3 player type cards\n"
    msg += "Rarity: Rare+\n"
    msg += "Command: !genpacktemp player <team>\n \n"

    msg += "= Inducement Positional pack =\n"
    msg += "Content: 3 positional player type cards\n"
    msg += "Rarity: Rare+\n"
    msg += "Command: !genpacktemp positional <team>\n \n"

    msg += "= Legendary pack =\n"
    msg += "Content: 1 legendary player type cards\n"
    msg += "Rarity: Legendary\n"
    msg += "Command: !genpacktemp legendary <team>\n \n"

    msg += "where <team> is one of following:\n"
    for team in PackService.MIXED_TEAMS:
        msg += "\t"+team["code"] +" - "+ team["name"] +f" ({', '.join(team['races'])})\n"

    msg += " \n"
    msg += "= Bloodweiser pack =\n"
    msg += "Content: 3 Bloodweiser Brawl Boost type cards\n"
    msg += "Command: !genpacktemp brawl\n"
    return msg

def check_gentemp_command(pack_type, subtype):
    """Checks the validity of genpacktemp parameters"""  
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

def check_gen_command(pack_type, subtype):
    """Checks the validity of genpack parameters"""
    if pack_type not in GEN_PACKS:
        return False
    # training/booster/special without quality
    if not subtype and pack_type not in ["training", "booster", "special"]:
        return False
    # training/special takes not other parameter
    if subtype and pack_type in ["training", "special"]:
        return False
    # booster with allowed quality
    if subtype and pack_type == "booster" and subtype not in GEN_QUALITY:
        return False
    # player with teams
    if subtype and pack_type == "player" and subtype not in PackService.team_codes():
        return False
    return True

class Pack(ImperiumCog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(help=gentemp_help())
    async def genpacktemp(self, ctx, pack_type:str, subtype:str=None):
        """Generates special play or inducement packs. These packs are for one time use and are not assigned to coaches permanent collection"""
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

    @commands.command(help=gen_help())
    async def genpack(self, ctx, pack_type:str, subtype:str=None):
        """Generates packs"""
        if not check_gen_command(pack_type, subtype):
          raise discord.ext.commands.CommandError("Invalid usage!")

        coach = CoachService.discord_user_to_coach(ctx.author)
        if coach is None:
          await ctx.send(f"Coach {ctx.author.mention} does not exist. Use !newcoach to create coach first.")
          return

        pp_count = db.session.query(Pck.id).filter_by(coach_id=coach.id, pack_type="player").count()

        if pack_type == "player":
          first = True if pp_count == 0 else False
          pack = PackService.generate(pack_type, team=subtype, first=first, coach=coach)
        elif pack_type == "training" or pack_type == "special":
          pack = PackService.generate(pack_type, coach=coach)
        elif pack_type == "booster":
          pack_type = "booster_budget" if not subtype else f"booster_{subtype}"
          pack = PackService.generate(pack_type, coach=coach)

        duster = coach.duster
        duster_on = False
        duster_txt = ""
        if pp_count > 0 and duster and duster.status == "COMMITTED":
          if (pack_type == "player" and duster.type == "Tryouts" or
                pack_type == "training" and duster.type == "Drills" or
                pack_type == "special" and duster.type == "Drills"):
            duster_on = True
            duster_txt = f" ({duster.type})"
            db.session.delete(duster)

        free_packs = coach.get_freepacks()

        if pack_type in ["player"] and not duster_on:
          if pack_type in free_packs:
            pack.price = 0
            coach.remove_from_freepacks(pack_type)
          else:
            raise TransactionError(
              "You need to commit Tryouts or earn the pack through" +
              " Achievements to be able to generate this pack!"
            )

        if pack_type in ["training", "special"] and not duster_on:
          raise TransactionError(
            "You need to commit Drills to be able to generate this pack!"
          )

        if pack_type in ["booster_budget", "booster_premium"]:
          if pack_type in free_packs:
            pack.price = 0
            coach.remove_from_freepacks(pack_type)

        tran = Transaction(pack=pack, price=pack.price, description=PackService.description(pack))
        coach.make_transaction(tran)

        title = f"**{PackService.description(pack)}** for **{ctx.message.author.name}** - **{pack.price}** coins{duster_txt}"
        description = f"**Bank:** {coach.account.amount} coins"
        pieces = DiscordCommand.format_pack_to_pieces(CardHelper.sort_cards_by_rarity_with_quatity(pack.cards))

        await auto_cards(pack, ctx)
        CoachService.check_collect_three_legends_quest(coach)

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

def setup(bot):
    bot.add_cog(Pack(bot))