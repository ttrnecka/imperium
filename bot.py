"""Bot"""
import os
import logging
from logging.handlers import RotatingFileHandler
import traceback

import discord
from sqlalchemy import func

from web import db, app
from models.data_models import Coach, Pack, Transaction
from models.data_models import TransactionError, Tournament, TournamentSignups
from misc.helpers import CardHelper
from misc.helpers import represents_int
from services import PackService, CardService, TournamentService, CoachService
from services import DusterService, RegistrationError, DustingError, TournamentError

ROOT = os.path.dirname(__file__)
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(
    os.path.join(ROOT, 'logs/discord.log'), maxBytes=10000000,
    backupCount=5, encoding='utf-8', mode='a'
)
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

app.app_context().push()

RULES_LINK = "https://bit.ly/2P9Y07F"
GEN_QUALITY = ["premium", "budget"]
GEN_PACKS = ["player", "training", "booster", "special"]
GEN_PACKS_TMP = ["player", "training", "booster", "special", "skill", "coaching", "positional", "legendary"]

AUTO_CARDS = {
    'Loose Change!':5,
    'Bank Error!':10,
    'Lottery Win!':15
}

client = discord.Client()
def log_response(response):
    """Log command response"""
    logger.info("Response:\n%s", response)

@client.event
async def on_message(message):
    """Message event handler"""
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    #ignore DM
    if isinstance(message.channel, discord.abc.PrivateChannel):
        await message.channel.send(
            "PM commands are not allowed. Please use the Imperium discord server."
        )
        return

    #ignore commands not starting with !
    if not message.content.startswith("!"):
        return

    logger.info("%s: %s", message.author, message.content)

    try:
        command = DiscordCommand(message, client)
        await command.process()
    finally:
        db.session.close()

@client.event
async def on_ready():
    """loads custom emojis upon ready"""
    logger.info('Logged in as')
    logger.info(client.user.name)
    logger.info(client.user.id)
    logger.info('------')
    for emoji in client.emojis:
        DiscordCommand.emojis[emoji.name] = str(emoji)

class LongMessage:
    """Class to handle long message sending in chunks"""
    def __init__(self, channel):
        self.limit = 2000
        self.parts = []
        self.channel = channel

    def add(self, part):
        """Adds part of long message"""
        self.parts.append(part)

    async def send(self):
        """sends the message to channel in limit chunks"""
        for chunk in self.chunks():
            await self.channel.send(chunk)
        log_response('\n'.join(self.lines()))

    def lines(self):
        """transforms the message to lines"""
        lines = []
        for part in self.parts:
            lines.extend(part.split("\n"))
        return lines

    def chunks(self):
        """Transform the lines to limit sized chunks"""
        lines = self.lines()
        while True:
            msg = ""
            if not lines:
                break
            while lines and len(msg + lines[0]) < self.limit:
                msg += lines.pop(0) + "\n"
            yield msg

