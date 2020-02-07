"""Imperiumr Sheet Service helpers"""
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from misc.helpers import represents_int

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
    TOURNAMENT_SHEET = "Tournaments"
    TOURNAMENT_TEMPLATES_SHEET = "Tournament Templates"
    SPONSOR_SHEET = "Tournament Sponsors"
    ROOM_SHEET = "Tournament Rooms"
    ADMIN_SHEET = "Admins"
    CONCLAVE_SHEET = "Conclave"

    CRACKERSHEET_ID = "1muYufpLnNZueKjkawL3yuKwepnHCccQQWYUL4QNV-Tw"
    CRACKER_TAB = "All Cards"
    

    @classmethod
    def __client(cls):
        return gspread.authorize(CREDS)

    @classmethod
    def __load(cls,sheet_id):
        return cls.__get_sheet(sheet_id).get_all_records()

    @classmethod
    def __get_sheet(cls,sheet_id):
        return cls.__client().open_by_key(cls.SPREADSHEET_ID).worksheet(sheet_id)

    @classmethod
    def templates(cls):
        """Load card templates from the sheet"""
        return cls.__load(cls.ALL_CARDS_SHEET)

    @classmethod
    def tournament_templates(cls):
        """Load card templates from the sheet"""
        return cls.__load(cls.TOURNAMENT_TEMPLATES_SHEET)

    @classmethod
    def tournaments(cls):
        """Returns torunaments from the sheet"""
        return cls.__load(cls.TOURNAMENT_SHEET)

    @classmethod
    def sponsors(cls):
        """Returns sponsors from the sheet"""
        return cls.__load(cls.SPONSOR_SHEET)

    @classmethod
    def admins(cls):
        """Returns admins from the sheet"""
        return cls.__load(cls.ADMIN_SHEET)

    @classmethod
    def rooms(cls):
        """Returns rooms from the sheet"""
        return cls.__load(cls.ROOM_SHEET)
    
    @classmethod
    def conclave_rules(cls):
        """Returns conclave rules from the sheet"""
        return cls.__load(cls.CONCLAVE_SHEET)

    @classmethod
    def max_tournament_id(cls):
        tournaments = cls.tournaments()
        if tournaments and represents_int(tournaments[-1]["Tournament ID"]):
            return int(tournaments[-1]["Tournament ID"])
        else:
            return 0

    @classmethod
    def append_tournaments(cls,tournaments):
        """Adds new tournament to the Tournamnet sheet"""
        max_id = cls.max_tournament_id()
        sheet = cls.__client().open_by_key(cls.SPREADSHEET_ID)
        for i,tournament in enumerate(tournaments,1):
            # ID
            tournament[0] = max_id + i
        sheet.values_append(
            f'{cls.TOURNAMENT_SHEET}', 
            params={'valueInputOption': 'RAW'}, 
            body={'values': tournaments}
        )

    @classmethod
    def find_tournament_index(cls,tournament_id):
        ts = cls.tournaments()
        return next((i+2 for i,tourn in enumerate(ts) if tourn["Tournament ID"]==tournament_id), None)
    
    @classmethod
    def update_tournament(cls, tournament):
        index = cls.find_tournament_index(tournament["Tournament ID"])
        sheet = cls.__get_sheet(cls.TOURNAMENT_SHEET)
        values = list(tournament.values())
        cells = sheet.range(index,1,index,len(values))
        for i,cell in enumerate(cells):
            cell.value = values[i]
        sheet.update_cells(cells)

        
    @classmethod
    def __cracker_load(cls,sheet_id):
        sheet = cls.__client().open_by_key(cls.CRACKERSHEET_ID).worksheet(sheet_id)
        return sheet.get_all_records()
    
    @classmethod
    def cracker_templates(cls):
        """Load card templates from the sheet"""
        return cls.__cracker_load(cls.CRACKER_TAB)
#if __name__ == "__main__":
