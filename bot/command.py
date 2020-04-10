from web import app
from misc.helpers import CardHelper
app.app_context().push()

class DiscordCommand():
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
        return switcher.get(number, str(number))

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