class DiscordCommand:
    """Main class to process commands"""
    emojis = {
        "Common": "",
        "Rare": ":diamonds:",
        "Epic": ":large_blue_diamond:",
        "Legendary": ":large_orange_diamond: ",
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
            value += card.get('value') * quantity
            msg += cls.number_emoji(quantity)
            msg += " x "
            msg += cls.rarity_emoji(card.get('rarity'))
            if not display():
                name = "Reaction Card"
                cvalue = "?"
            else:
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
            f"{cls.format_pack(CardHelper.sort_cards_by_rarity_with_quatity(coach.cards), show_hidden=True)}",
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

    @classmethod
    def commands(cls):
        """help message"""
        msg = "```asciidoc\n"
        msg += "__**Coach Commands**__\n"
        msg += "!list           - sends details of coach's own account by PM\n"
        msg += "!complist       - displays tournaments\n"
        msg += "!sign           - sign to tournament\n"
        msg += "!resign         - resign from tournament\n"
        msg += "!newcoach       - creates coach's account\n"
        msg += "!genpack        - generates pack and assigns it to coach\n"
        msg += "!genpacktemp    - generates inducement or special play pack,"
        msg += " does not assign it to coach, costs nothing\n"
        msg += " \n__**Admin Commands**__\n"
        msg += "!adminlist      - lists coach's account \n"
        msg += "!adminbank      - updates to coach's bank, sends notification to the coach \n"
        msg += "!admincard      - updates to coach's collection, sends notification to the coach \n"
        msg += "!adminreset     - resets coach's account, sends notification to the coach \n"
        msg += "!adminexport    - exports all card collections to the master sheet\n"
        msg += "!adminsign      - sign specified coach to tournament\n"
        msg += "!adminresign    - resign specified coach from tournament\n"
        msg += "!adminrole      - manage admin roles for web/bot\n"
        msg += "!adminquest     - marks quests are achieved or not achieved\n"
        msg += "```"
        return msg

    @classmethod
    def gen_help(cls):
        """help message"""
        msg = "```asciidoc\n"
        msg += "!genpack command generates new pack and assigns it to coach. The coach "
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

        msg += "```\n"
        return msg

    @classmethod
    def gentemp_help(cls):
        """help message"""
        msg = "```asciidoc\n"
        msg += "!genpacktemp command generates special play or inducement packs. "
        msg += "These packs are for one time use and are not assigned to coaches "
        msg += "permanent collection.\n \n"
        msg += "= Booster budget pack =\n"
        msg += "Content: 5 cards of any type\n"
        msg += "Rarity: 1 Rare and higher rarity, 4 Common and higher rarity\n"
        msg += "Command: !genpacktemp booster\n \n"

        msg += "= Booster premium pack =\n"
        msg += "Content: 5 cards any type\n"
        msg += "Rarity: Rare and higher\n"
        msg += "Command: !genpacktemp booster premium\n \n"

        msg += "= Training pack =\n"
        msg += "Content: 3 training type cards\n"
        msg += "Rarity: Common or higher\n"
        msg += "Command: !genpacktemp training\n \n"

        msg += "= Inducement Skill pack =\n"
        msg += "Content: 5 training type cards\n"
        msg += "Rarity: Common or higher\n"
        msg += "Command: !genpacktemp skill\n \n"

        msg += "= Inducement Coaching pack =\n"
        msg += "Content: 3 training type cards\n"
        msg += "Rarity: Rare or Epic\n"
        msg += "Command: !genpacktemp coaching\n \n"

        msg += "= Special Play pack (incl. Inducement) =\n"
        msg += "Content: 3 special play type cards\n"
        msg += "Rarity: Common or higher\n"
        msg += "Command: !genpacktemp special\n \n"

        msg += "= Player pack =\n"
        msg += "Content: 3 player type cards\n"
        msg += "Rarity: Rare or higher\n"
        msg += "Command: !genpacktemp player <team>\n \n"

        msg += "= Inducement Positional pack =\n"
        msg += "Content: 3 positional player type cards\n"
        msg += "Rarity: Rare or higher\n"
        msg += "Command: !genpacktemp positional <team>\n \n"

        msg += "= Legendary pack =\n"
        msg += "Content: 1 legendary player type cards\n"
        msg += "Rarity: Legendary\n"
        msg += "Command: !genpacktemp legendary <team>\n \n"

        msg += "where <team> is one of following:\n"
        for team in PackService.MIXED_TEAMS:
            msg += "\t"+team["code"] +" - "+ team["name"] +f" ({', '.join(team['races'])})\n"

        msg += "```"
        return msg

    @classmethod
    def adminbank_help(cls):
        """help message"""
        msg = "```"
        msg += "USAGE:\n"
        msg += "!adminbank <amount> <coach> <reason>\n"
        msg += "\t<amount>: number of coins to add to bank, if negative is used, "
        msg += "it will be deducted from bank\n"
        msg += "\t<coach>: coach discord name or its part, must be unique\n"
        msg += "\t<reason>: describe why you are changing the coach bank\n"
        msg += "```"
        return msg

    @classmethod
    def admincard_help(cls):
        """help message"""
        msg = "```"
        msg += "USAGE 1:\n"
        msg += "Adds or removes card or cards from the coach\n"
        msg += "!admincard add|remove <coach> <card>;...;<card>\n"
        msg += "\tadd|remove: select one based on desired operation\n"
        msg += "\t<coach>: coach discord name or its part, must be unique\n"
        msg += "\t<card>: Exact card name as is in the All Cards list, "
        msg += "if mutliple cards are specified separate them by **;**\n"
        msg += " \nUSAGE 2:\n"
        msg += "Updates card database from the master sheet\n"
        msg += "!admincard update\n"
        msg += "```"
        return msg

    @classmethod
    def adminrole_help(cls):
        """help message"""
        msg = "```"
        msg += "USAGE:\n"
        msg += "Adds or removes bot/web roles for coach\n"
        msg += "!adminrole add|remove <coach> <role>\n"
        msg += "\tadd|remove: select one based on desired operation\n"
        msg += "\t<coach>: coach discord name or its part, must be unique\n"
        msg += "\t<role>: webadmin - enables coach to do admin tasks on web\n"
        msg += "```"
        return msg

    @classmethod
    def adminreset_help(cls):
        """help message"""
        msg = "```"
        msg += "Resets all cards and bank account for given coach to initial state\n"
        msg += "USAGE:\n"
        msg += "!adminreset <coach>\n"
        msg += "\t<coach>: coach discord name or its part, must be unique\n"
        msg += "```"
        return msg

    @classmethod
    def sign_help(cls):
        """help message"""
        msg = "```"
        msg += "Signs coach to tournament\n"
        msg += "USAGE:\n"
        msg += "!sign <id>\n"
        msg += "\t<id>: id of tournament from !complist\n"
        msg += "```"
        return msg

    @classmethod
    def resign_help(cls):
        """help message"""
        msg = "```"
        msg += "Resigns coach from tournament\n"
        msg += "USAGE:\n"
        msg += "!resign <id>\n"
        msg += "\t<id>: id of tournament from !complist\n"
        msg += "```"
        return msg

    @classmethod
    def adminsign_help(cls):
        """help message"""
        msg = "```"
        msg += "Signs coach to tournament\n"
        msg += "USAGE:\n"
        msg += "!adminsign <id> <coach>\n"
        msg += "\t<id>: id of tournament from !complist\n"
        msg += "\t<coach>: coach discord name or its part, must be unique\n"
        msg += "```"
        return msg

    @classmethod
    def adminresign_help(cls):
        """help message"""
        msg = "```"
        msg += "Resigns coach from tournament\n"
        msg += "USAGE:\n"
        msg += "!adminresign <id> <coach>\n"
        msg += "\t<id>: id of tournament from !complist\n"
        msg += "\t<coach>: coach discord name or its part, must be unique\n"
        msg += "```"
        return msg

    @classmethod
    def adminquest_help(cls):
        """help message"""
        msg = "```"
        msg += "Manually marks the quest as achieved or not. Does not award the prize\n"
        msg += "USAGE:\n"
        msg += "!adminquest <on|off> <coach> <quest>\n"
        msg += "\t<on|off>: on to mark, off the clear flag\n"
        msg += "\t<coach>: coach discord name or its part, must be unique\n"
        msg += "\t<quest>: *collect3legends* or *buildyourownlegend*\n"
        msg += "```"
        return msg

    @classmethod
    def admincomp_help(cls):
        """help message"""
        msg = "```"
        msg += "Tournament helper\n"
        msg += "USAGE:\n"
        msg += "!admincomp start|stop|update|special_play|inducements|reaction|blood_bowl <id>\n"
        msg += "\tstart: Notifies all registered coaches that tournament started "
        msg += "in the tournament channel and links the ledger\n"
        msg += "\tstop: Resigns all coaches from the tournament\n"
        msg += "\tupdate: Updates data from Tournament sheet\n"
        msg += "\tspecial_play: Initiates special play phase\n"
        msg += "\tinducement: Initiates inducement phase\n"
        msg += "\treaction: Initiates reaction phase\n"
        msg += "\tblood_bowl: Initiates blood bowl phase\n"
        msg += "\t<id>: id of tournament from Tournamet master sheet\n"
        msg += "```"
        return msg

    @classmethod
    def dust_help(cls):
        """help message"""
        msg = "```"
        msg += "Dusts cards. When Player type card is added first the Tryouts dusting "
        msg += "will take place, otherwise Drills is initiated.\n \n"
        msg += "USAGE:\n"
        msg += "!dust show\n"
        msg += "\tshows the duster content\n"
        msg += "!dust add <card name>;...;<card_name>\n"
        msg += "\tadds card(s) to duster. Card is flagged for dusting but not deleted yet.\n"
        msg += "!dust remove <card name>;...;<card_name>\n"
        msg += "\tremoves card(s) from duster\n"
        msg += "!dust cancel\n"
        msg += "\tdiscards duster, all cards in it will be released\n"
        msg += "!dust commit\n"
        msg += "\tduster is submitted, the cards are deleted and appropriated pack will "
        msg += "be free of charge next time !genpack is issued\n"
        msg += "```"
        return msg

    @classmethod
    def check_gen_command(cls, command):
        """Checks the validity if genpack command"""
        args = command.split()
        length = len(args)
        if length not in [2, 3]:
            return False

        if args[1] not in GEN_PACKS:
            return False
        # training/booster/special without quality
        if length == 2 and args[1] not in ["training", "booster", "special"]:
            return False
        # training/special takes not other parameter
        if length > 2 and args[1] in ["training", "special"]:
            return False
        # booster with allowed quality
        if length == 3 and args[1] == "booster" and args[2] not in GEN_QUALITY:
            return False
        # player with teams
        if length == 3 and args[1] == "player" and args[2] not in PackService.team_codes():
            return False
        if length > 3:
            return False

        return True

    @classmethod
    def check_gentemp_command(cls, command):
        """Checks the validity if genpacktemp command"""
        args = command.split()
        length = len(args)
        if length not in [2, 3]:
            return False

        if args[1] not in GEN_PACKS_TMP:
            return False
        # skill/coaching/special/booster without quality
        if length == 2 and args[1] not in ["skill", "coaching", "special", "booster", "training"]:
            return False
        # skill/coaching/special takes not other parameter
        if length > 2 and args[1] in ["skill", "coaching", "special", "training"]:
            return False
        # booster with allowed quality
        if length == 3 and args[1] == "booster" and args[2] not in GEN_QUALITY:
            return False
        # player with teams
        if (length == 3 and args[1] in ["player", "positional", "legendary"]
                and args[2] not in PackService.team_codes()):
            return False
        if length > 3:
            return False

        return True

    def __init__(self, dmessage, dclient):
        self.message = dmessage
        self.client = dclient
        self.cmd = dmessage.content.lower()
        self.args = self.cmd.split()

    async def process(self):
        """Process the command"""
        try:
            if self.cmd.startswith('!newcoach'):
                await self.__run_newcoach()
            elif self.cmd.startswith('!admin'):
                await self.__run_admin()
            elif self.cmd.startswith('!list'):
                await self.__run_list()
            elif self.cmd.startswith('!genpacktemp'):
                await self.__run_genpacktemp()
            elif self.cmd.startswith('!genpack'):
                await self.__run_genpack()
            elif self.cmd.startswith('!complist'):
                await self.__run_complist()
            elif self.cmd.startswith('!sign'):
                await self.__run_sign()
            elif self.cmd.startswith('!resign'):
                await self.__run_resign()
            elif self.cmd.startswith('!dust'):
                await self.__run_dust()
            elif self.cmd.startswith('!done'):
                await self.__run_done()
            elif self.cmd.startswith('!left'):
                await self.__run_left()
        except (ValueError, TransactionError, RegistrationError) as e:
            await self.transaction_error(e)
        except Exception as e:
            await self.transaction_error(e)
            #raising will not kill the discord bot but will cause it to log this to log as well
            raise

    async def send_message(self, channel, message_list):
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

    #checks pack for AUTO_CARDS and process them
    async def auto_cards(self, pack):
        """Routine to process auto cards from the pack"""
        for card in pack.cards:
            if card.get('name') in AUTO_CARDS.keys():
                reason = "Autoprocessing "+card.get('name')
                amount = AUTO_CARDS[card.get('name')]
                msg = f"Your card {card.get('name')} has been processed. You were granted {amount} coins"
                tran = Transaction(description=reason, price=-1*amount)
                try:
                    db.session.delete(card)
                    pack.coach.make_transaction(tran)
                except TransactionError as e:
                    await self.transaction_error(e)
                    return
                else:
                    await  self.bank_notification(msg, pack.coach)
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
    # commands
    async def __run_newcoach(self):
        if Coach.get_by_discord_id(self.message.author.id):
            await self.reply([f"**{self.message.author.mention}** account exists already\n"])
        else:
            try:
                coach = CoachService.new_coach(self.message.author, self.message.author.id)
            except TransactionError as e:
                await self.transaction_error(e)
                return
            msg = [
                f"**{self.message.author.mention}** account created\n",
                f"**Bank:** {coach.account.amount} coins",
                f"**Rules**: <{RULES_LINK}>"
            ]
            await self.reply(msg)

    async def __run_list(self):
        with db.session.no_autoflush:
            coach = Coach.get_by_discord_id(self.message.author.id)
            show_starter = True if len(self.args) > 1 and self.args[1] == "all" else False

            if coach is None:
                await self.reply(
                    [(f"Coach {self.message.author.mention} does not exist."
                    "Use !newcoach to create coach first.")]
                )
                return

            all_cards = coach.cards
            sp_msg = " (with Starter Pack)"
            if not show_starter:
                all_cards = [card for card in all_cards if not card.is_starter]
                sp_msg = ""

            msg = [
                f"**Bank:** {coach.account.amount} coins\n",
                f"**Tournaments:**",
                *[f'{t.tournament_id}. {t.name}, status: {t.status}, expected start: {t.expected_start_date}' for t in coach.tournaments],
                f"\n**Collection**{sp_msg}:",
                "-" * 65 + "",
                self.__class__.format_pack(CardHelper.sort_cards_by_rarity_with_quatity(all_cards), show_hidden=True),
                "-" * 65 + "\n"
            ]

            if coach.duster:
                msg.append(f"**Dusting** - {coach.duster.type} - {coach.duster.status}")

            admin_in = Tournament.query.filter(Tournament.admin == coach.short_name(), Tournament.status.in_(("OPEN", "RUNNING"))).all()

            if admin_in:
                msg.append(f"**Tournament Admin:**")
                msg.extend([f'{t.tournament_id}. {t.name}, status: {t.status}, channel: {t.discord_channel}' for t in admin_in])

            free_packs = coach.get_freepacks()
            if free_packs:
                msg.append(f"**Free Packs:**")
                msg.append((', ').join(free_packs))

            await self.send_message(self.message.author, msg)
            await self.short_reply("Info sent to PM")
    
    async def __run_done(self):
        coach = Coach.get_by_discord_id(self.message.author.id)
        room = self.message.channel.name

        if coach is None:
            await self.reply(
                [(f"Coach {self.message.author.mention} does not exist."
                "Use !newcoach to create coach first.")]
            )
            return
        try:
            if TournamentService.confirm_phase(coach,room):
                msg = f"Phase confirmed for {coach.short_name()}"
            else:
                msg = "No deck found!"
        except TournamentError as e:
            await self.transaction_error(e)
            return
        await self.short_reply(msg)

    async def __run_left(self):
        room = self.message.channel.name
        try:
            coaches = TournamentService.left_phase(room)
            msg = ["**Left:**"]
            for coach in coaches:
                msg.append(coach.short_name())
        except TournamentError as e:
            await self.transaction_error(e)
            return
        await self.reply(msg)
        
    async def __run_genpacktemp(self):
        if self.__class__.check_gentemp_command(self.cmd):
            ptype = self.args[1]
            coach = Coach.get_by_discord_id(self.message.author.id)

            if coach is None:
                await self.reply([f"Coach {self.message.author.mention} does not exist. Use !newcoach to create coach first."])
                return

            if ptype in ["player", "positional", "legendary"]:
                team = self.args[2]
                pack = PackService.generate(ptype, team=team)
            elif ptype in ["training", "special", "skill", "coaching"]:
                pack = PackService.generate(ptype)
            elif ptype == "booster":
                ptype = "booster_budget" if len(self.args) < 3 else f"booster_{self.args[2]}"
                pack = PackService.generate(ptype)

            msg = [
                f"**Temporary {PackService.description(pack)}**:\n",
                f"{self.__class__.format_pack(CardHelper.sort_cards_by_rarity_with_quatity(pack.cards), show_hidden=True)}\n",
                "**Note**: This is one time pack for Special Play or Inducement purposes only!!!"]
            await self.reply(msg)
        else:
            await self.short_reply(self.__class__.gentemp_help())

    async def __run_genpack(self):
        if self.__class__.check_gen_command(self.cmd):
            ptype = self.args[1]
            coach = Coach.get_by_discord_id(self.message.author.id)

            if coach is None:
                await self.reply([f"Coach {self.message.author.mention} does not exist. Use !newcoach to create coach first."])
                return

            pp_count = db.session.query(Pack.id).filter_by(coach_id=coach.id, pack_type="player").count()

            if ptype == "player":
                team = self.args[2]
                first = True if pp_count == 0 else False
                pack = PackService.generate(ptype, team=team, first=first, coach=coach)
            elif ptype == "training" or ptype == "special":
                pack = PackService.generate(ptype, coach=coach)
            elif ptype == "booster":
                ptype = "booster_budget" if len(self.args) < 3 else f"booster_{self.args[2]}"
                pack = PackService.generate(ptype, coach=coach)

            try:
                duster = coach.duster
                duster_on = False
                duster_txt = ""
                if pp_count > 0 and duster and duster.status == "COMMITTED":
                    if (ptype == "player" and duster.type == "Tryouts" or
                            ptype == "training" and duster.type == "Drills" or
                            ptype == "special" and duster.type == "Drills"):
                        duster_on = True
                        duster_txt = f" ({duster.type})"
                        db.session.delete(duster)

                free_packs = coach.get_freepacks()

                if ptype in ["player"] and not duster_on:
                    if ptype in free_packs:
                        pack.price = 0
                        coach.remove_from_freepacks(ptype)
                    else:
                        raise TransactionError(
                            "You need to commit Tryouts or earn the pack through" +
                            " Achievements to be able to generate this pack!"
                        )

                if ptype in ["training", "special"] and not duster_on:
                    raise TransactionError(
                        "You need to commit Drills to be able to generate this pack!"
                    )

                if ptype in ["booster_budget", "booster_premium"]:
                    if ptype in free_packs:
                        pack.price = 0
                        coach.remove_from_freepacks(ptype)

                tran = Transaction(pack=pack, price=pack.price, description=PackService.description(pack))
                coach.make_transaction(tran)
            except TransactionError as e:
                await self.transaction_error(e)
                return
            else:
                # transaction is ok and coach is saved
                msg = [
                    f"**{PackService.description(pack)}** for **{self.message.author}** - **{pack.price}** coins{duster_txt}:\n",
                    f"{self.__class__.format_pack(CardHelper.sort_cards_by_rarity_with_quatity(pack.cards))}\n",
                    f"**Bank:** {coach.account.amount} coins"
                ]
                await self.reply(msg)
                await self.auto_cards(pack)
                CoachService.check_collect_three_legends_quest(coach)

                return
        else:
            await self.short_reply(self.__class__.gen_help())

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

            if self.args[1] not in ["start", "stop", "update", "special_play", "inducement", "reaction","blood_bowl"]:
                await self.reply(["Incorrect arguments!!!", self.__class__.admincomp_help()])

            if self.args[1] in ["start", "stop", "special_play", "inducement", "reaction","blood_bowl"]:
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
                TournamentService.release_one_time_cards(tourn)
                for coach in tourn.coaches:
                    TournamentService.unregister(tourn, coach, admin=True, refund=False)
                TournamentService.reset_phase(tourn)
                db.session.commit()
                await self.reply([f"Coaches have been resigned from {tourn.name}!!!\n"])
                return

            if self.args[1] in ["start", "special_play", "inducement", "reaction","blood_bowl"]:
                if not tourn.discord_channel:
                    await self.reply([f"Discord channel is not defined, please update it in Tournament sheet and run **!admincomp update**!\n"])
                    return

                channel = discord.utils.get(self.client.get_all_channels(), name=tourn.discord_channel.lower())
                if not channel:
                    await self.reply([f"Discord channel {tourn.discord_channel.lower()} does not exists, please create it and rerun this command!\n"])
                    return

                if not tourn.admin:
                    await self.reply([f"Tournament admin is not defined, please update it in Tournament sheet and run **!admincomp update**!\n"])
                    return

                admin = discord.utils.get(self.message.guild.members, name=tourn.admin)
                if not admin:
                    await self.reply([f"Tournament admin {tourn.admin} was not found on the discord server, check name in the Tournament sheet and run **!admincomp update**!\n"])
                    return

                if self.args[1] == "start":
                    TournamentService.reset_phase(tourn)
                    db.session.commit()
                    TournamentService.release_reserves(tourn)

                    submit_deck_channel = discord.utils.get(self.client.get_all_channels(), name='submit-a-deck')

                    members = [discord.utils.get(self.message.guild.members, id=coach.disc_id) for coach in tourn.coaches.filter(TournamentSignups.mode == "active")]
                    msg = [member.mention for member in members if member]
                    msg.append(f"This will be scheduling channel for your {tourn.name}")
                    if submit_deck_channel:
                        msg.append(f"Please submit decks as instructed in {submit_deck_channel.mention}")
                    msg.append(f"We start on {tourn.expected_start_date}!")
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
                
                if self.args[1] == "special_play":
                    msg = TournamentService.special_play_msg(tourn)
                if self.args[1] == "inducement":
                    msg = TournamentService.inducement_msg(tourn)
                if self.args[1] == "reaction":
                    msg = TournamentService.reaction_msg(tourn)
                if self.args[1] == "blood_bowl":
                    msg = TournamentService.blood_bowl_msg(tourn)
                await self.send_message(channel, msg)
            return

    async def __run_complist(self):
        if len(self.args) == 2 and not (represents_int(self.args[1]) or self.args[1] in ["all", "full", "free"]):
            await self.reply([f"**{self.args[1]}** is not a number or 'all', 'full' or 'free'!!!\n"])
            return

        if len(self.args) > 2:
            if self.args[1] not in ["all", "full", "free"]:
                await self.reply([f"**{self.args[1]}** is not 'all', 'full' or 'free'!!!\n"])
                return

            if self.args[2] not in ["bigo", "gman", "rel"]:
                await self.reply([f"**{self.args[2]}** is not 'bigo', 'gman' or 'rel'!!!\n"])
                return

        #detail
        if len(self.args) == 2 and represents_int(self.args[1]):
            tourn = Tournament.query.filter_by(tournament_id=int(self.args[1])).one_or_none()
            if not tourn:
                await self.reply([f"Tournament **id** does not exist\n"])
                return
            coaches = tourn.coaches.filter(TournamentSignups.mode == "active").all()
            count = len(coaches)

            msg = [
                f"__**{tourn.name}**__  - **{tourn.status}**\n",
                f"**Type**: {tourn.region} - {tourn.type} - {tourn.mode}",
                f"**Dates**: Signup By/Start By/End By/Deadline  - {tourn.signup_close_date}/{tourn.expected_start_date}/{tourn.expected_end_date}/{tourn.deadline_date}",
                f"**Entrance Fee**: {tourn.fee}",
                f"**Deck Size**: {tourn.deck_limit}",
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

            await self.reply(msg)
            return

        #list
        else:
            if len(self.args) >= 2 and self.args[1] == "all":
                tourns = Tournament.query.all()
                tmsg = "All"
            elif len(self.args) >= 2 and self.args[1] == "full":
                tourns = Tournament.query.outerjoin(Tournament.tournament_signups).filter(Tournament.status == "OPEN").group_by(Tournament).having(func.count_(Tournament.tournament_signups) == Tournament.coach_limit+Tournament.reserve_limit).all()
                tmsg = "Full"
            elif len(self.args) >= 2 and self.args[1] == "free":
                tourns = Tournament.query.outerjoin(Tournament.tournament_signups).filter(Tournament.status == "OPEN").group_by(Tournament).having(func.count_(Tournament.tournament_signups) < Tournament.coach_limit+Tournament.reserve_limit).all()
                tmsg = "Free"
            else:
                tourns = Tournament.query.filter_by(status="OPEN").all()
                tmsg = "Open"

            if len(self.args) > 2:
                tourns = [tourn for tourn in tourns if tourn.region.lower().replace(" ", "") == self.args[2] or tourn.region.lower() == "all"]

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
            await self.reply(msg)
            return

    async def __run_sign(self):
        coach = Coach.get_by_discord_id(self.message.author.id)
        if coach is None:
            await self.reply([f"Coach {self.message.author.mention} does not exist. Use !newcoach to create coach first."])
            return
        if not await self.sign(self.args, coach):
            await self.short_reply(self.__class__.sign_help())
        return

    async def __run_resign(self):
        coach = Coach.get_by_discord_id(self.message.author.id)
        if coach is None:
            await self.reply([f"Coach {self.message.author.mention} does not exist. Use !newcoach to create coach first."])
            return
        if not await self.resign(self.args, coach):
            await self.short_reply(self.__class__.resign_help())
        return

    async def __run_dust(self):
        if (len(self.args) < 2 or
                (self.args[1] not in ["show", "add", "remove", "cancel", "commit"]) or
                self.args[1] in ["show", "cancel", "commit"] and len(self.args) != 2 or
                self.args[1] in ["add", "remove"] and len(self.args) < 3):
            await self.reply([self.__class__.dust_help()])
            return

        name = str(self.message.author)
        coach = Coach.get_by_discord_id(self.message.author.id)
        if coach is None:
            await self.reply([f"Coach {self.message.author.mention} does not exist. Use !newcoach to create coach first."])

        duster = DusterService.get_duster(coach)

        if duster.status != "OPEN":
            free_cmd = "!genpack player <type>" if duster.type == "Tryouts" else "!genpack training or !genpack special"
            await self.reply([f"Dusting has been already committed, Use **{free_cmd}** to generate a free pack first!"])
            return

        if self.args[1] in ["add", "remove"]:
            card_names = [card.strip() for card in " ".join(self.args[2:]).split(";")]

        #show
        if self.args[1] == "show":
            count = len(duster.cards)
            msg = [f"**{duster.type}** ({count}/10):"]
            for card in duster.cards:
                msg.append(card.get('name'))
            if count == 10:
                msg.append(" \nList full. You can commit the dusting now!!!")
            await self.reply(msg)
            return

        #cancel
        if self.args[1] == "cancel":
            DusterService.cancel_duster(coach)
            await self.reply(["Dusting canceled!!!"])
            return

        #commit
        if self.args[1] == "commit":
            try:
                DusterService.commit_duster(coach)
            except (TransactionError, DustingError) as e:
                await self.transaction_error(e)
                return
            else:
                msg = []
                free_cmd = "!genpack player <type>" if duster.type == "Tryouts" else "!genpack training or !genpack special"
                msg.append(f"Dusting committed! Use **{free_cmd}** to generate a free pack.\n")
                await self.reply(msg)
                return

        #add/remove
        if self.args[1] in ["add", "remove"]:
            msg = []
            for name in card_names:
                try:
                    if self.args[1] == "add":
                        result = DusterService.dust_card_by_name(coach, name)
                    if  self.args[1] == "remove":
                        result = DusterService.undust_card_by_name(coach, name)
                    if result is not None:
                        msg.append(result)
                except DustingError as e:
                    msg.append(str(e))

            await self.reply(msg)
            return

with open(os.path.join(ROOT, 'config/TOKEN'), 'r') as token_file:
    TOKEN = token_file.read()

client.run(TOKEN)
