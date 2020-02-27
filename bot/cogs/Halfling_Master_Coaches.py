import discord
from .. import dice
from discord.ext import commands


class HalflingMasterCoaches(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def HalflingMasterCoaches(self, ctx, *, member: discord.Member = None):
        """Roll 3D6 at the start of the tournament to see what effect the coaches' detailed playbooks has on the team. 
           For each dice that rolls 4 or more, a member of the crowd spots a potential weakness and joins the coaching
           staff for the tournament, gaining you an assistant coach. Additionally, the opposing coaches are so 
           distracted by the idea of your team actually preparing that they quit on the spot. 
           Each opponent loses a coaching assistant (but only if they have any to lose)."""
        result = dice.dice(6,3)
        embed = discord.Embed(title='Halfling Master Coaches',  color=0xEE8700)
        embed.set_thumbnail(url='https://cdn2.rebbl.net/images/skills/CoachSkill.png')
        success = sum(x > 3 for x in result)
        description = f'You gain {success} assistant coaches.\nAll your opponents loose {success} assistant coaches.'
        embed.add_field(name=':game_die: :' + ','.join(map(str,result)), value=description, inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(HalflingMasterCoaches(bot))