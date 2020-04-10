import discord
import random

from sqlalchemy import func
from discord.ext import commands
from models.data_models import db, Tournament as Tourn, ConclaveRule, TournamentSignups, Transaction
from misc.helpers import image_merge, represents_int
from services import TournamentService, CoachService, CompetitionService
from bot.base_cog import ImperiumCog
from bot.helpers import send_message, sign, resign, bank_notification

class Tournament(ImperiumCog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    async def conclave(self, ctype, level, ctx):
      rule1 = random.choice(getattr(ConclaveRule,f'{ctype}s')())
      rule2 = None

      if ctype == "blessing":
        rule2 = random.choice(getattr(ConclaveRule,f'{ctype}s')())
        while rule1.same_class(rule2):
          rule2 = random.choice(getattr(ConclaveRule,f'{ctype}s')())

      r1_file = rule1.img(level)
      files = []
      if ctype == "blessing":
        r2_file = rule2.img(level)
        if r1_file and r2_file:
          files = [r1_file,ConclaveRule.divider_img(),r2_file]
      else:
        if r1_file:
          files = [r1_file]

      if files:
        buf = image_merge(files)
        d_file = discord.File(image_merge(files), filename=f"{ctype}.png")
        buf.close()
        async with ctx.channel.typing():
          await ctx.send(f"Conclave is undergoing the ritual, please stand by...")
          await ctx.send(file=d_file)
      else:
        if rule2:
          await ctx.send(f"Conclave casts upon you:\n**{rule1.name}**: {getattr(rule1,f'level{level}_description')}\nOR\n**{rule2.name}**: {getattr(rule2,f'level{level}_description')}")
        else:
          await ctx.send(f"Conclave casts upon you **{rule1.name}**: {getattr(rule1,f'level{level}_description')}")
      return

    @commands.command()
    async def ransom(self, ctx):
      """Pay ransom for the kidnapped player"""
      coach = CoachService.discord_user_to_coach(ctx.author)
      if coach is None:
          await ctx.send(f"Coach {ctx.author.mention} does not exist. Use !newcoach to create coach first.")
          return
      reason = 'Ransom'
      amount = -5
      tran = Transaction(description=reason, price=-1*amount)
      coach.make_transaction(tran)

      msg = [
          f"Bank for {coach.name} updated to **{coach.account.amount}** coins:\n",
          f"Note: {reason}\n",
          f"Change: {amount} coins"
      ]
      await send_message(ctx.channel, msg)
      await bank_notification(ctx, f"Your bank has been updated by **{amount}** coins - {reason}", coach)
      return

    @commands.command()
    async def sign(self, ctx, tournament_id:int):
      """Signs coach to tournament
      USAGE:
      !sign <tournament_id>
        <tournament_id>: id of tournament from !complist
      """
      coach = CoachService.discord_user_to_coach(ctx.author)
      if coach is None:
          await ctx.send(f"Coach {ctx.author.mention} does not exist. Use !newcoach to create coach first.")
          return
      await sign(tournament_id, coach, ctx)
      return

    @commands.command()
    async def resign(self, ctx, tournament_id:int):
      """Resigns coach from tournament
      USAGE:
      !resign <tournament_id>
        <tournament_id>: id of tournament from !complist
      """
      coach = CoachService.discord_user_to_coach(ctx.author)
      if coach is None:
          await ctx.send(f"Coach {ctx.author.mention} does not exist. Use !newcoach to create coach first.")
          return
      await resign(tournament_id, coach, ctx)
      return

    @commands.command()
    async def blessing(self, ctx, level:int):
      """Returns random blessing
      USAGE:
      !blessing <level>
        <level>: 1,2 or 3
      """
      await self.conclave("blessing", level, ctx)

    @commands.command()
    async def curse(self, ctx, level:int):
      """Returns random curse
      USAGE:
      !curse <level>
        <level>: 1,2 or 3
      """
      await self.conclave("curse", level, ctx)

    @commands.command()
    async def left(self, ctx):
      """Lists coaches left to finish current tournament phase"""
      room = ctx.channel.name

      coaches = TournamentService.left_phase(room)
      phase = TournamentService.get_phase(room)
      msg = f"**Phase:** {phase}\n**Left:**\n"
      for coach in coaches:
        msg += f"{coach.short_name()}\n"
      await ctx.send(msg)

    @commands.command()
    async def done(self, ctx):
      """Confirms Special Play, Inducement and Blood Bowl phase"""
      coach = CoachService.discord_user_to_coach(ctx.author)
      room = ctx.channel.name

      if coach is None:
        await ctx.send(f"Coach {ctx.author.mention} does not exist. Use !newcoach to create coach first.")
        return

      if TournamentService.get_phase(room) in [Tourn.DB_PHASE, Tourn.LOCKED_PHASE]:
          msg = "This command has no effect in this phase. Go and commit your deck!"
      elif TournamentService.confirm_phase(coach,room):
          msg = f"Phase confirmed for {coach.short_name()}"
      else:
          msg = "No deck found!"
      await ctx.send(msg)

    @commands.command()
    async def complist(self, ctx, *args):
      """List all available tournaments"""
      if len(args) == 1 and not (represents_int(args[0]) or args[0] in ["all", "full", "free"]):
        raise ValueError(f"**{args[0]}** is not a number or 'all', 'full' or 'free'!!!")

      if len(args) > 1:
        if args[0] not in ["all", "full", "free"]:
          raise ValueError(f"**{args[0]}** is not 'all', 'full' or 'free'!!!")

        if args[1] not in ["bigo", "gman", "rel"]:
          raise ValueError(f"**{args[1]}** is not 'bigo', 'gman' or 'rel'!!!")

      #detail
      if len(args) == 1 and represents_int(args[0]):
        tourn = Tourn.query.filter_by(tournament_id=int(args[0])).one_or_none()
        if not tourn:
          raise ValueError(f"Tournament **id** does not exist")
        coaches = tourn.coaches.filter(TournamentSignups.mode == "active").all()
        count = len(coaches)

        msg = [
            f"__**{tourn.name}**__  - **{tourn.status}**\n",
            f"**Type**: {tourn.region} - {tourn.type} - {tourn.mode}",
            f"**Dates**: Signup By/Start By/End By/Deadline  - {tourn.signup_close_date}/{tourn.expected_start_date}/{tourn.expected_end_date}/{tourn.deadline_date}",
            f"**Entrance Fee**: {tourn.fee}",
            f"**Deck Size/Value**: {tourn.deck_limit}/{tourn.deck_value_limit}",
            f"**Sponsor**: {tourn.sponsor}",
            f"**Sponsor Description**: {tourn.sponsor_description}",
            f"**Special Rules**: {tourn.special_rules}",
            f"**Prizes**: {tourn.prizes}",
            f"**Unique Prize**: {tourn.unique_prize}",
            f"**Channel**: {tourn.discord_channel}",
            f"**Admin**: {tourn.admin}",
        ]
        if tourn.status == "RUNNING":
          msg.append(f"**Signups**: {count}/{tourn.coach_limit} {', '.join([coach.short_name() for coach in coaches])}")
        else:
          msg.append(f"**Signups**: {count}/{tourn.coach_limit}")

        if tourn.reserve_limit > 0:
          reserves = tourn.coaches.filter(TournamentSignups.mode == "reserve").all()
          count_res = len(reserves)
          if tourn.status == "RUNNING":
            msg.append(f"**Reserves**: {count_res}/{tourn.reserve_limit} {', '.join([coach.short_name() for coach in reserves])}")
          else:
            msg.append(f"**Reserves**: {count_res}/{tourn.reserve_limit}")

        await send_message(ctx.channel, msg)
        return
      #list
      else:
        if len(args) >= 1 and args[0] == "all":
          tourns = Tourn.query.all()
          tmsg = "All"
        elif len(args) >= 1 and args[0] == "full":
          tourns = Tourn.query.outerjoin(Tourn.tournament_signups).filter(Tourn.status == "OPEN").group_by(Tourn).having(func.count_(Tourn.tournament_signups) == Tourn.coach_limit+Tourn.reserve_limit).all()
          tmsg = "Full"
        elif len(args) >= 1 and args[0] == "free":
          tourns = Tourn.query.outerjoin(Tourn.tournament_signups).filter(Tourn.status == "OPEN").group_by(Tourn).having(func.count_(Tourn.tournament_signups) < Tourn.coach_limit+Tourn.reserve_limit).all()
          tmsg = "Free"
        else:
          tourns = Tourn.query.filter_by(status="OPEN").all()
          tmsg = "Open"

        if len(args) > 1:
          tourns = [tourn for tourn in tourns if tourn.region.lower().replace(" ", "") == args[1] or tourn.region.lower() == "all"]

        msg = [f"__**{tmsg} Tournaments:**__"]
        for tournament in tourns:
          coaches = tournament.coaches.filter(TournamentSignups.mode == "active").all()
          reserves = tournament.coaches.filter(TournamentSignups.mode == "reserve").all()
          count = len(coaches)
          count_res = len(reserves)
          reserve_message = f" ({count_res}/{tournament.reserve_limit}) " if tournament.reserve_limit != 0 else ""
          msg.append(f"**{tournament.tournament_id}.** {tournament.name}{' (Imperium)' if tournament.type == 'Imperium' else ''} - Signups: {count}/{tournament.coach_limit}{reserve_message}, Closes: {tournament.signup_close_date}")

        msg.append(" \nUse **!complist all|full|free <bigo|gman|rel>** to display tournaments")
        msg.append("Use **!complist <id>** to display details of the tournament")
        msg.append("Use **!sign <id>** to register for tournament")
        msg.append("Use **!resign <id>** to resign from tournament")
        await send_message(ctx.channel, msg)
        return
    
    @commands.command()
    async def comp(self, ctx, *args):
      """Manages in-game competitions for tournaments. Needs to be run in the tournament discord channel
      USAGE:
      !comp list
        list all competitions for tournament
      !comp create ladder
        creates ladder comp for tournament if it does not exists
      !comp create 1on1 <name>
        creates 1 on 1 comp with <name> for tournament if it does not exists
      !comp create knockout <team_number> <name>
        creates knockout comp with <name> for <team_number> teams
      !comp ticket <competition_name>
        sends ticket to the <competition_name> to the coach issuing the command in the tournament room
      """
      room = ctx.channel.name
      args_len = len(args)
      if args_len == 0 \
          or (args_len > 0 and args[0] not in ["list","create", "ticket"]) \
          or (args[0] == "create" and \
              (args_len < 2 or args[1] not in ["ladder", "1on1","knockout"] or (args[1] == "1on1" and args_len == 2) \
                  or (args[1] == "knockout" and args_len < 4 and not represents_int(args[2])))) \
          or (args[0] == "ticket" and args_len < 2):
          raise ValueError("Incorrect arguments")
          
      tourn = TournamentService.get_tournament_using_room(room)
      
      if tourn.status != "RUNNING":
        await ctx.send("Tournament is not running!")
        return

      if args[0] == "create":
        if args[1] == "ladder":
          comp_name = tourn.ladder_room_name()
          comp = CompetitionService.create_imperium_ladder(comp_name)
        if args[1] == "1on1":
          comp_name = " ".join(args[2:])
          comp_name = comp_name[:25] if len(comp_name) > 25 else comp_name
          comp = CompetitionService.create_imperium_rr(comp_name)
        if args[1] == "knockout":
          comp_name = " ".join(args[3:])
          comp_name = comp_name[:25] if len(comp_name) > 25 else comp_name
          comp = CompetitionService.create_imperium_knockout(comp_name, int(args[2]))
        tourn.competitions.append(comp)
        db.session.commit()
        await ctx.send(f"Competition **{comp.name}** created in **{comp.league_name}**")
        return
      
      if args[0] == "list":
        msg = ["**Competitions:**"]
        msg.append("```")
        msg.append(
          '{:25s} | {:25} | {:25}'.format("League","Name","Type")
        )
        msg.append(78*"-")
        for comp in tourn.competitions:
          msg.append(
              '{:25s} | {:25} | {:25}'.format(comp.league_name,comp.name,comp.type_str())
          )

        msg.append("```")
        await ctx.send("\n".join(msg))
        return

      if args[0] == "ticket":
        comp_name = " ".join(args[1:])
        # get coach
        coach = CoachService.discord_user_to_coach(ctx.author)
        result = CompetitionService.ticket_competition(comp_name, coach, tourn)
        team_name = result['ResponseCreateCompetitionTicket']['TicketInfos']['RowTeam']['Name']
        await ctx.send(f"Ticket sent to **{team_name}** for competition **{comp_name}**")
        return
  
def setup(bot):
    bot.add_cog(Tournament(bot))
