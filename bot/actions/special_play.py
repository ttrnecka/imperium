import random
from bot import dice
from misc.helpers import CardHelper, PackHelper
from misc.decorators import remove_session
from services import TournamentService, CoachService, PackService, DeckService, CardService
from models.data_models import Coach, db

def get_coach_deck_for_room_or_raise(room, coach):
    tourn = TournamentService.get_tournament_using_room(room)
    deck = [ts.deck for ts in tourn.tournament_signups if ts.coach == coach]
    if not deck:
        raise Exception(f"#{coach.short_name()} is not signed into the tournament. Nice try!")
    return deck[0]

def randomize_packs(decks, packs):
    local_skill_map = {}
    result = []
    for pack in packs:
      for card in pack.cards:
        deck = random.choice(decks)
        coach = deck.tournament_signup.coach
        sorted_player_cards = CardHelper.sort_cards_by_rarity(DeckService.assignable_players(deck))
        player_list = DeckService.eligible_players(deck, card)
        skills = CardService.skill_names_for(card, api_format=False)
        # variable used to check if the multitarget cards is not given to the same target 
        local_assigned_cards = []
        for _ in range(CardService.number_of_assignments(card)):
          local_player_list = [player for player in player_list if CardService.valid_skill_combination(local_skill_map.get(CardService.card_id_or_uuid(player), []), skills+DeckService.skills_for(deck, player, api_format=False)) \
            and player not in local_assigned_cards]

          selected = None

          if local_player_list:
            selected = random.choice(local_player_list)
            uid = CardService.card_id_or_uuid(selected)
            if not uid in local_skill_map:
              local_skill_map[uid] = []  
            local_skill_map[uid].extend(skills)
            local_assigned_cards.append(selected)

          idx = None
          if selected:
            # get player index in the deck
            idx = sorted_player_cards.index(selected) + 1
            if isinstance(selected, dict):
              value = f'{idx}. {selected["template"]["name"]} ({coach.short_name()})'
            else:
              value = f'{idx}. {selected.template.name} ({coach.short_name()})'
          else:
            value = f"No eligible player has been found ({coach.short_name()})"
          result.append({
            'card': card,
            'coach': coach,
            'player': selected,
            'idx': idx,
            'value': value,
          })
    return result

def Bullcanoe():
    result = dice.dice(2,1)
    title = "Bullcanoe!"
    subtitles = ['*Get the paddles ready!*','*it definitely rhymes with volcano!*']
    skills = ['Sprint & Sure Feet', 'Mighty Blow & Piling On']
    description = subtitles[result[0]-1]
    value_field1 = f'All players with Strength 4 or higher gain {skills[result[0]-1]}'

    return {
        'embed_title': title,
        'embed_desc': description,
        'thumbnail_url': 'https://cdn2.rebbl.net/images/skills/PositiveRookieSkills.png',
        'embed_fields': [
            {
                'name': f':game_die: : {",".join(map(str,result))}',
                'value': value_field1,
                'inline': False,
            }
        ],
        'rolls': result
    }

def TailsNeverFails():
    result = dice.dice(2,3)
    title = "Tails Never Fails"
    description = "Or does it?"
    ef1 = {
        'name': f':game_die: : {",".join(map(str,result))}',
        'value': 'You **must** use the following skills and **obey doubles restrictions**.',
        'inline': False,
    }
    first =['Diving Catch', 'Diving Tackle']
    second=['Pass Block', 'Block']
    third =['Sure Feet', 'Sure Hands']
    ef2 = {
        'name': 'First roll',
        'value': first[result[0]-1],
        'inline': True,
    }
    ef3 = {
        'name': 'Second roll',
        'value': second[result[1]-1],
        'inline': True,
    }
    ef4 = {
        'name': 'Third roll',
        'value': third[result[2]-1],
        'inline': True,
    }
    return {
        'embed_title': title,
        'embed_desc': description,
        'thumbnail_url': 'https://cdn2.rebbl.net/images/skills/PrehensileTail.png',
        'embed_fields': [ ef1, ef2, ef3, ef4 ],
        'rolls': result
    }

def Gnomercy():
    result = dice.dice(1,3)
    title = "Gnomercy"
    description = ""
    
    if result[0] == 1:
        value = "AG+, Leap and Sure Feet"
    if result[0] == 2:
        value = "Block, Tackle and Mighty Blow"
    if result[0] == 3:
        value = "Wrestle, Tackle and Strip Ball"

    ef1 = {
        'name': f':game_die: : {result[0]}',
        'value': f'Assign {value} to the **targeted** halfling/gnoblar',
        'inline': False,
    }

    return {
        'embed_title': title,
        'embed_desc': description,
        'thumbnail_url': 'https://cdn2.rebbl.net/images/skills/Stunty.png',
        'embed_fields': [ ef1 ],
        'rolls': result
    }

