const Cards = {
  data() {
    return {
      skill_groups: ['G', 'A', 'P', 'S', 'M'],
      skills: {
        G: ['Dauntless', 'Dirty Player', 'Fend', 'Kick-Off Return', 'Pass Block', 'Shadowing', 'Tackle', 'Wrestle', 'Block', 'Frenzy', 'Kick', 'Pro', 'Strip Ball', 'Sure Hands'],
        A: ['Catch', 'Diving Catch', 'Diving Tackle', 'Jump Up', 'Leap', 'Sidestep', 'SideStep', 'Sneaky Git', 'Sprint', 'Dodge', 'Sure Feet'],
        P: ['Accurate', 'Dump-Off', 'Hail Mary Pass', 'Nerves of Steel', 'Pass', 'Safe Throw', 'Leader'],
        S: ['Break Tackle', 'Grab', 'Juggernaut', 'Multiple Block', 'Piling On', 'Stand Firm', 'Strong Arm', 'Thick Skull', 'Guard', 'Mighty Blow'],
        M: ['Big Hand', 'Disturbing Presence', 'Extra Arms', 'Foul Appearance', 'Horns', 'Prehensile Tail', 'Tentacles', 'Two Heads', 'Very Long Legs', 'Claw'],
      },
      skillreg: /(Diving Catch|Kick-Off Return|Safe Throw|Shadowing|Disturbing Presence|Sneaky Git|Horns|Guard|Mighty Blow|ST\+|\+ST|MA\+|\+MA|AG\+|\+AG|AV\+|\+AV|Block|Accurate|Strong Arm|Dodge|Juggernaut|Claw|Sure Feet|Break Tackle|Jump Up|Two Heads|Wrestle|Frenzy|Multiple Block|Tentacles|Pro|Strip Ball|Sure Hands|Stand Firm|Grab|Hail Mary Pass|Dirty Player|Extra Arms|Foul Appearance|Dauntless|Thick Skull|Tackle|Nerves of Steel|Catch|Pass Block|Piling On|Pass|Fend|Sprint|Grab|Kick|Pass Block|Leap|Sprint|Leader|Diving Tackle|Tentacles|Prehensile Tail|Sidestep|Dump-Off|Big Hand|Very Long Legs)( |,|\.|$)/g,
    };
  },
  methods: {
    has_keyword(card, keyword) {
      const regex = new RegExp(`\\*\\*${keyword}\\*\\*`, 'i');
      if (regex.exec(card.template.description) !== null) {
        return true;
      }
      return false;
    },
    skill_access_for(card) {
      const groups = card.template.skill_access.split('');
      const skillArray = groups.map((e) => this.skills[e]);
      return Array.prototype.concat.apply([], skillArray);
    },
    is_skill_double(playerCard, skill) {
      return !(playerCard.template.skill_access.indexOf(this.skill_to_group_map[skill]) > -1);
    },
    is_locked(card) {
      return (card.in_development_deck || card.in_imperium_deck);
    },
    number_of_assignments(card) {
      if (card.template.name === 'Bodyguard') {
        return 1;
      }
      if (card.template.name === 'Hired Muscle') {
        return 2;
      }
      if (card.template.name === 'Personal Army') {
        return 3;
      }
      if (card.template.card_type !== 'Training') {
        return 0;
      }
      if (card.template.name === 'Super Wildcard') {
        return 3;
      }
      if (card.template.description.match(/ one /)) {
        return 1;
      }
      if (card.template.description.match(/ three /)) {
        return 3;
      }
      return 1;
    },
    skill_names_for_player_card(card) {
      if (card.template.card_type !== 'Player') {
        return [];
      }
      let str;
      if (['Unique', 'Legendary', 'Inducement', 'Blessed', 'Cursed'].includes(card.template.rarity)) {
        str = card.template.description;
      } else {
        str = card.template.name;
      }
      const matches = [];
      let match;
      match = this.skillreg.exec(str);
      while (match) {
        if (!(match.input.match('Pro Elf') && match[1] === 'Pro')) {
          if (match[1]) {
            matches.push(match[1]);
          } else if (match[2]) {
            matches.push(match[2]);
          }
        }

        if (this.skillreg.lastIndex === match.index) {
          this.skillreg.lastIndex += 1;
        }
        match = this.skillreg.exec(str);
      }
      return matches.map((s) => this.skill_to_api_skill(s));
    },
    skill_to_api_skill(skill) {
      let name;
      switch (skill) {
        case 'Strength Up!':
        case 'ST+':
        case '+ST':
          name = 'IncreaseStrength';
          break;
        case 'Agility Up!':
        case 'AG+':
        case '+AG':
          name = 'IncreaseAgility';
          break;
        case 'Movement Up!':
        case 'MA+':
        case '+MA':
          name = 'IncreaseMovement';
          break;
        case 'Armour Up!':
        case 'AV+':
        case '+AV':
          name = 'IncreaseArmour';
          break;
        case 'Nerves of Steel':
          name = 'NervesOfSteel';
          break;
        case 'Sidestep':
          name = 'SideStep';
          break;
        default:
          name = skill.replace(/[\s-]/g, '');
      }
      return name;
    },
  },
  computed: {
    skill_to_group_map() {
      const map = {};
      this.skill_groups.forEach((g) => {
        this.skills[g].forEach((e) => { map[e] = g; });
        this.skills[g].forEach((e) => { map[e.replace(/[\s-]/g, '')] = g; });
      });
      return map;
    },
  },
};

export { Cards as default };
