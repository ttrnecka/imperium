import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

ROOT = os.path.dirname(__file__)

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(ROOT, 'config/client_secret.json'), scope)

class ImperiumSheet:
    #SPREADSHEET_ID = "1t5IoiIjPAS2CD63P6xI4hWwx9c1SEzW9AL1LJ4LK6og"
    # dev spreadsheet below
    SPREADSHEET_ID = "1z59ftfIYxsSZ_OwQs2KaFGzSuYizSMdSCdW6DGAj4Ms"
    ALL_CARDS_SHEET = "All Cards"
    TRAINING_CARDS_SHEET = "Training Cards"
    STARTER_PACK_SHEET="Starter Pack"
    TOURNAMENT_SHEET="Tournaments"

    with open(os.path.join(ROOT, 'config/MASTERSHEET_ID'), 'r') as file:
        MASTERSHEET_ID=file.read()

    MASTER_NAME = "Master List"

    CARD_HEADER = [
        "Rarity",
        "Type",
        "Subtype",
        "Card Name",
        "Race",
        "Description",
        "Notes"
    ]
    MASTER_LIST_HEADER = ["Coach"] + CARD_HEADER


    @classmethod
    def cards(cls,reload=False):
        if not reload and hasattr(cls,"_cards"):
            return cls._cards
        # if they are not leaded yet do it
        client = gspread.authorize(creds)
        sheet = client.open_by_key(cls.SPREADSHEET_ID).worksheet(cls.ALL_CARDS_SHEET)
        tmp_cards = sheet.get_all_records()
        cls._cards =  [] 
        for card in tmp_cards:
            for _ in range(int(card['Multiplier'])):
                cls._cards.append(card)
        return cls._cards

    @classmethod
    def starter_cards(cls):
        if hasattr(cls,"_starter_cards"):
            return cls._starter_cards
        # if they are not loaded yet do it
        client = gspread.authorize(creds)
        sheet = client.open_by_key(cls.SPREADSHEET_ID).worksheet(cls.STARTER_PACK_SHEET)
        cls._starter_cards = sheet.get_all_records()
        return cls._starter_cards

    @classmethod
    def tournaments(cls):
        client = gspread.authorize(creds)
        # TODO change the sheet ID
        sheet = client.open_by_key(cls.SPREADSHEET_ID).worksheet(cls.TOURNAMENT_SHEET)
        return sheet.get_all_records()

    @classmethod
    def store_cards(cls,cards):
        client = gspread.authorize(creds)
        ws = client.open_by_key(cls.MASTERSHEET_ID)
        try:
            sheet = ws.worksheet(cls.MASTER_NAME)
        except gspread.exceptions.WorksheetNotFound:
            sheet = ws.add_worksheet(title=cls.MASTER_NAME,rows=100, cols=15)

        sheet.clear()

        cards.insert(0,cls.MASTER_LIST_HEADER)
        cards_amount, keys_amount = len(cards), len(cls.MASTER_LIST_HEADER)

        cell_list = sheet.range(f"A1:{gspread.utils.rowcol_to_a1(cards_amount, keys_amount)}")

        for cell in cell_list:
            if cell.row==1:
                cell.value = cards[cell.row-1][cell.col-1]
            else:
                cell.value = cards[cell.row-1][cls.MASTER_LIST_HEADER[cell.col-1]]
        sheet.update_cells(cell_list)



#if __name__ == "__main__":