def EverythingMustGo():
    result = dice.dice(6,1)
    title = 'Everything must go!'
    description = ""
    ef1 = {
        'name': f':game_die: : {",".join(map(str,result))}',
        'value': f'Each team in the tournament must apply **{result[0]} -AV injuries** to their team.\nEach coach may choose which of their own team players will be affected. No player may take more than one -AV injury as a result of this card.',
        'inline': False,
    }
    return {
        'embed_title': title,
        'embed_desc': description,
        'thumbnail_url': 'https://cdn2.rebbl.net/images/skills/ArmourBust.png',
        'embed_fields': [ef1],
        'rolls': result
    }

def HalflingMasterCoaches():
    result = dice.dice(6,3)
    title = 'Halfling Master Coaches'
    description = ""
    success = sum(x > 3 for x in result)
    ef1 = {
        'name': f':game_die: : {",".join(map(str,result))}',
        'value': f'You gain {success} assistant coaches.\nAll your opponents loose {success} assistant coaches.',
        'inline': False,
    }
    return {
        'embed_title': title,
        'embed_desc': description,
        'thumbnail_url': 'https://cdn2.rebbl.net/images/skills/CoachSkill.png',
        'embed_fields': [ef1],
        'rolls': result
    }

def HalflingMasterCheerleaders():
    result = dice.dice(6,3)
    title = 'Halfling Master Cheerleaders'
    description = ""
    success = sum(x > 3 for x in result)
    ef1 = {
        'name': f':game_die: : {",".join(map(str,result))}',
        'value': f'You gain {success} cheerleaders.\nAll your opponents loose {success} cheerleaders.',
        'inline': False,
    }
    return {
        'embed_title': title,
        'embed_desc': description,
        'thumbnail_url': 'https://cdn2.rebbl.net/images/sponsors/mcmurtys.png',
        'embed_fields': [ef1],
        'rolls': result
    }

@remove_session
def CelebrityMasterChef(room, caller: Coach):
    tourn = TournamentService.get_tournament_using_room(room)
    coaches = TournamentService.coaches_for(tourn)

    if not caller in coaches:
        raise f"#{caller.short_name()} is not signed into the tournament"
    coaches.remove(caller)

    title = 'Celebrity Master Chef'
    description = ""
    
    result = dice.dice(6,1)[0]
    if result >= 4:
        value = f'{caller.mention()} gains one team re-roll.'
    else:
        value = f'{caller.mention()} gains no re-roll.'

    efs = [{
        'name': f':game_die: : {result}',
        'value': value,
        'inline': False,
    }]

    for coach in coaches:
        result = dice.dice(6,1)[0]
        if result < 4:
            value = f'{coach.mention()} loses one team re-roll.'
        else:
            value = f'{coach.mention()} does not lose re-roll.'
        
        efs.append({
            'name': f':game_die: : {result}',
            'value': value,
            'inline': True,
        })

    return {
        'embed_title': title,
        'embed_desc': description,
        'thumbnail_url': 'https://cdn2.rebbl.net/images/cards/chef_small.png',
        'embed_fields': efs,
        'rolls': result
    }

@remove_session
def CoM2000(room, caller: Coach):
    deck = get_coach_deck_for_room_or_raise(room, caller)

    title = 'Coach-o-Matic 2000'
    description = ""
    with db.session.no_autoflush:
      pack = PackService.generate('skill')
      message = PackHelper.format_pack(pack.cards, show_hidden=True)
      efs = [{
          'name': 'Skill Pack',
          'value': message,
          'inline': False,
      }]
      randomized = randomize_packs([deck], [pack])
      for card in randomized:
        efs.append({
          'name': f'{card["card"].template.name}',
          'value': card['value'],
          'inline': False,
        })

    return {
        'embed_title': title,
        'embed_desc': description,
        'thumbnail_url': 'https://cdn2.rebbl.net/images/sponsors/goblinbambling.png',
        'embed_fields': efs,
        'rolls': pack
    }

@remove_session
def CoM5000(room, caller: Coach):
    deck = get_coach_deck_for_room_or_raise(room, caller)
    title = 'Coach-o-Matic 5000'
    description = ""
    packs = []
    efs = []
    with db.session.no_autoflush:
        pack = PackService.generate('skill')
        packs.append(pack)
        message = PackHelper.format_pack(pack.cards, show_hidden=True)
        efs.append({
            'name': 'Skill Pack',
            'value': message,
            'inline': False,
        })
        pack = PackService.generate('coaching')
        packs.append(pack)
        message = PackHelper.format_pack(pack.cards, show_hidden=True)
        efs.append({
            'name': 'Coaching Pack',
            'value': message,
            'inline': False,
        })
        randomized = randomize_packs([deck], packs)
        for card in randomized:
            efs.append({
            'name': f'{card["card"].template.name}',
            'value': card['value'],
            'inline': False,
            })
    return {
        'embed_title': title,
        'embed_desc': description,
        'thumbnail_url': 'https://cdn2.rebbl.net/images/sponsors/goblinbambling.png',
        'embed_fields': efs,
        'rolls': packs
    }

