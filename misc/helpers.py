"""Various helpers"""
from flask import session
from sqlalchemy.orm import raiseload

from models.data_models import Coach, Card, db

import io

class CardHelper:
    """CardHelper namespace"""
    rarityorder = {"Starter":10, "Common":9, "Rare":8, "Epic":7, "Inducement":6, "Blessed":5, "Cursed":4, "Legendary":2, "Unique":1}

    @staticmethod
    def card_fix(card):
        if isinstance(card, dict):
            return card['template']
        return card

    @classmethod
    def sort_cards_by_rarity(cls, cards):
        """sorts cards by rarity"""
        return sorted(cards, key=lambda x: (cls.rarityorder[cls.card_fix(x).get('rarity')], cls.card_fix(x).get('name'), cls.card_id_or_uuid(x)))

    @classmethod
    def sort_cards_by_rarity_with_quatity(cls, cards):
        """sorts cards by rarity and sums the same cards"""
        new_collection = {}
        for card in cls.sort_cards_by_rarity(cards):
            if card.get('name') in new_collection:
                new_collection[card.get('name')]["quantity"] += 1
            else:
                new_collection[card.get('name')] = {}
                new_collection[card.get('name')]["card"] = card
                new_collection[card.get('name')]["quantity"] = 1

        return [(card["card"], card["quantity"]) for card in list(new_collection.values())]
    
    @staticmethod
    def card_id_or_uuid(card):
      if isinstance(card, dict):
        id = card.get('id') if card.get('id', None) else card.get('uuid')
      else:
        id = card.id if card.id else card.uuid
      return str(id)

    @staticmethod
    def dummy_template_dict():
        template = {
            'name': "Hidden",
            'description': "",
            'card_type': "Reaction",
            'rarity': "Common",
            'value': 0
        }
        return template

    @classmethod
    def censor_cards(cls, cards):
        for card in cards:
            if isinstance(card, dict):
                if card['template']['card_type']=="Reaction":
                    card['template'] = cls.dummy_template_dict()
        return cards

def represents_int(string):
    """Check if the `s` is int"""
    try:
        int(string)
        return True
    except ValueError:
        return False

def current_user():
    """current_user"""
    return session['discord_user'] if 'discord_user' in session else None

def current_coach():
    """Returns current coach or None"""
    return Coach.query.options(
        raiseload(Coach.cards), raiseload(Coach.packs)
    ).filter_by(disc_id=current_user()['id']).one_or_none()

def owning_coach(coach):
    current = current_coach_with_inactive()
    if current and current.id == coach.id:
        return True
    return False

def current_coach_with_inactive():
    """Returns current coach or None"""
    if current_user():
        return Coach.query.with_deleted().options(
            raiseload(Coach.packs)
        ).filter_by(disc_id=current_user()['id']).one_or_none()
    return None

class InvalidUsage(Exception):
    """Error handling exception"""
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """to_dict"""
        value = dict(self.payload or ())
        value['message'] = self.message
        return value


import sys
from PIL import Image 

def image_merge(image_files):
    """Merges the image files vertically and return IO buffer with them to process further"""
    images = [Image.open(x) for x in image_files]
    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths)
    max_height = max(heights)

    new_im = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset,0))
        x_offset += im.size[0]
    bts = io.BytesIO()
    new_im.save(bts, format="png")
    bts.seek(0)
    return bts