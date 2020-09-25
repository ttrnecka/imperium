const Cards = {
  data() {
    return {
      rarityorder: {
        Starter: 10,
        Common: 9,
        Rare: 8,
        Epic: 7,
        Inducement: 6,
        Blessed: 5,
        Cursed: 4,
        Legendary: 2,
        Unique: 1,
      },
      mixed_teams: [
        {
          idraces: 38,
          code: 'aog',
          tier_tax: 0,
          name: 'Alliance of Goodness',
          races: ['Bretonnian', 'Human', 'Dwarf', 'Halfling', 'Wood Elf'],
        },
        {
          idraces: 42,
          code: 'au',
          tier_tax: 0,
          name: 'Afterlife United',
          races: ['Undead', 'Necromantic', 'Khemri', 'Vampire'],
        },
        {
          idraces: 37,
          code: 'afs',
          tier_tax: 0,
          name: 'Anti-Fur Society',
          races: ['Kislev', 'Norse', 'Amazon', 'Lizardman'],
        },
        {
          idraces: 34,
          code: 'cgs',
          tier_tax: 0,
          name: 'Chaos Gods Selection',
          races: ['Chaos', 'Nurgle'],
        },
        {
          idraces: 33,
          code: 'cpp',
          tier_tax: 0,
          name: 'Chaotic Player Pact',
          races: ['Chaos', 'Skaven', 'Dark Elf', 'Underworld'],
        },
        {
          idraces: 36,
          code: 'egc',
          tier_tax: 0,
          name: 'Elfic Grand Coalition',
          races: ['High Elf', 'Dark Elf', 'Wood Elf', 'Pro Elf'],
        },
        {
          idraces: 35,
          code: 'fea',
          tier_tax: 0,
          name: 'Far East Association',
          races: ['Chaos Dwarf', 'Orc', 'Goblin', 'Skaven', 'Ogre'],
        },
        {
          idraces: 39,
          code: 'hl',
          tier_tax: 0,
          name: 'Human League',
          races: ['Bretonnian', 'Human', 'Kislev', 'Norse', 'Amazon'],
        },
        {
          idraces: 32,
          code: 'sbr',
          tier_tax: 0,
          name: 'Superior Being Ring',
          races: ['Bretonnian', 'High Elf', 'Vampire', 'Chaos Dwarf'],
        },
        {
          idraces: 41,
          code: 'uosp',
          tier_tax: 0,
          name: 'Union of Small People',
          races: ['Ogre', 'Goblin', 'Halfling'],
        },
        {
          idraces: 40,
          code: 'vt',
          tier_tax: 0,
          name: 'Violence Together',
          races: ['Ogre', 'Goblin', 'Orc', 'Lizardman'],
        },
      ],
      skill_groups: ['G', 'A', 'P', 'S', 'M'],
      skills: {
        G: ['Dauntless', 'Dirty Player', 'Fend', 'Kick-Off Return', 'Pass Block', 'Shadowing', 'Tackle', 'Wrestle', 'Block', 'Frenzy', 'Kick', 'Pro', 'Strip Ball', 'Sure Hands'],
        A: ['Catch', 'Diving Catch', 'Diving Tackle', 'Jump Up', 'Leap', 'Sidestep', 'SideStep', 'Sneaky Git', 'Sprint', 'Dodge', 'Sure Feet'],
        P: ['Accurate', 'Dump-Off', 'Hail Mary Pass', 'Nerves of Steel', 'Pass', 'Safe Throw', 'Leader'],
        S: ['Break Tackle', 'Grab', 'Juggernaut', 'Multiple Block', 'Piling On', 'Stand Firm', 'Strong Arm', 'Thick Skull', 'Guard', 'Mighty Blow'],
        M: ['Big Hand', 'Disturbing Presence', 'Extra Arms', 'Foul Appearance', 'Horns', 'Prehensile Tail', 'Tentacles', 'Two Heads', 'Very Long Legs', 'Claw'],
      },
      skillreg: /(Diving Catch|Kick-Off Return|Safe Throw|Shadowing|Disturbing Presence|Sneaky Git|Horns|Guard|Mighty Blow|ST\+|\+ST|MA\+|\+MA|AG\+|\+AG|AV\+|\+AV|Block|Accurate|Strong Arm|Dodge|Juggernaut|Claw|Sure Feet|Break Tackle|Jump Up|Two Heads|Wrestle|Frenzy|Multiple Block|Tentacles|Pro|Strip Ball|Sure Hands|Stand Firm|Grab|Hail Mary Pass|Dirty Player|Extra Arms|Foul Appearance|Dauntless|Thick Skull|Tackle|Nerves of Steel|Catch|Pass Block|Piling On|Pass|Fend|Sprint|Grab|Kick|Pass Block|Leap|Sprint|Leader|Diving Tackle|Tentacles|Prehensile Tail|Sidestep|Dump-Off|Big Hand|Very Long Legs)( |,|\.|$)/g,
      injuryreg: /(Smashed Knee|Damaged Back|Niggle|Smashed Ankle|Smashed Hip|Serious Concussion|Fractured Skull|Broken Neck|Smashed Collarbone)( |,|\.|$)/g,
      nonassignable_exceptions: ['Brock Ferth', 'Snotty', 'Arthur 1-3', 'Arthur 4-5', 'Arthur 6'],
      guards: ['Bodyguard', 'Hired Muscle', 'Personal Army'],
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
      // check if the skill exists in the list
      if (this.skill_to_group_map[skill]) {
        return !(playerCard.template.skill_access.indexOf(this.skill_to_group_map[skill]) > -1);
      }
      return false;
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
      if (card.template.description.match(/ five /)) {
        return 5;
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
    default_skills_for_player(card) {
      if (card.default_skills) {
        const skills = card.default_skills.map((s) => this.skill_to_api_skill(s));
        return skills;
      }
      return [];
    },
    skills_for_player(card) {
      const matches = this.default_skills_for_player(card).concat(this.skill_names_for_player_card(card));
      return matches.map((s) => this.imgs_for_skill(s)).join('');
    },
    skills_for(card, double = false) {
      if (card.template.card_type === 'Player') {
        return this.skills_for_player(card);
      }
      if (['Special Play', 'Staff', 'Upgrade', 'Reaction', 'High Command'].includes(card.template.card_type)) {
        return this.skills_for_special_and_staff(card);
      }
      const skills = this.skill_names_for(card);
      const imgs = skills.map((s) => this.imgs_for_skill(s, double));
      return imgs.join('');
    },
    imgs_for_skill(skill, double = false) {
      const name = this.skill_to_api_skill(skill);
      const url = 'https://cdn2.rebbl.net/images/skills/';
      const doubleClass = double ? 'skill_double' : 'skill_single';
      return `<img class="skill_icon "${doubleClass}" src="${url + name}.png" title="${skill}"></img>`;
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
        case 'Mutant Roshi\'s Scare School':
          return '';
        default:
          name = skill.replace(/[\s-]/g, '');
      }
      return name;
    },
    cardsValue(cards) {
      return cards.reduce((total, e) => {
        if (e.is_starter) {
          return total + 0;
        }
        return total + e.template.value;
      }, 0);
    },
    injury_to_api_injury(injury) {
      let name;
      switch (injury) {
        case 'Smashed Collarbone':
          name = 'SmashedCollarBone';
          break;
        default:
          name = injury.replace(/[\s-]/g, '');
      }
      return name;
    },
    injury_names_for_player_card(card) {
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
      match = this.injuryreg.exec(str);
      while (match) {
        if (match[1]) {
          matches.push(match[1]);
        } else if (match[2]) {
          matches.push(match[2]);
        }

        if (this.injuryreg.lastIndex === match.index) {
          this.injuryreg.lastIndex += 1;
        }
        match = this.injuryreg.exec(str);
      }
      return matches.map((s) => this.injury_to_api_injury(s));
    },
    skills_for_special_and_staff(card) {
      if (!['Special Play', 'Staff', 'Upgrade', 'Reaction'].includes(card.template.card_type)) {
        return card.template.name;
      }
      const str = card.template.description;
      const matches = [];
      let match;
      match = this.skillreg.exec(str);
      while (match) {
        if (!(card.template.name === 'The Apple Pie Killer' && match[1] === 'Block')
            && !(match.input.match('Pro Elf') && match[1] === 'Pro')) {
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
      return matches.map((s) => this.imgs_for_skill(s)).join('');
    },
    skill_names_for(card) {
      let skills = [];
      switch (card.template.name) {
        case 'Block Party':
          skills = ['Block'];
          break;
        case 'Dodge like a Honeybadger, Sting like the Floor':
          skills = ['Tackle'];
          break;
        case 'Gengar Mode':
          skills = ['DirtyPlayer'];
          break;
        case 'Roger Dodger':
          skills = ['Dodge'];
          break;
        case 'Packing a Punch':
          skills = ['MightyBlow'];
          break;
        case 'Ballhawk':
          skills = ['Wrestle', 'Tackle', 'StripBall'];
          break;
        case 'Roadblock':
          skills = ['Block', 'Dodge', 'StandFirm'];
          break;
        case 'Cold-Blooded Killer':
          skills = ['MightyBlow', 'PilingOn'];
          break;
        case 'Sniper':
          skills = ['Accurate', 'StrongArm'];
          break;
        case 'A Real Nuisance':
          skills = ['SideStep', 'DivingTackle'];
          break;
        case 'Insect DNA':
          skills = ['TwoHeads', 'ExtraArms'];
          break;
        case 'Super Wildcard':
          skills = ['MVPCondition'];
          break;
        case 'I Didn\'t Read The Rules':
          skills = ['MVPCondition', 'MVPCondition', 'MVPCondition'];
          break;
        case 'Counterfeit Skill Shop':
          skills = ['DivingTackle'];
          break;
        case 'Laying the Smackdown':
          skills = ['Wrestle'];
          break;
        case 'Need for Speed':
          skills = ['IncreaseMovement'];
          break;
        case 'The Great Wall':
          skills = ['Guard'];
          break;
        case 'Tubthumping':
          skills = ['PilingOn', 'JumpUp', 'Dauntless'];
          break;
        case 'Training Wildcard':
          skills = ['MVPCondition2'];
          break;
        case 'Sidestep':
          skills = ['SideStep'];
          break;
        case 'Crowd Pleaser':
          skills = ['Frenzy', 'Juggernaut'];
          break;
        case 'Designated Ball Carrier':
          skills = ['Block', 'SureHands'];
          break;
        case 'Bodyguard':
        case 'Hired Muscle':
        case 'Personal Army':
        case 'Mutant Roshi\'s Scare School':
          skills = [];
          break;
        case 'Pre-Season Block':
          skills = ['Block'];
          break;
        case 'Pre-Season Dodge':
          skills = ['Dodge'];
          break;
        case 'Pre-Season Guard':
          skills = ['Guard'];
          break;
        case 'Pre-Season Mighty Blow':
          skills = ['Mighty Blow'];
          break;
        case 'Pre-Season Tackle':
          skills = ['Tackle'];
          break;
        default:
          skills = [card.template.name];
      }
      return skills;
    },
    max_uses(card) {
      if (card.template.number_of_uses === 0) {
        return '∞';
      }
      return card.template.number_of_uses;
    },
    dust(method, card) {
      let path;
      if (card) {
        path = `/duster/${method}/${card.id}`;
      } else {
        path = `/duster/${method}`;
      }
      let msg;
      this.processing = true;
      this.axios.get(path)
        .then((res) => {
          if (method === 'add') {
            msg = `Card ${card.template.name} flagged for dusting`;
          } else if (method === 'remove') {
            msg = `Card ${card.template.name} - dusting flag removed`;
          } else if (method === 'cancel') {
            msg = 'Dusting cancelled';
          } else if (method === 'commit') {
            const freeCmd = (res.data.type === 'Tryouts' ? '!genpack player <type>' : '!genpack training or !genpack special');
            msg = `Dusting committed! Use ${freeCmd} to generate a free pack!`;
            this.getCoach(this.loggedCoach.id);
          }
          this.loggedCoach.duster = res.data;
          this.flash(msg, 'success', { timeout: 3000 });
        })
        .catch((error) => {
          if (error.response) {
            this.flash(error.response.data.message, 'error', { timeout: 3000 });
          } else {
            console.error(error);
          }
        })
        .then(() => {
          this.processing = false;
        });
    },
    dust_cancel() {
      this.dust('cancel');
    },
    dust_commit() {
      this.dust('commit');
    },
    dust_add(card) {
      this.dust('add', card);
    },
    dust_remove(card) {
      this.dust('remove', card);
    },
    card_id_or_uuid(card) {
      if (card.id) {
        return String(card.id);
      }
      return String(card.uuid);
    },
    injuryPickerOpened(card) {
      if (card.cas_pick) {
        return false;
      }
      return true;
    },
    isEnabled(card) {
      if (this.deck.id && this.deck.disabled_cards !== '' && this.deck.disabled_cards.includes(this.card_id_or_uuid(card))) {
        return false;
      }
      return true;
    },
    get_card_assignment(card) {
      if (this.deck.id && card.assigned_to_array[this.deck.id]) {
        return card.assigned_to_array[this.deck.id];
      }
      return [];
    },
    assigned_cards(card) {
      return this.cards.filter((c) => this.get_card_assignment(c).includes(this.card_id_or_uuid(card)));
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