@remove_session
def CoM9000(room, caller: Coach):
    deck = get_coach_deck_for_room_or_raise(room, caller)
    title = 'Coach-o-Matic 9000'
    description = ""
    packs = []
    efs = []
    with db.session.no_autoflush:
        for i in range(3):
            pack = PackService.generate('coaching')
            packs.append(pack)
            message = PackHelper.format_pack(pack.cards, show_hidden=True)
            efs.append({
                'name': f'Coaching Pack {i + 1}',
                'value': message,
                'inline': False,
            })
        randomized = randomize_packs([deck], packs)
        for card in randomized:
            efs.append({
            'name': f'{card["card"].template.name}',
            'value': card['value'],
            'inline': False,
            })
    return {
        'embed_title': title,
        'embed_desc': description,
        'thumbnail_url': 'https://cdn2.rebbl.net/images/sponsors/goblinbambling.png',
        'embed_fields': efs,
        'rolls': packs
    }

@remove_session
def CoMWithFriends(room, caller: Coach):
    tourn = TournamentService.get_tournament_using_room(room)
    decks = [ts.deck for ts in tourn.tournament_signups]
    deck = get_coach_deck_for_room_or_raise(room, caller)
    decks.remove(deck)

    title = 'Coach-o-Matic With Your Friends'
    description = ""
    packs = []
    efs = []
    with db.session.no_autoflush:
        pack = PackService.generate('skill')
        packs.append(pack)
        message = PackHelper.format_pack(pack.cards, show_hidden=True)
        efs.append({
            'name': f'Skill Pack',
            'value': message,
            'inline': False,
        })
        randomized = randomize_packs(decks, packs)
        for card in randomized:
            efs.append({
            'name': f'{card["card"].template.name}',
            'value': card['value'],
            'inline': False,
            })
    return {
        'embed_title': title,
        'embed_desc': description,
        'thumbnail_url': 'https://cdn2.rebbl.net/images/sponsors/goblinbambling.png',
        'embed_fields': efs,
        'rolls': packs
    }

@remove_session
def SoM3000(room, caller: Coach):
    tourn = TournamentService.get_tournament_using_room(room)
    coaches = TournamentService.coaches_for(tourn)

    if not caller in coaches:
        raise f"#{caller.short_name()} is not signed into the tournament"

    title = 'Stadium-o-Matic 3000'
    description = "Each team in the tournament receives a random stadium enhancement"
    efs = []

    stadiums = {
      1: 'Security Gate',
      2: 'Beer Stand',
      3: 'Magician\' Shop',
      4: 'Referee Rest Area',
      5: 'Astrogranite',
      6: 'Elf Turf',
      7: 'Royal Box',
      8: 'Squig Sandwich Kiosk',
      9: 'Magic Dome',
      10: 'Nuffle\'s Altar'
    }

    for coach in coaches:
        result = dice.dice(10,1)[0]
        value = f'{coach.mention()} gets {stadiums.get(result)}'
        efs.append({
            'name': f':game_die: : {result}',
            'value': value,
            'inline': True,
        })

    return {
        'embed_title': title,
        'embed_desc': description,
        'thumbnail_url': 'https://cdn2.rebbl.net/images/stadium/refreshmentarea.png',
        'embed_fields': efs,
        'rolls': result
    }

def ReturnOfTheKing():
    result = dice.dice(6,1)
    title = "Return Of The King!"
    skills = ['Agility Up!', 'Strength Up!', '2 x Strength Up!']
    description = ""
    if result[0] in [1,2,3]:
        gain = skills[0]
    elif result[0] in [4,5]:
        gain = skills[1]
    else:
        gain = skills[2]
    value_field1 = f'King Arthur gains {gain}'

    return {
        'embed_title': title,
        'embed_desc': description,
        'thumbnail_url': 'https://cdn2.rebbl.net/images/logo/256x256/logo_bretonnia_02.png',
        'embed_fields': [
            {
                'name': f':game_die: : {",".join(map(str,result))}',
                'value': value_field1,
                'inline': False,
            }
        ],
        'rolls': result
    }

@remove_session
def CommentatorsCurse(room, caller: Coach):
    tourn = TournamentService.get_tournament_using_room(room)
    coaches = TournamentService.coaches_for(tourn)

    if not caller in coaches:
        raise f"#{caller.short_name()} is not signed into the tournament"

    title = 'Commentator\'s Curse'
    description = ""
    coaches.remove(caller)

    caller_curse2 = True
    efs = []
    for coach in coaches:
        result = dice.dice(6,1)[0]
        if result < 3:
            caller_curse2 = False
            value = f'{coach.mention()} rolls !curse 1.'
        else:
            value = f'{coach.mention()} remains uncursed.'
        
        efs.append({
            'name': f':game_die: : {result}',
            'value': value,
            'inline': True,
        })

    result = dice.dice(6,1)[0]
    if result < 3:
        caller_curse2 = False
        value = f'{caller.mention()} rolls !curse 1.'
    else:
        v = 1
        if caller_curse2:
            v = 2
        value = f'{caller.mention()} rolls !curse {v}'

    efs.append({
        'name': f':game_die: : {result}',
        'value': value,
        'inline': False,
    })

    return {
        'embed_title': title,
        'embed_desc': description,
        'thumbnail_url': 'https://cdn2.rebbl.net/images/cards/dice_small.png',
        'embed_fields': efs,
        'rolls': result
    }