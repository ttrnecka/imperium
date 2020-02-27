import discord
from .. import dice
from discord.ext import commands
from discord.utils import get


class Bullcanoe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def Bullcanoe(self, ctx, *, member: discord.Member = None):
        """Roll a D2. On a result of 1, get the paddles ready! 
          All players with Strength 4 or higher gain Sprint and Sure Feet. 
        On a result of 2, it definitely rhymes with volcano! 
          All player with Strength 4 or higher gain Mighty Blow and Piling On"""
        
        result = dice.dice(2,1)
        text=['*Get the paddles ready!*','*it definitely rhymes with volcano!*']
        embed = discord.Embed(title='Bullcanoe!', description=text[result[0]-1], color=0xEE8700)
        embed.set_thumbnail(url='https://cdn2.rebbl.net/images/skills/PositiveRookieSkills.png')
        skills = [f'{get(ctx.guild.emojis, name="Sprint") or ""} Sprint & {get(ctx.guild.emojis, name="SureFeet") or ""} Sure Feet', \
                  f'{get(ctx.guild.emojis, name="MightyBlow") or ""} Might Blow & {get(ctx.guild.emojis, name="PilingOn") or ""} Piling On']
        description = f'All player with Strength 4 or higher gain {skills[result[0]-1]}'
        embed.add_field(name=':game_die: :' + ','.join(map(str,result)), value=description, inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Bullcanoe(bot))