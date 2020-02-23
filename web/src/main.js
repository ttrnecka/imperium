import Vue from 'vue';
import axios from 'axios';
import VueAxios from 'vue-axios';
import 'bootstrap';
// import { BootstrapVue, IconsPlugin } from 'bootstrap-vue';
import $ from 'jquery';
import showdown from 'showdown';
import App from './App.vue';
import VueFlashMessage from './components/VueFlashMessage/index';

import 'bootstrap/dist/css/bootstrap.css';
import './assets/css/main.css';
// import 'bootstrap-vue/dist/bootstrap-vue.css';

Vue.use(VueAxios, axios);
// Vue.use(BootstrapVue);
// Vue.use(IconsPlugin);
Vue.use(VueFlashMessage);
Vue.prototype.$ = $;

Vue.config.productionTip = false;

Vue.mixin({
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
      skills: {
        G: ['Dauntless', 'Dirty Player', 'Fend', 'Kick-Off Return', 'Pass Block', 'Shadowing', 'Tackle', 'Wrestle', 'Block', 'Frenzy', 'Kick', 'Pro', 'Strip Ball', 'Sure Hands'],
        A: ['Catch', 'Diving Catch', 'Diving Tackle', 'Jump Up', 'Leap', 'Sidestep', 'SideStep', 'Sneaky Git', 'Sprint', 'Dodge', 'Sure Feet'],
        P: ['Accurate', 'Dump-Off', 'Hail Mary Pass', 'Nerves of Steel', 'Pass', 'Safe Throw', 'Leader'],
        S: ['Break Tackle', 'Grab', 'Juggernaut', 'Multiple Block', 'Piling On', 'Stand Firm', 'Strong Arm', 'Thick Skull', 'Guard', 'Mighty Blow'],
        M: ['Big Hand', 'Disturbing Presence', 'Extra Arms', 'Foul Appearance', 'Horns', 'Prehensile Tail', 'Tentacles', 'Two Heads', 'Very Long Legs', 'Claw'],
      },
      card_types: ['Player', 'Training', 'Special Play', 'Reaction', 'Staff', 'Upgrade'],
      deck_card_types: ['Player', 'Training', 'Special Play', 'Staff'],
      show_starter: 1,
      rarity_order: 1,
      skillreg: /(Diving Catch|Kick-Off Return|Safe Throw|Shadowing|Disturbing Presence|Sneaky Git|Horns|Guard|Mighty Blow|ST\+|\+ST|MA\+|\+MA|AG\+|\+AG|AV\+|\+AV|Block|Accurate|Strong Arm|Dodge|Juggernaut|Claw|Sure Feet|Break Tackle|Jump Up|Two Heads|Wrestle|Frenzy|Multiple Block|Tentacles|Pro|Strip Ball|Sure Hands|Stand Firm|Grab|Hail Mary Pass|Dirty Player|Extra Arms|Foul Appearance|Dauntless|Thick Skull|Tackle|Nerves of Steel|Catch|Pass Block|Piling On|Pass|Fend|Sprint|Grab|Kick|Pass Block|Leap|Sprint|Leader|Diving Tackle|Tentacles|Prehensile Tail|Sidestep|Dump-Off|Big Hand|Very Long Legs)( |,|\.|$)/g,
      injuryreg: /(Smashed Knee|Damaged Back|Niggle|Smashed Ankle|Smashed Hip|Serious Concussion|Fractured Skull|Broken Neck|Smashed Collarbone)( |,|\.|$)/g,
      markdown: new showdown.Converter(),
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
    is_skill_double(playerCard, skill) {
      if (['Strength Up!', 'Agility Up!', 'Movement Up!', 'Armour Up!', 'IncreaseMovement', 'IncreaseMovement', 'IncreaseStrength', 'IncreaseAgility'].includes(skill)) {
        return false;
      }
      if (playerCard.template.skill_access.indexOf(this.skill_to_group_map[skill]) > -1) {
        // single
        return false;
      }
      // double
      return true;
    },
    skill_access_for(access) {
      const groups = access.split('');
      const skillArray = groups.map((e) => this.skills[e]);
      return Array.prototype.concat.apply([], skillArray);
    },
    race(raceid) {
      const team = this.mixed_teams.find((t) => t.idraces === raceid);
      if (team) {
        return team.name;
      }
      return 'Unknown race';
    },
    positional_from_api(positional) {
      const names = positional.split('_');
      names.shift();
      return names.join(' ');
    },
    stadium_enhacement(team) {
      const building = team.cards.find((c) => c.type === 'Building');
      if (building) {
        switch (building.name) {
          case 'Bazar':
            return 'Magician\'s Shop';
          case 'SecurityArea':
            return 'Security Gate';
          case 'RefreshmentArea':
            return 'Beer Stand';
          case 'RefereeArea':
            return 'Referee Rest Area';
          case 'Astrogranit':
            return 'Astrogranite';
          case 'ElfTurf':
            return 'Elf Turf';
          case 'VIPArea':
            return 'Royal Box';
          case 'FoodArea':
            return 'Squig Sandwich Kiosk';
          case 'Nuffle':
            return 'Nuffle Altar';
          case 'Roof':
            return 'Magic Dome';
          default:
            return 'None';
        }
      }
      return 'None';
    },
    rarityclass(rarity) {
      let klass;
      switch (rarity) {
        case 'Common':
        case 'Starter':
          klass = 'table-light';
          break;
        case 'Rare':
          klass = 'table-info';
          break;
        case 'Epic':
          klass = 'table-danger';
          break;
        case 'Legendary':
          klass = 'table-warning';
          break;
        case 'Unique':
          klass = 'table-success';
          break;
        case 'Inducement':
        case 'Blessed':
        case 'Cursed':
          klass = 'table-inducement';
          break;
        default:
          klass = 'table-light';
      }
      return klass;
    },
    cardsValue(cards) {
      return cards.reduce((total, e) => {
        if (e.is_starter) {
          return total + 0;
        }
        return total + e.template.value;
      }, 0);
    },
    sortedCards(cards) {
      if (this.rarity_order === 0) {
        return cards;
      }
      const order = this.rarityorder;
      function compare(a, b) {
        return (order[a.template.rarity] - order[b.template.rarity])
          || a.template.name.localeCompare(b.template.name);
      }
      return cards.slice().sort(compare);
    },

    sortedCardsWithoutQuantity(cards, filter = '', mixedFilter = true) {
      let tmCards;
      if (!this.show_starter) {
        tmCards = cards.filter((i) => !i.is_starter);
      } else {
        tmCards = cards;
      }
      if (filter !== '') {
        tmCards = tmCards.filter((i) => i.template.card_type === filter);
      }

      if (this.selected_team !== 'All' && filter === 'Player' && mixedFilter) {
        const { races } = this.mixed_teams.find((e) => e.name === this.selected_team);
        tmCards = tmCards.filter((i) => i.template.race.split('/').some((r) => races.includes(r)));
      }
      return this.sortedCards(tmCards);
    },

    sortedCardsWithQuantity(cards, filter = '') {
      const newCollection = {};
      const sorted = this.sortedCardsWithoutQuantity(cards, filter);
      for (let i = 0, len = sorted.length; i < len; i += 1) {
        const { name } = sorted[i].template;
        if (Object.prototype.hasOwnProperty.call(newCollection, name)) {
          newCollection[name].quantity += 1;
        } else {
          newCollection[name] = {};
          newCollection[name].card = sorted[i];
          newCollection[name].quantity = 1;
        }
      }
      return newCollection;
    },
    is_locked(card) {
      if (card.in_development_deck || card.in_imperium_deck) {
        return true;
      }
      return false;
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
    imgs_for_skill(skill, double = false) {
      const name = this.skill_to_api_skill(skill);
      const url = 'https://cdn2.rebbl.net/images/skills/';
      const doubleClass = double ? 'skill_double' : 'skill_single';
      return `<img class="skill_icon "${doubleClass}" src="${url + name}.png" title="${skill}"></img>`;
    },
    skill_names_for_player_card(card) {
      if (card.template.card_type !== 'Player') {
        return card.template.name;
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
    injury_names_for_player_card(card) {
      if (card.template.card_type !== 'Player') {
        return card.template.name;
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
    skills_for_player(card) {
      const matches = this.skill_names_for_player_card(card);
      return matches.map((s) => this.imgs_for_skill(s)).join('');
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
        if (!(card.name === 'The Apple Pie Killer' && match[1] === 'Block')) {
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
          skills = [];
          break;
        default:
          skills = [card.template.name];
      }
      return skills;
    },
    skills_for(card, double = false) {
      if (card.template.card_type === 'Player') {
        return this.skills_for_player(card);
      }
      if (['Special Play', 'Staff', 'Upgrade', 'Reaction'].includes(card.template.card_type)) {
        return this.skills_for_special_and_staff(card);
      }
      const skills = this.skill_names_for(card);
      const imgs = skills.map((s) => this.imgs_for_skill(s, double));
      return imgs.join('');
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
    print_date(pdate) {
      const jdate = new Date(pdate);
      const options = {
        year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric',
      };
      return jdate.toLocaleDateString('default', options);
    },
    per_game(total, games) {
      // at least minimum of 6 games
      if (games >= 6) {
        return total / games;
      }
      return 0;
    },
  },
  computed: {
    skill_to_group_map() {
      const map = {};
      ['G', 'A', 'P', 'S', 'M'].forEach((g) => {
        this.skills[g].forEach((e) => { map[e] = g; });
        this.skills[g].forEach((e) => { map[e.replace(/[\s-]/g, '')] = g; });
      });
      return map;
    },
  },
});

new Vue({
  render: (h) => h(App),
}).$mount('#app');
