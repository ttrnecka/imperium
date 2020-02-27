import discord
from .. import dice
from discord.ext import commands
from discord.utils import get


class TailsNeverFails(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def TailsNeverFails(self, ctx, *, member: discord.Member = None):
        """Or does it? Roll a D2 three times. 
        On the first roll, a result of 1 grants you a Diving Catch Training Card while a result of 2 grants a Diving Tackle Training Card. 
        On the second roll, a result of 1 grants a Pass Block Training Card while a result of 2 grants a Block Training Card. 
        On the final roll, a result of 1 grants a Sure Feet Training Card while a result of 2 grants a Sure Hands Training Card. 
        Once complete, all Training Cards awarded MUST be used and must also obey doubles restrictions."""
        
        result = dice.dice(2,3)
        embed = discord.Embed(title='Tails Never Fails', description='Or does it?',  color=0xEE8700)
        embed.set_thumbnail(url='https://cdn2.rebbl.net/images/skills/PrehensileTail.png')
        embed.add_field(name=':game_die: :' + ','.join(map(str,result)), value='You **must** use the following skills and **obey doubles restrictions**.', inline=False)
        first =[f'{get(ctx.guild.emojis, name="DivingCatch") or ""} Diving Catch', f'{get(ctx.guild.emojis, name="DivingTackle") or ""} Diving Tackle']
        second=[f'{get(ctx.guild.emojis, name="PassBlock") or ""} Pass Block', f'{get(ctx.guild.emojis, name="Block") or ""} Block']
        third =[f'{get(ctx.guild.emojis, name="SureFeet") or ""} Sure Feet', f'{get(ctx.guild.emojis, name="SureHands") or ""} Sure Hands']
        embed.add_field(name='First roll', value=first[result[0]-1], inline=True)
        embed.add_field(name='Second roll', value=second[result[1]-1], inline=True)
        embed.add_field(name='Third roll', value=third[result[2]-1], inline=True)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(TailsNeverFails(bot))