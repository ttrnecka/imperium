"""Various helpers"""
from services import PackService
import os
import logging
from logging.handlers import RotatingFileHandler

ROOT = os.path.dirname(__file__)
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(
    os.path.join(ROOT,'..', 'logs','discord.log'), maxBytes=10000000,
    backupCount=5, encoding='utf-8', mode='a'
)
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

class BotHelp:
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
        msg += "!blessing       - returns random blessing\n"
        msg += "!curse          - returns random curse\n"
        msg += "!comp           - manages in-game comps\n"
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
        msg += "Content: 5 cards\n"
        msg += "Rarity: 1 Rare+, 4 Common+\n"
        msg += "Command: !genpacktemp booster\n \n"

        msg += "= Booster premium pack =\n"
        msg += "Content: 5 cards any type\n"
        msg += "Rarity: Rare+\n"
        msg += "Command: !genpacktemp booster premium\n \n"

        msg += "= Training pack =\n"
        msg += "Content: 3 training type cards\n"
        msg += "Rarity: Common+\n"
        msg += "Command: !genpacktemp training\n \n"

        msg += "= Inducement Skill pack =\n"
        msg += "Content: 5 training type cards\n"
        msg += "Rarity: Common+\n"
        msg += "Command: !genpacktemp skill\n \n"

        msg += "= Inducement Coaching pack =\n"
        msg += "Content: 3 training type cards\n"
        msg += "Rarity: Rare or Epic\n"
        msg += "Command: !genpacktemp coaching\n \n"

        msg += "= Special Play pack (incl. Inducement) =\n"
        msg += "Content: 3 special play type cards\n"
        msg += "Rarity: Common+\n"
        msg += "Command: !genpacktemp special\n \n"

        msg += "= Player pack =\n"
        msg += "Content: 3 player type cards\n"
        msg += "Rarity: Rare+\n"
        msg += "Command: !genpacktemp player <team>\n \n"

        msg += "= Inducement Positional pack =\n"
        msg += "Content: 3 positional player type cards\n"
        msg += "Rarity: Rare+\n"
        msg += "Command: !genpacktemp positional <team>\n \n"

        msg += "= Legendary pack =\n"
        msg += "Content: 1 legendary player type cards\n"
        msg += "Rarity: Legendary\n"
        msg += "Command: !genpacktemp legendary <team>\n \n"

        msg += "where <team> is one of following:\n"
        for team in PackService.MIXED_TEAMS:
            msg += "\t"+team["code"] +" - "+ team["name"] +f" ({', '.join(team['races'])})\n"

        msg += " \n"
        msg += "= Bloodweiser pack =\n"
        msg += "Content: 3 Bloodweiser Brawl Boost type cards\n"
        msg += "Command: !genpacktemp brawl\n \n"

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
        msg += "!admincomp start|stop|update|special_play|inducements|blood_bowl <id>\n"
        msg += "\tstart: Notifies all registered coaches that tournament started "
        msg += "in the tournament channel and links the ledger\n"
        msg += "\tstop: Resigns all coaches from the tournament\n"
        msg += "\tupdate: Updates data from Tournament sheet\n"
        msg += "\tspecial_play: Initiates special play phase\n"
        msg += "\tinducement: Initiates inducement phase\n"
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
    def blessing_help(cls):
        """help message"""
        msg = "```"
        msg += "Returns random blessing\n"
        msg += "USAGE:\n"
        msg += "!blessing <level>\n"
        msg += "\t<leve>: 1,2 or 3\n"
        msg += "```"
        return msg

    @classmethod
    def curse_help(cls):
        """help message"""
        msg = "```"
        msg += "Returns random curse\n"
        msg += "USAGE:\n"
        msg += "!curse <level>\n"
        msg += "\t<leve>: 1,2 or 3\n"
        msg += "```"
        return msg

    @classmethod
    def comp_help(cls):
        """help message"""
        msg = "```"
        msg += "Manages in-game competitions for tournaments. Needs to be run in tournament channel\n"
        msg += "USAGE:\n"
        msg += "!comp list\n"
        msg += "\tlist all competitions for tournament\n"
        msg += "!comp create ladder\n"
        msg += "\tcreates ladder comp for tournament if it does not exists\n"
        msg += "```"
        return msg

def log_response(response):
    """Log command response"""
    logger.info("Response:\n%s", response)

class LongMessage:
    """Class to handle long message sending in chunks
        channel needs to have send() method
    """
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
