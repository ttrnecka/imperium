"""Imperiumr Sheet Service helpers"""
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

ROOT = os.path.dirname(__file__)

# use CREDS to create a client to interact with the Google Drive API
SCOPE = ['https://spreadsheets.google.com/feeds']
CREDS = ServiceAccountCredentials.from_json_keyfile_name(
    os.path.join(ROOT, '../config/client_secret.json'), SCOPE)


class ImperiumSheetService:
    """Namespace class"""
    SPREADSHEET_ID = "1t5IoiIjPAS2CD63P6xI4hWwx9c1SEzW9AL1LJ4LK6og"
    # dev spreadsheet below
    #SPREADSHEET_ID = "1z59ftfIYxsSZ_OwQs2KaFGzSuYizSMdSCdW6DGAj4Ms"
    ALL_CARDS_SHEET = "All Cards"
    TRAINING_CARDS_SHEET = "Training Cards"
    STARTER_PACK_SHEET = "Starter Pack"
    TOURNAMENT_SHEET = "Tournaments"

    CARD_HEADER = [
        "Rarity",
        "Type",
        "Subtype",
        "Card Name",
        "Race",
        "Description",
        "Card Value",
        "Notes",
        "Skill Access"
    ]

    @classmethod
    def cards(cls, reload=False):
        """Returns all cards from the sheet"""
        if not reload and hasattr(cls, "_cards"):
            return cls._cards
        # if they are not leaded yet do it
        client = gspread.authorize(CREDS)
        sheet = client.open_by_key(cls.SPREADSHEET_ID).worksheet(cls.ALL_CARDS_SHEET)
        tmp_cards = sheet.get_all_records()
        cls._cards = []
        for card in tmp_cards:
            for _ in range(int(card['Multiplier'])):
                cls._cards.append(card)
        return cls._cards

    @classmethod
    def starter_cards(cls):
        """Returns starter cards from the sheet"""
        if hasattr(cls, "_starter_cards"):
            return cls._starter_cards
        # if they are not loaded yet do it
        client = gspread.authorize(CREDS)
        sheet = client.open_by_key(cls.SPREADSHEET_ID).worksheet(cls.STARTER_PACK_SHEET)
        cls._starter_cards = sheet.get_all_records()
        return cls._starter_cards

    @classmethod
    def tournaments(cls):
        """Returns torunaments from the sheet"""
        client = gspread.authorize(CREDS)
        sheet = client.open_by_key(cls.SPREADSHEET_ID).worksheet(cls.TOURNAMENT_SHEET)
        return sheet.get_all_records()

#if __name__ == "__main__":
