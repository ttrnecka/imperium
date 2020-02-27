import discord
from .. import dice
from discord.ext import commands

# Roll 3D6 at the start of the tournament to see what effect the cheerleaders' dancing has on the team. 
# For each dice that rolls 4 or more, a member of the crowd is so inspired that they join the cheerleading 
# squad and you gain a cheerleader. Additionally, the opposing cheerleaders are so distracted by the 
# intimidating dancing ritual that they quit on the spot. Each opponent loses a cheerleader 
# (but only if they have any to lose).

class HalflingMasterCheerleaders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def HalflingMasterCheerleaders(self, ctx, *, member: discord.Member = None):
        """Roll 3D6 at the start of the tournament to see what effect the cheerleaders' dancing has on the team. 
        For each dice that rolls 4 or more, a member of the crowd is so inspired that they join the cheerleading 
        squad and you gain a cheerleader. Additionally, the opposing cheerleaders are so distracted by the 
        intimidating dancing ritual that they quit on the spot. Each opponent loses a cheerleader 
        (but only if they have any to lose)."""

        result = dice.dice(6,3)
        embed = discord.Embed(title='Halfling Master Cheerleaders',  color=0xEE8700)
        embed.set_thumbnail(url='https://cdn2.rebbl.net/images/sponsors/mcmurtys.png')
        success = sum(x > 3 for x in result)
        description = f'You gain {success} cheerleaders.\nAll your opponents loose {success} cheerleaders.'
        embed.add_field(name=':game_die: :' + ','.join(map(str,result)), value=description, inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(HalflingMasterCheerleaders(bot))