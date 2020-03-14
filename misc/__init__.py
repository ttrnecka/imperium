import re

KEYWORDREG = re.compile(r'\*\*(\S+)\*\*')

def imperium_keywords(text:str):
    return KEYWORDREG.findall(text)


SKILLREG = re.compile(r'(Animosity|Wild Animal|Always Hungry|Throw Team Mate|Decay|Loner|Bombardier|Chainsaw|Nurgles Rot|Bone Head|Stunty|Right Stuff|Titchy|No Hands|Ball Chain|Secret Weapon|Stab|Take Root|Hypnotic Gaze|Bloodlust|Regeneration|Really Stupid|Diving Catch|Kick-Off Return|Safe Throw|Shadowing|Disturbing Presence|Sneaky Git|Horns|Guard|Mighty Blow|ST\+|\+ST|MA\+|\+MA|AG\+|\+AG|AV\+|\+AV|Block|Accurate|Strong Arm|Dodge|Juggernaut|Claw|Sure Feet|Break Tackle|Jump Up|Two Heads|Wrestle|Frenzy|Multiple Block|Tentacles|Pro|Strip Ball|Sure Hands|Stand Firm|Grab|Hail Mary Pass|Dirty Player|Extra Arms|Foul Appearance|Dauntless|Thick Skull|Tackle|Nerves of Steel|Catch|Pass Block|Piling On|Pass|Fend|Sprint|Grab|Kick|Pass Block|Leap|Sprint|Leader|Diving Tackle|Tentacles|Prehensile Tail|Sidestep|Dump-Off|Big Hand|Very Long Legs)( |,|\.|$)')
INJURYREG = re.compile(r'(Smashed Knee|Damaged Back|Niggle|Smashed Ankle|Smashed Hip|Serious Concussion|Fractured Skull|Broken Neck|Smashed Collarbone)( |,|\.|$)')


class KEYWORDS:
  TARGET    = "Target"
  PAYOUT    = "Payout"
  RANDOMISE = "Randomise"
  ENHANCE   = "Enhance"
  IMMUNE    = "Immune"
  ARENA     = "Arena"
  ANNOUNCE  = "Announce"

  def __init__(self, text):
    self.text = text

  def is_target(self):
    return self.TARGET in imperium_keywords(self.text)

  def is_immune(self):
    return self.IMMUNE in imperium_keywords(self.text)

  def is_announce(self):
    return self.ANNOUNCE in imperium_keywords(self.text)

  def is_randomise(self):
    return self.RANDOMISE in imperium_keywords(self.text)