import os
import traceback
import random
import discord

from sqlalchemy import func

from web import db, app
from models.data_models import Coach, Pack, Transaction, Competition
from models.data_models import TransactionError, Tournament, TournamentSignups
from misc.helpers import CardHelper
from misc.helpers import represents_int
from services import PackService, CardService, TournamentService, CoachService, CompetitionError, CompetitionService
from services import RegistrationError, TournamentError

from .helpers import BotHelp, LongMessage, log_response, logger

app.app_context().push()

AUTO_CARDS = {
    'Loose Change!':5,
    'Bank Error!':10,
    'Lottery Win!':15
}

class DiscordCommand(BotHelp):
    """Main class to process commands"""
    emojis = {
        "Common": "",
        "Rare": ":diamonds:",
        "Epic": ":large_blue_diamond:",
        "Legendary": ":large_orange_diamond:",
    }

    @classmethod
    def rarity_emoji(cls, rarity):
        """returns emoji rarity"""
        return cls.emojis.get(rarity, "")

    @classmethod
    def number_emoji(cls, number):
        """returns number emoji"""
        switcher = {
            0: ":zero:",
            1: ":one:",
            2: ":two:",
            3: ":three:",
            4: ":four:",
            5: ":five:",
            6: ":six:",
            7: ":seven:",
            8: ":eight:",
            9: ":nine:",

        }
        return switcher.get(number, "")

    @classmethod
    def is_admin_channel(cls, dchannel):
        """checks if it is admin channel"""
        if dchannel.name is not None and dchannel.name == "admin-channel":
            return True
        return False

    @classmethod
    def format_pack(cls, cards, show_hidden=False):
        """formats response message for pack"""
        msg = ""
        value = 0
        def display():
            if not show_hidden and card.get('card_type') == "Reaction":
                return False
            return True

        for card, quantity in cards:
            msg += cls.number_emoji(quantity)
            msg += " x "
            msg += cls.rarity_emoji(card.get('rarity'))
            if not display():
                name = "Reaction Card"
                cvalue = "?"
            else:
                value += card.get('value') * quantity
                name = card.get("name")
                cvalue = card.get("value")
            msg += f' **{name}** ({card.get("subtype")} {card.get("race")} '
            msg += f'{card.get("card_type")} Card) ({cvalue})\n'

        msg += f"\n \n__Total value__: {value}\n \n"
        msg += "__Description__:\n \n"
        for card, quantity in cards:
            if display() and card.get('description') != "":
                msg += f"**{card.get('name')}**: {card.get('description')}\n"
            elif card.get('card_type') == "Reaction":
                msg += f"**Reaction**: owner can use !list or web to see the card detail\n"
        return msg.strip("\n")

    @classmethod
    def format_pack_to_pieces(cls, cards, show_hidden=False):
        """formats response message for pack"""
        pieces = {
          'cards': "",
          'descriptions': [],
        }
        value = 0
        def display():
          if not show_hidden and card.get('card_type') == "Reaction":
            return False
          return True

        for card, quantity in cards:
          pieces['cards'] += cls.number_emoji(quantity)
          pieces['cards'] += " x "
          pieces['cards'] += cls.rarity_emoji(card.get('rarity'))
          if not display():
              name = "Reaction Card"
              cvalue = "?"
          else:
              value += card.get('value') * quantity
              name = card.get("name")
              cvalue = card.get("value")
          race = "" if card.get('race') == "All" else f"{card.get('race')} "
          pieces['cards'] += f' **{name}** ({race}'
          pieces['cards'] += f'{card.get("card_type")} Card) ({cvalue})\n'

        pieces['cards'] += f"\n \n__Total value__: {value}\n \n"
        for card, quantity in cards:
          desc = {
            'name': '',
            'description': '',
          }
          if display() and card.get('description') != "":
            desc['name'] = f"**{card.get('name')}**"
            desc['description'] = card.get('description')
            pieces['descriptions'].append(desc)
          elif card.get('card_type') == "Reaction":
            desc['name'] = "Reaction"
            desc['description'] = "Owner can use !list or web to see the card detail"
            pieces['descriptions'].append(desc)
        return pieces

    @classmethod
    def coach_collection_msg(cls, coach):
        """Creates message out of coaches collection"""
        msg = [
            f"Coach **{coach.name}**\n",
            f"**Bank:** {coach.account.amount} coins\n",
            f"**Tournaments:**",
            *[f'{t.tournament_id}. {t.name}, status: {t.status}, '+
              f'expected start: {t.expected_start_date}' for t in coach.tournaments],
            "\n**Collection**:",
            "-" * 65 + "",
            f"{cls.format_pack(CardHelper.sort_cards_by_rarity_with_quatity(coach.active_cards()), show_hidden=True)}",
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

    def __init__(self, dmessage, dclient):
        self.message = dmessage
        self.client = dclient
        self.cmd = dmessage.content.lower()
        self.args = self.cmd.split()
        self.args_len = len(self.args)

    async def process(self):
        """Process the command"""
        try:
            if self.cmd.startswith('!admin'):
                await self.__run_admin()
            else:
              return
            db.session.close()
        except Exception as e:
            await self.transaction_error(e)
            db.session.close()
            #raising will not kill the discord bot but will cause it to log this to log as well
            raise

    @classmethod
    async def send_message(cls, channel, message_list):
        """Sends messages to channel"""
        msg = LongMessage(channel)
        for message in message_list:
            msg.add(message)
        await msg.send()

    async def reply(self, message_list):
        """Replies in the same channel"""
        await self.send_message(self.message.channel, message_list)

    async def short_reply(self, message):
        """Short message not using LongMesage class"""
        await self.message.channel.send(message)
        log_response(message)

    async def transaction_error(self, error):
        """Sends and logs transaction error"""
        text = type(error).__name__ +": "+str(error)
        await self.send_message(self.message.channel, [text])
        logger.error(text)
        logger.error(traceback.format_exc())

    # must me under 2000 chars
    async def bank_notification(self, msg, coach):
        """Notifies coach about bank change"""
        member = discord.utils.get(self.message.guild.members, id=coach.disc_id)
        if member is None:
            mention = coach.name
        else:
            mention = member.mention

        channel = discord.utils.get(self.client.get_all_channels(), name='bank-notifications')
        await self.send_message(channel, [f"{mention}: "+msg])
        return

    async def coach_unique(self, name):
        """finds uniq coach by name"""
        coaches = Coach.find_all_by_name(name)
        if not coaches:
            await self.reply([f"<coach> __{name}__ not found!!!\n"])
            return None

        if len(coaches) > 1:
            emsg = f"<coach> __{name}__ not **unique**!!!\n"
            emsg += "Select one: "
            for coach in coaches:
                emsg += coach.name
                emsg += " "
            await self.short_reply(emsg)
            return None
        return coaches[0]

    async def sign(self, args, coach, admin=False):
        """routine to sign a coach to tournament"""
        if len(args) != 2:
            await self.reply(["Incorrect number of arguments!!!\n"])
            return False

        if not represents_int(args[1]):
            await self.reply([f"**{args[1]}** is not a number!!!\n"])
            return False

        if admin:
            tourn = Tournament.query.filter_by(tournament_id=int(args[1])).one_or_none()
        else:
            tourn = Tournament.query.filter_by(
                status="OPEN", tournament_id=int(args[1])
            ).one_or_none()
        if not tourn:
            await self.reply([f"Incorrect tournament **id** specified\n"])
            return False

        signup = TournamentService.register(tourn, coach, admin)
        add_msg = "" if signup.mode == "active" else " as RESERVE"
        await self.reply([f"Signup succeeded{add_msg}!!!\n"])
        return True

    async def resign(self, args, coach, admin=False):
        """routine to resign a coach to tournament"""
        if len(args) != 2:
            await self.reply(["Incorrect number of arguments!!!\n"])
            return False

        if not represents_int(args[1]):
            await self.reply([f"**{args[1]}** is not a number!!!\n"])
            return False

        if admin:
            tourn = Tournament.query.filter_by(tournament_id=int(args[1])).one_or_none()
        else:
            tourn = Tournament.query.filter_by(
                status="OPEN", tournament_id=int(args[1])
            ).one_or_none()

        if not tourn:
            await self.reply([f"Incorrect tournament **id** specified\n"])
            return False

        if TournamentService.unregister(tourn, coach, admin):
            await self.reply([f"Resignation succeeded!!!\n"])

            coaches = [
                discord.utils.get(self.message.guild.members, id=str(signup.coach.disc_id))
                for signup in TournamentService.update_signups(tourn)
            ]
            msg = [coach.mention for coach in coaches if coach]
            msg.append(f"Your signup to {tourn.name} has been updated from RESERVE to ACTIVE")

            if len(msg) > 1:
                tourn_channel = discord.utils.get(
                    self.client.get_all_channels(), name='tournament-notice-board'
                )
                if tourn_channel:
                    await self.send_message(tourn_channel, msg)
                else:
                    await self.reply(msg)
        return True

    async def __run_admin(self):
        # if not started from admin-channel
        if not self.__class__.is_admin_channel(self.message.channel):
            await self.reply([f"Insuficient rights"])
            return

        #adminhelp cmd
        if self.message.content.startswith('!adminhelp'):
            await self.short_reply(self.__class__.commands())
            return

        #adminlist cmd
        if self.message.content.startswith('!adminlist'):
            # require username argument
            if len(self.args) == 1:
                await self.reply(["Username missing"])
                return

            coaches = Coach.find_all_by_name(self.args[1])
            msg = []

            if not coaches:
                msg.append("No coaches found")

            for coach in coaches:
                for messg in self.__class__.coach_collection_msg(coach):
                    msg.append(messg)
            await self.reply(msg)
            return

        if self.message.content.startswith('!adminbank'):
            # require username argument
            if len(self.args) < 4:
                await self.reply(["Not enough arguments!!!\n"])
                await self.short_reply(self.__class__.adminbank_help())
                return

            # amount must be int
            if not represents_int(self.args[1]):
                await self.reply(["<amount> is not whole number!!!\n"])
                return

            coach = await self.coach_unique(self.args[2])
            if coach is None:
                return

            amount = int(self.args[1])
            reason = ' '.join(str(x) for x in self.message.content.split(" ")[3:]) + " - updated by " + str(self.message.author.name)

            tran = Transaction(description=reason, price=-1*amount)
            try:
                coach.make_transaction(tran)
            except TransactionError as e:
                await self.transaction_error(e)
                return
            else:
                msg = [
                    f"Bank for {coach.name} updated to **{coach.account.amount}** coins:\n",
                    f"Note: {reason}\n",
                    f"Change: {amount} coins"
                ]
                await self.reply(msg)
                await self.bank_notification(f"Your bank has been updated by **{amount}** coins - {reason}", coach)

        if self.message.content.startswith('!adminrole'):
            if len(self.args) != 4:
                await self.reply([self.__class__.adminrole_help()])
                return

            if self.args[1] not in ["add", "remove"]:
                await self.reply(["Specify **add** or **remove** operation!!!\n"])
                return

            if self.args[3] not in ["webadmin"]:
                await self.reply(["Specify **webadmin** role!!!\n"])
                return

            coach = await self.coach_unique(self.args[2])
            if coach is None:
                return

            if self.args[1] == "add":
                coach.web_admin = True
            if self.args[1] == "remove":
                coach.web_admin = False
            db.session.commit()
            await self.reply([f"Role updated for {coach.short_name()}: {self.args[3]} - {coach.web_admin}"])
            return

        if self.message.content.startswith('!adminquest'):
            if len(self.args) != 4:
                await self.reply([self.__class__.adminquest_help()])
                return

            if self.args[1] not in ["on", "off"]:
                await self.reply(["Specify **on** or **off** operation!!!\n"])
                return

            if self.args[3] not in ["collect3legends", "buildyourownlegend"]:
                await self.reply(["Specify **collect3legends** or **buildyourownlegend** quest!!!\n"])
                return

            coach = await self.coach_unique(self.args[2])
            if coach is None:
                return

            if self.args[1] == "on":
                value = True
            if self.args[1] == "off":
                value = False
            CoachService.set_achievement(coach, ["quests",self.args[3]], value)
            db.session.commit()
            await self.reply([f"Quest updated for {coach.short_name()}: {self.args[3]} - {self.args[1]}"])
            return

        if self.message.content.startswith('!adminreset'):
            # require username argument
            if len(self.args) != 2:
                await self.reply(["Bad number of arguments!!!\n"])
                await self.reply([self.__class__.adminreset_help()])
                return

            coach = await self.coach_unique(self.args[1])
            if coach is None:
                return

            try:
                new_coach = coach.reset()
            except TransactionError as e:
                await self.transaction_error(e)
                return
            else:
                await self.reply([f"Coach {new_coach.name} was reset"])
                await self.bank_notification(f"Your account was reset", new_coach)

        if self.message.content.startswith('!admincard'):
            if len(self.args) == 1:
                await self.reply([self.__class__.admincard_help()])
                return

            if len(self.args) > 1 and self.args[1] not in ["add", "remove", "update"]:
                await self.reply(["specify **add**, **remove** or **update** operation!!!\n"])
                return

            if len(self.args) < 4 and self.args[1] in ["add", "remove"]:
                await self.reply(["Not enough arguments!!!", self.__class__.admincard_help()])
                return

            if self.args[1] == "update":
                await self.reply([f"Updating...\n"])
                CardService.update()
                await self.reply([f"Cards updated!!!\n"])
                return
            else:
                coach = await self.coach_unique(self.args[2])
                if coach is None:
                    return
                card_names = [card.strip() for card in " ".join(self.args[3:]).split(";")]

            if self.args[1] == "add":
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
                    await self.reply(msg)
                    return
                reason = f"{self.args[1].capitalize()} {';'.join([str(card.get('name')) for card in pack.cards])} - by " + str(self.message.author.name)

                tran = Transaction(pack=pack, description=reason, price=0)
                try:
                    coach.make_transaction(tran)
                except TransactionError as e:
                    await self.transaction_error(e)
                    return
                else:
                    msg = []
                    msg.append(f"**{PackService.description(pack)}** for @{coach.name} - **{pack.price}** coins:\n")
                    # message sent to admin so display the hidden cards
                    msg.append(f"{self.__class__.format_pack(CardHelper.sort_cards_by_rarity_with_quatity(pack.cards), show_hidden=True)}\n")
                    msg.append(f"**Bank:** {coach.account.amount} coins")
                    await self.reply(msg)
                    # message sent to discord so hide the names
                    await self.bank_notification(f"Card(s) **{', '.join([card.get('name', show_hidden=False) for card in pack.cards])}** added to your collection by {str(self.message.author.name)}", coach)
                    await self.auto_cards(pack)
                    CoachService.check_collect_three_legends_quest(coach)
                    return

            if self.args[1] == "remove":
                try:
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
                    reason = f"{self.args[1].capitalize()} {';'.join([card.get('name') for card in removed_cards])} - by " + str(self.message.author.name)
                    tran = Transaction(description=reason, price=0)
                    coach.make_transaction(tran)
                except TransactionError as e:
                    await self.transaction_error(e)
                    return
                else:
                    if removed_cards:
                        msg = []
                        msg.append(f"Cards removed from @{coach.name} collection:\n")
                        msg.append(f"{self.__class__.format_pack(CardHelper.sort_cards_by_rarity_with_quatity(removed_cards), show_hidden=True)}\n")
                        await self.reply(msg)
                        await self.bank_notification(f"Card(s) **{', '.join([card.get('name') for card in removed_cards])}** removed from your collection by {str(self.message.author.name)}", coach)

                    if unknown_cards:
                        msg = ["**Warning** - these cards have been skipped:"]
                        for name in unknown_cards:
                            msg.append(f"{name}: **not found**")
                        await self.reply(msg)
                    return

        if self.message.content.startswith("!adminsign"):
            if len(self.args) != 3:
                await self.reply(["Incorrect number of arguments!!!", self.__class__.adminsign_help()])
                return
            coach = await self.coach_unique(self.args[-1])
            if coach is None:
                return
            if not await self.sign(self.args[:-1], coach, admin=True):
                await self.reply([self.__class__.adminsign_help()])
            return

        if self.message.content.startswith("!adminresign"):
            if len(self.args) != 3:
                await self.reply(["Incorrect number of arguments!!!", self.__class__.adminresign_help()])
                return
            coach = await self.coach_unique(self.args[-1])
            if coach is None:
                return
            if not await self.resign(self.args[:-1], coach, admin=True):
                await self.reply([self.__class__.adminresign_help()])
            return

        if self.message.content.startswith("!admincomp"):
            if len(self.args) not in [2, 3]:
                await self.reply(["Incorrect number of arguments!!!", self.__class__.admincomp_help()])
                return

            if self.args[1] not in ["start", "stop", "update", Tournament.SP_PHASE, Tournament.IND_PHASE, Tournament.BB_PHASE]:
                await self.reply(["Incorrect arguments!!!", self.__class__.admincomp_help()])

            if self.args[1] in ["start", "stop", Tournament.SP_PHASE, Tournament.IND_PHASE, Tournament.BB_PHASE]:
                if not represents_int(self.args[2]):
                    await self.reply([f"**{self.args[2]}** is not a number!!!\n"])
                    return

                tourn = Tournament.query.filter_by(tournament_id=int(self.args[2])).one_or_none()
                if not tourn:
                    await self.reply([f"Incorrect tournament **id** specified\n"])
                    return

            if self.args[1] == "update":
                await self.reply([f"Updating...\n"])
                TournamentService.update()
                await self.reply([f"Tournaments updated!!!\n"])
            if self.args[1] == "stop":
                TournamentService.close_tournament(tourn)
                await self.reply([f"Coaches have been resigned from {tourn.name}!!!\n"])
                return

            if self.args[1] in ["start", Tournament.SP_PHASE, Tournament.IND_PHASE,Tournament.BB_PHASE]:
                
                result, err = TournamentService.start_check(tourn)
                if err:
                    await self.reply([err])
                    return

                channel = discord.utils.get(self.client.get_all_channels(), name=tourn.discord_channel.lower())
                if not channel:
                    await self.reply([f"Discord channel {tourn.discord_channel.lower()} does not exists, please create it and rerun this command!\n"])
                    return

                admin = discord.utils.get(self.message.guild.members, name=tourn.admin)
                if not admin:
                    await self.reply([f"Tournament admin {tourn.admin} was not found on the discord server, check name in the Tournament sheet and run **!admincomp update**!\n"])
                    return

                if self.args[1] == "start":
                    TournamentService.reset_phase(tourn)
                    TournamentService.set_status(tourn,status="RUNNING")
                    db.session.commit()
                    TournamentService.release_reserves(tourn)

                    submit_deck_channel = discord.utils.get(self.client.get_all_channels(), name='submit-a-deck')

                    members = [discord.utils.get(self.message.guild.members, id=coach.disc_id) for coach in tourn.coaches.filter(TournamentSignups.mode == "active")]
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
                        try:
                            CompetitionService.import_competitions()
                            comp = Competition.query.filter_by(name=tourn.ladder_room_name()).one_or_none()
                            if not comp:
                                comp = CompetitionService.create_imperium_ladder(tourn.ladder_room_name())
                            
                            comp.tournament_id = tourn.id
                            db.session.commit()
                        except CompetitionError as e:
                            await self.short_reply(e)
                        msg.append(f"**In-game rooms:**")
                        for comp in tourn.competitions:
                            msg.append(f"**{comp.name}** in **{comp.league_name}** league")
                
                if self.args[1] == Tournament.SP_PHASE:
                    msg = TournamentService.special_play_msg(tourn)
                if self.args[1] == Tournament.IND_PHASE:
                    msg = TournamentService.inducement_msg(tourn)
                if self.args[1] == Tournament.BB_PHASE:
                    msg = TournamentService.blood_bowl_msg(tourn)
                await self.send_message(channel, msg)
            return