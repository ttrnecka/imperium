const Cards = {
  data() {
    return {
      skills: {
        G: ['Dauntless', 'Dirty Player', 'Fend', 'Kick-Off Return', 'Pass Block', 'Shadowing', 'Tackle', 'Wrestle', 'Block', 'Frenzy', 'Kick', 'Pro', 'Strip Ball', 'Sure Hands'],
        A: ['Catch', 'Diving Catch', 'Diving Tackle', 'Jump Up', 'Leap', 'Sidestep', 'SideStep', 'Sneaky Git', 'Sprint', 'Dodge', 'Sure Feet'],
        P: ['Accurate', 'Dump-Off', 'Hail Mary Pass', 'Nerves of Steel', 'Pass', 'Safe Throw', 'Leader'],
        S: ['Break Tackle', 'Grab', 'Juggernaut', 'Multiple Block', 'Piling On', 'Stand Firm', 'Strong Arm', 'Thick Skull', 'Guard', 'Mighty Blow'],
        M: ['Big Hand', 'Disturbing Presence', 'Extra Arms', 'Foul Appearance', 'Horns', 'Prehensile Tail', 'Tentacles', 'Two Heads', 'Very Long Legs', 'Claw'],
      },
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
};

export { Cards as default };
