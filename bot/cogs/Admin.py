import discord

from discord.ext import commands
from bot.helpers import sign, resign, coach_unique
from misc.helpers import PackHelper
from models.data_models import db, Transaction, Coach, Tournament, Competition, TournamentSignups
from services import CoachService, TournamentService, CompetitionService, CardService, PackService
from bot.base_cog import ImperiumCog

class Admin(ImperiumCog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    def is_admin_channel(self, dchannel):
      """checks if it is admin channel"""
      if dchannel.name is not None and dchannel.name == "admin-channel":
          return True
      raise Exception(f"Insuficient rights")

    def coach_collection_msg(self, coach):
      """Creates message out of coaches collection"""
      msg = [
        f"Coach **{coach.name}**\n",
        f"**Bank:** {coach.account.amount} coins\n",
        f"**Tournaments:**",
        *[f'{t.tournament_id}. {t.name}, status: {t.status}, '+
          f'expected start: {t.expected_start_date}' for t in coach.tournaments],
        "\n**Collection**:",
        "-" * 65 + "",
        f"{PackHelper.format_pack(coach.active_cards(), show_hidden=True)}",
        "-" * 65 + "\n"
      ]

      admin_in = Tournament.query.filter(
        Tournament.admin == coach.short_name(), Tournament.status.in_(("OPEN", "RUNNING"))
      ).all()

      if admin_in:
        msg.append(f"**Tournament Admin:**")
        msg.extend(
          [(f'{t.tournament_id}. {t.name}, status: {t.status}, channel: {t.discord_channel}')
            for t in admin_in]
        )
      return msg
    
    @commands.command()
    async def adminsign(self, ctx, tournament_id:int, coach_name):
      """Signs coach to a tournament
      USAGE:
      !adminsign <tournament_id> <coach>
        <tournament_id>: id of tournament from !complist
        <coach>: coach discord name or its part, must be unique
      """
      self.is_admin_channel(ctx.channel)
      coach = await coach_unique(coach_name, ctx)
      if coach is None:
        return
      if not await sign(tournament_id, coach, ctx, admin=True):
        await Exception(f"Could not sign {coach.short_name()}")
      return

    @commands.command()
    async def adminresign(self, ctx, tournament_id:int, coach_name):
      """Resigns coach from a tournament
      USAGE:
      !adminresign <id> <coach>
        <id>: id of tournament from !complist
        <coach>: coach discord name or its part, must be unique
      """
      self.is_admin_channel(ctx.channel)
      coach = await coach_unique(coach_name, ctx)
      if coach is None:
        return
      if not await resign(tournament_id, coach, ctx, admin=True):
        await Exception(f"Could not resign {coach.short_name()}")
      return

    @commands.command()
    async def adminrole(self, ctx, action:str, coach_name:str, role:str):
      """Change role for a coach
      USAGE:
      Adds or removes bot/web roles for coach
      !adminrole <action> <coach> <role>
        <action>: add or remove
        <coach>: coach discord name or its part, must be unique
        <role>: 
          webadmin - enables coach to do admin tasks on web
          superadmin - enables coach to do super admin tasks on web
      """
      self.is_admin_channel(ctx.channel)
      if action not in ["add", "remove"]:
        raise ValueError("Invalid action")

      if role not in ["webadmin", "superadmin"]:
        raise ValueError("Invalid role")

      coach = await coach_unique(coach_name, ctx)
      if coach is None:
        return

      if action == "add":
        state = True
        if role == "webadmin":
          coach.web_admin = state
        if role == "superadmin":
          coach.super_admin = state
      if action == "remove":
        state = False
        if role == "webadmin":
          coach.web_admin = state
        if role == "superadmin":
          coach.super_admin = state
      db.session.commit()
      await ctx.send(f"Role updated for {coach.short_name()}: {role} - {state}")
      return

    @commands.command()
    async def adminquest(self, ctx, action:str, coach_name:str, quest:str):
      """Manually marks the quest as achieved or not. Does not award the prize
      USAGE:
      !adminquest <action> <coach> <quest>
        <action>: on to mark as complete, off the clear flag
        <coach>: coach discord name or its part, must be unique
        <quest>: *collect3legends* or *buildyourownlegend*
      """
      self.is_admin_channel(ctx.channel)
      if action not in ["on", "off"]:
        raise ValueError("Invalid action")

      if quest not in ["collect3legends", "buildyourownlegend"]:
        raise ValueError("Invalid quest")

      coach = await coach_unique(coach_name, ctx)
      if coach is None:
          return

      if action == "on":
          value = True
      if action == "off":
          value = False
      CoachService.set_achievement(coach, ["quests",quest], value)
      db.session.commit()
      await ctx.send(f"Quest updated for {coach.short_name()}: {quest} - {action}")
      return

    @commands.command()
    async def adminbank(self, ctx, amount:int, coach_name:str, *reason):
      """Add or remove cash from coach
      USAGE:
      !adminbank <amount> <coach> <reason>
        <amount>: number of coins to add to bank, if negative is used, it will be deducted from bank
        <coach>: coach discord name or its part, must be unique
        <reason>: describe why you are changing the coach bank
      """
      self.is_admin_channel(ctx.channel)

      coach = await coach_unique(coach_name, ctx)
      if coach is None:
          return

      reason = ' '.join(reason) + " - updated by " + str(ctx.author.name)

      tran = Transaction(description=reason, price=-1*amount)
      coach.make_transaction(tran)

      msg = [
          f"Bank for {coach.name} updated to **{coach.account.amount}** coins:\n",
          f"Note: {reason}\n",
          f"Change: {amount} coins"
      ]
      await self.send_message(ctx.channel, msg)
      await self.bank_notification(ctx, f"Your bank has been updated by **{amount}** coins - {reason}", coach)

    @commands.command()
    async def adminlist(self, ctx, coach:str):
      """List details of coach"""
      self.is_admin_channel(ctx.channel)
      coaches = Coach.find_all_by_name(coach)
      msg = []

      if not coaches:
        msg.append("No coaches found")

      for coach in coaches:
        for messg in self.coach_collection_msg(coach):
          msg.append(messg)
      await self.send_message(ctx.channel, msg)
      return

    @commands.command()
    async def admincomp(self, ctx, action:str, tournamnent_id:int=None):
      """Manipulate tournaments
      USAGE:
      !admincomp <action> [tournament_id]
        start: Notifies all registered coaches that tournament started in the tournament channel and links the ledger
        stop: Resigns all coaches from the tournament
        update: Updates data from Tournament sheet
        special_play: Initiates special play phase
        inducement: Initiates inducement phase
        blood_bowl: Initiates blood bowl phase
        <tournament_id>: id of tournament from Tournament master sheet
      """
      self.is_admin_channel(ctx.channel)
      if action not in ["start", "stop", "update", Tournament.SP_PHASE, Tournament.IND_PHASE, Tournament.BB_PHASE]:
          raise ValueError("Incorrect arguments!!!")

      if action in ["start", "stop", Tournament.SP_PHASE, Tournament.IND_PHASE, Tournament.BB_PHASE]:
        if not tournamnent_id:
          raise ValueError("Incorrect arguments!!!")

        tourn = Tournament.query.filter_by(tournament_id=tournamnent_id).one_or_none()
        if not tourn:
          raise ValueError(f"Incorrect tournament **id** specified")

      if action == "update":
        await ctx.send("Updating...")
        TournamentService.update()
        await ctx.send("Tournaments updated!!!")
      
      if action == "stop":
        TournamentService.close_tournament(tourn)
        await ctx.send(f"Coaches have been resigned from {tourn.name}!!!")
        return

      if action in ["start", Tournament.SP_PHASE, Tournament.IND_PHASE,Tournament.BB_PHASE]:
        result, err = TournamentService.start_check(tourn)
        if err:
          raise Exception(err)

        channel = discord.utils.get(ctx.bot.get_all_channels(), name=tourn.discord_channel.lower())
        if not channel:
          await ctx.send(f"Discord channel {tourn.discord_channel.lower()} does not exists, please create it and rerun this command!")
          return

        admin = discord.utils.get(ctx.guild.members, name=tourn.admin)
        if not admin:
          await ctx.send(f"Tournament admin {tourn.admin} was not found on the discord server, check name in the Tournament sheet and run **!admincomp update**!")
          return

        if action == "start":
          TournamentService.reset_phase(tourn)
          TournamentService.set_status(tourn,status="RUNNING")
          db.session.commit()
          TournamentService.release_reserves(tourn)

          submit_deck_channel = discord.utils.get(ctx.bot.get_all_channels(), name='submit-a-deck')

          members = [discord.utils.get(ctx.guild.members, id=coach.disc_id) for coach in tourn.coaches.filter(TournamentSignups.mode == "active")]
          msg = [member.mention for member in members if member]
          msg.append(f"This will be scheduling channel for your {tourn.name}")
          if submit_deck_channel:
              msg.append(f"Please submit decks as instructed in {submit_deck_channel.mention}")
          msg.append(f"We start on {tourn.expected_start_date}!")
          msg.append(f"Deadline is on {tourn.deadline_date}")
          msg.append(f"Your tournament admin is {admin.mention}")
          msg.append(f"**Deck Limit:** {tourn.deck_limit}")
          msg.append(f"**Tournament Sponsor:** {tourn.sponsor}")
          msg.append(f"{tourn.sponsor_description}")
          msg.append(f"**Special Rules:**")
          msg.append(f"{tourn.special_rules}")
          msg.append(f"**Prizes:**")
          msg.append(f"{tourn.prizes}")
          msg.append(f"**Unique Prize:**")
          msg.append(f"{tourn.unique_prize}")

          #room setup
          if tourn.is_development():
            CompetitionService.import_competitions()
            comp = Competition.query.filter_by(name=tourn.ladder_room_name()).one_or_none()
            if not comp:
              comp = CompetitionService.create_imperium_ladder(tourn.ladder_room_name())
            
            comp.tournament_id = tourn.id
            db.session.commit()
            msg.append(f"**In-game rooms:**")
            for comp in tourn.competitions:
              msg.append(f"**{comp.name}** in **{comp.league_name}** league")
        
        if action == Tournament.SP_PHASE:
            msg = TournamentService.special_play_msg(tourn)
        if action == Tournament.IND_PHASE:
            msg = TournamentService.inducement_msg(tourn)
        if action == Tournament.BB_PHASE:
            msg = TournamentService.blood_bowl_msg(tourn)
        await self.send_message(channel, msg)
        await ctx.send("Done.")
      return

    @commands.command()
    async def admincard(self, ctx, action:str, coach_name:str=None, *cards):
      """Adds or removes cards from coach, or updates card database
      USAGE 1:
      Add or remove cards from coach
      !admincard <action> <coach> <card>;...;<card>
        <action>: add or remove
        <coach>: coach discord name or its part, must be unique
        <card>: Exact card name as is in the All Cards list, if mutliple cards are specified separate them by **;**
      USAGE 2:
      Updates card database from the master sheet
      !admincard update
      """
      if action not in ["add", "remove", "update"]:
        raise ValueError("Incorrect action")

      if not cards and not coach_name and action in ["add", "remove"]:
        raise ValueError("Missing arguments")

      if action == "update":
        await ctx.send(f"Updating...")
        CardService.update()
        await ctx.send(f"Cards updated!!!")
        return
      else:
        coach = await coach_unique(coach_name, ctx)
        if coach is None:
            return
        card_names = [card.strip() for card in " ".join(cards).split(";")]

      if action == "add":
        pack = PackService.admin_pack(0, card_names, coach)
        # situation when some of the cards could not be found
        if len(card_names) != len(pack.cards):
          msg = []
          msg.append(f"Not all cards were found, check the names!!!\n")
          for card in card_names:
            if card in [card.get('name').lower() for card in pack.cards]:
                found = True
            else:
                found = False
            found_msg = "**not found**" if not found else "found"
            msg.append(f"{card}: {found_msg}")
          await self.send_message(ctx.channel, msg)
          return
        
        reason = f"{action.capitalize()} {';'.join([str(card.get('name')) for card in pack.cards])} - by " + str(ctx.author.name)
        tran = Transaction(pack=pack, description=reason, price=0)
        coach.make_transaction(tran)
        
        msg = []
        msg.append(f"**{PackService.description(pack)}** for @{coach.name} - **{pack.price}** coins:\n")
        # message sent to admin so display the hidden cards
        msg.append(f"{PackHelper.format_pack(pack.cards, show_hidden=True)}")
        msg.append(f"**Bank:** {coach.account.amount} coins")
        await self.send_message(ctx.channel, msg)
        # message sent to discord so hide the names
        await self.bank_notification(ctx, f"Card(s) **{', '.join([card.get('name', show_hidden=False) for card in pack.cards])}** added to your collection by {str(ctx.author.name)}", coach)
        await self.auto_cards(pack, ctx)
        CoachService.check_collect_three_legends_quest(coach)
        return

      if action == "remove":
        removed_cards = []
        unknown_cards = []

        for name in card_names:
          card = CardService.get_card_from_coach(coach, name)
          if card:
            removed_cards.append(card)
            db.session.delete(card)
            db.session.expire(coach, ['cards'])
          else:
            unknown_cards.append(name)
        reason = f"{action.capitalize()} {';'.join([card.get('name') for card in removed_cards])} - by " + str(ctx.author.name)
        tran = Transaction(description=reason, price=0)
        coach.make_transaction(tran)
          
        if removed_cards:
          msg = []
          msg.append(f"Cards removed from @{coach.name} collection:\n")
          msg.append(f"{PackHelper.format_pack(removed_cards, show_hidden=True)}")
          await self.send_message(ctx.channel, msg)
          await self.bank_notification(ctx, f"Card(s) **{', '.join([card.get('name') for card in removed_cards])}** removed from your collection by {str(ctx.author.name)}", coach)

        if unknown_cards:
          msg = ["**Warning** - these cards have been skipped:"]
          for name in unknown_cards:
              msg.append(f"{name}: **not found**")
          await self.send_message(ctx.channel, msg)
        return

def setup(bot):
    bot.add_cog(Admin(bot))