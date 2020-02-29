import discord
import inspect

from discord.ext import commands
from discord.utils import get
from bot.helpers import transform_message
from services import CoachService
from ..actions import special_play

async def send_embed(data, ctx):
    embed = discord.Embed(title=data['embed_title'], description=data['embed_desc'], color=0xEE8700)
    embed.set_thumbnail(url=data['thumbnail_url'])
    for field in data['embed_fields']:
        embed.add_field(name=field['name'], value=transform_message(field['value'], ctx), inline=field['inline'])
    await ctx.send(embed=embed)

class SpecialPlays(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def Bullcanoe(self, ctx):
        """Roll a D2. On a result of 1, get the paddles ready! 
          All players with Strength 4 or higher gain Sprint and Sure Feet. 
        On a result of 2, it definitely rhymes with volcano! 
          All player with Strength 4 or higher gain Mighty Blow and Piling On"""
        
        # calls the same named method from special_play
        data = getattr(special_play, inspect.currentframe().f_code.co_name)()
        await send_embed(data, ctx)

    @commands.command()
    async def TailsNeverFails(self, ctx):
        """Or does it? Roll a D2 three times. 
        On the first roll, a result of 1 grants you a Diving Catch Training Card while a result of 2 grants a Diving Tackle Training Card. 
        On the second roll, a result of 1 grants a Pass Block Training Card while a result of 2 grants a Block Training Card. 
        On the final roll, a result of 1 grants a Sure Feet Training Card while a result of 2 grants a Sure Hands Training Card. 
        Once complete, all Training Cards awarded MUST be used and must also obey doubles restrictions."""
        
        data = getattr(special_play, inspect.currentframe().f_code.co_name)()
        await send_embed(data, ctx)

    @commands.command()
    async def EverythingMustGo(self, ctx):
        """Roll a D6. Each team in the tournament must apply that many -AV injuries to their own team. 
        Each coach may choose which of their own players will be affected, but no player may take more 
        than one -AV injury as a result of this card."""
        
        data = getattr(special_play, inspect.currentframe().f_code.co_name)()
        await send_embed(data, ctx)

    @commands.command()
    async def HalflingMasterCheerleaders(self, ctx):
        """Roll 3D6 at the start of the tournament to see what effect the cheerleaders' dancing has on the team. 
        For each dice that rolls 4 or more, a member of the crowd is so inspired that they join the cheerleading 
        squad and you gain a cheerleader. Additionally, the opposing cheerleaders are so distracted by the 
        intimidating dancing ritual that they quit on the spot. Each opponent loses a cheerleader 
        (but only if they have any to lose)."""

        data = getattr(special_play, inspect.currentframe().f_code.co_name)()
        await send_embed(data, ctx)

    @commands.command()
    async def HalflingMasterCoaches(self, ctx):
        """Roll 3D6 at the start of the tournament to see what effect the coaches' detailed playbooks has on the team. 
           For each dice that rolls 4 or more, a member of the crowd spots a potential weakness and joins the coaching
           staff for the tournament, gaining you an assistant coach. Additionally, the opposing coaches are so 
           distracted by the idea of your team actually preparing that they quit on the spot. 
           Each opponent loses a coaching assistant (but only if they have any to lose)."""
        data = getattr(special_play, inspect.currentframe().f_code.co_name)()
        await send_embed(data, ctx)
    
    @commands.command()
    async def CelebrityMasterChef(self, ctx):
        """All other teams in the tournament roll a D6. On a result of 1-3, they permanently lose a team re-roll
           for the entire tournament! Roll a D6. On a result of 4-6, you gain one team re-roll for the entire
           tournament! If multiple Celebrity Master Chefs are played, each team can only ever lose a maximum
           of one team re-roll across all instances of the card."""
        me = CoachService.discord_user_to_coach(ctx.author)
        data = getattr(special_play, inspect.currentframe().f_code.co_name)(ctx.channel.name, me)
        await send_embed(data, ctx)

    @commands.command()
    async def CoM2000(self, ctx):
        """**Randomise**. In the Deck Inducement phase, open an additional Inducement Skill Pack.
           Each Training Card in the pack must be applied to a random player on your team. This card
           is removed from your collection after use."""
        me = CoachService.discord_user_to_coach(ctx.author)
        data = getattr(special_play, inspect.currentframe().f_code.co_name)(ctx.channel.name, me)
        await send_embed(data, ctx)

    @commands.command()
    async def CoM5000(self, ctx):
        """**Randomise**. In the Deck Inducement phase, open one additional Inducement Skill Pack and
           one additional Inducement Coaching Pack. Each Training Card in the pack must be applied to
           a random player on your team. This card is removed from your collection after use."""
        me = CoachService.discord_user_to_coach(ctx.author)
        data = getattr(special_play, inspect.currentframe().f_code.co_name)(ctx.channel.name, me)
        await send_embed(data, ctx)

    @commands.command()
    async def CoM9000(self, ctx):
        """**Randomise**. Choose one Special Play card that is yet to be resolved. The chosen card must
           now be played as if it had the **Randomise** key word. In the Deck Inducement phase, open three
           additional Inducement Coaching Packs. Each Training Card in the pack must be applied to a random
           player on your team. This card is removed from your collection after use."""
        me = CoachService.discord_user_to_coach(ctx.author)
        data = getattr(special_play, inspect.currentframe().f_code.co_name)(ctx.channel.name, me)
        await send_embed(data, ctx)

    @commands.command()
    async def CoMWithFriends(self, ctx):
        """**Randomise**. Open an Inducement Skill Pack and randomly apply all Training cards across your opponents' teams."""
        me = CoachService.discord_user_to_coach(ctx.author)
        data = getattr(special_play, inspect.currentframe().f_code.co_name)(ctx.channel.name, me)
        await send_embed(data, ctx)
def setup(bot):
    bot.add_cog(SpecialPlays(bot))