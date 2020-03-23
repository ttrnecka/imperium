import random
from bot import dice

injuries = {
    1: "Smashed Knee (Niggle)",
    2: "Damaged Back (Niggle)",
    3: "Smashed Ankle (MA-)",
    4: "Smashed Hip (MA-)",
    5: "Serious Concussion (AV-)",
    6: "Fractured Skull (AV-)",
    7: "Broken Neck (AG-)",
    8: "Smashed Collar Bone (STR-)",
}

def injury():
    result = dice.dice(8,1)
    title = "Injury randomizer"
    description = "What is on the menu?"
    value_field1 = injuries.get(result[0])

    return {
        'embed_title': title,
        'embed_desc': description,
        'thumbnail_url': 'https://cdn2.rebbl.net/images/skills/SmashedHand.png',
        'embed_fields': [
            {
                'name': f':game_die: : {",".join(map(str,result))}',
                'value': value_field1,
                'inline': False,
            }
        ],
        'rolls': result
    }