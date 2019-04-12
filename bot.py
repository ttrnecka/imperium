# Works with Python 3.6
import logging
import discord
import os

from imperiumbase import ImperiumSheet
from web import db, create_app
from models.data_models import Coach, Account, Card, Pack, Transaction, TransactionError
from misc.helpers import CardHelper
from services import PackService, SheetService, CoachService, CardService


app = create_app()
app.app_context().push()

ROOT = os.path.dirname(__file__)
RULES_LINK = "https://goo.gl/GqWRwD"

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=os.path.join(ROOT, 'logs/discord.log'), encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

with open(os.path.join(ROOT, 'config/TOKEN'), 'r') as token_file:
    TOKEN=token_file.read()

client = discord.Client()

GEN_QUALITY = ["premium","budget"]
GEN_PACKS = ["player","training","booster"]


@client.event
async def on_message(message):
    logger.info(f"{message.author}: {message.content}")
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    try:
        dc = DiscordCommand(message,client)
        await dc.process()
    except:
        raise
    finally:
        db.session.close()

@client.event
async def on_ready():
    logger.info('Logged in as')
    logger.info(client.user.name)
    logger.info(client.user.id)
    logger.info('------')
    for emoji in client.get_all_emojis():
        DiscordCommand.emojis[emoji.name]=str(emoji)


class LongMessage:
    def __init__(self,client,channel):
        self.limit = 2000
        self.parts = []
        self.client = client
        self.channel=channel

    def add(self,part):
        self.parts.append(part)

    async def send(self):
        for chunk in self.chunks():
            await self.client.send_message(self.channel, chunk)

    def lines(self):
        lines = []
        for part in self.parts:
            lines.extend(part.split("\n"))
        return lines

    def chunks(self):
        lines = self.lines()
        while True:
            msg=""
            if not lines:
                break
            while len(lines)>0 and len(msg + lines[0]) < self.limit:
                msg += lines.pop(0) + "\n"
            yield msg

