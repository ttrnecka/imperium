import discord
from .. import dice
from discord.ext import commands
from discord.utils import get

from services import TournamentService, CoachService


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
        
        result = dice.dice(2,1)
        text=['*Get the paddles ready!*','*it definitely rhymes with volcano!*']
        embed = discord.Embed(title='Bullcanoe!', description=text[result[0]-1], color=0xEE8700)
        embed.set_thumbnail(url='https://cdn2.rebbl.net/images/skills/PositiveRookieSkills.png')
        skills = [f'{get(ctx.guild.emojis, name="Sprint") or ""} Sprint & {get(ctx.guild.emojis, name="SureFeet") or ""} Sure Feet', \
                  f'{get(ctx.guild.emojis, name="MightyBlow") or ""} Might Blow & {get(ctx.guild.emojis, name="PilingOn") or ""} Piling On']
        description = f'All player with Strength 4 or higher gain {skills[result[0]-1]}'
        embed.add_field(name=':game_die: :' + ','.join(map(str,result)), value=description, inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def TailsNeverFails(self, ctx):
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

    @commands.command()
    async def EverythingMustGo(self, ctx):
        """Roll a D6. Each team in the tournament must apply that many -AV injuries to their own team. 
        Each coach may choose which of their own players will be affected, but no player may take more 
        than one -AV injury as a result of this card."""
        
        result = dice.dice(6,1)
        embed = discord.Embed(title='Everything must go!', color=0xEE8700)
        embed.set_thumbnail(url='https://cdn2.rebbl.net/images/skills/ArmourBust.png')
        description = f'Each team in the tournament must apply **{result[0]} -AV injuries** to their team.\nEach coach may choose which of their own team players will be affected. No player may take more than one -AV injury as a result of this card.'
        embed.add_field(name=':game_die: :' + ','.join(map(str,result)), value=description, inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def HalflingMasterCheerleaders(self, ctx):
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

    @commands.command()
    async def HalflingMasterCoaches(self, ctx):
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
    
    @commands.command()
    async def CelebrityMasterChef(self, ctx):
        """All other teams in the tournament roll a D6. On a result of 1-3, they permanently lose a team re-roll
           for the entire tournament! Roll a D6. On a result of 4-6, you gain one team re-roll for the entire
           tournament! If multiple Celebrity Master Chefs are played, each team can only ever lose a maximum
           of one team re-roll across all instances of the card."""
        
        tourn = TournamentService.get_tournament_using_room(ctx.channel.name)
        coaches = TournamentService.coaches_for(tourn)
        me = CoachService.discord_user_to_coach(ctx.author)
        if not me in coaches:
            raise f"#{me.short_name()} is not signed into the tournament"
        coaches.remove(me)
        
        coach_dices = [(coach, dice.dice(6,1)[0]) for coach in coaches]
        me_dice = (me, dice.dice(6,1)[0])

        embed = discord.Embed(title='Celebrity Master Chef',  color=0xEE8700)
        embed.set_thumbnail(url='https://cdn2.rebbl.net/images/cards/chef_small.png')
        result = dice.dice(6,1)[0]
        if result >= 4:
            description = f'{me.mention()} gains one team re-roll.'
        else:
            description = f'{me.mention()} gains no re-roll.'
        embed.add_field(name=f':game_die: : {result}', value=description, inline=False)

        for coach in coaches:
            result = dice.dice(6,1)[0]
            if result < 4:
                description = f'{coach.mention()} loses one team re-roll.'
            else:
                description = f'{coach.mention()} does not lose re-roll.'
            embed.add_field(name=f':game_die: : {result}', value=description, inline=True)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(SpecialPlays(bot))