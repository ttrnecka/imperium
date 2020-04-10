import traceback
import discord
import re
from misc import SKILLREG

from discord.ext import commands
from bot.helpers import logger, LongMessage
from models.data_models import db, Transaction

AUTO_CARDS = {
    'Loose Change!':5,
    'Bank Error!':10,
    'Lottery Win!':15
}

def transform_message(message, ctx):
    def skill_transform(m):
        skill_emoji = discord.utils.get(ctx.guild.emojis, name=re.sub(r'[\s-]', '', m.group(1))) or ""
        return f'{skill_emoji} {m.group(1)}{m.group(2)}'
    trans_message = re.sub(SKILLREG, skill_transform, message)
    return trans_message

class ImperiumCog(commands.Cog):
  async def cog_command_error(self, ctx, error):
      await ctx.send(error)
      text = type(error).__name__ +": "+str(error)
      logger.error(text)
      logger.error(traceback.format_exc())
      await ctx.send_help(ctx.command)
      await self.cog_after_invoke(ctx)

  async def cog_after_invoke(self, ctx):
    db.session.remove()

  @staticmethod
  async def send_embed(data, ctx):
    embed = discord.Embed(title=data['embed_title'], description=data['embed_desc'], color=0xEE8700)
    embed.set_thumbnail(url=data['thumbnail_url'])
    for field in data['embed_fields']:
        embed.add_field(name=field['name'], value=transform_message(field['value'], ctx), inline=field['inline'])
    await ctx.send(embed=embed)

  @staticmethod
  async def send_message(channel, message_list):
    """Sends messages to channel"""
    msg = LongMessage(channel)
    for message in message_list:
        msg.add(message)
    await msg.send()

  # must me under 2000 chars
  @classmethod
  async def bank_notification(cls, ctx, msg, coach):
    """Notifies coach about bank change"""
    member = discord.utils.get(ctx.guild.members, id=coach.disc_id)
    if member is None:
        mention = coach.name
    else:
        mention = member.mention

    channel = discord.utils.get(ctx.bot.get_all_channels(), name='bank-notifications')
    await cls.send_message(channel, [f"{mention}: "+msg])
    return

  #checks pack for AUTO_CARDS and process them
  @classmethod
  async def auto_cards(cls, pack, ctx):
    """Routine to process auto cards from the pack"""
    for card in pack.cards:
      if card.get('name') in AUTO_CARDS.keys():
        reason = "Autoprocessing "+card.get('name')
        amount = AUTO_CARDS[card.get('name')]
        msg = f"Your card {card.get('name')} has been processed. You were granted {amount} coins"
        tran = Transaction(description=reason, price=-1*amount)

        db.session.delete(card)
        pack.coach.make_transaction(tran)
        await cls.bank_notification(ctx, msg, pack.coach)
    return