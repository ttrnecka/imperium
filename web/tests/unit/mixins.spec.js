import { shallowMount } from '@vue/test-utils';
import Cards from '@/mixins/cards';

const card_1 = {
  template: {
    description: 'Has **Payout**',
    skill_access: 'GS',
  },
};

const Component = {
  render() {},
  mixins: [Cards],
};

let wrapper;

beforeAll(() => {
  wrapper = shallowMount(Component);
});
describe('Cards Mixin', () => {  
  it('has_keyword returns true for Payout', () => {
    expect(wrapper.vm.has_keyword(card_1, 'Payout')).toBe(true);
  });
  it('has_keyword returns false for Payout!', () => {
    expect(wrapper.vm.has_keyword(card_1, 'Payout!')).toBe(false);
  });

  it('skill_access_for returns all skills from the access tree', () => {
    const skills = wrapper.vm.skill_access_for(card_1);
    expect(skills).toContain('Dauntless');
    expect(skills).toContain('Break Tackle');
    expect(skills).not.toContain('Hail Mary Pass');
  });

  it('contains correct skill_to_group_map', () => {
    expect(wrapper.vm.skill_to_group_map.Accurate).toBe('P');
    expect(wrapper.vm.skill_to_group_map['Disturbing Presence']).toBe('M');
    expect(wrapper.vm.skill_to_group_map.DisturbingPresence).toBe('M');
  });

  it('is_skill_double - Dodge is double for non A access player', () => {
    expect(wrapper.vm.is_skill_double(card_1, 'Dodge')).toBe(true);
  });

  it('is_skill_double - Mighty Blow is double for non A access player', () => {
    expect(wrapper.vm.is_skill_double(card_1, 'Mighty Blow')).toBe(false);
  });

  it('is_skill_double - Movement Up! is not double', () => {
    expect(wrapper.vm.is_skill_double(card_1, 'Movement Up!')).toBe(false);
  });

  it('is_locked - properly handles in_development_deck and in_imperium_deck flags', () => {
    expect(wrapper.vm.is_locked({ in_development_deck: true, in_imperium_deck: true })).toBe(true);
    expect(wrapper.vm.is_locked({ in_development_deck: false, in_imperium_deck: true })).toBe(true);
    expect(wrapper.vm.is_locked({ in_development_deck: true, in_imperium_deck: false })).toBe(true);
    expect(wrapper.vm.is_locked({ in_development_deck: false, in_imperium_deck: false })).toBe(false);
  });

  it('return proper number of assignments', () => {
    expect(wrapper.vm.number_of_assignments({ template: { card_type: 'Training', description: ' one skill' } })).toEqual(1);
    expect(wrapper.vm.number_of_assignments({ template: { card_type: 'Training', description: ' three skills' } })).toEqual(3);
    expect(wrapper.vm.number_of_assignments({ template: { card_type: 'Training', description: '' } })).toEqual(1);
    expect(wrapper.vm.number_of_assignments({ template: { card_type: 'Player', description: ' one skill' } })).toEqual(0);
    expect(wrapper.vm.number_of_assignments({ template: { card_type: 'Staff', name: 'Bodyguard' } })).toEqual(1);
    expect(wrapper.vm.number_of_assignments({ template: { card_type: 'Staff', name: 'Hired Muscle' } })).toEqual(2);
    expect(wrapper.vm.number_of_assignments({ template: { card_type: 'Staff', name: 'Personal Army' } })).toEqual(3);
    expect(wrapper.vm.number_of_assignments({ template: { card_type: 'Training', name: 'Super Wildcard' } })).toEqual(3);
  });

  it('return default_skills_for_player', () => {
    expect(wrapper.vm.default_skills_for_player({ default_skills: ['Block'] })).toEqual(['Block']);
    expect(wrapper.vm.default_skills_for_player({ default_skills: ['Sidestep'] })).toEqual(['SideStep']);
  });  
});

describe('Cards Mixin skill_names_for_player_card method', () => {
  it('Return empty array for non Player card', () => {
    expect(wrapper.vm.skill_names_for_player_card({ template: { card_type: 'Training' } })).toEqual([]);
  });
  it('Returns skills from description for Legendary, Unique, Induced, Cursed or Blessed player', () => {
    ['Legendary','Unique','Inducement', 'Blessed', 'Cursed'].forEach((r) => {
      expect(wrapper.vm.skill_names_for_player_card({ template: { rarity: r, card_type: 'Player', description: "Block, Dodge." } })).toEqual(["Block", "Dodge"]);
    });
  });
  it('Returns skills from name for Common, Rare or Epic player', () => {
    ['Common','Rare','Epic'].forEach((r) => {
      expect(wrapper.vm.skill_names_for_player_card({ template: { rarity: r, card_type: 'Player', name: "Kick Player" } })).toEqual(["Kick"]);
    });
  });
});