class DiscordCommand:
    emojis = {
        "Common": "",
        "Rare": ":diamonds:",
        "Epic": ":large_blue_diamond:",
        "Legendary": ":large_orange_diamond: ",
    }

    @classmethod
    def is_private_admin_channel(cls,dchannel):
        if dchannel.name is not None and "admin-channel" in dchannel.name:
            return True
        return False

    @classmethod
    def format_pack(cls,cards):
        msg=""
        for card,quantity in cards:
            msg+=cls.number_emoji(quantity)
            msg+=" x "
            msg+=cls.rarity_emoji(card.rarity)
            msg+=f' **{card.name}** ({card.rarity} {card.race} {card.card_type} Card)\n'
        return msg.strip("\n")

    @classmethod
    def commands(cls):
        msg="```asciidoc\n"
        msg+="__**Coach Commands**__\n"
        msg+="!list           - sends details of coach's own account by PM\n"
        msg+="!newcoach       - creates coach's account\n"
        msg+="!genpack        - generates pack and assigns it to coach\n"
        msg+="!genpackspecial - generates special play pack, does not assign it to coach, costs nothing\n"
        msg+=" \n__**Admin Commands**__\n"
        msg+="!adminlist      - lists coach's account \n"
        msg+="!adminbank      - updates to coach's bank, sends notification to the coach \n"
        msg+="!admincard      - updates to coach's collection, sends notification to the coach \n"
        msg+="!adminreset     - resets coach's account, sends notification to the coach \n"
        msg+="!adminexport    - exports all card collections to the master sheet\n"
        msg+="```"
        return msg

    @classmethod
    def gen_help(cls):
        msg="```asciidoc\n"
        msg+="!genpack command generates new pack and assigns it to coach. The coach needs to have enough coins to buy the pack.\n \n"
        msg+="= Booster budget pack =\n"
        msg+="Content: 5 cards of any type\n"
        msg+=f"Price: {PackService.PACK_PRICES['booster_budget']} coins\n"
        msg+="Rarity: 1 Rare and higher rarity, 4 Common and higher rarity\n"
        msg+="Command: !genpack booster\n \n"

        msg+="= Booster budget pack PREMIUM =\n"
        msg+="Content: 5 cards any type\n"
        msg+=f"Price: {PackService.PACK_PRICES['booster_premium']} coins\n"
        msg+="Rarity: Rare and higher\n"
        msg+="Command: !genpack booster premium\n \n"

        msg+="= Training pack =\n"
        msg+="Content: 3 training type cards\n"
        msg+=f"Price: {PackService.PACK_PRICES['training']} coins\n"
        msg+="Rarity: Commom or higher\n"
        msg+="Command: !genpack training\n \n"

        msg+="= Player pack =\n"
        msg+="Content: 3 player type cards\n"
        msg+=f"Price: {PackService.PACK_PRICES['player']} coins\n"
        msg+="Rarity: Rare or higher\n"
        msg+="Command: !genpack player <team>\n"
        msg+="where <team> is one of following:\n"
        for team in PackService.MIXED_TEAMS:
            msg+="\t"+team["code"] +" - "+ team["name"] +f" ({', '.join(team['races'])})\n"

        msg+="```"
        return msg

    @classmethod
    def adminbank_help(cls):
        msg="```"
        msg+="USAGE:\n"
        msg+="!adminbank <amount> <coach> <reason>\n"
        msg+="\t<amount>: number of coins to add to bank, if negative is used, it will be deducted from bank\n"
        msg+="\t<coach>: coach discord name or its part, must be unique\n"
        msg+="\t<reason>: describe why you are changing the coach bank\n"
        msg+="```"
        return msg

    @classmethod
    def admincard_help(cls):
        msg="```"
        msg+="USAGE:\n"
        msg+="Adds or remove card or cards from the coach\n"
        msg+="!admincard add|remove <coach> <card>;...;<card>\n"
        msg+="\tadd|remove: select one based on desired operation\n"
        msg+="\t<coach>: coach discord name or its part, must be unique\n"
        msg+="\t<card>: Exact card name as is in the All Cards list, if mutliple cards are specified separate them by **;**\n"
        msg+="```"
        return msg
    
    @classmethod
    def adminreset_help(cls):
        msg="```"
        msg+="Resets all cards and bank account for given coach to initial state\n"
        msg+="USAGE:\n"
        msg+="!adminreset <coach>\n"
        msg+="\t<coach>: coach discord name or its part, must be unique\n"
        msg+="```"
        return msg

    @classmethod
    def check_gen_command(cls,command):
        args = command.split()
        length = len(args)
        if length not in [2,3]:
            return False

        if args[1] not in GEN_PACKS:
            return False
        # training/booster without quality
        if length == 2 and args[1] not in ["training","booster"]:
            return False
        # training takes not other parameter
        if length > 2 and args[1]=="training":
            return False
        # booster with allowed quality
        if length == 3 and args[1]=="booster" and args[2] not in GEN_QUALITY:
            return False
        # player with teams
        if length == 3 and args[1]=="player" and args[2] not in PackService.team_codes():
            return False
        return True

    @classmethod
    def rarity_emoji(cls,rarity):
        return cls.emojis.get(rarity, "")

    @classmethod
    def number_emoji(cls,number):
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

    async def transaction_error(self,error):
        text = type(error).__name__ +": "+str(error)
        msg = LongMessage(self.client,self.message.channel)
        msg.add(text)
        await msg.send()
        logger.error(text)

    def __init__(self,dmessage,dclient):
        self.message = dmessage
        self.client = dclient
        self.cmd = dmessage.content.lower()
        self.args = self.cmd.split(" ")

    async def process(self):
        try:
            if self.cmd.startswith('!admin'):
                await self.__run_admin()
            if self.cmd.startswith('!list'):
                await self.__run_list()
            if self.cmd.startswith('!genpack'):
                await self.__run_genpack()
            if self.cmd.startswith('!newcoach'):
                await self.__run_newcoach()
        except ValueError as e:
            await self.transaction_error(e)
        except Exception as e:
            await self.transaction_error(e)
            #raising will not kill the discord bot but will cause it to log this to error.log as well
            raise

    async def __run_newcoach(self):
        name = str(self.message.author)
        if Coach.get_by_name(name):
            msg = LongMessage(self.client,self.message.channel)
            msg.add(f"**{self.message.author.mention}** account exists already\n")
            await msg.send()
        else:
            coach = Coach.create(str(self.message.author))
            msg = LongMessage(self.client,self.message.channel)
            msg.add(f"**{self.message.author.mention}** account created\n")
            msg.add(f"**Bank:** {coach.account.amount} coins")
            msg.add(f"**Rules**: <{RULES_LINK}>")
            await msg.send()

    async def __run_admin(self):
        # if not started from admin-channel
        if not self.__class__.is_private_admin_channel(self.message.channel):
            emsg="Insuficient rights"
            logger.error(emsg)
            await self.client.send_message(self.message.channel, emsg)
            return

        #adminhelp cmd
        if self.message.content.startswith('!adminhelp'):
            await self.client.send_message(self.message.channel, self.__class__.commands())
            return

        #adminexport cmd
        if self.message.content.startswith('!adminexport'):
            msg = LongMessage(self.client,self.message.channel)
            msg.add(f"Cards have been exported to master sheet!!! {self.message.author.mention}")
            await msg.send()
            # export
            SheetService.export_cards()
            return

        #adminlist cmd
        if self.message.content.startswith('!adminlist'):
            # require username argument
            if len(self.args)==1:
                emsg="Username missing"
                await self.client.send_message(self.message.channel, emsg)
                return

            coaches = Coach.find_all_by_name(self.args[1])
            msg = LongMessage(self.client,self.message.channel)

            if len(coaches)==0:
                msg.add("No coaches found")

            for coach in coaches:
                msg.add(f"Coach **{coach.name}**\n")
                msg.add(f"**Bank:** {coach.account.amount} coins\n")
                msg.add("**Collection**:")
                msg.add("-" * 65 + "")
                msg.add(f"{self.__class__.format_pack(CardHelper.sort_cards_by_rarity_with_quatity(coach.cards))}")
                msg.add("-" * 65 + "\n")

            await msg.send()
            return
        if self.message.content.startswith('!adminbank'):
            # require username argument
            if len(self.args)<4:
                emsg="Not enough arguments!!!\n"
                await self.client.send_message(self.message.channel, emsg)
                await self.client.send_message(self.message.channel, self.__class__.adminbank_help())
                return

            # amount must be int
            if not RepresentsInt(self.args[1]):
                emsg="<amount> is not whole number!!!\n"
                await self.client.send_message(self.message.channel, emsg)
                return

            coach = await self.coach_unique(self.args[2])
            if coach is None:
                return

            amount = int(self.args[1])
            reason = ' '.join(str(x) for x in self.message.content.split(" ")[3:]) + " - updated by " + str(self.message.author.name)

            t = Transaction(description=reason,price=-1*amount)
            try:
                coach.make_transaction(t)
            except TransactionError as e:
                await self.transaction_error(e)
                return
            else:
                msg = LongMessage(self.client,self.message.channel)
                msg.add(f"Bank for {coach.name} updated to **{coach.account.amount}** coins:\n")
                msg.add(f"Note: {reason}\n")
                msg.add(f"Change: {amount} coins")
                await msg.send()
                await  self.bank_notification(f"Your bank has been updated by **{amount}** coins due to {reason}",coach)
        
        if self.message.content.startswith('!admincard'):
            # !adminpack add/remove <coach> <card>;...;<card>
            if len(self.args)<4:
                emsg="Not enough arguments!!!\n"
                await self.client.send_message(self.message.channel, emsg)
                await self.client.send_message(self.message.channel, self.__class__.admincard_help())
                return

            # amount must be int
            if self.args[1] not in ["add","remove"]:
                emsg="specify **add** or **remove** operation!!!\n"
                await self.client.send_message(self.message.channel, emsg)
                return

            coach = await self.coach_unique(self.args[2])
            if coach is None:
                return

            card_names = [card.strip() for card in " ".join(self.args[3:]).split(";")]
            if self.args[1]=="add":
                pack = PackService.admin_pack(0,card_names)
                # situation when som of the cards cound not be found
                if len(card_names)!= len(pack.cards):
                    msg = LongMessage(self.client,self.message.channel)
                    msg.add(f"Not all cards were found, check the names!!!\n")
                    for card in card_names:
                        if card in [card.name.lower() for card in pack.cards]:
                            found = True
                        else:
                            found = False
                        found_msg = "**not found**" if not found else "found"
                        msg.add(f"{card}: {found_msg}")
                    await msg.send()
                    return
                reason = f"{self.args[1].capitalize()} {';'.join(card_names)} - by " + str(self.message.author.name)

                t = Transaction(pack=pack, description=reason,price=0)
                try:
                    coach.make_transaction(t)
                except TransactionError as e:
                    await self.transaction_error(e)
                    return
                else:
                    msg = LongMessage(self.client,self.message.channel)
                    msg.add(f"**{PackService.description(pack)}** for @{coach.name} - **{pack.price}** coins:\n")
                    msg.add(f"{self.__class__.format_pack(CardHelper.sort_cards_by_rarity_with_quatity(pack.cards))}\n")
                    msg.add(f"**Bank:** {coach.account.amount} coins")
                    await msg.send()
                    await  self.bank_notification(f"Card(s) **{' ,'.join([card.name for card in pack.cards])}** added to your collection by {str(self.message.author.name)}",coach)
                    return

            if self.args[1]=="remove":
                cards = [CardService.get_Card_from_coach(coach,name) for name in card_names]
                cards = [card for card in cards if card is not None]
                # situation when som of the cards could not be found
                if len(card_names)!= len(cards):
                    msg = LongMessage(self.client,self.message.channel)
                    msg.add(f"Not all cards were found, check the names!!!\n")
                    for card in card_names:
                        if card in [card.name.lower() for card in cards]:
                            found = True
                        else:
                            found = False
                        found_msg = "**not found**" if not found else "found"
                        msg.add(f"{card}: {found_msg}")
                    await msg.send()
                    return

                reason = f"{self.args[1].capitalize()} {';'.join(card_names)} - by " + str(self.message.author.name)
                t = Transaction(description=reason,price=0)

                try:
                    for card in cards:
                        db.session.delete(card)
                       # db.session.commit()
                    coach.make_transaction(t)
                except TransactionError as e:
                    await self.transaction_error(e)
                    return
                else:
                    msg = LongMessage(self.client,self.message.channel)
                    msg.add(f"Cards removed from @{coach.name} collection:\n")
                    msg.add(f"{self.__class__.format_pack(CardHelper.sort_cards_by_rarity_with_quatity(cards))}\n")
                    await msg.send()
                    await  self.bank_notification(f"Card(s) **{' ,'.join([card.name for card in cards])}** removed from your collection by {str(self.message.author.name)}",coach)
                    return
                    
        if self.message.content.startswith('!adminreset'):
            # require username argument
            if len(self.args)!=2:
                emsg="Bad number of arguments!!!\n"
                await self.client.send_message(self.message.channel, emsg)
                await self.client.send_message(self.message.channel, self.__class__.adminreset_help())
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
                msg = LongMessage(self.client,self.message.channel)
                msg.add(f"Coach {new_coach.name} was reset")
                await msg.send()
                await  self.bank_notification(f"Your account was reset",new_coach)

    async def __run_list(self):
        coach = Coach.get_by_name(str(self.message.author))
        if coach is not None:

            msg = LongMessage(self.client,self.message.author)
            msg.add(f"**Bank:** {coach.account.amount} coins\n")
            msg.add("**Collection**:\n")
            msg.add("-" * 65 + "")
            msg.add(f"{self.__class__.format_pack(CardHelper.sort_cards_by_rarity_with_quatity(coach.cards))}")
            msg.add("-" * 65 + "\n")
            await msg.send()
            await self.client.send_message(self.message.channel, "Collection sent to PM")
        else:
            await self.client.send_message(self.message.channel, f"Coach {self.message.author.mention} does not exist. Use !newcoach to create coach first.")

    async def __run_genpack(self):
        if self.__class__.check_gen_command(self.cmd):
            ptype = self.args[1]
            if ptype=="player":
                team = self.args[2]
                pack = PackService.generate(ptype,team)
            elif ptype=="training":
                pack = PackService.generate(ptype)
            elif ptype=="booster":
                ptype = "booster_budget" if len(self.args)<3 else f"booster_{self.args[2]}"
                pack = PackService.generate(ptype)

            #free pack
            if self.cmd.startswith('!genpackspecial'):
                #just send message, no processing
                msg = LongMessage(self.client,self.message.channel)
                msg.add(f"**Special Play {PackService.description(pack)}**:\n")
                msg.add(f"{self.__class__.format_pack(CardHelper.sort_cards_by_rarity_with_quatity(pack.cards))}\n")
                msg.add("**Note**: This is used for Special Play purposes only!!!")
                await msg.send()
            #standard pack
            else:
                coach=Coach.get_by_name(str(self.message.author))
                
                just_joined = True if len(coach.packs)==0 else False

                if coach is None:
                    await self.client.send_message(self.message.channel, f"Coach {self.message.author.mention} does not exist. Use !newcoach to create coach first.")
                    return
                t = Transaction(pack = pack,price=pack.price,description=PackService.description(pack))
                try:
                    coach.make_transaction(t)
                except TransactionError as e:
                    await self.transaction_error(e)
                    return
                else:
                    # transaction is ok and coach is saved
                    msg = LongMessage(self.client,self.message.channel)
                    msg.add(f"**{PackService.description(pack)}** for **{self.message.author}** - **{pack.price}** coins:\n")
                    msg.add(f"{self.__class__.format_pack(CardHelper.sort_cards_by_rarity_with_quatity(pack.cards))}\n")
                    msg.add(f"**Bank:** {coach.account.amount} coins")
                    await msg.send()

                    #if just joined
                    if just_joined:
                        amount = 5
                        reason = 'Joining bonus'

                        t = Transaction(description=reason,price=-1*amount)
                        try:
                            coach.make_transaction(t)
                        except TransactionError as e:
                            await self.transaction_error(e)
                            return
                        else:
                            await  self.bank_notification(f"Your bank has been updated by **{amount}** coins due to {reason}",coach)
                            return
                    
                    return
        else:
            await self.client.send_message(self.message.channel, self.__class__.gen_help())

    async def coach_unique(self,name):
        # find coach
            coaches = Coach.find_all_by_name(name)
            if len(coaches)==0:
                emsg=f"<coach> __{name}__ not found!!!\n"
                await self.client.send_message(self.message.channel, emsg)
                return None

            if len(coaches)>1:
                emsg=f"<coach> __{name}__ not **unique**!!!\n"
                emsg+="Select one: "
                for coach in coaches:
                    emsg+=coach.name
                    emsg+=" "
                await self.client.send_message(self.message.channel, emsg)
                return None
            return coaches[0]

    #must me under 2000 chars
    async def bank_notification(self,msg,coach):
        print(coach.discord_id())

        member = discord.utils.get(self.client.get_all_members(), name=coach.short_name(), discriminator=coach.discord_id())
        channel = discord.utils.get(self.client.get_all_channels(), name='bank-notifications')
        await self.client.send_message(channel, f"{member.mention}: "+msg)
        return 

def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

client.run(TOKEN)