describe('Cards Mixin Cyanide api mapper', () => {
  it('return IncreaseStrength for stregths', () => {
    expect(wrapper.vm.skill_to_api_skill('Strength Up!')).toEqual('IncreaseStrength');
    expect(wrapper.vm.skill_to_api_skill('ST+')).toEqual('IncreaseStrength');
    expect(wrapper.vm.skill_to_api_skill('+ST')).toEqual('IncreaseStrength');
  });
  it('return IncreaseAgility for agility', () => {
    expect(wrapper.vm.skill_to_api_skill('Agility Up!')).toEqual('IncreaseAgility');
    expect(wrapper.vm.skill_to_api_skill('AG+')).toEqual('IncreaseAgility');
    expect(wrapper.vm.skill_to_api_skill('+AG')).toEqual('IncreaseAgility');
  });
  it('return IncreaseMovement for agility', () => {
    expect(wrapper.vm.skill_to_api_skill('Movement Up!')).toEqual('IncreaseMovement');
    expect(wrapper.vm.skill_to_api_skill('MA+')).toEqual('IncreaseMovement');
    expect(wrapper.vm.skill_to_api_skill('+MA')).toEqual('IncreaseMovement');
  });
  it('return IncreaseArmour for armour', () => {
    expect(wrapper.vm.skill_to_api_skill('Armour Up!')).toEqual('IncreaseArmour');
    expect(wrapper.vm.skill_to_api_skill('AV+')).toEqual('IncreaseArmour');
    expect(wrapper.vm.skill_to_api_skill('+AV')).toEqual('IncreaseArmour');
  });
  it('return NervesOfSteel', () => {
    expect(wrapper.vm.skill_to_api_skill('Nerves of Steel')).toEqual('NervesOfSteel');
  });
  it('return SideStep', () => {
    expect(wrapper.vm.skill_to_api_skill('Sidestep')).toEqual('SideStep');
  });
  it('return empty for Mutant', () => {
    expect(wrapper.vm.skill_to_api_skill('Mutant Roshi\'s Scare School')).toEqual('');
  });
  it('return KickOffReturn for Kick-Off Return', () => {
    expect(wrapper.vm.skill_to_api_skill('Kick-Off Return')).toEqual('KickOffReturn');
  });
  it('return SmashedCollarBone for Smashed Collarbone', () => {
    expect(wrapper.vm.injury_to_api_injury('Smashed Collarbone')).toEqual('SmashedCollarBone');
  });
  it('return - and spaces removed', () => {
    expect(wrapper.vm.injury_to_api_injury('Smashed Hip')).toEqual('SmashedHip');
    expect(wrapper.vm.injury_to_api_injury('Broken-Neck')).toEqual('BrokenNeck');
  });
});

describe('Cards Mixin injury_names_for_player_card method', () => {
  it('return empty array for non Player card', () => {
    expect(wrapper.vm.injury_names_for_player_card({ template: { card_type: 'Training' } })).toEqual([]);
  });
  it('Returns injuries from description for Legendary, Unique, Induced, Cursed or Blessed player', () => {
    ['Legendary','Unique','Inducement', 'Blessed', 'Cursed'].forEach((r) => {
      expect(wrapper.vm.injury_names_for_player_card({ template: { rarity: r, card_type: 'Player', description: "Block, Dodge. Broken Neck." } })).toEqual(["BrokenNeck"]);
    });
  });
  it('Returns injuries from name for Common, Rare or Epic player', () => {
    ['Common','Rare','Epic'].forEach((r) => {
      expect(wrapper.vm.injury_names_for_player_card({ template: { rarity: r, card_type: 'Player', name: "Broken Neck, Smashed Collarbone Kicker" } })).toEqual(["BrokenNeck", "SmashedCollarBone"]);
    });
  });
});

describe('Cards Mixin cards value', () => {
  it('return 0 for starter cards', () => {
    const cards = [
      { is_starter: true, template: { value: 10 }},
      { is_starter: true, template: { value: 20 }},
    ]
    expect(wrapper.vm.cardsValue(cards)).toEqual(0);
  });
  it('return sum of non-starter cards', () => {
    const cards = [
      { is_starter: true, template: { value: 10 }},
      { is_starter: false, template: { value: 20 }},
    ]
    expect(wrapper.vm.cardsValue(cards)).toEqual(20);
  });
});

describe('Cards Mixin injury picker opened', () => {
  it('return true', () => {
    expect(wrapper.vm.injuryPickerOpened({ cas_pick: false})).toBeTruthy();
    expect(wrapper.vm.injuryPickerOpened({})).toBeTruthy();
  });
  it('return false', () => {
    expect(wrapper.vm.injuryPickerOpened({ cas_pick: true})).toBeFalsy();
  });
  
});

describe('Cards Mixin isEnabled', () => {
  const card = {
    id: 1,
  }
  it('return true if no deck', () => {
    wrapper.vm.deck = {};
    expect(wrapper.vm.isEnabled(card)).toBeTruthy();
  });

  it('return true if deck but disabled_cards is empty', () => {
    wrapper.vm.deck = { id: 1, disabled_cards: [] };
    expect(wrapper.vm.isEnabled(card)).toBeTruthy();
  });

  it('return true if deck, disabled_cards is not empty', () => {
    wrapper.vm.deck = { id: 1, disabled_cards: ['1']};
    expect(wrapper.vm.isEnabled(card)).toBeFalsy();
  });
});

describe('Cards Mixin card_id_or_uuid', () => {
  it('return id as string if provided', () => {
    const card = { id: 1, uuid: '32f3' }
    expect(wrapper.vm.card_id_or_uuid(card)).toEqual('1');
  });
  it('return uuid as string if id not provided', () => {
    const card = { id: undefined, uuid: '32f3' }
    expect(wrapper.vm.card_id_or_uuid(card)).toEqual('32f3');
  });
});

describe('Cards Mixin assigned_cards', () => {
  it('return return cards assigned to card', () => {
    const card1 = { id: 1, uuid: '32f1', assigned_to_array: {} };
    const card2 = { id: 2, uuid: '32f2', assigned_to_array: {1: ['1']} };
    const card3 = { id: 3, uuid: '32f3', assigned_to_array: {} };
    wrapper.vm.cards = [
      card1, card2, card3,
    ]
    wrapper.vm.external_cards = []
    wrapper.vm.deck = {
      id: 1
    }
    expect(wrapper.vm.assigned_cards(card1)).toEqual([card2]);
  });
});